import pytest

from brownie import accounts, chain


EPOCH_END = 42


@pytest.fixture
def epoch(CoordinapeEpoch):
    end = len(chain) + EPOCH_END
    return CoordinapeEpoch.deploy(100, end, {"from": accounts[0]})


def test_epoch_timing(epoch):
    assert epoch.ended() == False
    chain.mine(EPOCH_END)
    assert epoch.ended() == True


def test_epoch_minting(epoch):
    assert epoch.totalSupply() == 0
    for i in range(3):
        epoch.addParticipant(accounts[i])
        assert epoch.balanceOf(accounts[i]) == 100
        assert epoch.totalSupply() == 100 * (i + 1)
