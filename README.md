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
You can generate the documentation for the plugin. First change directories (`cd`) to position the cursor in the (`doc`) directory.
Then run the following command to generate the HTML documentation files:

```bash
make html
```

To view the generated documentation, open the following file in a browser:
`BRAKET_OCEAN_PLUGIN_ROOT/build/documentation/html/index.html`

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

Create an S3 bucket in the same account as the `AWS_PROFILE` with the following naming convention `braket-ocean-plugin-integ-tests-{account_id}`.

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

