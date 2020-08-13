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

from enum import Enum
from typing import Any, Dict

from braket.ocean_plugin.exceptions import InvalidSolverDeviceArn


class BraketSolverMetadata(dict, Enum):
    """
    Per solver a dict containing solver metadata.

    The solver metadata format is liable to change.
    """

    DWAVE = {
        "parameters": {  # D-Wave to Braket
            "anneal_offsets": "annealingOffsets",
            "anneal_schedule": "annealingSchedule",
            "annealing_time": "annealingDuration",
            "auto_scale": "autoScale",
            "beta": "beta",
            "chains": "chains",
            "flux_drift_compensation": "compensateFluxDrift",
            "flux_biases": "fluxBiases",
            "initial_state": "initialState",
            "max_answers": "maxResults",
            "postprocess": "postprocessingType",
            "programming_thermalization": "programmingThermalizationDuration",
            "readout_thermalization": "readoutThermalizationDuration",
            "reduce_intersample_correlation": "reduceIntersampleCorrelation",
            "reinitialize_state": "reinitializeState",
            "answer_mode": "resultFormat",
            "num_spin_reversal_transforms": "spinReversalTransformCount",
            "num_reads": "shots",
        },
        "properties": {  # Braket to D-Wave
            "provider": {
                "annealingOffsetStep": "anneal_offset_step",
                "annealingOffsetStepPhi0": "anneal_offset_step_phi0",
                "annealingOffsetRanges": "anneal_offset_ranges",
                "annealingDurationRange": "annealing_time_range",
                "couplers": "couplers",
                "defaultAnnealingDuration": "default_annealing_time",
                "defaultProgrammingThermalizationDuration": "default_programming_thermalization",
                "defaultReadoutThermalizationDuration": "default_readout_thermalization",
                "extendedJRange": "extended_j_range",
                "hGainScheduleRange": "h_gain_schedule_range",
                "hRange": "h_range",
                "jRange": "j_range",
                "maximumAnnealingSchedulePoints": "max_anneal_schedule_points",
                "maximumHGainSchedulePoints": "max_h_gain_schedule_points",
                "perQubitCouplingRange": "per_qubit_coupling_range",
                "programmingThermalizationDurationRange": "programming_thermalization_range",
                "qubitCount": "num_qubits",
                "qubits": "qubits",
                "quotaConversionRate": "quota_conversion_rate",
                "readoutThermalizationDurationRange": "readout_thermalization_range",
                "taskRunDurationRange": "problem_run_duration_range",
                "topology": "topology",
            },
            "service": {"shotsRange": "num_reads_range"},
        },
        "device_parameters_key_name": "providerLevelParameters",
    }

    @staticmethod
    def get_metadata_by_arn(device_arn: str) -> Dict[str, Any]:
        """
        Get metadata by device ARN

        Args:
            device_arn (str): The ARN of the device

        Returns:
            Dict[str, Any]: Dictionary containing solver metadata.

        Raises:
            InvalidSolverDeviceArn: If the device ARN is invalid for getting
                the metadata
        """
        if device_arn.split("/")[-2] == "d-wave":
            return BraketSolverMetadata.DWAVE
        raise InvalidSolverDeviceArn(f"Invalid device ARN {device_arn}")
