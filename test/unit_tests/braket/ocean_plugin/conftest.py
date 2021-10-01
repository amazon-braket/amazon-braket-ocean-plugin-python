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

import json
import logging
from unittest.mock import Mock

import jsonref
import pytest
from braket.annealing.problem import Problem, ProblemType
from braket.device_schema.dwave import (
    Dwave2000QDeviceParameters,
    DwaveAdvantageDeviceParameters,
    DwaveDeviceCapabilities,
)
from braket.tasks import AnnealingQuantumTaskResult
from dimod import BINARY, SPIN, SampleSet


@pytest.fixture
def dwave_arn():
    return "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6"


@pytest.fixture
def shots():
    return 100


@pytest.fixture
def service_properties():
    return {"shotsRange": (0, 10)}


@pytest.fixture
def provider_properties():
    return {
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
        "taskRunDurationRange": [3, 6],
        "topology": {"type": "chimera", "topology": [1, 1, 1]},
    }


@pytest.fixture
def two_thousand_q_device_parameters():
    return jsonref.loads(Dwave2000QDeviceParameters.schema_json())


@pytest.fixture
def advantage_device_parameters():
    return jsonref.loads(DwaveAdvantageDeviceParameters.schema_json())


@pytest.fixture
def braket_sampler_properties(
    provider_properties, service_properties, two_thousand_q_device_parameters
):
    return DwaveDeviceCapabilities.parse_obj(
        {
            "braketSchemaHeader": {
                "name": "braket.device_schema.dwave.dwave_device_capabilities",
                "version": "1",
            },
            "provider": provider_properties,
            "service": {
                "executionWindows": [
                    {
                        "executionDay": "Everyday",
                        "windowStartHour": "11:00",
                        "windowEndHour": "12:00",
                    }
                ],
                "shotsRange": service_properties["shotsRange"],
            },
            "action": {
                "braket.ir.annealing.problem": {
                    "actionType": "braket.ir.annealing.problem",
                    "version": ["1"],
                }
            },
            "deviceParameters": two_thousand_q_device_parameters,
        }
    )


@pytest.fixture
def advantage_braket_sampler_properties(
    provider_properties, service_properties, advantage_device_parameters
):
    return DwaveDeviceCapabilities.parse_obj(
        {
            "braketSchemaHeader": {
                "name": "braket.device_schema.dwave.dwave_device_capabilities",
                "version": "1",
            },
            "provider": provider_properties,
            "service": {
                "executionWindows": [
                    {
                        "executionDay": "Everyday",
                        "windowStartHour": "11:00",
                        "windowEndHour": "12:00",
                    }
                ],
                "shotsRange": service_properties["shotsRange"],
            },
            "action": {
                "braket.ir.annealing.problem": {
                    "actionType": "braket.ir.annealing.problem",
                    "version": ["1"],
                }
            },
            "deviceParameters": advantage_device_parameters,
        }
    )


@pytest.fixture
def active_variables():
    return [4, 5, 6]


@pytest.fixture()
def additional_metadata(active_variables):
    return {
        "additionalMetadata": {
            "action": {
                "type": "ISING",
                "linear": {"0": 0.3333, "1": -0.333, "4": -0.333, "5": 0.333},
                "quadratic": {"0,4": 0.667, "0,5": -1.0, "1,4": 0.667, "1,5": 0.667},
            },
            "dwaveMetadata": {
                "activeVariables": active_variables,
                "timing": {
                    "qpuSamplingTime": 100,
                    "qpuAnnealTimePerSample": 20,
                    "qpuAccessTime": 10917,
                    "qpuAccessOverheadTime": 3382,
                    "qpuReadoutTimePerSample": 274,
                    "qpuProgrammingTime": 9342,
                    "qpuDelayTimePerSample": 21,
                    "postProcessingOverheadTime": 117,
                    "totalPostProcessingTime": 117,
                    "totalRealTime": 10917,
                    "runTimeChip": 1575,
                    "annealTimePerRun": 20,
                    "readoutTimePerRun": 274,
                },
            },
        }
    }


@pytest.fixture
def task_metadata(shots, dwave_arn):
    return {"taskMetadata": {"id": "task_arn", "shots": shots, "deviceId": dwave_arn}}


@pytest.fixture
def result(additional_metadata, task_metadata):
    result = {
        "solutions": [[-1, -1, -1], [1, -1, 1], [1, -1, -1]],
        "solutionCounts": [3, 2, 4],
        "values": [0.0, 1.0, 2.0],
        "variableCount": 2048,
    }
    result.update(additional_metadata)
    result.update(task_metadata)
    return result


@pytest.fixture
def s3_ising_result(result):
    result["additionalMetadata"]["action"]["type"] = ProblemType.ISING
    return json.dumps(result)


@pytest.fixture
def s3_qubo_result(result):
    result["additionalMetadata"]["action"]["type"] = ProblemType.QUBO
    return json.dumps(result)


@pytest.fixture
def s3_destination_folder():
    return ("test_bucket", "test_folder_prefix")


@pytest.fixture
def info(result):
    result = AnnealingQuantumTaskResult.from_string(json.dumps(result))
    additional_metadata = result.additional_metadata.dict()
    task_metadata = result.task_metadata.dict()
    info = {}
    info.update({"additionalMetadata": additional_metadata})
    info.update({"taskMetadata": task_metadata})
    return info


@pytest.fixture
def logger():
    return logging.getLogger("newLogger")


def _sample_common_asserts(
    sampler,
    s3_destination_folder,
    device_parameters,
    shots,
    logger,
    linear,
    quadratic,
    problem_type,
):
    call_list = sampler.solver.run.call_args_list
    args, kwargs = call_list[0]
    assert args[1] == s3_destination_folder
    assert kwargs["logger"] == logger
    assert kwargs["device_parameters"] == device_parameters
    assert kwargs["shots"] == shots
    problem = args[0]
    assert isinstance(problem, Problem)
    assert problem.problem_type == problem_type
    if isinstance(linear, list):
        assert problem.linear == {0: -1, 1: 1, 2: -1}
    else:
        assert problem.linear == linear
    assert problem.quadratic == quadratic


def sample_ising_quantum_task_common_testing(
    linear,
    quadratic,
    sampler,
    s3_ising_result,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    """Common testing of sample_ising_quantum_task for Braket samplers"""
    task = Mock()
    sampler.solver.run.return_value = task
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_ising_result)
    actual = sampler.sample_ising_quantum_task(linear, quadratic, **sample_kwargs)
    _sample_common_asserts(
        sampler,
        s3_destination_folder,
        device_parameters,
        shots,
        logger,
        linear,
        quadratic,
        ProblemType.ISING,
    )
    assert actual == task


def sample_ising_common_testing(
    linear,
    quadratic,
    sampler,
    s3_ising_result,
    info,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    """Common testing of sample_ising for Braket samplers"""
    task = Mock()
    sampler.solver.run.return_value = task
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_ising_result)
    actual = sampler.sample_ising(linear, quadratic, **sample_kwargs)
    _sample_common_asserts(
        sampler,
        s3_destination_folder,
        device_parameters,
        shots,
        logger,
        linear,
        quadratic,
        ProblemType.ISING,
    )
    assert isinstance(actual, SampleSet)
    assert actual.vartype == SPIN
    assert actual.record.sample.shape == (3, 3)
    assert actual.info == info


def sample_qubo_quantum_task_common_testing(
    sampler,
    s3_qubo_result,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    """Common testing of sample_qubo_quantum_task for Braket samplers"""
    task = Mock()
    sampler.solver.run.return_value = task
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    Q = {(0, 0): 0, (1, 2): 1, (0, 2): 0}
    actual = sampler.sample_qubo_quantum_task(Q, **sample_kwargs)
    _sample_common_asserts(
        sampler,
        s3_destination_folder,
        device_parameters,
        shots,
        logger,
        {0: 0},
        {(1, 2): 1, (0, 2): 0},
        ProblemType.QUBO,
    )
    assert actual == task


def sample_qubo_common_testing(
    sampler,
    s3_qubo_result,
    info,
    s3_destination_folder,
    device_parameters,
    sample_kwargs,
    shots,
    logger,
):
    """Common testing of sample_qubo for Braket samplers"""
    task = Mock()
    sampler.solver.run.return_value = task
    task.result.return_value = AnnealingQuantumTaskResult.from_string(s3_qubo_result)
    Q = {(0, 0): 0, (1, 2): 1, (0, 2): 0}
    actual = sampler.sample_qubo(Q, **sample_kwargs)
    _sample_common_asserts(
        sampler,
        s3_destination_folder,
        device_parameters,
        shots,
        logger,
        {0: 0},
        {(1, 2): 1, (0, 2): 0},
        ProblemType.QUBO,
    )
    assert isinstance(actual, SampleSet)
    assert actual.vartype == BINARY
    assert actual.record.sample.shape == (3, 3)
    assert actual.info == info
