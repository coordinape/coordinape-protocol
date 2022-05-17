
**N1 - Risk of Replay Attack - Suggestion**
Understood, need to discuss with team. Issue is fork happens. funds could be transferred if parmit stored or of huge deadline

What has been done: DOMAIN_SEPARATOR has become a public view functions that returns the separator on execution call instead of being instantiated on contract creation

**N2 - Missing event records - Others - Suggestion**
Adding events should resolve this. Not major downsides in adding events

What has been done: Added events to function mentionned in audit

**N3 - Coding optimization - Authority Control Vulnerability -Suggestion**
Ommission on our side, this function should indeed be view

What has been done: view attribute added to function

**N4 - Business logic is not clear Others - High**
Ignore any circle_obsolete comments

_migrate(address(this)) in apeMigrate needs clarification, added a comment explaining what it does

internal _migrate is not wrong. In the yearn logic there is always 2 parties for an deposit or withdrawal (the person that has the funds and the receiver of funds). In our logic those 2 parties are the same.

No changes needed

**N5 - Coding standards issues - Others - Suggestion**
Need to amend to suit the CEI pattern

What has been done: mutate code to support CEI pattern


**N6 - The external call does not judge the return value - Unsafe External Call -  Audit - Medium**
Should change to change all transfer occurences into safeTransfer occurances

What has been done: change transfer(...) -> safeTransfer(...) and transferFrom(...) -> safeTransferFrom(...) using the safeERC20 library

**N7 - Excessive authority issue - Authority Control - Vulnerability - High**
Designed system, it's their money, they should not need timelock to move their funds.
Acknowledged, nothing to change


**N8 - Lack of permission checks - Authority Control Vulnerability - High**
First assessment: On creation of a new ape vault, the _token param will be sent to yearnReg.latestVault(_token) which will revert if the token is not endorsed. Yes yearn can get hacked but hacking a gnosis safe of 10 users is quite a feat. So no checks required on _token

For _simpleToken we don't see how it could create bad execution that could impact other users.
All critical functions are properly secured by accessors and we don't have any internal calls that can send a different token that was initially given

Any contract interaction with simpleToken are executed at the end of CEI patterns and reentrancy cannot be achieved

Acknowledged, nothing to change
