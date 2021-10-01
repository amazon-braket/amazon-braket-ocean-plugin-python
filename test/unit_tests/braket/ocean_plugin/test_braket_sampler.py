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

import copy
import json
from unittest.mock import Mock, patch

import pytest
from boltons.dictutils import FrozenDict
from braket.tasks import AnnealingQuantumTaskResult
from conftest import (
    sample_ising_common_testing,
    sample_ising_quantum_task_common_testing,
    sample_qubo_common_testing,
    sample_qubo_quantum_task_common_testing,
)
from dimod.exceptions import BinaryQuadraticModelStructureError

from braket.ocean_plugin import BraketSampler, BraketSolverMetadata


@pytest.fixture
def braket_dwave_parameters():
    return {"postprocessingType": "SAMPLING"}


@pytest.fixture
def sample_kwargs(braket_dwave_parameters, shots):
    kwargs = copy.deepcopy(braket_dwave_parameters)
    kwargs.update({"shots": shots})
    return kwargs


@pytest.fixture
def device_parameters(braket_dwave_parameters):
    return {BraketSolverMetadata.DWAVE["device_parameters_key_name"]: braket_dwave_parameters}


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsDevice")
def braket_sampler(mock_qpu, braket_sampler_properties, s3_destination_folder, logger, dwave_arn):
    mock_qpu.return_value.properties = braket_sampler_properties
    sampler = BraketSampler(s3_destination_folder, dwave_arn, Mock(), logger)
    return sampler


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsDevice")
def advantage_braket_sampler(
    mock_qpu, advantage_braket_sampler_properties, s3_destination_folder, logger, dwave_arn
):
    mock_qpu.return_value.properties = advantage_braket_sampler_properties
    sampler = BraketSampler(s3_destination_folder, dwave_arn, Mock(), logger)
    return sampler


def test_parameters(braket_sampler):
    expected_params = {
        param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"].values()
    }
    assert braket_sampler.parameters == expected_params
    assert isinstance(braket_sampler.parameters, FrozenDict)


def test_advantage_parameters(advantage_braket_sampler):
    expected_params = {
        param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"].values()
    }
    del expected_params["beta"]
    del expected_params["chains"]
    del expected_params["postprocessingType"]

    assert advantage_braket_sampler.parameters == expected_params
    assert isinstance(advantage_braket_sampler.parameters, FrozenDict)


def test_properties(braket_sampler, provider_properties, service_properties):
    provider_properties.update(service_properties)
    assert isinstance(braket_sampler.properties, FrozenDict)
    assert braket_sampler.properties == provider_properties


def test_edgelist(braket_sampler):
    assert braket_sampler.edgelist == ((0, 2), (1, 2))


def test_nodelist(braket_sampler):
    assert braket_sampler.nodelist == (0, 1, 2)


@pytest.mark.xfail(raises=BinaryQuadraticModelStructureError)
@pytest.mark.parametrize(
    "h, J", [({0: -1, 500: 1}, {}), ({0: -1, 1: 1}, {(0, 1): 3}), ({0: -1, 2: 1}, {(3, 500): 3})]
)
def test_sample_ising_bqm_structure_error(braket_sampler, h, J):
    braket_sampler.sample_ising(h, J)


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
    device_parameters,
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
        device_parameters,
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
    device_parameters,
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
        device_parameters,
        sample_kwargs,
        shots,
        logger,
    )


@pytest.mark.xfail(raises=BinaryQuadraticModelStructureError)
@pytest.mark.parametrize("Q", [{(1, 500): 0}, {(0, 1): 0}, {(500, 500): 0}])
def test_sample_qubo_bqm_structure_error(braket_sampler, Q):
    braket_sampler.sample_qubo(Q)


@pytest.mark.xfail(raises=ValueError)
def test_sample_qubo_value_error(braket_sampler):
    braket_sampler.sample_qubo({(0, 0): 0}, unsupported="hi")


def test_get_task_sample_set_variables(
    s3_qubo_result,
):
    s3_dict = json.loads(s3_qubo_result)
    del s3_dict["additionalMetadata"]["dwaveMetadata"]
    task = Mock()
    variables = [8, 9, 10]
    task.result.return_value = AnnealingQuantumTaskResult.from_string(json.dumps(s3_dict))
    actual = BraketSampler.get_task_sample_set(task, variables=variables)
    assert list(actual.variables) == variables


def test_get_task_sample_active_variables(s3_qubo_result, active_variables):
    task = Mock()
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    actual = BraketSampler.get_task_sample_set(task)
    assert list(actual.variables) == active_variables


def test_get_task_sample_no_active_variables(
    s3_qubo_result,
):
    s3_dict = json.loads(s3_qubo_result)
    del s3_dict["additionalMetadata"]["dwaveMetadata"]
    s3_dict["variableCount"] = 3
    task = Mock()
    task.result.return_value = AnnealingQuantumTaskResult.from_string(json.dumps(s3_dict))
    actual = BraketSampler.get_task_sample_set(task)
    assert list(actual.variables) == list(range(s3_dict["variableCount"]))


def test_sample_qubo_dict_success(
    braket_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        device_parameters,
        sample_kwargs,
        shots,
        logger,
    )


def test_sample_qubo_quasntum_task_dict_success(
    braket_sampler,
    s3_qubo_result,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    sample_qubo_quantum_task_common_testing(
        braket_sampler,
        s3_qubo_result,
        s3_destination_folder,
        device_parameters,
        sample_kwargs,
        shots,
        logger,
    )
