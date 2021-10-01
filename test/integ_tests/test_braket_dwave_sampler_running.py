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

from conftest import to_base_ten
from dwave.system.composites import EmbeddingComposite

from braket.ocean_plugin import BraketDWaveSampler


def test_factoring_embedded_composite(
    dwave_arn, aws_session, s3_destination_folder, factoring_bqm, integer_to_factor
):
    sampler = BraketDWaveSampler(
        s3_destination_folder, device_arn=dwave_arn, aws_session=aws_session
    )
    embedding_sampler = EmbeddingComposite(sampler)
    response = embedding_sampler.sample(
        factoring_bqm, chain_strength=3, num_reads=1000, answer_mode="histogram"
    )
    sample, energy = next(response.data(["sample", "energy"]))
    a, b = to_base_ten(sample)
    assert a * b == integer_to_factor
