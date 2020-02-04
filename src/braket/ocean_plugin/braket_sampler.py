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

from typing import Any, Dict, List, Tuple, Union

from dimod import Sampler, SampleSet, Structured

# TODO: implementation


class BraketSampler(Sampler, Structured):
    """
    A class for using Amazon Braket as a sampler
    """

    def __init__(self):
        self._properties = {}
        self._parameters = {}

    @property
    def properties(self) -> Dict[str, Any]:
        """
        dict: Solver properties in Braket boto3 response format

        TODO: link boto3 docs

        Solver properties are dependent on the selected solver and subject to change;
        for example, new released features may add properties.
        """
        return self._properties

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

    @property
    def nodelist(self) -> List[int]:
        """List[int]: List of active qubits for the solver."""
        raise NotImplementedError()

    @property
    def edgelist(self) -> List[Tuple[int, int]]:
        """List[Tuple[int, int]]: List of active couplers for the solver."""

        raise NotImplementedError()

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
                >>> sampler = BraketSampler()
                >>> sampleset = sampler.sample_ising({0: -1, 1: 1}, {})
                >>> for sample in sampleset.samples():    # doctest: +SKIP
                ...    print(sample)
                ...
                {0: 1, 1: -1}
        """
        raise NotImplementedError()

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
                0 and 4 on a D-Wave system.
                >>> from braket.ocean_plugin import BraketSampler
                >>> sampler = BraketSampler()
                >>> Q = {(0, 0): -1, (4, 4): -1, (0, 4): 2}
                >>> sampleset = sampler.sample_qubo(Q)
                >>> for sample in sampleset.samples():    # doctest: +SKIP
                ...    print(sample)
                ...
                {0: 0, 4: 1}
        """
        raise NotImplementedError()
