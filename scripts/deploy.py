import sys
import json

from brownie import accounts, chain, CoordinapeCircle, CoordinapeEpoch


PERM_EXTERNAL = 0
PERM_PARTICIPANT = 1
PERM_RECEIVER = 2
PERM_GIVER = 4

deployment = "0xe6B9e9133428855709978BB42a5D195632397A1e"


def main():
    account = accounts.load("test")
    CoordinapeCircle.deploy(
        "Coordinape Test Circle",
        "INVITE",
        "https://example.com/",
        {"from": account},
        publish_source=True,
    )


def invite():
    account = accounts.load("test")
    circle = CoordinapeCircle.at(deployment)
    circle.invite(account, {"from": account})


def grant_permissions():
    account = accounts.load("test")
    circle = CoordinapeCircle.at(deployment)
    members = circle.members()
    for member in members:
        circle.edit(
            member, PERM_PARTICIPANT | PERM_RECEIVER | PERM_GIVER, {"from": account},
        )


def start_epoch():
    account = accounts.load("test")
    end = len(chain) + 604800
    circle = CoordinapeCircle.at(deployment)
    circle.startEpoch(100, end, {"from": account})


def abi():
    abi = CoordinapeEpoch.abi
    print(json.dumps(abi), file=sys.stderr)


def flattened_source():
    source = CoordinapeEpoch.get_verification_info()["flattened_source"]
    print(source, file=sys.stderr)
