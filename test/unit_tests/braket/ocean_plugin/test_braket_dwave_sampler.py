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

from unittest.mock import Mock, patch

import pytest
from boltons.dictutils import FrozenDict
from braket.ocean_plugin import (
    BraketDWaveSampler,
    BraketSampler,
    BraketSamplerArns,
    BraketSolverMetadata,
)
from conftest import sample_ising_common_testing, sample_qubo_common_testing


@pytest.fixture
def sample_kwargs_1(shots):
    return {"postprocess": "sampling", "answer_mode": "histogram", "num_reads": shots}


@pytest.fixture
def backend_parameters_1():
    return {
        BraketSolverMetadata.DWAVE["backend_parameters_key_name"]: {
            "postprocessingType": "SAMPLING",
            "resultFormat": "HISTOGRAM",
        }
    }


@pytest.fixture
def sample_kwargs_2(shots):
    return {"num_reads": shots}


@pytest.fixture
def backend_parameters_2():
    return {BraketSolverMetadata.DWAVE["backend_parameters_key_name"]: {}}


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsQpu")
def braket_dwave_sampler(mock_qpu, braket_sampler_properties, s3_destination_folder, logger):
    mock_qpu.return_value.properties = braket_sampler_properties
    arn = BraketSamplerArns.DWAVE
    sampler = BraketDWaveSampler(s3_destination_folder, arn, Mock(), logger)
    assert isinstance(sampler, BraketSampler)
    return sampler


def test_parameters(braket_dwave_sampler):
    expected_params = {param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"]}
    assert braket_dwave_sampler.parameters == expected_params
    assert isinstance(braket_dwave_sampler.parameters, FrozenDict)


def test_properties(braket_dwave_sampler, braket_sampler_properties):
    assert isinstance(braket_dwave_sampler.properties, FrozenDict)
    expected = FrozenDict(
        {
            BraketSolverMetadata.DWAVE["properties"][braket_key]: braket_sampler_properties[
                braket_key
            ]
            for braket_key in braket_sampler_properties
        }
    )
    assert braket_dwave_sampler.properties == expected


@pytest.mark.parametrize("linear, quadratic", [({0: -1, 1: 1, 2: -1}, {}), ([-1, 1, -1], {})])
def test_sample_ising_dict_success(
    linear,
    quadratic,
    braket_dwave_sampler,
    s3_ising_result,
    info,
    s3_destination_folder,
    backend_parameters_1,
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
        backend_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )


def test_sample_qubo_dict_success_backend_parameters(
    braket_dwave_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    backend_parameters_1,
    sample_kwargs_1,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_dwave_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        backend_parameters_1,
        sample_kwargs_1,
        shots,
        logger,
    )


def test_sample_qubo_dict_success_no_backend_parameters(
    braket_dwave_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    backend_parameters_2,
    sample_kwargs_2,
    shots,
    logger,
):
    sample_qubo_common_testing(
        braket_dwave_sampler,
        s3_qubo_result,
        info,
        s3_destination_folder,
        backend_parameters_2,
        sample_kwargs_2,
        shots,
        logger,
    )
