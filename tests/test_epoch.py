# import pytest

# from brownie import accounts, chain, reverts


# EPOCH_END = 42
# PERM_EXTERNAL = 0
# PERM_PARTICIPANT = 1
# PERM_RECEIVER = 2
# PERM_GIVER = 4


# @pytest.fixture
# def epoch(CoordinapeEpoch):
#     end = len(chain) + EPOCH_END
#     return CoordinapeEpoch.deploy(100, end, {"from": accounts[0]})


# def test_epoch_timing(epoch):
#     assert epoch.ended() is False
#     chain.mine(EPOCH_END)
#     assert epoch.ended() is True


# def test_epoch_minting(epoch):
#     assert epoch.totalSupply() == 0
#     for i in range(3):
#         epoch.addParticipant(accounts[i], PERM_PARTICIPANT | PERM_RECEIVER)
#         assert epoch.balanceOf(accounts[i]) == 100
#         assert epoch.totalSupply() == 100 * (i + 1)


# def test_epoch_participants(epoch):
#     assert len(epoch.participants()) == 0

#     epoch.addParticipant(accounts[1], PERM_PARTICIPANT)

#     assert len(epoch.participants()) == 1

#     with reverts("recipient is already a participant."):
#         epoch.addParticipant(accounts[1], PERM_PARTICIPANT)

#     with reverts("call removeParticipant to remove participant."):
#         epoch.editParticipant(accounts[1], PERM_EXTERNAL)

#     with reverts("permissions must contain at least 'PARTICIPANT'."):
#         epoch.editParticipant(accounts[1], PERM_RECEIVER)

#     epoch.editParticipant(accounts[1], PERM_PARTICIPANT | PERM_RECEIVER)

#     epoch.removeParticipant(accounts[1])

#     # still one, because a when a user is removed from an epoch he loses
#     # all permissions but the the PERM_PARTICIPANT one, to prevent rejoining
#     assert len(epoch.participants()) == 1

#     with reverts("sender is already a non-receiver participant."):
#         epoch.removeParticipant(accounts[1])


# def test_epoch_notes(epoch):
#     with reverts("method can only be called by a registered participant."):
#         epoch.addNote(accounts[1], "noop", {"from": accounts[1]})

#     epoch.addParticipant(accounts[1], PERM_PARTICIPANT | PERM_RECEIVER)

#     with reverts("cannot add a note to self."):
#         epoch.addNote(accounts[1], "noop", {"from": accounts[1]})

#     with reverts("recipient is not a participant."):
#         epoch.addNote(accounts[2], "noop", {"from": accounts[1]})

#     epoch.addParticipant(accounts[2], PERM_PARTICIPANT | PERM_RECEIVER)
#     epoch.addParticipant(accounts[3], PERM_PARTICIPANT)

#     epoch.addNote(accounts[2], "Good note", {"from": accounts[1]})
