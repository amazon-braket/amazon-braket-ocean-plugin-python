# Copyright 2019-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import copy
import json
from unittest.mock import Mock, patch

import pytest
from boltons.dictutils import FrozenDict
from conftest import (
    sample_ising_common_testing,
    sample_ising_quantum_task_common_testing,
    sample_qubo_common_testing,
    sample_qubo_quantum_task_common_testing,
)
from dimod.exceptions import BinaryQuadraticModelStructureError

from braket.ocean_plugin import (
    BraketSampler,
    BraketSamplerArns,
    BraketSolverMetadata,
    InvalidSolverDeviceArn,
)
from braket.tasks import AnnealingQuantumTaskResult


@pytest.fixture
def braket_dwave_parameters():
    return {"postprocessingType": "SAMPLING"}


@pytest.fixture
def sample_kwargs(braket_dwave_parameters, shots):
    kwargs = copy.deepcopy(braket_dwave_parameters)
    kwargs.update({"shots": shots})
    return kwargs


@pytest.fixture
def backend_parameters(braket_dwave_parameters):
    return {BraketSolverMetadata.DWAVE["backend_parameters_key_name"]: braket_dwave_parameters}


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsQpu")
def braket_sampler(mock_qpu, braket_sampler_properties, s3_destination_folder, logger):
    mock_qpu.return_value.properties = braket_sampler_properties
    arn = BraketSamplerArns.DWAVE
    sampler = BraketSampler(s3_destination_folder, arn, Mock(), logger)
    return sampler


def test_parameters(braket_sampler):
    expected_params = {
        param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"].values()
    }
    assert braket_sampler.parameters == expected_params
    assert isinstance(braket_sampler.parameters, FrozenDict)


@pytest.mark.xfail(raises=InvalidSolverDeviceArn)
@patch("braket.ocean_plugin.braket_sampler.AwsQpu")
def test_arn_invalid(mock_qpu, braket_sampler_properties, s3_destination_folder):
    mock_qpu.return_value.properties = braket_sampler_properties
    arn = "test_arn"
    BraketSampler(s3_destination_folder, arn, Mock())


def test_properties(braket_sampler, braket_sampler_properties):
    assert isinstance(braket_sampler.properties, FrozenDict)
    assert braket_sampler.properties == braket_sampler_properties


def test_edgelist(braket_sampler):
    assert braket_sampler.edgelist == ((0, 2), (1, 2))


def test_nodelist(braket_sampler):
    assert braket_sampler.nodelist == (0, 1, 2)


@pytest.mark.xfail(raises=BinaryQuadraticModelStructureError)
def test_sample_ising_bqm_structure_error(braket_sampler):
    braket_sampler.sample_ising({0: -1, 500: 1}, {})


@pytest.mark.xfail(raises=ValueError)
def test_sample_ising_value_error(braket_sampler):
    braket_sampler.sample_ising({}, {(0, 0): 1}, unsupported="hi")


@pytest.mark.parametrize("linear, quadratic", [({0: -1, 1: 1, 2: -1}, {}), ([-1, 1, -1], {})])
def test_sample_ising_success(
    linear,
    quadratic,
    braket_sampler,
    s3_ising_result,
    info,
    s3_destination_folder,
    backend_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_ising_common_testing(
        linear,
        quadratic,
        braket_sampler,
        s3_ising_result,
        info,
        s3_destination_folder,
        backend_parameters,
        sample_kwargs,
        shots,
        logger,
    )


@pytest.mark.parametrize("linear, quadratic", [({0: -1, 1: 1, 2: -1}, {}), ([-1, 1, -1], {})])
def test_sample_ising_quantum_task_success(
    linear,
    quadratic,
    braket_sampler,
    s3_ising_result,
    s3_destination_folder,
    backend_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_ising_quantum_task_common_testing(
        linear,
        quadratic,
        braket_sampler,
        s3_ising_result,
        s3_destination_folder,
        backend_parameters,
        sample_kwargs,
        shots,
        logger,
    )


@pytest.mark.xfail(raises=BinaryQuadraticModelStructureError)
def test_sample_qubo_bqm_structure_error(braket_sampler):
    braket_sampler.sample_qubo({(1, 500): 0})


@pytest.mark.xfail(raises=ValueError)
def test_sample_qubo_value_error(braket_sampler):
    braket_sampler.sample_qubo({(0, 0): 0}, unsupported="hi")


def test_get_task_sample_set_variables(s3_qubo_result,):
    task = Mock()
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    actual = BraketSampler.get_task_sample_set(task, variables=[1])
    assert list(actual.variables) == [1]


def test_get_task_sample_active_variables(s3_qubo_result,):
    task = Mock()
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    actual = BraketSampler.get_task_sample_set(task)
    assert list(actual.variables) == [0]


def test_get_task_sample_no_active_variables(s3_qubo_result,):
    s3_dict = json.loads(s3_qubo_result)
    del s3_dict["additionalMetadata"]["dwaveMetadata"]
    task = Mock()
    task.result.return_value = AnnealingQuantumTaskResult.from_string(json.dumps(s3_dict))
    actual = BraketSampler.get_task_sample_set(task)
    assert list(actual.variables) == [0, 1]


def test_sample_qubo_dict_success(
    braket_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    backend_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        backend_parameters,
        sample_kwargs,
        shots,
        logger,
    )


def test_sample_qubo_quasntum_task_dict_success(
    braket_sampler,
    s3_qubo_result,
    s3_destination_folder,
    backend_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_qubo_quantum_task_common_testing(
        braket_sampler,
        s3_qubo_result,
        s3_destination_folder,
        backend_parameters,
        sample_kwargs,
        shots,
        logger,
    )
