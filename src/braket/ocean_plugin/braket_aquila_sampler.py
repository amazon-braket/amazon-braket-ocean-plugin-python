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

from __future__ import annotations

import copy
from functools import lru_cache
from logging import Logger, getLogger
from typing import Any, Dict, List, Tuple, Union

import jsonref
from boltons.dictutils import FrozenDict
from braket.aws import AwsSession
from braket.tasks import QuantumTask
from dimod import SampleSet
from dwave.cloud.solver import StructuredSolver

from braket.ocean_plugin.braket_sampler import BraketSampler
from braket.ocean_plugin.braket_solver_metadata import BraketSolverMetadata


class BraketAquilaSampler(BraketSampler):
    """
    A class for using Aquila-formatted parameters and properties with Amazon Braket as a sampler.

    Args:
        s3_destination_folder (AwsSession.S3DestinationFolder): NamedTuple with bucket (index 0)
            and key (index 1) that is the results destination folder in S3.
        device_arn (str): AWS quantum device arn. Default is the latest D-Wave QPU device ARN.
        aws_session (AwsSession): AwsSession to call AWS with.
        logger (Logger): Python Logger object with which to write logs, such as `QuantumTask`
            statuses while polling for task to complete. Default is `getLogger(__name__)`

    Examples:
        >>> from braket.ocean_plugin import BraketDWaveSampler
        >>> s3_destination_folder = ('test_bucket', 'test_folder')
        >>> sampler = BraketDWaveSampler(s3_destination_folder)
    """

    def __init__(
        self,
        s3_destination_folder: AwsSession.S3DestinationFolder = None,
        device_arn: str = None,
        aws_session: AwsSession = None,
        logger: Logger = getLogger(__name__),
    ):
        super().__init__(s3_destination_folder, device_arn, aws_session, logger)
