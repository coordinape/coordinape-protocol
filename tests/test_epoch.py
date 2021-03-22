import pytest

from brownie import accounts, chain, reverts


EPOCH_END = 42
PERM_EXTERNAL = 0
PERM_PARTICIPANT = 1
PERM_RECEIVING = 2


@pytest.fixture
def epoch(CoordinapeEpoch):
    end = len(chain) + EPOCH_END
    return CoordinapeEpoch.deploy(100, end, {"from": accounts[0]})


def test_epoch_timing(epoch):
    assert epoch.ended() is False
    chain.mine(EPOCH_END)
    assert epoch.ended() is True


def test_epoch_minting(epoch):
    assert epoch.totalSupply() == 0
    for i in range(3):
        epoch.addParticipant(accounts[i], PERM_PARTICIPANT | PERM_RECEIVING)
        assert epoch.balanceOf(accounts[i]) == 100
        assert epoch.totalSupply() == 100 * (i + 1)


def test_epoch_notes(epoch):
    with reverts("method can only be called by a registered participant."):
        epoch.addNote(accounts[1], "noop", {"from": accounts[1]})

    epoch.addParticipant(accounts[1], PERM_PARTICIPANT | PERM_RECEIVING)

    with reverts("cannot add a note to self."):
        epoch.addNote(accounts[1], "noop", {"from": accounts[1]})

    with reverts("recipient is not a participant."):
        epoch.addNote(accounts[2], "noop", {"from": accounts[1]})

    epoch.addParticipant(accounts[2], PERM_PARTICIPANT | PERM_RECEIVING)
    epoch.addParticipant(accounts[3], PERM_PARTICIPANT)

    epoch.addNote(accounts[2], "Good note", {"from": accounts[1]})
