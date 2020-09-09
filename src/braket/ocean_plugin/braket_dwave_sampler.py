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

from __future__ import annotations

import copy
from functools import lru_cache
from logging import Logger, getLogger
from typing import Any, Dict, List, Tuple, Union

from boltons.dictutils import FrozenDict
from dimod import SampleSet

from braket.aws import AwsDevice, AwsSession
from braket.ocean_plugin.braket_sampler import BraketSampler
from braket.ocean_plugin.braket_solver_metadata import BraketSolverMetadata
from braket.tasks import QuantumTask


class BraketDWaveSampler(BraketSampler):
    """
    A class for using DWave-formatted parameters and properties with Amazon Braket as a sampler.

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
        s3_destination_folder: AwsSession.S3DestinationFolder,
        device_arn: str = None,
        aws_session: AwsSession = None,
        logger: Logger = getLogger(__name__),
    ):
        if not device_arn:
            try:
                device_arn = AwsDevice.get_devices(
                    provider_names=["D-Wave Systems"], statuses=["ONLINE"]
                )[0].arn
            except IndexError:
                raise RuntimeError("No D-Wave devices online")
        super().__init__(s3_destination_folder, device_arn, aws_session, logger)

    @property
    @lru_cache(maxsize=1)
    def properties(self) -> FrozenDict[str, Any]:
        """
        FrozenDict[str, Any]: Solver properties in D-Wave format.

        `D-Wave System Documentation <https://docs.dwavesys.com/docs/latest/doc_solver_ref.html>`_
        describes the parameters and properties supported on the D-Wave system.

        Solver properties are dependent on the selected solver and subject to change;
        for example, new released features may add properties.
        """
        mapping_dict = BraketSolverMetadata.get_metadata_by_arn(self._device_arn)["properties"]
        return_dict = {}
        for top_level_key in mapping_dict:
            solver_dict = getattr(self.solver.properties, top_level_key).dict()
            for key in mapping_dict[top_level_key]:
                return_dict[mapping_dict[top_level_key][key]] = copy.deepcopy(solver_dict[key])
        return FrozenDict(return_dict)

    @property
    @lru_cache(maxsize=1)
    def parameters(self) -> FrozenDict[str, List]:
        """
        FrozenDict[str, List]: Solver parameters in the form of a dict, where keys are
        keyword parameters in D-Wave format and values are lists of properties in
        :attr:`.BraketSampler.properties` for each key.

        `D-Wave System Documentation <https://docs.dwavesys.com/docs/latest/doc_solver_ref.html>`_
        describes the parameters and properties supported on the D-Wave system.

        Solver parameters are dependent on the selected solver and subject to change;
        for example, new released features may add parameters.
        """
        return FrozenDict(
            {
                param: ["parameters"]
                for param in BraketSolverMetadata.get_metadata_by_arn(self._device_arn)[
                    "parameters"
                ]
            }
        )

    def sample_ising(
        self, h: Union[Dict[int, int], List[int]], J: Dict[int, int], **kwargs
    ) -> SampleSet:
        """
        Sample from the specified Ising model.

        Args:
            h (dict/list):
                Linear biases of the Ising model. If a dict, should be of the
                form `{v: bias, ...}` where `v` is a spin-valued variable and
                `bias` is its associated bias. If a list, it is treated as a
                list of biases where the indices are the variable labels,
                except in the case of missing qubits in which case 0 biases are
                ignored while a non-zero bias set on a missing qubit raises an
                error.
            J (dict[(int, int): float]):
                Quadratic biases of the Ising model.
            **kwargs:
                Optional keyword arguments for the sampling method in D-Wave format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Examples:
            This example submits a two-variable Ising problem mapped directly to qubits
            0 and 1.

            >>> from braket.ocean_plugin import BraketDWaveSampler
            >>> sampler = BraketDWaveSampler(s3_destination_folder)
            >>> sampleset = sampler.sample_ising({0: -1, 1: 1}, {}, answer_mode="HISTOGRAM")
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """
        return super().sample_ising(h, J, **kwargs)

    def sample_ising_quantum_task(
        self, h: Union[Dict[int, int], List[int]], J: Dict[int, int], **kwargs
    ) -> QuantumTask:
        """
        Sample from the specified Ising model and return a `QuantumTask`. This has the same inputs
        as `BraketDWaveSampler.sample_ising`.

        Args:
            h (dict/list):
                Linear biases of the Ising model. If a dict, should be of the
                form `{v: bias, ...}` where `v` is a spin-valued variable and
                `bias` is its associated bias. If a list, it is treated as a
                list of biases where the indices are the variable labels,
                except in the case of missing qubits in which case 0 biases are
                ignored while a non-zero bias set on a missing qubit raises an
                error.
            J (dict[(int, int): float]):
                Quadratic biases of the Ising model.
            **kwargs:
                Optional keyword arguments for the sampling method in D-Wave format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Examples:
            This example submits a two-variable Ising problem mapped directly to qubits
            0 and 1.

            >>> from braket.ocean_plugin import BraketDWaveSampler
            >>> sampler = BraketDWaveSampler(s3_destination_folder)
            >>> task = sampler.sample_ising_quantum_task({0: -1, 1: 1}, {}, answer_mode="HISTOGRAM")
            >>> sampleset = BraketDWaveSampler.get_task_sample_set(task)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """
        return super().sample_ising_quantum_task(h, J, **kwargs)

    def sample_qubo(self, Q: Dict[Tuple[int, int], int], **kwargs) -> SampleSet:
        """
        Sample from the specified QUBO.

        Args:
            Q (dict):
                Coefficients of a quadratic unconstrained binary optimization (QUBO) model.
            **kwargs:
                Optional keyword arguments for the sampling method in D-Wave format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Examples:
            This example submits a two-variable QUBO mapped directly to qubits
            0 and 4 on a sampler

            >>> from braket.ocean_plugin import BraketDWaveSampler
            >>> sampler = BraketDWaveSampler(s3_destination_folder)
            >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
            >>> sampleset = sampler.sample_qubo(Q, postprocess="SAMPLING", num_reads=100)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 4: 0}
        """
        return super().sample_qubo(Q, **kwargs)

    def sample_qubo_quantum_task(self, Q: Dict[Tuple[int, int], int], **kwargs) -> QuantumTask:
        """
        Sample from the specified QUBO and return a `QuantumTask`. This has the same inputs
        as `BraketDWaveSampler.sample_qubo`.

        Args:
            Q (dict):
                Coefficients of a quadratic unconstrained binary optimization (QUBO) model.
            **kwargs:
                Optional keyword arguments for the sampling method in D-Wave format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Examples:
            This example submits a two-variable QUBO mapped directly to qubits
            0 and 4 on a sampler

            >>> from braket.ocean_plugin import BraketDWaveSampler
            >>> sampler = BraketDWaveSampler(s3_destination_folder)
            >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
            >>> task = sampler.sample_qubo_quantum_task(Q, postprocess="SAMPLING", num_reads=100)
            >>> sampleset = BraketDWaveSampler.get_task_sample_set(task)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 4: 0}
        """
        return super().sample_qubo_quantum_task(Q, **kwargs)

    def _process_solver_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        Process kwargs to be compatible as kwargs for the solver.

        Args:
            **kwargs: Optional keyword arguments for sampling method
        Return:
            Dict[str, Any]: a dict of kwargs to the solver
        """
        self._check_kwargs_solver(**kwargs)

        # Translate kwargs from D-Wave format to Braket format
        parameter_dict = BraketSolverMetadata.get_metadata_by_arn(self._device_arn)["parameters"]
        translated_kwargs = {parameter_dict[key]: kwargs[key] for key in kwargs}
        if "resultFormat" in translated_kwargs:
            translated_kwargs["resultFormat"] = translated_kwargs["resultFormat"].upper()
        if "postprocessingType" in translated_kwargs:
            translated_kwargs["postprocessingType"] = translated_kwargs[
                "postprocessingType"
            ].upper()
        return self._create_solver_kwargs(**translated_kwargs)
