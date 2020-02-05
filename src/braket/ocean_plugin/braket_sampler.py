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
from typing import Any, Dict, List, Tuple, Union

from braket.annealing.problem import Problem, ProblemType
from braket.aws import AwsQpu, AwsSession
from braket.ocean_plugin.braket_sampler_arns import BraketSamplerArns
from braket.ocean_plugin.braket_sampler_parameters import BraketSamplerParameters
from braket.tasks import AnnealingQuantumTaskResult
from dimod import BINARY, SPIN, Sampler, SampleSet, Structured
from dimod.exceptions import BinaryQuadraticModelStructureError


class BraketSampler(Sampler, Structured):
    """
    A class for using Amazon Braket as a sampler

    Args:
        s3_destination_folder (AwsSession.S3DestinationFolder): NamedTuple with bucket (index 0)
            and key (index 1) that is the results destination folder in S3.
        device_arn (str): AWS quantum device arn. Default is D-Wave.
        aws_session (AwsSession): AwsSession to call AWS with.

    Examples:
        >>> from braket.ocean_plugin import BraketSampler
        >>> s3_destination_folder = ('test_bucket', 'test_folder')
        >>> sampler = BraketSampler(s3_destination_folder)
    """

    def __init__(
        self,
        s3_destination_folder: AwsSession.S3DestinationFolder,
        device_arn: str = BraketSamplerArns.DWAVE,
        aws_session: AwsSession = None,
    ):
        self._s3_destination_folder = s3_destination_folder
        self._device_arn = device_arn
        self.solver = AwsQpu(device_arn, aws_session)
        self._properties = copy.deepcopy(self.solver.properties)
        self._parameters = self._create_parameters()
        self._edgelist = self._create_edgelist()
        self._nodelist = self._create_nodelist()

    @property
    def properties(self) -> Dict[str, Any]:
        """
        dict: Solver properties in Braket boto3 response format

        TODO: link boto3 docs

        Solver properties are dependent on the selected solver and subject to change;
        for example, new released features may add properties.
        """
        return self._properties

    def _create_parameters(self) -> Dict[str, Any]:
        """
        Create parameter dict

        TODO: use AwsQpu when we have an API that returns parameters schema

        Returns:
            Dict[str, List]: Solver parameters in the form of a dict, where keys are
            keyword parameters in Braket format and values are lists of properties in
            :attr:`.BraketSampler.properties` for each key.
        """
        if self._device_arn == BraketSamplerArns.DWAVE:
            return {param: ["parameters"] for param in BraketSamplerParameters.DWAVE}
        else:
            raise NotImplementedError

    @property
    def parameters(self) -> Dict[str, List]:
        """
        Dict[str, List]: Solver parameters in the form of a dict, where keys are
        keyword parameters in Braket format and values are lists of properties in
        :attr:`.BraketSampler.properties` for each key.

        TODO: link boto3 docs

        Solver parameters are dependent on the selected solver and subject to change;
        for example, new released features may add parameters.
        """
        return self._parameters

    def _create_nodelist(self) -> List[int]:
        """
        Create nodelist

        List[int]: List of active qubits for the solver.
        """
        return sorted(set(self.properties["qubits"]))

    @property
    def nodelist(self) -> List[int]:
        """List[int]: List of active qubits for the solver."""
        return self._nodelist

    def _create_edgelist(self) -> List[Tuple[int, int]]:
        """
        Create edgelist

        List[Tuple[int, int]]: List of active couplers for the solver.
        """
        return sorted(set((u, v) if u < v else (v, u) for u, v in self.properties["couplers"]))

    @property
    def edgelist(self) -> List[Tuple[int, int]]:
        """List[Tuple[int, int]]: List of active couplers for the solver."""

        return self._edgelist

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
                    Optional keyword arguments for the sampling method
            Returns:
                :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.
            Examples:
                This example submits a two-variable Ising problem mapped directly to qubits
                0 and 1.

                >>> from braket.ocean_plugin import BraketSampler
                >>> sampler = BraketSampler(s3_destination_folder)
                >>> params = {"dWaveParameters": {"postprocessingType": "SAMPLING"}}
                >>> sampleset = sampler.sample_ising({0: -1, 1: 1}, {}, backend_parameters=params)
                >>> for sample in sampleset.samples():
                ...    print(sample)
                ...
                {0: 1, 1: -1}
        """
        if isinstance(h, list):
            h = dict((v, b) for v, b in enumerate(h) if b or v in self.nodelist)

        edges = self.edgelist
        if not (
            all(v in self.nodelist for v in h)
            and all((u, v) in edges or (v, u) in edges for u, v in J)
        ):
            raise BinaryQuadraticModelStructureError("Problem graph incompatible with solver.")

        future = self.solver.run(
            Problem(ProblemType.ISING, h, J), self._s3_destination_folder, **kwargs
        ).async_result()

        variables = set(h).union(*J)

        hook = BraketSampler._result_to_response_hook(variables, SPIN)
        return SampleSet.from_future(future, hook)

    def sample_qubo(self, Q: Dict[Tuple[int, int], int], **kwargs) -> SampleSet:
        """
        Sample from the specified QUBO.
            Args:
                Q (dict):
                    Coefficients of a quadratic unconstrained binary optimization (QUBO) model.
                **kwargs:
                    Optional keyword arguments for the sampling method
            Returns:
                :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.
            Examples:
                This example submits a two-variable QUBO mapped directly to qubits
                0 and 4 on a sampler

                >>> from braket.ocean_plugin import BraketSampler
                >>> sampler = BraketSampler(s3_destination_folder)
                >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
                >>> sampleset = sampler.sample_qubo(Q)
                >>> for sample in sampleset.samples():
                ...    print(sample)
                ...
                {0: 1, 1: -1}
        """
        if not all(
            u in self.nodelist if u == v else ((u, v) in self.edgelist or (v, u) in self.edgelist)
            for u, v in Q
        ):
            raise BinaryQuadraticModelStructureError("Problem graph incompatible with solver.")

        linear = {}
        quadratic = {}
        for (u, v), bias in Q.items():
            if u == v:
                linear[u] = bias
            else:
                quadratic[(u, v)] = bias

        future = self.solver.run(
            Problem(ProblemType.QUBO, linear, quadratic), self._s3_destination_folder, **kwargs
        ).async_result()

        variables = set().union(*Q)

        hook = BraketSampler._result_to_response_hook(variables, BINARY)
        return SampleSet.from_future(future, hook)

    @staticmethod
    def _result_to_response_hook(variables, vartype):
        def _hook(computation):
            result: AnnealingQuantumTaskResult = computation.result()
            # get the samples. The future will return all spins so filter for the ones in variables
            samples = [[sample[v] for v in variables] for sample in result.record_array.solution]
            energy = result.record_array.value
            num_occurrences = result.record_array.solution_count
            info = {
                "TaskMetadata": result.task_metadata,
                "AdditionalMetadata": result.additional_metadata,
            }

            return SampleSet.from_samples(
                (samples, variables),
                info=info,
                vartype=vartype,
                energy=energy,
                num_occurrences=num_occurrences,
                sort_labels=True,
            )

        return _hook
