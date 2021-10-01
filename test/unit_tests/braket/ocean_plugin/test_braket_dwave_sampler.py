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

from unittest.mock import Mock, patch

import pytest
from boltons.dictutils import FrozenDict
from conftest import (
    sample_ising_common_testing,
    sample_ising_quantum_task_common_testing,
    sample_qubo_common_testing,
    sample_qubo_quantum_task_common_testing,
)

from braket.ocean_plugin import BraketDWaveSampler, BraketSampler, BraketSolverMetadata


@pytest.fixture
def sample_kwargs_1(shots):
    return {"postprocess": "sampling", "answer_mode": "histogram", "num_reads": shots}


@pytest.fixture
def device_parameters_1():
    return {
        BraketSolverMetadata.DWAVE["device_parameters_key_name"]: {
            "postprocessingType": "SAMPLING",
            "resultFormat": "HISTOGRAM",
        }
    }


@pytest.fixture
def sample_kwargs_2(shots):
    return {"num_reads": shots}


@pytest.fixture
def device_parameters_2():
    return {BraketSolverMetadata.DWAVE["device_parameters_key_name"]: {}}


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsDevice")
def braket_dwave_sampler(
    mock_qpu, braket_sampler_properties, s3_destination_folder, logger, dwave_arn
):
    mock_qpu.return_value.properties = braket_sampler_properties
    sampler = BraketDWaveSampler(s3_destination_folder, dwave_arn, Mock(), logger)
    assert isinstance(sampler, BraketSampler)
    return sampler


@patch("braket.ocean_plugin.braket_sampler.AwsDevice")
@patch("braket.ocean_plugin.braket_dwave_sampler.AwsDevice")
def test_default_device_arn(
    dwave_sampler_mock_qpu,
    sampler_mock_qpu,
    braket_sampler_properties,
    s3_destination_folder,
    logger,
    dwave_arn,
):
    mock_device = Mock()
    mock_device.arn = dwave_arn
    dwave_sampler_mock_qpu.get_devices.return_value = [mock_device]
    sampler_mock_qpu.return_value.properties = braket_sampler_properties
    sampler = BraketDWaveSampler(s3_destination_folder, None, Mock(), logger)
    assert isinstance(sampler, BraketSampler)
    assert sampler._device_arn == dwave_arn


@pytest.mark.xfail(raises=RuntimeError)
@patch("braket.ocean_plugin.braket_dwave_sampler.AwsDevice")
def test_default_device_arn_error(dwave_sampler_mock_qpu, s3_destination_folder, logger, dwave_arn):
    mock_device = Mock()
    mock_device.arn = dwave_arn
    dwave_sampler_mock_qpu.get_devices.return_value = []
    BraketDWaveSampler(s3_destination_folder, None, Mock(), logger)


def test_parameters(braket_dwave_sampler):
    expected_params = {param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"]}
    assert braket_dwave_sampler.parameters == expected_params
    assert isinstance(braket_dwave_sampler.parameters, FrozenDict)


def test_properties(braket_dwave_sampler, provider_properties, service_properties):
    assert isinstance(braket_dwave_sampler.properties, FrozenDict)
    translated_provider_properties = {
        BraketSolverMetadata.DWAVE["properties"]["provider"][braket_key]: provider_properties[
            braket_key
        ]
        for braket_key in provider_properties
    }
    translated_service_properties = {
        BraketSolverMetadata.DWAVE["properties"]["service"][braket_key]: service_properties[
            braket_key
        ]
        for braket_key in service_properties
    }
    translated_provider_properties.update(translated_service_properties)
    expected = FrozenDict(translated_provider_properties)
    assert braket_dwave_sampler.properties == expected


@pytest.mark.parametrize("linear, quadratic", [({0: -1, 1: 1, 2: -1}, {}), ([-1, 1, -1], {})])
def test_sample_ising_dict_success(
    linear,
    quadratic,
    braket_dwave_sampler,
    s3_ising_result,
    info,
    s3_destination_folder,
    device_parameters_1,
    sample_kwargs_1,
    shots,
    logger,
):
    sample_ising_common_testing(
        linear,
        quadratic,
        braket_dwave_sampler,
        s3_ising_result,
        info,
        s3_destination_folder,
        device_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )


@pytest.mark.parametrize("linear, quadratic", [({0: -1, 1: 1, 2: -1}, {}), ([-1, 1, -1], {})])
def test_sample_ising_quantum_task_success(
    linear,
    quadratic,
    braket_dwave_sampler,
    s3_ising_result,
    s3_destination_folder,
    device_parameters_1,
    sample_kwargs_1,
    shots,
    logger,
):
    sample_ising_quantum_task_common_testing(
        linear,
        quadratic,
        braket_dwave_sampler,
        s3_ising_result,
        s3_destination_folder,
        device_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )


def test_sample_qubo_dict_success_device_parameters(
    braket_dwave_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    device_parameters_1,
    sample_kwargs_1,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_dwave_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        device_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )


def test_sample_qubo_dict_success_no_device_parameters(
    braket_dwave_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    device_parameters_2,
    sample_kwargs_2,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_dwave_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        device_parameters_2,
        sample_kwargs_2,
        shots,
        logger,
    )


def test_sample_qubo_quantum_task_dict_success(
    braket_dwave_sampler,
    s3_qubo_result,
    s3_destination_folder,
    device_parameters_1,
    sample_kwargs_1,
    shots,
    logger,
):
    sample_qubo_quantum_task_common_testing(
        braket_dwave_sampler,
        s3_qubo_result,
        s3_destination_folder,
        device_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )
