# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for ExampleGen components."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Any, Dict, List, Text

import six
import tensorflow as tf

from tfx.proto import example_gen_pb2


_DEFAULT_ENCODING = 'utf-8'


def dict_to_example(instance: Dict[Text, Any]) -> tf.train.Example:
  """Converts dict to tf example."""
  feature = {}
  for key, value in instance.items():
    # TODO(jyzhao): support more types.
    if value is None:
      feature[key] = tf.train.Feature()
    elif isinstance(value, six.integer_types):
      feature[key] = tf.train.Feature(
          int64_list=tf.train.Int64List(value=[value]))
    elif isinstance(value, float):
      feature[key] = tf.train.Feature(
          float_list=tf.train.FloatList(value=[value]))
    elif isinstance(value, six.text_type) or isinstance(value, str):
      feature[key] = tf.train.Feature(
          bytes_list=tf.train.BytesList(
              value=[value.encode(_DEFAULT_ENCODING)]))
    elif isinstance(value, list):
      if not value:
        feature[key] = tf.train.Feature()
      elif isinstance(value[0], six.integer_types):
        feature[key] = tf.train.Feature(
            int64_list=tf.train.Int64List(value=value))
      elif isinstance(value[0], float):
        feature[key] = tf.train.Feature(
            float_list=tf.train.FloatList(value=value))
      elif isinstance(value[0], six.text_type) or isinstance(value[0], str):
        feature[key] = tf.train.Feature(
            bytes_list=tf.train.BytesList(
                value=[v.encode(_DEFAULT_ENCODING) for v in value]))
      else:
        raise RuntimeError('Column type `list of {}` is not supported.'.format(
            type(value[0])))
    else:
      raise RuntimeError('Column type {} is not supported.'.format(type(value)))
  return tf.train.Example(features=tf.train.Features(feature=feature))


def generate_output_split_names(input_config: example_gen_pb2.Input,
                                output_config: example_gen_pb2.Output
                               ) -> List[Text]:
  """Return output split name based on input and output config.

  Return output split name if it's specified and input only contains one split,
  otherwise output split will be same as input.

  Args:
    input_config: example_gen_pb2.Input instance.
    output_config: example_gen_pb2.Output instance.

  Returns:
    List of split names.

  Raises:
    RuntimeError: if configs are not valid, including:
      - Missing field.
      - Duplicated split.
      - Output split is specified while input has more than one split.
      - Missing train and eval split.
  """
  result = []
  if output_config.split_config.splits:
    if len(input_config.splits) != 1:
      # If output is specified, then there should only be one input split.
      raise RuntimeError(
          'ExampleGen instance specified output splits but at the same time input has more than one split.'
      )
    for split in output_config.split_config.splits:
      if not split.name or split.hash_buckets <= 0:
        raise RuntimeError('Output split name and hash_buckets are required.')
      result.append(split.name)
  else:
    # If output is not specified, it will have the same split as the input.
    for split in input_config.splits:
      if not split.name or not split.pattern:
        raise RuntimeError('Input split name and pattern are required.')
      result.append(split.name)

  if not result:
    raise RuntimeError('ExampleGen splits are missing.')
  if len(result) != len(set(result)):
    raise RuntimeError('Duplicated split name {}.'.format(result))

  return result


def make_default_input_config(split_pattern: Text = '*'
                             ) -> example_gen_pb2.Input:
  """Returns default input config."""
  # Treats input base dir as a single split.
  return example_gen_pb2.Input(splits=[
      example_gen_pb2.Input.Split(name='single_split', pattern=split_pattern)
  ])


def make_default_output_config(input_config: example_gen_pb2.Input
                              ) -> example_gen_pb2.Output:
  """Returns default output config based on input config."""
  if len(input_config.splits) > 1:
    # Returns empty output split config as output split will be same as input.
    return example_gen_pb2.Output()
  else:
    # Returns 'train' and 'eval' splits with size 2:1.
    return example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(splits=[
            example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=2),
            example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=1)
        ]))
