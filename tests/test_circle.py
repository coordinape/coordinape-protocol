import pytest

from brownie import accounts, chain, reverts


EPOCH_END = 42
PERM_EXTERNAL = 0
PERM_PARTICIPANT = 1
PERM_RECEIVING = 2


@pytest.fixture
def circle(CoordinapeCircle):
    return CoordinapeCircle.deploy("YEARN", "capeYFI", {"from": accounts[0]})


def test_circle_simple_data(circle):
    assert circle.owner() == accounts[0]

    assert circle.minimumVouches() == 2 ** 256 - 1
    circle.setMinimumVouches(2)
    assert circle.minimumVouches() == 2


def test_circle_total_supply(circle):
    assert circle.totalSupply() == 0
    circle.invite(accounts[1])
    assert circle.totalSupply() == 1
    circle.revoke(accounts[1])
    assert circle.totalSupply() == 0


def test_circle_start_epoch(circle):
    with reverts("Ownable: caller is not the owner"):
        circle.startEpoch(100, len(chain) + EPOCH_END, {"from": accounts[1]})

    with reverts("end block must be in the future."):
        circle.startEpoch(100, 0)

    circle.startEpoch(100, len(chain) + EPOCH_END)

    with reverts("another epoch is already in progress."):
        circle.startEpoch(100, len(chain) + EPOCH_END)

    chain.mine(EPOCH_END)
    circle.startEpoch(100, len(chain) + EPOCH_END)


def test_circle_invite(circle):
    with reverts("Ownable: caller is not the owner"):
        circle.invite(accounts[2], {"from": accounts[1]})

    circle.invite(accounts[1])
    circle.inviteNonReceiving(accounts[2])

    assert circle.permissionsOf(accounts[1]) == PERM_PARTICIPANT | PERM_RECEIVING
    assert circle.permissionsOf(accounts[2]) == PERM_PARTICIPANT

    assert circle.inviteOf(accounts[1]) == 1
    assert circle.inviteOf(accounts[2]) == 2

    with reverts("recipient is already invited."):
        circle.invite(accounts[2])
    with reverts("recipient is already invited."):
        circle.inviteNonReceiving(accounts[1])


def test_circle_edit(circle):
    with reverts("recipient is not invited."):
        circle.edit(accounts[1], PERM_PARTICIPANT)

    circle.invite(accounts[1])

    assert circle.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
    assert circle.permissionsOf(accounts[1]) & PERM_RECEIVING != 0

    circle.edit(accounts[1], PERM_PARTICIPANT)

    assert circle.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
    assert circle.permissionsOf(accounts[1]) & PERM_RECEIVING == 0

    with reverts("call revoke to remove user."):
        circle.edit(accounts[1], PERM_EXTERNAL)


def test_circle_revoke(circle):
    with reverts("recipient is not invited."):
        circle.revoke(accounts[1])

    circle.invite(accounts[1])
    assert circle.totalSupply() == 1
    circle.revoke(accounts[1])
    assert circle.totalSupply() == 0


def test_circle_vouch(circle):
    circle.invite(accounts[1])
    circle.inviteNonReceiving(accounts[2])

    circle.setMinimumVouches(2)

    with reverts("sender didn't receive minimum vouches."):
        circle.enter({"from": accounts[3]})
    with reverts("sender didn't receive minimum vouches."):
        circle.enterNonReceiving({"from": accounts[4]})

    assert circle.vouchesOf(accounts[3]) == 0
    circle.vouch(accounts[3], {"from": accounts[1]})
    assert circle.vouchesOf(accounts[3]) == 1

    with reverts("sender didn't receive minimum vouches."):
        circle.enter({"from": accounts[3]})
    with reverts("sender didn't receive minimum vouches."):
        circle.enterNonReceiving({"from": accounts[4]})

    circle.vouch(accounts[3], {"from": accounts[2]})

    with reverts("sender already vouched for recipient."):
        circle.vouch(accounts[3], {"from": accounts[2]})

    assert circle.vouchesOf(accounts[3]) == 2

    circle.vouch(accounts[4], {"from": accounts[1]})
    circle.vouch(accounts[4], {"from": accounts[2]})

    circle.enter({"from": accounts[3]})
    circle.enterNonReceiving({"from": accounts[4]})

    with reverts("sender is already invited."):
        circle.enter({"from": accounts[3]})
    with reverts("sender is already invited."):
        circle.enterNonReceiving({"from": accounts[4]})

    with reverts("recipient is already invited."):
        circle.vouch(accounts[3], {"from": accounts[2]})


def test_circle_join_epoch(circle, CoordinapeEpoch):
    with reverts("method can only be called by an invited user."):
        circle.joinCurrentEpoch({"from": accounts[1]})

    circle.invite(accounts[1])
    with reverts("no epoch currently in progress."):
        circle.joinCurrentEpoch({"from": accounts[1]})

    epoch = circle.startEpoch(100, len(chain) + EPOCH_END)
    epoch = CoordinapeEpoch.at(epoch.return_value)

    circle.joinCurrentEpoch({"from": accounts[1]})
    assert epoch.isParticipant(accounts[1]) is True
    assert epoch.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
    assert epoch.permissionsOf(accounts[1]) & PERM_RECEIVING != 0

    circle.leaveCurrentEpoch({"from": accounts[1]})
    assert epoch.isParticipant(accounts[1]) is True
    assert epoch.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
    assert epoch.permissionsOf(accounts[1]) & PERM_RECEIVING == 0


def test_circle_transfer(circle):
    circle.invite(accounts[1])

    invite_id = circle.inviteOf(accounts[1])

    with reverts("recipient didn't receive minimum vouches."):
        circle.transferFrom(accounts[1], accounts[4], invite_id, {"from": accounts[1]})

    circle.setMinimumVouches(2)
    circle.invite(accounts[2])
    circle.invite(accounts[3])
    circle.vouch(accounts[4], {"from": accounts[2]})
    circle.vouch(accounts[4], {"from": accounts[3]})

    perm = circle.permissionsOf(accounts[1])
    circle.transferFrom(accounts[1], accounts[4], invite_id, {"from": accounts[1]})

    assert circle.permissionsOf(accounts[1]) == PERM_EXTERNAL
    assert circle.permissionsOf(accounts[4]) == perm


def test_circle_members(circle):
    assert circle.membersCount() == 0
    assert len(circle.members()) == 0

    circle.invite(accounts[1])
    circle.invite(accounts[2])

    assert circle.membersCount() == 2
    assert accounts[1] in circle.members()
    assert accounts[2] in circle.members()
    assert accounts[3] not in circle.members()
