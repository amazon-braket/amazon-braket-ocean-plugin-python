**This prerelease documentation is confidential and is provided under the terms of your nondisclosure agreement with Amazon Web Services (AWS) or other agreement governing your receipt of AWS confidential information.**

The Amazon Braket Ocean Plugin is an open source library that provides a framework that you can use to interact with Ocean tools on top of Amazon Braket.

## Prerequisites
Before you begin working with the Amazon Braket Ocean Plugin, make sure that you've installed or configured the following prerequisites.

### Python 3.7.2 or greater
Download and install Python 3.7.2 or greater from [Python.org](https://www.python.org/downloads/).
If you are using Windows, choose **Add Python to environment variables** before you begin the installation.

### Amazon Braket SDK
Download and install the Amazon Braket SDK. Follow the instructions in the [README](https://github.com/aws/braket-python-sdk/blob/stable/latest/README.md).

### Ocean tools
Download and install [Ocean tools](https://docs.ocean.dwavesys.com/en/latest/overview/install.html).
```bash
pip install dwave-ocean-sdk
```

## Install the Amazon Braket Ocean plug-in package
Use the following commands to install the package:

```bash
pip install -e braket-ocean-python-plugin
```

## Documentation
You can generate the documentation for the plugin.

First, you must have tox installed.

```bash
pip install tox
```

Then, you can run the following command with tox to generate the documentation:

```bash
tox -e docs
```

To view the generated documentation, open the following file in a browser:
`BRAKET_OCEAN_PLUGIN_ROOT/build/documentation/html/index.html`

## Usage

This package provides samplers which use Braket solvers. These samplers extend abstract base classes provided in Ocean's dimod and thus have the same interfaces as other samplers in Ocean.

`BraketSampler` is a structured sampler that uses Braket-formatted parameters and properties. For example, instead of `answer_mode`, which is used for D-Wave QPU samplers, Braket uses `resultFormat` instead.
Below is a sample example of solving the [minimum vertex cover](https://en.wikipedia.org/wiki/Vertex_cover) problem using `BraketSampler`.

```python
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
```

`BraketDWaveSampler` is a structured sampler that uses D-Wave-formatted parameters and properties. It is interchangeable with D-Wave's `DWaveSampler`.
Below is the same example as above of solving the minimum vertext cover problem. Only the parameter inputs to the solver have been changed to be D-Wave formatted (e.g. `answer_mode` instead of `resultFormat`).

```python
from braket.ocean_plugin import BraketSamplerArns, BraketDWaveSampler
import networkx as nx
import dwave_networkx as dnx
from dwave.system.composites import EmbeddingComposite

s3_destination_folder = ("your-s3-bucket", "your-folder")
sampler = BraketDWaveSampler(s3_destination_folder, BraketSamplerArns.DWAVE)

star_graph = nx.star_graph(4) # star graph where node 0 is connected to 4 other nodes

# EmbeddingComposite automatically maps the problem to the structure of the solver.
embedded_sampler = EmbeddingComposite(sampler)

# The below result should be 0 because node 0 is connected to the 4 other nodes in a star graph
print(dnx.min_vertex_cover(star_graph, embedded_sampler, answer_mode="histogram"))
```
These usage examples can also be found as python scripts in the `BRAKET_OCEAN_PLUGIN_ROOT/examples/` folder.

## Install Additional Packages for Testing
Make sure to install test dependencies first:
```bash
pip install -e "braket-ocean-python-plugin[test]"
```

### Unit Tests
```bash
tox -e unit-tests
```

To run an individual test
```
tox -e unit-tests -- -k 'your_test'
```

To run linters and doc generators and unit tests
```bash
tox
```

### Integration Tests
Set the `AWS_PROFILE`, similar to in the braket-python-sdk [README](https://github.com/aws/braket-python-sdk/blob/stable/latest/README.md).
```bash
export AWS_PROFILE=Your_Profile_Name
```

Running the integration tests will create an S3 bucket in the same account as the `AWS_PROFILE` with the following naming convention `braket-ocean-plugin-integ-tests-{account_id}`.

Run the tests
```bash
tox -e integ-tests
```

To run an individual test
```bash
tox -e integ-tests -- -k 'your_test'
```

## License

This project is licensed under the Apache-2.0 License.
