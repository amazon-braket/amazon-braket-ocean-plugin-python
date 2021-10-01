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

import os

import boto3
import dwavebinarycsp as dbc
import pytest
from botocore.exceptions import ClientError
from braket.aws import AwsDevice, AwsSession


@pytest.fixture
def dwave_arn():
    return AwsDevice.get_devices(provider_names=["D-Wave Systems"], statuses=["ONLINE"])[0].arn


@pytest.fixture(scope="session")
def boto_session():
    profile_name = os.environ["AWS_PROFILE"]
    return boto3.session.Session(profile_name=profile_name)


@pytest.fixture(scope="session")
def aws_session(boto_session):
    return AwsSession(boto_session)


@pytest.fixture(scope="session")
def s3_resource(boto_session):
    return boto_session.resource("s3")


@pytest.fixture(scope="session")
def s3_client(boto_session):
    return boto_session.client("s3")


@pytest.fixture(scope="session")
def account_id(boto_session):
    return boto_session.client("sts").get_caller_identity()["Account"]


@pytest.fixture(scope="session")
def s3_bucket(s3_resource, s3_client, account_id, boto_session):
    """Create / get S3 bucket for tests"""

    region_name = boto_session.region_name
    bucket_name = f"amazon-braket-ocean-plugin-integ-tests-{account_id}"
    bucket = s3_resource.Bucket(bucket_name)

    try:
        # Determine if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            bucket.create(
                ACL="private", CreateBucketConfiguration={"LocationConstraint": region_name}
            )

    return bucket_name


@pytest.fixture(scope="module")
def s3_prefix():
    """Returns the module path of the test, e.g. integ_tests/test_braket_sampler_running"""

    # current test path, e.g. ...
    # test/integ_tests/test_simulator_quantum_task.py::test_simulator_quantum_task (setup)
    current_test_path = os.environ.get("PYTEST_CURRENT_TEST")

    # strip off the filename extension and test/
    return current_test_path.rsplit(".py")[0].replace("test/", "")


@pytest.fixture(scope="module")
def s3_destination_folder(s3_bucket, s3_prefix):
    return AwsSession.S3DestinationFolder(s3_bucket, s3_prefix)


@pytest.fixture(scope="session")
def integer_to_factor():
    # must be <=2^6, with factors <=2^3
    return 15


@pytest.fixture(scope="session")
def factoring_bqm(integer_to_factor):
    csp = dbc.factories.multiplication_circuit(3)
    bqm = dbc.stitch(csp, min_classical_gap=0.1)
    # variables generated from multiplication_circuit()
    p_vars = ["p0", "p1", "p2", "p3", "p4", "p5"]
    # Convert integer to factor from decimal to binary
    fixed_variables = dict(
        zip(reversed(p_vars), [int(s) for s in "{:06b}".format(integer_to_factor)])
    )
    # Fix product variables
    for var, value in fixed_variables.items():
        bqm.fix_variable(var, value)
    return bqm


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
