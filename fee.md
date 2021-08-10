**Explanations of fee revenue strategy**

Tap fee function:
	for x being the yild/full_tap ratio between [0;5]
	Let we describe f(x), Deducted tap fee as: 
    
	f(x) = 1.25 * x / 5

1. Full yield

	Easiest one to understand/implement.
    
	If circle tap only with yield (Example: Vault deposits 1M usdc at 12% APY, if they tap 10k/month, this is considered full yield)
    
	They pay 0 fees.

2. Mixture of yield + underlying value (Some yield, some tap)

	If profits from yield don't cover an epoch, the vault's underlying value will decrease as it is tapped into.
    
	This means that for an epoch, we can calculate the ratio 1 - yield/full_tap. 
    
	Example:
    
      Vault deposits 500k USDC at 12% APY, if they tap 10k for an epoch, 5K will be from yield, 5k will be from tap
    
      This puts the ratio at 5k / (10k) = 50%
    
      Assuming a linear gradient from 100% to 0% yield, we can calculate the fee taken from the yield
    
      This fee will range between [0-100]%, with 100% when ratio is 0%
    
      For this epoch, the vault will be deducted a total of
        
			total_deducted = tap_value + yield_value * yield_fee
						   = 10k       + 5k          * 50%
						   = 12.5k

    With 2.5k going to coordinape.
    
    Note:
    
    Previous example is in a system where after each epoch, the base value will decrease, making the yield also decrease over time

    This means that the fee from yield will slowly rise and tend to 100%

3. Mostly Tap (top up scheme)

	From case n.2, we see that fees from yield increase the lower the yield but this also means the lower the yield, even if a higher % fee is taken, the revenue in will be very small.
    
	To remedy this, adding a fee that is taken from the underlying value could be implemented.
    
	This fee would range from 0% to 1.25% of the tap value.
    
	Numbers to be discussed but this fee could start increasing the moment the yield/full_tap ratio goes below 5% and increase to 1.25% the close the ratio is to 0%

	Example:
    
    Vault deposits 20k at 12% apy, if they tap 10k after one month of yield
    
    the ratio would be 2% as they'd farm around 200 usd
    
    This makes the yield fee be 98%
    
    Tap fee would be 0.5%
    
		For this epoch, the vault will be deducted a total of
			total_deducted = tap_value + yield_value * yield_fee + tap_value * tap_fee
						   = 10k       + 200          * 98%        + 9.8k      * 0.5%
						   = 10k + 196 + 49
						   = 10245 
		With 245 going to coordinape

4. Shitcoin

	Tokens that can't be farmed by a yearn vault will be deducted a 2.5% fee
    
	If a vault decides to tap 10k $RANDOM to their circle, the vault will be deducted:
    
		total_deducted = 10k + 10k * 2.5%
					   = 10250



last meeting with trach


Yearn
Sushi
Cream
Curve
Aave
DAOs

150 circles
20 users on average
20k/month/circle

3M distribution / month


60k/month from fees


==
25 yield based circles

50M TVL @ 5% apy

0.5% of 50M 

250k/year

40M issued
1% => 400k
2% => 800k
3% => 1.2M
4% => 1.6M


proposal:
- 1% from yield
- [1;4]% from capital (tap)

- affiliate fee (passive)


13/07/21

Based on yearn calc
If we manage 50M TVL all year around with a yield around 5% (unlikely atm as apy are quite low around 5%)
=> revenue generated would be around 210k USD / year

=> if we take another 1% from yield (which would be 2.5M distributed per year)
	25k/year

assuming 3M yearly distro with smaller circle:
We could try to hit the partner fee but will most likely not be very big
taking a 1-4% fee (lets assume 2.5% for now) would generate 75k/month = > 900k/year

Total would be near ~1.13M/year revenue


TODO on contracts:
vault :
=> partnership program integration
=> fee model finalised and implemented

Circle :
=> pseudo admin roles (role system)
=> super admin (owner)
=> tweak the vouching system (make it more flexible[changing vouching param...])/kicking too
	=> optionally add a multisig-like voting system to execute proposals
	=> allow super admins/admins to change anything (assume the responsability that admins could act maliciously)



New proposal:
static X % fee in all taps

+ 

dynamic yield fee, the more you yield, the less we take



until we find a more dynamic and optimised version we can do it as such
if yield size is:
- 0-10%  => 80% fee on yield
- 10-20% => 32% fee on yield
- 30-40%  => 16% fee on yield
- 40-50% => 8% fee on yield
- 50-60%  => 4% fee on yield
- 60-70% => 2.5% fee on yield
- 70-80%  => 1% fee on yield
- 80+% => 0% fee 

the curve drop aggressively making it a lot more advantageous to go full yield