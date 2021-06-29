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
