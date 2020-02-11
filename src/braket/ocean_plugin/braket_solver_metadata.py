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


class BraketSolverMetadata(dict, Enum):
    """
    Per solver a dict containing solver metadata. Keys include "parameters"
        which is a dict containing Braket formatted parameters to D-Wave formatted parameters,
        "backend_parameters_key_name" which is the key name per solver for
        "backend_parameters" argument in Braket create_quantum_task API.
    """

    DWAVE = {
        "parameters": {
            "annealingOffsets": "anneal_offsets",
            "annealingSchedule": "anneal_schedule",
            "annealingDuration": "annealing_time",
            "autoScale": "auto_scale",
            "beta": "beta",
            "chains": "chains",
            "compensateFluxDrift": "flux_drift_compensation",
            "fluxBiases": "flux_biases",
            "initialState": "initial_state",
            "maxResults": "max_answers",
            "postprocessingType": "postprocess",
            "programmingThermalizationDuration": "programming_thermalization",
            "readoutThermalizationDuration": "readout_thermalization",
            "reduceIntersampleCorrelation": "reduce_intersample_correlation",
            "reinitializeState": "reinitialize_state",
            "resultFormat": "answer_mode",
            "spinReversalTransformCount": "num_spin_reversal_transforms",
        },
        "backend_parameters_key_name": "dWaveParameters",
    }
