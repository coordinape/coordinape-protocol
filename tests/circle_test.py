import pytest

from brownie import accounts, chain, reverts


EPOCH_END = 42


@pytest.fixture
def circle(CoordinapeCircle):
    return CoordinapeCircle.deploy("YEARN", "CAPE-YFI", {"from": accounts[0]})


def test_circle(circle):
    assert circle.owner() == accounts[0]


def test_circle_epoch(circle):
    circle.startEpoch(100, EPOCH_END)
    with reverts():  # only one epoch per circle is allowed at a time
        circle.startEpoch(100, EPOCH_END)
    chain.mine(EPOCH_END)
    circle.startEpoch(100, EPOCH_END)
