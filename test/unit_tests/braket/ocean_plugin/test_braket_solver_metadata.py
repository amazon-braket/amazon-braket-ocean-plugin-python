# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


import pytest

from braket.ocean_plugin import BraketSolverMetadata, InvalidSolverDeviceArn


def test_get_metadata_by_arn(dwave_arn):
    assert isinstance(BraketSolverMetadata.get_metadata_by_arn(dwave_arn), dict)


@pytest.mark.xfail(raises=InvalidSolverDeviceArn)
def test_get_metadata_by_arn_invalid():
    BraketSolverMetadata.get_metadata_by_arn("arn:aws:braket:::device/qpu/foo/DW_2000Q_6")
