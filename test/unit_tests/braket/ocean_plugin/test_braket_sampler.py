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

import json
from unittest.mock import Mock, patch

import pytest
from boltons.dictutils import FrozenDict
from braket.annealing.problem import Problem, ProblemType
from braket.ocean_plugin import (
    BraketSampler,
    BraketSamplerArns,
    BraketSolverMetadata,
    InvalidSolverDeviceArn,
)
from braket.tasks import AnnealingQuantumTaskResult
from dimod import BINARY, SPIN, SampleSet
from dimod.exceptions import BinaryQuadraticModelStructureError


@pytest.fixture
def braket_sampler_properties():
    return {
        "activeQubitCount": 2,
        "annealingOffsetStep": 2.0,
        "annealingOffsetStepPhi0": 4.0,
        "annealingOffsetRanges": [[1.34, 5.23], [3.24, 1.44]],
        "annealingDurationRange": [3, 5],
        "couplers": [[1, 2], [0, 2]],
        "defaultAnnealingDuration": 4,
        "defaultProgrammingThermalizationDuration": 2,
        "defaultReadoutThermalizationDuration": 1,
        "extendedJRange": [3.0, 4.0],
        "hGainScheduleRange": [2.0, 3.0],
        "hRange": [3.4, 5.6],
        "jRange": [1.0, 2.0],
        "maximumAnnealingSchedulePoints": 3,
        "maximumHGainSchedulePoints": 2,
        "qubitCount": 3,
        "qubits": [1, 0, 2],
        "perQubitCouplingRange": [1.0, 3.0],
        "programmingThermalizationDurationRange": [1, 2],
        "quotaConversionRate": 2.5,
        "readoutThermalizationDurationRange": [4, 6],
        "shotsRange": [3, 5],
        "taskRunDurationRange": [3, 6],
        "topology": {"type": "chimera", "topology": [1, 1, 1]},
    }


@pytest.fixture()
def additional_metadata():
    return {
        "DWaveMetadata": {
            "ActiveVariables": [0],
            "Timing": {
                "QpuSamplingTime": 1575,
                "QpuAnnealTimePerSample": 20,
                "QpuReadoutTimePerSample": 274,
                "QpuAccessTime": 10917,
                "QpuAccessOverheadTime": 3382,
                "QpuProgrammingTime": 9342,
                "QpuDelayTimePerSample": 21,
                "TotalPostProcessingTime": 117,
                "PostProcessingOverheadTime": 117,
                "TotalRealTime": 10917,
                "RunTimeChip": 1575,
                "AnnealTimePerRun": 20,
                "ReadoutTimePerRun": 274,
            },
        }
    }


@pytest.fixture
def task_metadata():
    return {
        "TaskMetadata": {
            "Id": "UUID_blah_1",
            "Status": "COMPLETED",
            "BackendArn": BraketSamplerArns.DWAVE,
            "Shots": 5,
        }
    }


@pytest.fixture
def result(additional_metadata, task_metadata):
    result = {
        "Solutions": [[-1, -1, -1], [1, -1, 1], [1, -1, -1]],
        "VariableCount": 2,
        "Values": [0.0, 1.0, 2.0],
        "SolutionCounts": None,
        "DWaveMetadata": {
            "ActiveVariables": [0],
            "Timing": {
                "QpuSamplingTime": 1575,
                "QpuAnnealTimePerSample": 20,
                "QpuReadoutTimePerSample": 274,
                "QpuAccessTime": 10917,
                "QpuAccessOverheadTime": 3382,
                "QpuProgrammingTime": 9342,
                "QpuDelayTimePerSample": 21,
                "TotalPostProcessingTime": 117,
                "PostProcessingOverheadTime": 117,
                "TotalRealTime": 10917,
                "RunTimeChip": 1575,
                "AnnealTimePerRun": 20,
                "ReadoutTimePerRun": 274,
            },
        },
        "TaskMetadata": {
            "Id": "UUID_blah_1",
            "Status": "COMPLETED",
            "BackendArn": BraketSamplerArns.DWAVE,
            "Shots": 5,
        },
    }
    result.update(additional_metadata)
    result.update(task_metadata)
    return result


@pytest.fixture
def s3_ising_result(result):
    result.update({"ProblemType": "ising"})
    return json.dumps(result)


@pytest.fixture
def s3_qubo_result(result):
    result.update({"ProblemType": "qubo"})
    return json.dumps(result)


@pytest.fixture
def s3_destination_folder():
    return ("test_bucket", "test_folder_prefix")


@pytest.fixture
def dwave_parameters():
    return {"postprocessingType": "SAMPLING"}


@pytest.fixture
def backend_parameters(dwave_parameters):
    return {BraketSolverMetadata.DWAVE["backend_parameters_key_name"]: dwave_parameters}


@pytest.fixture
def info(additional_metadata, task_metadata):
    info = {}
    info.update({"AdditionalMetadata": additional_metadata})
    info.update(task_metadata)
    return info


@pytest.fixture
@patch("braket.ocean_plugin.braket_sampler.AwsQpu")
def braket_sampler(mock_qpu, braket_sampler_properties, s3_destination_folder):
    mock_qpu.return_value.properties = braket_sampler_properties
    arn = BraketSamplerArns.DWAVE
    sampler = BraketSampler(s3_destination_folder, arn, Mock())
    return sampler


def test_parameters(braket_sampler):
    expected_params = {param: ["parameters"] for param in BraketSolverMetadata.DWAVE["parameters"]}
    assert braket_sampler.parameters == expected_params
    assert isinstance(braket_sampler.properties, FrozenDict)


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
def test_sample_ising_dict_success(
    linear,
    quadratic,
    braket_sampler,
    s3_ising_result,
    info,
    s3_destination_folder,
    backend_parameters,
    dwave_parameters,
):
    task = Mock()
    braket_sampler.solver.run.return_value = task
    future = Mock()
    task.async_result.return_value = future
    future.result.return_value = AnnealingQuantumTaskResult.from_string(s3_ising_result)
    actual = braket_sampler.sample_ising(linear, quadratic, **dwave_parameters)
    call_list = braket_sampler.solver.run.call_args_list
    args, kwargs = call_list[0]
    problem = args[0]
    assert isinstance(problem, Problem)
    assert problem.problem_type == ProblemType.ISING
    if isinstance(linear, list):
        assert problem.linear == {0: -1, 1: 1, 2: -1}
    else:
        assert problem.linear == linear
    assert problem.quadratic == quadratic
    assert args[1] == s3_destination_folder
    assert kwargs["backend_parameters"] == backend_parameters
    assert isinstance(actual, SampleSet)
    assert actual.vartype == SPIN
    assert actual.record.sample.shape == (3, 3)
    assert actual.info == info


@pytest.mark.xfail(raises=BinaryQuadraticModelStructureError)
def test_sample_qubo_bqm_structure_error(braket_sampler):
    braket_sampler.sample_qubo({(1, 500): 0})


@pytest.mark.xfail(raises=ValueError)
def test_sample_qubo_value_error(braket_sampler):
    braket_sampler.sample_qubo({(0, 0): 0}, unsupported="hi")


def test_sample_qubo_dict_success(
    braket_sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    backend_parameters,
    dwave_parameters,
):
    task = Mock()
    braket_sampler.solver.run.return_value = task
    future = Mock()
    task.async_result.return_value = future
    future.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    Q = {(0, 0): 0, (1, 2): 1, (0, 2): 0}
    actual = braket_sampler.sample_qubo(Q, **dwave_parameters)
    call_list = braket_sampler.solver.run.call_args_list
    args, kwargs = call_list[0]
    problem = args[0]
    assert isinstance(problem, Problem)
    assert problem.problem_type == ProblemType.QUBO
    assert problem.linear == {0: 0}
    assert problem.quadratic == {(1, 2): 1, (0, 2): 0}
    assert args[1] == s3_destination_folder
    assert kwargs["backend_parameters"] == backend_parameters
    assert isinstance(actual, SampleSet)
    assert actual.vartype == BINARY
    assert actual.record.sample.shape == (3, 3)
    assert actual.info == info
