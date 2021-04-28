# coordinape-protocol
🏆 Coordinape contracts
Coordinape Spec 

https://github.com/coordinape/coordinape-protocol/tree/feat/V1


Specifications and definitions for the Coordinape Beta version, first on-chain release, to be built on a EVM compatible L2 (xDai, Fantom, etc.)

Definitions
- Gift Circles are launched via an admin summon process. Userlists for circle access are defined by circle members “vouching” for a curated whitelist of wallets.  Wallets that have N vouches are able to mint a NFT Badge for access to the circle.
- Epochs are launched per Circle, defined around a start and end date.
- GIVE is off chain, allowing it to be moved around from circle member to circle member.
- GET is an ERC-1155 token, minted via a synch against the DB when an epoch ends. It is claimable by users and redeemable for pro-rata budget tokens from the epoch by which it was minted.


Gift Circles

-Each gift circle is unique, it could be for multiple protocols (yearn ecosystem) protocol wide (yearn) or for a specific team (strategists) or subteam (1337 strategists).
(Circle contracts are similar to Uniswap pools, will one day need a Circle factory.  Initially this would be centralized with Coordinape team, but eventually could become permissionless.)


-Yearn will have multiple overlapping gift circles, each with their own budget stream.
(Circles are unique, each is independent and can contain unique metadata to organize them within protocols and configure to budget streams.)


-Each circle requires an NFT badge for access 
(Circle is a contract, each circle would mint NFTs to provide access).


-Budget is decided outside of Coordinape, for now.
(Treasury integration is out of scope for now, treasury contracts would eventually would distribute against GET)


-Controls for gift circles can have centralized or decentralized at the discretion of the circle summoner.
(Circle parameters are controlled by admin or multisig for now, v2 will address decentralized parameter control)

-Gift circle creation could eventually be permissionless
(v2 feature, for now Gift Circles are created by admins).


-Badged members opt into each epoch and opt into receiving GIVE.
(Members can call “join current epoch” to opt in, set selves as receiver)


-GIVE allocations during epoch are flexible
(Gifting is handled off-chain during an epoch so that GIVEs can be freely moved around, permit allows this to be synched in with blockchain when epoch is over, another option is a merkle proof).

NFT Badges


-New badges can be created in a centralized way by the circle summoner, or decentralized.
(Circle is a contract, each circle would mint NFTs to provide access, at first would be centrally managed, vouch system later).


-For decentralized creation, N members need to vouch for a new member to create a badge with 1 prime advocate.
(Map to view vouches on-chain, if you have enough vouches, user can mint NFT badge.  This mechanic is also used to approve transfers of NFTs)


-Badges can be revoked or restricted by prime advocate or by a vote of all circle badge-holders
(similar to Vouching, if you have enough Revokes, NFT is made obsolete or inactive, permissions set to 0; reinstatement can be supported as well).


-Badges can be set with various toggles, here are examples of restriction options set within badges: 
--Can’t vouch for new members
--Can’t receive initial GIVE allocations
--Can’t receive GIVE during gift circle
--Can’t convert GIVE to GET (is this needed?)
--User gets more or less GIVE
(BitMask can contain tons of toggles for various features)


-NFT Artwork:
(can rely on 721 standard features, we would need to maintain endpoints and front end for IPFS, etc.)

-GIVE & GET
each gift circle allocates N nondivisible, limited-transferable GIVE tokens (default is 100) to each user for each epoch.
(1155 method outlined above, two phase (GIVE, GET) or three phase standard (GIVE, REGIVE, GET).)


-GIVE is gifted between members over a period of days.
(This would be off-chain, as outlined above, then synched)


-After first gift round, there is a short period for regifting.
(Various functions for regift, transfer, burn, etc, are off chain via central DB).

-Notes features kept off chain.
(Treated similarly to profile bios -- non public and easily editable).


-At the end of an epoch, received GIVE is converted to GET and the total budget for that epoch is distributed proportional to GET
(GIVE is transformed to GET tokens, after the regift phase, additional synch function could be maintained to airdrop GET or present for claiming, but this still needs some development)


Master Parameters:


-Coordinape has a master level, which contains key system wide attributes.
(Coordinape team can have control over the factory for basic administration, each circle can be self-maintained, some variables such as fee structure can be maintained there).


-Other elements would be governance decided for entire Coordinape ecosystem and application.







Open Items: 
----
Synching v.s. Merkle Tree for GET distribution

Synching

-Current iteration of Coordinape smart contracts work in a way that collects the participants’ choices backed up with a signature.

-Once the allocation/regifting phases are over (epoch end), we sync all the allocations thanks to the signatures. This is similar to queueing all transfers at once to obtain the final state of the allocation.

-After syncing each participant, we end up with the final GIVE/GET allocations allowing participants to claim their share of the epoch’s grant. 

-What is needed to support this structure:
--Database holding all participant allocations + signature per epoch
--Smart contracts using DB data to generate final epoch state

-CONS:
--Scales poorly with high participant number due to the increasing number of syncs (function call) required

Merkle Trees

-Another solution would be to work with Merkle trees.Once Allocation and true up phase are over, the GET token allocation for the epoch is final. This makes the use of a Merkle tree very sensible for the coordinape use case.

-Current flow would be similar with users which would sign signatures to distribute their allocation to other participants.

-Once Phase 1 & 2 are over. We generate the merkle tree thanks to the signatures and final GIVE shares which then allow to claim a specific share of the epoch grant.

-Circle contract could remain as it would be used to verify that a user can claim their grant via function call to the merkle epoch distributor.
Or all could be off chain. Log in with address

-Circle admin would then need to approve the tree before pushing the root on chain

-What is needed to support this structure:
--Database holding the merkle trees for each epoch

CONS:
-Data accessibility of each tree to allow participants to claim without the need to manually fetch the proof data required.
-More centralised approach. Signature is simply to prove the user’s data is real.




