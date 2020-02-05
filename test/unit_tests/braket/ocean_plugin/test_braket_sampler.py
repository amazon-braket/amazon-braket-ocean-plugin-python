import pytest
from braket.ocean_plugin import BraketSampler


@pytest.fixture
def braket_sampler():
    return BraketSampler()


def test_parameters(braket_sampler):
    assert braket_sampler.parameters == {}


def test_properties(braket_sampler):
    assert braket_sampler.properties == {}


@pytest.mark.xfail(raises=NotImplementedError)
def test_edgelist(braket_sampler):
    braket_sampler.edgelist


@pytest.mark.xfail(raises=NotImplementedError)
def test_nodelist(braket_sampler):
    braket_sampler.nodelist


@pytest.mark.xfail(raises=NotImplementedError)
def test_sample_qubo(braket_sampler):
    braket_sampler.sample_qubo({})


@pytest.mark.xfail(raises=NotImplementedError)
def test_sample_ising(braket_sampler):
    braket_sampler.sample_ising({}, {})
