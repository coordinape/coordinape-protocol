# import pytest

# from brownie import accounts, chain, reverts


# EPOCH_END = 42
# PERM_EXTERNAL = 0
# PERM_PARTICIPANT = 1
# PERM_RECEIVER = 2
# PERM_GIVER = 4


# @pytest.fixture
# def circle(CoordinapeCircle, TokenSet):
#     _set = TokenSet.deploy('0xf521Bb7437bEc77b0B15286dC3f49A87b9946773',{"from": accounts[0]})
#     circle = CoordinapeCircle.deploy("YEARN", "capeYFI", "", 5, {"from": accounts[0]})
#     circle.setTokenSet(_set, {'from':accounts[0]})
#     _set.transferOwnership(circle, {'from':accounts[0]})
#     return circle

# def test_circle_simple_data(circle):
#     assert circle.owner() == accounts[0]

#     assert circle.minimumVouches() == 5
#     circle.setMinimumVouches(2)
#     assert circle.minimumVouches() == 2


# def test_circle_total_supply(circle):
#     assert circle.totalSupply() == 0
#     circle.invite(accounts[1], PERM_PARTICIPANT)
#     assert circle.totalSupply() == 1
#     circle.revoke(accounts[1])
#     assert circle.totalSupply() == 0


# def test_circle_start_epoch(circle):
#     with reverts("Ownable: caller is not the owner"):
#         circle.startEpoch(100, len(chain) + EPOCH_END, 0,{"from": accounts[1]})

#     with reverts("end block must be in the future."):
#         circle.startEpoch(100, 0, 0)

#     circle.startEpoch(100, len(chain) + EPOCH_END, 0)

#     with reverts("another epoch is already in progress."):
#         circle.startEpoch(100, len(chain) + EPOCH_END, 0)

#     chain.mine(EPOCH_END)
#     circle.startEpoch(100, len(chain) + EPOCH_END, 0)


# def test_circle_invite(circle):
#     with reverts("Ownable: caller is not the owner"):
#         circle.invite(accounts[2], PERM_PARTICIPANT,{"from": accounts[1]})

#     circle.invite(accounts[1], PERM_PARTICIPANT)

#     assert circle.permissionsOf(accounts[1]) == PERM_PARTICIPANT

#     assert circle.inviteOf(accounts[1]) == 1

#     with reverts("recipient is already invited."):
#         circle.invite(accounts[1], PERM_PARTICIPANT)


# def test_circle_edit(circle):
#     with reverts("recipient is not invited."):
#         circle.edit(accounts[1], PERM_PARTICIPANT)

#     circle.invite(accounts[1], PERM_PARTICIPANT)

#     assert circle.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
#     assert circle.permissionsOf(accounts[1]) & PERM_RECEIVER == 0

#     circle.edit(accounts[1], PERM_PARTICIPANT)

#     assert circle.permissionsOf(accounts[1]) & PERM_PARTICIPANT != 0
#     assert circle.permissionsOf(accounts[1]) & PERM_RECEIVER == 0

#     with reverts("call revoke to remove user."):
#         circle.edit(accounts[1], PERM_EXTERNAL)


# def test_circle_revoke(circle):
#     with reverts("recipient is not invited."):
#         circle.revoke(accounts[1])

#     circle.invite(accounts[1], PERM_PARTICIPANT)
#     assert circle.totalSupply() == 1
#     circle.revoke(accounts[1])
#     assert circle.totalSupply() == 0


# def test_circle_vouch(circle):
#     circle.invite(accounts[1], PERM_GIVER)
#     circle.invite(accounts[2], PERM_GIVER)

#     circle.setMinimumVouches(2)

#     with reverts("sender didn't receive minimum vouches."):
#         circle.enter({"from": accounts[3]})

#     assert circle.vouchesOf(accounts[3]) == 0
#     circle.vouch(accounts[3], {"from": accounts[1]})
#     assert circle.vouchesOf(accounts[3]) == 1

#     with reverts("sender didn't receive minimum vouches."):
#         circle.enter({"from": accounts[3]})

#     circle.vouch(accounts[3], {"from": accounts[2]})

#     with reverts("sender already vouched for recipient."):
#         circle.vouch(accounts[3], {"from": accounts[2]})

#     assert circle.vouchesOf(accounts[3]) == 2

#     circle.enter({"from": accounts[3]})

#     with reverts("sender is already invited."):
#         circle.enter({"from": accounts[3]})

#     with reverts("recipient is already invited."):
#         circle.vouch(accounts[3], {"from": accounts[2]})


# def test_circle_join_epoch(circle, CoordinapeEpoch, TokenSet):
#     with reverts("method can only be called by an invited user."):
#         circle.joinCurrentEpoch(False, {"from": accounts[1]})

#     circle.invite(accounts[1], PERM_PARTICIPANT)
#     with reverts("no epoch currently in progress."):
#         circle.joinCurrentEpoch(False, {"from": accounts[1]})

#     circle.edit(accounts[1], PERM_PARTICIPANT | PERM_RECEIVER)

#     circle.startEpoch(100, len(chain) + EPOCH_END, 0)
#     token_set = circle.tokenSet()
#     token_set = TokenSet.at(token_set)
#     current = circle.currentEpochId()

#     circle.joinCurrentEpoch(False, {"from": accounts[1]})
#     assert token_set.isParticipant(current, accounts[1]) is True
#     assert token_set.permissionsOf(current, accounts[1]) & PERM_PARTICIPANT != 0
#     assert token_set.permissionsOf(current, accounts[1]) & PERM_RECEIVER != 0

#     circle.leaveCurrentEpoch({"from": accounts[1]})
#     assert token_set.isParticipant(current, accounts[1]) is True
#     assert token_set.permissionsOf(current, accounts[1]) & PERM_PARTICIPANT != 0
#     assert token_set.permissionsOf(current, accounts[1]) & PERM_RECEIVER == 0


# # def test_circle_transfer(circle):
# #     circle.invite(accounts[1], PERM_PARTICIPANT)

# #     invite_id = circle.inviteOf(accounts[1])

# #     with reverts("Ownable: caller is not the owner"):
# #         circle.transferFrom(accounts[1], accounts[4], invite_id, {"from": accounts[1]})

# #     circle.setMinimumVouches(2)
# #     circle.invite(accounts[2], PERM_PARTICIPANT)
# #     circle.invite(accounts[3], PERM_PARTICIPANT)
# #     circle.vouch(accounts[4], {"from": accounts[2]})
# #     circle.vouch(accounts[4], {"from": accounts[3]})

# #     perm = circle.permissionsOf(accounts[1])

# #     with reverts("Ownable: caller is not the owner"):
# #         circle.transferFrom(accounts[1], accounts[3], invite_id, {"from": accounts[1]})

# #     circle.transferFrom(accounts[1], accounts[4], invite_id, {"from": accounts[1]})

# #     assert circle.permissionsOf(accounts[1]) == PERM_EXTERNAL
# #     assert circle.permissionsOf(accounts[4]) == perm


# def test_circle_members(circle):
#     assert circle.activeMembersCount() == 0
#     assert len(circle.members()) == 0

#     circle.invite(accounts[1], PERM_PARTICIPANT)
#     circle.invite(accounts[2], PERM_PARTICIPANT)

#     assert circle.activeMembersCount() == 2
#     assert accounts[1] in circle.members()
#     assert accounts[2] in circle.members()
#     assert accounts[3] not in circle.members()

#     circle.revoke(accounts[2])

#     assert circle.activeMembersCount() == 1
#     assert accounts[1] in circle.members()
#     assert accounts[2] not in circle.members()
