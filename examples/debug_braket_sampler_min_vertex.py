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

import logging
import sys

import dwave_networkx as dnx
import networkx as nx
from braket.aws import AwsDevice
from dwave.system.composites import EmbeddingComposite

from braket.ocean_plugin import BraketSampler

logger = logging.getLogger("newLogger")  # create new logger
logger.addHandler(logging.StreamHandler(stream=sys.stdout))  # configure to print to sys.stdout
logger.setLevel(logging.DEBUG)  # print to sys.stdout all log messages with level DEBUG or above

s3_destination_folder = ("your-s3-bucket", "your-folder")

# Get an online D-Wave device ARN
device_arn = AwsDevice.get_devices(provider_names=["D-Wave Systems"], statuses=["ONLINE"])[0].arn
print("Using device ARN", device_arn)

# Pass in logger to BraketSampler
sampler = BraketSampler(s3_destination_folder, device_arn, logger=logger)

star_graph = nx.star_graph(4)  # star graph where node 0 is connected to 4 other nodes

# EmbeddingComposite automatically maps the problem to the structure of the solver.
embedded_sampler = EmbeddingComposite(sampler)

# The below result should be 0 because node 0 is connected to the 4 other nodes in a star graph
logger.info(dnx.min_vertex_cover(star_graph, embedded_sampler, resultFormat="HISTOGRAM"))
