# Changelog

## v1.0.6 (2021-10-04)

### Bug Fixes and Other Changes

 * update copyright headers

### Testing and Release Infrastructure

 * pin colorama >=0.4.3

## v1.0.5 (2021-08-05)

### Bug Fixes and Other Changes

 * Update dependency versions and git workflow builds

## v1.0.4 (2021-06-03)

### Bug Fixes and Other Changes

 * filter device parameters based on arn

## v1.0.3.post2 (2021-06-03)

### Testing and Release Infrastructure

 * Use GitHub source for tox tests

## v1.0.3.post1 (2021-03-11)

### Testing and Release Infrastructure

 * Add Python 3.9

## v1.0.3.post0 (2021-03-03)

### Testing and Release Infrastructure

 * Use main instead of PyPi for build dependencies

## v1.0.3 (2021-02-06)

### Bug Fixes and Other Changes

 * Throw BinaryQuadraticModelStructureError on bad edges

## v1.0.2.post2 (2021-01-12)

### Testing and Release Infrastructure

 * Enable Codecov

## v1.0.2.post1 (2020-12-30)

### Testing and Release Infrastructure

 * Add build badge
 * Use GitHub Actions for CI

## v1.0.2.post0 (2020-12-04)

### Testing and Release Infrastructure

 * Change tox basepython to python3

## v1.0.2 (2020-11-23)

### Bug Fixes and Other Changes

 * Optimized graph validation
 * Leaner graph validation

## v1.0.1.post3 (2020-10-30)

### Testing and Release Infrastructure

 * updating codeowners

## v1.0.1.post2 (2020-10-05)

### Testing and Release Infrastructure

 * change check for s3 bucket exists
 * change bucket creation setup for integ tests

## v1.0.1.post1 (2020-09-10)

### Testing and Release Infrastructure

 * fix black formatting

## v1.0.1.post0 (2020-09-09)

### Testing and Release Infrastructure

 * Add CHANGELOG.md

## v1.0.1 (2020-09-09)

## Bug Fixes and Other Changes
* Remove hard-coded ARNs and replace with `AwsDevice.get_devices`

## Documentation
* Add factoring example

## v1.0.0.post1 (2020-08-14)

The only way to update a description in PyPi is to upload new files;
however, uploading an existing version is prohibited. The recommended
way to deal with this is with
[post-releases](https://www.python.org/dev/peps/pep-0440/#post-releases).

## v1.0.0 (2020-08-13)

This is the public release of the Amazon Braket Ocean Plugin!

The Amazon Braket Ocean Plugin is an open source library in Python that provides a framework that you can use to interact with Ocean tools on top of Amazon Braket.
