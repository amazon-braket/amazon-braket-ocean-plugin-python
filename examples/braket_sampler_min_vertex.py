from braket.ocean_plugin import BraketSamplerArns, BraketSampler
import networkx as nx
import dwave_networkx as dnx
from dwave.system.composites import EmbeddingComposite

s3_destination_folder = ("your-s3-bucket", "your-folder")
sampler = BraketSampler(s3_destination_folder, BraketSamplerArns.DWAVE)

star_graph = nx.star_graph(4) # star graph where node 0 is connected to 4 other nodes

# EmbeddingComposite automatically maps the problem to the structure of the solver.
embedded_sampler = EmbeddingComposite(sampler)

# The below result should be 0 because node 0 is connected to the 4 other nodes in a star graph
print(dnx.min_vertex_cover(star_graph, embedded_sampler, resultFormat="HISTOGRAM"))