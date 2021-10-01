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

import dwavebinarycsp as dbc
import minorminer
from dwave.embedding import embed_qubo, unembed_sampleset

from braket.ocean_plugin import BraketDWaveSampler

# Factoring example adapted from https://github.com/dwave-examples/factoring-notebook
# This example shows how to find the factors of a number using D-Wave

# It also shows an example of:
# Using minorminer instead of EmbeddingComposite to map the problem to the QPU
# How to get the quantum task object when a problem is run on a device
# Getting the SampleSet from the quantum task object


# Declare folder to save S3 results
s3_destination_folder = ("your-s3-bucket", "your-folder")
# Declare sampler
sampler = BraketDWaveSampler(s3_destination_folder)

integer_to_factor = 15

# Create a BQM representing the factorization problem
csp = dbc.factories.multiplication_circuit(3)
bqm = dbc.stitch(csp, min_classical_gap=0.1)
# Variables generated from multiplication_circuit()
p_vars = ["p0", "p1", "p2", "p3", "p4", "p5"]
# Convert integer to factor from decimal to binary
fixed_variables = dict(zip(reversed(p_vars), [int(s) for s in "{:06b}".format(integer_to_factor)]))
# Fix product variables
for var, value in fixed_variables.items():
    bqm.fix_variable(var, value)

# Find embedding using minorminer
Q, offset = bqm.to_qubo()
_, target_edgelist, target_adjacency = sampler.structure
embedding = minorminer.find_embedding(Q, target_edgelist)
qubo_embedded = embed_qubo(Q, embedding, target_adjacency, 3.0)

# Run embedded problem on D-Wave
task = sampler.sample_qubo_quantum_task(qubo_embedded, num_reads=1000, answer_mode="histogram")
print(task)

# Get response to original problem
unembedded_response = BraketDWaveSampler.get_task_sample_set(task)
sampleset = unembed_sampleset(unembedded_response, embedding, source_bqm=bqm)
sampleset.change_vartype(bqm.vartype, energy_offset=offset)


def to_base_ten(sample):
    a = b = 0
    # variables created by multiplication_circuit() in factoring_bqm
    a_vars = ["a0", "a1", "a2"]
    b_vars = ["b0", "b1", "b2"]
    for var in reversed(a_vars):
        a = (a << 1) | sample[var]
    for var in reversed(b_vars):
        b = (b << 1) | sample[var]
    return a, b


# Find solution to factorization from sampleset
sample, energy = next(sampleset.data(["sample", "energy"]))
a, b = to_base_ten(sample)
assert a * b == integer_to_factor
print(f"factors of {integer_to_factor}:", a, b)
