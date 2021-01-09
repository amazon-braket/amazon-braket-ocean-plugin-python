# Amazon Braket Ocean Plugin

[![Latest Version](https://img.shields.io/pypi/v/amazon-braket-ocean-plugin.svg)](https://pypi.python.org/pypi/amazon-braket-ocean-plugin)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/amazon-braket-ocean-plugin.svg)](https://pypi.python.org/pypi/amazon-braket-ocean-plugin)
[![Build Status](https://img.shields.io/github/workflow/status/aws/amazon-braket-ocean-plugin-python/Python%20package/main?logo=github)](https://github.com/aws/amazon-braket-ocean-plugin-python/actions?query=workflow%3A%22Python+package%22)
[![codecov](https://codecov.io/gh/aws/amazon-braket-ocean-plugin-python/branch/main/graph/badge.svg?token=NVBIB4BUX3)](https://codecov.io/gh/aws/amazon-braket-ocean-plugin-python)
[![Documentation Status](https://img.shields.io/readthedocs/amazon-braket-ocean-plugin-python.svg?logo=read-the-docs)](https://amazon-braket-ocean-plugin-python.readthedocs.io/en/latest/?badge=latest)
[![Code Style: Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)

The Amazon Braket Ocean Plugin is an open source library in Python that provides a framework that you can use to interact with Ocean tools on top of Amazon Braket.

## Prerequisites
Before you begin working with the Amazon Braket Ocean Plugin, make sure that you've installed or configured the following prerequisites.

### Python 3.7.2 or greater
Download and install Python 3.7.2 or greater from [Python.org](https://www.python.org/downloads/).
If you are using Windows, choose **Add Python to environment variables** before you begin the installation.

### Amazon Braket SDK
Make sure that your AWS account is onboarded to Amazon Braket, as per the instructions in the [README](https://github.com/aws/amazon-braket-sdk-python#prerequisites).

### Ocean tools
Download and install [Ocean tools](https://docs.ocean.dwavesys.com/en/latest/overview/install.html).
```bash
pip install dwave-ocean-sdk
```

## Install the Amazon Braket Ocean Plugin

The Amazon Braket Ocean Plugin can be installed with pip as follows:

```bash
pip install amazon-braket-ocean-plugin
```

You can also install from source by cloning this repository and running a pip install command in the root directory of the repository:

```bash
git clone https://github.com/aws/amazon-braket-ocean-plugin-python.git
cd amazon-braket-ocean-plugin-python
pip install .
```

You can check your currently installed version of `amazon-braket-ocean-plugin` with `pip show`:

```bash
pip show amazon-braket-ocean-plugin
```

or alternatively from within Python:

```
>>> from braket import ocean_plugin
>>> ocean_plugin.__version__
```

## Documentation

Detailed documentation, including the API reference, can be found on [Read the Docs](https://amazon-braket-ocean-plugin-python.readthedocs.io/en/latest/).

**To generate the API Reference HTML in your local environment**

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
[Linked](https://github.com/aws/amazon-braket-ocean-plugin-python/blob/main/examples/braket_sampler_min_vertex.py) is a sample example of solving the [minimum vertex cover](https://en.wikipedia.org/wiki/Vertex_cover) problem using `BraketSampler`.

`BraketDWaveSampler` is a structured sampler that uses D-Wave-formatted parameters and properties. It is interchangeable with D-Wave's `DWaveSampler`.
[Linked](https://github.com/aws/amazon-braket-ocean-plugin-python/blob/main/examples/braket_dwave_sampler_min_vertex.py) is the same example as above of solving the minimum vertex cover problem. Only the parameter inputs to the solver have been changed to be D-Wave formatted (e.g. `answer_mode` instead of `resultFormat`).

These usage examples can be found as python scripts in the `BRAKET_OCEAN_PLUGIN_ROOT/examples/` folder.

### Debugging Logs

Tasks sent to QPUs don't always complete right away. To view task status, you can enable debugging logs. An example of how to enable these logs is included in the repo: `BRAKET_OCEAN_PLUGIN_ROOT/examples/debug_*`. These examples enable task logging so that status updates are continuously printed to terminal after a quantum task is executed. The logs can also be configured to save to a file or output to another stream. You can use the debugging example to get information on the tasks you submit, such as the current status, so that you know when your task completes.

## Install Additional Packages for Testing
Make sure to install test dependencies first:
```bash
pip install -e "amazon-braket-ocean-plugin-python[test]"
```

### Unit Tests

To run the unit tests:

```bash
tox -e unit-tests
```

You can also pass in various pytest arguments to run selected tests:

```bash
tox -e unit-tests -- your-arguments
```

For more information, please see [pytest usage](https://docs.pytest.org/en/stable/usage.html).

To run linters and doc generators and unit tests:

```bash
tox
```

### Integration Tests

Set the `AWS_PROFILE`, as instructed in the amazon-braket-sdk-python [README](https://github.com/aws/amazon-braket-sdk-python/blob/main/README.md).

```bash
export AWS_PROFILE=YOUR_PROFILE_NAME
```

Running the integration tests will create an S3 bucket in the same account as the `AWS_PROFILE` with the following naming convention `amazon-braket-ocean-plugin-integ-tests-{account_id}`.

Run the tests:

```bash
tox -e integ-tests
```

As with unit tests, you can also pass in various pytest arguments:

```bash
tox -e integ-tests -- your-arguments
```

## License

This project is licensed under the Apache-2.0 License.
