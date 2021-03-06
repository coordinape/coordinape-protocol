https://github.com/coordinape/coordinape-protocol/commits/feat/fix_from_audit

1. Incorrect delay time in schedule (TimeLock.sol)
	Change made, this is correct, better stay consistent

2. Potential unsafe check  (TimeLock.sol)
	changed check to make it similar to OZ's impl.

3. Suspicious checking logic (ApeRouter.sol)
	Does not look suspicious, contract is calling the yearn registry to fetch the lastest vault associated with _token,
	we make sure sure the latest is indeed _yvToken to make sure yearn's backend can correctly fetch TVL raised by coordinape

	no changes to be made beside discussing with yearn if this technique is fine

4. Potential inconsistency (ApeRouter.sol)
	It is expected that apeVaults directly call this function, so the msg.sender check is correct

	no changes to be made

5. Potential uninitialized variable (ApeVault.sol)
	That's intended design, probably need to discuss this once more to get a final verdict

5. 1. _token and _simpleToken (ApeVault.sol)
	Added a require to make sure both variables are not address(0) at the same time

6. Potential affect the calculation of the token balance of the Vault (BaseWrapperImplementation.sol)
	Changed based on Panda's recommendation
	Ultimately, this doesnt affect us because sender will always be != to address(this)

7. Suspicious public function
	Added onlyOwner modifier to the function execution

8. Potential inconsistency
	underlyingValue is used to store the amount of funds that has been sent into the vault. Any yield build on top should not be considered to allow to calculate profit.

	example: I deposit 1M usdc that is yielding 10% apy. Assuming no fund has happened, the yv shares would be worth 1.1M, therefore making profit be equal to 100k. 

	undervalue should only be changed if we withdraw funds from the vault or contribute to a circle and tap more than what profit is equal to at the time of tapping.

9. Attacker can claim unclaimed tokens in ApeDistributor 
	We think this is handled already.
	When a circle admin uploads an epoch root, they can indeed send a merkle tree that could try to claim tokens of other circles but this wouldn't be possible thanks to the circleAlloc mapping that is updated line 69. Furthermore, we check that the ApeDistributor contract has recieved the correct amount of tokens it is expecting (lines 70-73) so if a user tries to fund a circle X amount of tokens but does not have them, the function will revert.
	circleAlloc mapping allows to track how much tokens each circle has funded to users and ensures they can't claim more than they've added

	Example: 
	Lets assume we have 2 circles. Circle A which is funded monthly with 1M USDC per epoch and circle B which has 0 funding and is trying to steal circle A's funds.
	Circle A is legit and when it calls the uploadEpochRoot function, they have the funds to supply its users. The circleAlloc mapping increases accordingly to allow the circle to withdraw at most the amount it has put initially. After 5 epochs, Circle A users will be able to withdraw at most 5M from the distributor contract. Circle B sees that circle A is well funded and is trying to steal the funds. They will push a merkle tree where one user could claim the 5M usdc (assuming circle A has never withdrawn) but will pass either 0 or very little USDC (100 for our example). This means the circleAlloc of circle B will be very small (at most 100). When the malicious user from circle B will try to claim the 5M usdc, line 124 will revert because solidity 0.8.X reverts on substraction overflows.

Recommendations:

1. Unlimited approval (ApeRouter.sol)
	Changed unlimited approval to _amount

2. Mixed use of transfer() and safeTransfer() (ApeVault.sol)
	Changed to remain consistent

3. New Implementation of ApeVault may change the storage layout of Proxy
	It is true. When we will be pushing out new implementations, it will be mandatory to keep storage layout the way it is and add new storage at the end of the current layout

4. Guarantee that state variables in ApeRegistry must be properly initialized (ApeRegistry.sol)
	treasury address added in constructor to prevent this mistake

5. Remove unused variables (ApeVault.sol)
	Removed

6. Potential inconsistency due to the hardcoded yearnRegistry (ApeRouter.sol and ApeVaultFactoryBeacon.sol) *PENDING*
	Will ask yearn team if registry would ever change, if not, have all hardcoded, if yes, add mutable option
	- Should make it upgradeable

7. Add more check (ApeDistributor.sol)
	Worst outcome is that function execution would revert if token is not a yvToken. No change needed

8. Potential incorrect comment (FeeRegistry.sol)
	Current proposal of our fee model
	TOTAL_SHARES = 10000 in our ape vaults
	Assuming a high yield ratio (100% ratio is when circle funding comes only from yield), a vault would have less fees taken out
	





Gas costs for disperse method: 
- static overhead (base tx cost + mutations surrounding tap in vaults) = C (300k)
- token transfer cost = T (35k gas)
- User amount = N

Total_cost_D = C + T * N (300k + 35k * N)
Total cost in eth = Total_cost * gas_price (in wei)

Gas costs for merkle method:
- static overhead (base tx cost + mutations surrounding tap in vaults) = C (300k)
- Merkle state updates (3 SSTORE ops) = M (15k - 60k)
- User amount = N

Total_cost_M = C + M (360k)

in Comparison:
Total_cost_D < Total_cost_M
Total_cost_D - Total_cost_M < 0
C + T * N - (C + M) < 0
T * N < M

Setip: 5/10/30/100 users @ 10

Total_cost_D = 300k + 35k * 5 = 475,000
Total_cost_D = 300k + 35k * 10 = 650,000
Total_cost_D = 300k + 35k * 30 = 1,350,000
Total_cost_D = 300k + 35k * 100 = 3,800,000

Total_cost_M = 360k + 150k * 5 = 1,110,000
Total_cost_M = 360k + 150k * 10 = 1,860,000
Total_cost_M = 360k + 150k * 30 = 4,860,000
Total_cost_M = 360k + 150k * 100 = 15,360,000
caveat : users claim so gas to claim is not on us, each user

