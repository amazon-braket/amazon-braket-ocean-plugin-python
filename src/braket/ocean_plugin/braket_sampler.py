# Copyright 2019-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# ). You
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
from typing import Any, Dict, FrozenSet, List, Set, Tuple, Union

from boltons.dictutils import FrozenDict
from braket.annealing.problem import Problem, ProblemType
from braket.aws import AwsQpu, AwsQuantumTask, AwsSession
from braket.ocean_plugin.braket_sampler_arns import get_arn_to_enum_name_mapping
from braket.ocean_plugin.braket_solver_metadata import BraketSolverMetadata
from braket.ocean_plugin.exceptions import InvalidSolverDeviceArn
from braket.tasks import AnnealingQuantumTaskResult, QuantumTask
from dimod import BINARY, SPIN, Sampler, SampleSet, Structured
from dimod.exceptions import BinaryQuadraticModelStructureError


class BraketSampler(Sampler, Structured):
    """
    A class for using Amazon Braket as a sampler

    Args:
        s3_destination_folder (AwsSession.S3DestinationFolder): NamedTuple with bucket (index 0)
            and key (index 1) that is the results destination folder in S3.
        device_arn (str): AWS quantum device arn.
        aws_session (AwsSession): AwsSession to call AWS with.
        logger (Logger): Python Logger object with which to write logs, such as `QuantumTask`
            statuses while polling for task to complete. Default is `getLogger(__name__)`

    Raises:
        InvalidSolverDeviceArn: If provided device ARN for solver is unsupported.

    Examples:
        >>> from braket.ocean_plugin import BraketSampler, BraketSamplerArns
        >>> s3_destination_folder = ('test_bucket', 'test_folder')
        >>> sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)
    """

    ISING_PROBLEM_TYPE = "ising"
    QUBO_PROBLEM_TYPE = "qubo"

    def __init__(
        self,
        s3_destination_folder: AwsSession.S3DestinationFolder,
        device_arn: str,
        aws_session: AwsSession = None,
        logger: Logger = getLogger(__name__),
    ):
        self._s3_destination_folder = s3_destination_folder

        if device_arn not in get_arn_to_enum_name_mapping():
            raise InvalidSolverDeviceArn(f"Invalid device ARN {device_arn}")
        self._device_arn = device_arn
        self._logger = logger

        self.solver = AwsQpu(device_arn, aws_session)

    @property
    @lru_cache(maxsize=1)
    def properties(self) -> FrozenDict[str, Any]:
        """
        FrozenDict[str, Any]: Solver properties in Braket boto3 response format

        TODO: link boto3 docs

        Solver properties are dependent on the selected solver and subject to change;
        for example, new released features may add properties.
        """
        return FrozenDict(copy.deepcopy(self.solver.properties))

    @property
    @lru_cache(maxsize=1)
    def parameters(self) -> FrozenDict[str, List]:
        """
        FrozenDict[str, List]: Solver parameters in the form of a dict, where keys are
        keyword parameters in Braket format and values are lists of properties in
        :attr:`.BraketSampler.properties` for each key.

        TODO: link boto3 docs

        Solver parameters are dependent on the selected solver and subject to change;
        for example, new released features may add parameters.
        """
        enum_name = get_arn_to_enum_name_mapping()[self._device_arn]
        return FrozenDict(
            {
                param: ["parameters"]
                for param in BraketSolverMetadata[enum_name]["parameters"].values()
            }
        )

    @property
    @lru_cache(maxsize=1)
    def nodelist(self) -> Tuple[int]:
        """Tuple[int]: Tuple of active qubits for the solver."""
        return tuple(sorted(set(self.properties["qubits"])))

    @property
    @lru_cache(maxsize=1)
    def edgelist(self) -> Tuple[Tuple[int, int]]:
        """Tuple[Tuple[int, int]]: Tuple of active couplers for the solver."""
        return tuple(
            sorted(set((u, v) if u < v else (v, u) for u, v in self.properties["couplers"]))
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
                Optional keyword arguments for the sampling method in Braket boto3 format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Raises:
            BinaryQuadraticModelStructureError: If problem graph is incompatible with solver
            ValueError: If keyword argument is unsupported by solver

        Examples:
            This example submits a two-variable Ising problem mapped directly to qubits
            0 and 1.

            >>> from braket.ocean_plugin import BraketSampler
            >>> sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)
            >>> sampleset = sampler.sample_ising({0: -1, 1: 1}, {}, resultFormat="HISTOGRAM")
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """

        if isinstance(h, list):
            h = dict((v, b) for v, b in enumerate(h) if b or v in self.nodelist)

        aws_task = self.sample_ising_quantum_task(h, J, **kwargs)
        variables = set(h).union(*J)

        return BraketSampler.get_task_sample_set(aws_task, variables)

    def sample_ising_quantum_task(
        self, h: Union[Dict[int, int], List[int]], J: Dict[int, int], **kwargs
    ) -> QuantumTask:
        """
        Sample from the specified Ising model and return a `QuantumTask`. This has the same inputs
        as `BraketSampler.sample_ising`.

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
                Optional keyword arguments for the sampling method in Braket boto3 format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Raises:
            BinaryQuadraticModelStructureError: If problem graph is incompatible with solver
            ValueError: If keyword argument is unsupported by solver

        Examples:
            This example submits a two-variable Ising problem mapped directly to qubits
            0 and 1.

            >>> from braket.ocean_plugin import BraketSampler
            >>> sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)
            >>> task = sampler.sample_ising_quantum_task({0: -1}, {}, resultFormat="HISTOGRAM")
            >>> sampleset = BraketSampler.get_task_sample_set(task)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """
        solver_kwargs = self._process_solver_kwargs(**kwargs)

        if isinstance(h, list):
            h = dict((v, b) for v, b in enumerate(h) if b or v in self.nodelist)

        edges = self.edgelist
        if not (
            all(v in self.nodelist for v in h)
            and all((u, v) in edges or (v, u) in edges for u, v in J)
        ):
            raise BinaryQuadraticModelStructureError("Problem graph incompatible with solver.")

        return self.solver.run(
            Problem(ProblemType.ISING, h, J),
            self._s3_destination_folder,
            logger=self._logger,
            **solver_kwargs,
        )

    def sample_qubo(self, Q: Dict[Tuple[int, int], int], **kwargs) -> SampleSet:
        """
        Sample from the specified QUBO.

        Args:
            Q (dict):
                Coefficients of a quadratic unconstrained binary optimization (QUBO) model.
            **kwargs:
                Optional keyword arguments for the sampling method in Braket boto3 format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Raises:
            BinaryQuadraticModelStructureError: If problem graph is incompatible with solver
            ValueError: If keyword argument is unsupported by solver

        Examples:
            This example submits a two-variable QUBO mapped directly to qubits
            0 and 4 on a sampler

            >>> from braket.ocean_plugin import BraketSampler
            >>> sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)
            >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
            >>> sampleset = sampler.sample_qubo(Q, postprocessingType="SAMPLING", shots=100)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """
        aws_task = self.sample_qubo_quantum_task(Q, **kwargs)
        variables = set().union(*Q)
        return BraketSampler.get_task_sample_set(aws_task, variables)

    def sample_qubo_quantum_task(self, Q: Dict[Tuple[int, int], int], **kwargs) -> QuantumTask:
        """
        Sample from the specified QUBO and return a `QuantumTask`. This has the same inputs
        as `BraketSampler.sample_qubo`

        Args:
            Q (dict):
                Coefficients of a quadratic unconstrained binary optimization (QUBO) model.
            **kwargs:
                Optional keyword arguments for the sampling method in Braket boto3 format

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Raises:
            BinaryQuadraticModelStructureError: If problem graph is incompatible with solver
            ValueError: If keyword argument is unsupported by solver

        Examples:
            This example submits a two-variable QUBO mapped directly to qubits
            0 and 4 on a sampler

            >>> from braket.ocean_plugin import BraketSampler
            >>> sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)
            >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
            >>> task = sampler.sample_qubo_quantum_task(Q, resultFormat="HISTOGRAM", shots=100)
            >>> sampleset = BraketSampler.get_task_sample_set(task)
            >>> for sample in sampleset.samples():
            ...    print(sample)
            ...
            {0: 1, 1: -1}
        """
        solver_kwargs = self._process_solver_kwargs(**kwargs)

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

        return self.solver.run(
            Problem(ProblemType.QUBO, linear, quadratic),
            self._s3_destination_folder,
            logger=self._logger,
            **solver_kwargs,
        )

    @staticmethod
    def get_task_sample_set(task: AwsQuantumTask, variables: Set[int] = None) -> SampleSet:
        """
        Get SampleSet from an `AwsQuantumTask` object

        Args:
            task (AwsQuantumTask): task from which to get `SampleSet`
            variables (Set[int], optional): variables for samples in `SampleSet`.
                The default is the set of active variables for D-Wave.
                If there are no active variables marked as part of the task result,
                the default is `list(range(result.variable_count))`.

        Returns:
            :class:`dimod.SampleSet`: A `dimod` :obj:`~dimod.SampleSet` object.

        Examples:
            >>> from braket.ocean_plugin import BraketSampler
            >>> from braket.aws import AwsQuantumTask
            >>> sample_set = sampler.get_task_sample_set(AwsQuantumTask(arn="your_arn"))
        """
        hook = BraketSampler._result_to_response_hook(variables)
        return SampleSet.from_future(task, hook)

    def _process_solver_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        Process kwargs to be compatible as kwargs for the solver.

        Args:
            **kwargs: Optional keyword arguments for sampling method
        Return:
            Dict[str, Any]: a dict of kwargs to the solver
        """
        self._check_kwargs_solver(**kwargs)
        return self._create_solver_kwargs(**kwargs)

    def _check_kwargs_solver(self, **kwargs):
        """
        Check if kwargs are supported by solver

        Args:
            **kwargs: Optional keyword arguments for sampling method
        Raises:
            ValueError: If key word argument is unsupported by solver
        """
        for parameter in kwargs:
            if parameter not in self.parameters:
                raise ValueError(f"Parameter {parameter} not supported")

    def _create_solver_kwargs(self, **kwargs):
        """
        Transform **kwargs to create a dict of kwargs to the solver.

        Args:
            **kwargs: Optional keyword arguments for sampling method
        Return:
            Dict[str, Any]: a dict of kwargs to the solver
        """
        enum_name = get_arn_to_enum_name_mapping()[self._device_arn]
        key_name = BraketSolverMetadata[enum_name]["backend_parameters_key_name"]
        solver_kwargs = {"backend_parameters": {key_name: kwargs}}
        if "shots" in kwargs:
            shots = kwargs["shots"]
            del kwargs["shots"]
            solver_kwargs.update({"shots": shots})
        return solver_kwargs

    @staticmethod
    def _result_to_response_hook(variables: Set[int] = None):
        def _hook(computation):
            result: AnnealingQuantumTaskResult = computation.result()
            # get the samples. The future will return all spins so filter for the ones in variables
            vars = BraketSampler._vars_from_variables(result, variables)
            samples = [[sample[v] for v in vars] for sample in result.record_array.solution]
            energy = result.record_array.value
            num_occurrences = result.record_array.solution_count
            info = {
                "TaskMetadata": result.task_metadata,
                "AdditionalMetadata": result.additional_metadata,
            }
            vartype = BraketSampler._vartype_from_problem_type(result.problem_type)
            return SampleSet.from_samples(
                (samples, vars),
                info=info,
                vartype=vartype,
                energy=energy,
                num_occurrences=num_occurrences,
                sort_labels=True,
            )

        return _hook

    @staticmethod
    def _vars_from_variables(
        result: AnnealingQuantumTaskResult, variables: Set[int] = None
    ) -> FrozenSet[int]:
        if variables:
            return frozenset(variables)
        additional_metadata = result.additional_metadata.get("DWaveMetadata", {})
        if "ActiveVariables" in additional_metadata:
            return frozenset(additional_metadata.get("ActiveVariables"))
        return frozenset(list(range(result.variable_count)))

    @staticmethod
    def _vartype_from_problem_type(problem_type: str) -> Union[SPIN, BINARY]:
        if problem_type == BraketSampler.QUBO_PROBLEM_TYPE:
            return BINARY
        elif problem_type == BraketSampler.ISING_PROBLEM_TYPE:
            return SPIN
        else:
            raise ValueError(f"Unknown problem type {problem_type}")
