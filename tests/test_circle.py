import pytest

from brownie import accounts, chain, reverts


EPOCH_END = 42
PERM_EXTERNAL = 0
PERM_PARTICIPANT = 1
PERM_RECEIVING = 2


@pytest.fixture
def circle(CoordinapeCircle):
    return CoordinapeCircle.deploy("YEARN", "capeYFI", {"from": accounts[0]})


def test_circle_owner(circle):
    assert circle.owner() == accounts[0]


def test_circle_start_epoch(circle):
    with reverts():  # only owner can start a new epoch
        circle.startEpoch(100, len(chain) + EPOCH_END, {"from": accounts[1]})

    circle.startEpoch(100, len(chain) + EPOCH_END)
    with reverts():  # only one epoch per circle is allowed at a time
        circle.startEpoch(100, len(chain) + EPOCH_END)
    chain.mine(EPOCH_END)
    circle.startEpoch(100, len(chain) + EPOCH_END)


def test_circle_invite(circle):
    with reverts():  # user can be invited only by owner
        circle.invite(accounts[2], {"from": accounts[1]})

    circle.invite(accounts[1])
    circle.inviteNonReceiving(accounts[2])

    assert circle.permissionsOf(accounts[1]) == PERM_PARTICIPANT | PERM_RECEIVING
    assert circle.permissionsOf(accounts[2]) == PERM_PARTICIPANT

    with reverts():  # user can be invited only once
        circle.invite(accounts[1])


def test_circle_vouch(circle):
    circle.invite(accounts[1])
    circle.inviteNonReceiving(accounts[2])

    circle.setMinimumVouches(2)

    with reverts():  # user can enter the circle only if vouched by 2 members
        circle.enter({"from": accounts[3]})

    assert circle.vouchesOf(accounts[3]) == 0
    circle.vouch(accounts[3], {"from": accounts[1]})
    assert circle.vouchesOf(accounts[3]) == 1

    with reverts():  # user can enter the circle only if vouched by 2 members
        circle.enter({"from": accounts[3]})

    circle.vouch(accounts[3], {"from": accounts[2]})
    assert circle.vouchesOf(accounts[3]) == 2

    circle.enter({"from": accounts[3]})


def test_circle_join_epoch(circle, CoordinapeEpoch):
    with reverts("CoordinapeCircle: method can only be called by an invited user."):
        circle.joinCurrentEpoch({"from": accounts[1]})

    circle.invite(accounts[1])
    with reverts("CoordinapeCircle: no epoch currently in progress."):
        circle.joinCurrentEpoch({"from": accounts[1]})

    epoch = circle.startEpoch(100, len(chain) + EPOCH_END)
    circle.joinCurrentEpoch({"from": accounts[1]})

    epoch = CoordinapeEpoch.at(epoch.return_value)
    assert epoch.isParticipant(accounts[1]) is True
