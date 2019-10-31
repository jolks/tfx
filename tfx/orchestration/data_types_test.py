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
"""Tests for tfx.orchestration.data_types."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from typing import Text
from tfx.orchestration import data_types


class DataTypesTest(tf.test.TestCase):

  def test_runtime_parameter_sweetpath(self):
    runtime_parameter = data_types.RuntimeParameter(
        name='test-parameter',
        default=u'test-default',
        ptype=Text,
        description='test-description')
    parsed = data_types.RuntimeParameter.parse(runtime_parameter)
    self.assertEqual(parsed.name, 'test-parameter')
    self.assertEqual(parsed.default, 'test-default')
    self.assertEqual(parsed.ptype, Text)
    self.assertEqual(parsed.description, 'test-description')

  def test_runtime_parameter_nonstr_ptype(self):
    with self.assertRaises(TypeError):
      runtime_parameter = data_types.RuntimeParameter(  # pylint: disable=unused-variable
          name='test-parameter', ptype=int)

  def test_runtime_parameter_mismatch_default_ptype(self):
    with self.assertRaises(TypeError):
      runtime_parameter = data_types.RuntimeParameter(  # pylint: disable=unused-variable
          name='test-parameter', ptype=Text, default=42)


if __name__ == '__main__':
  tf.test.main()
