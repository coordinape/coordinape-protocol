pragma solidity ^0.8.2;

abstract contract ApeAllowanceModule {

	struct Allowance {
		uint256 maxAmount;
		uint256 maxInterval;
		//uint256 tapType; // 0 pure profit | 1 any | 2 shitcoins 
	}

	struct CurrentAllowance {
		uint256 debt;
		uint256 intervalStart;
		uint256 epochs;
	}

	// vault => circle => token => allowance
	mapping(address => mapping(bytes32 => mapping(address => Allowance))) public allowances;
	mapping(address => mapping(bytes32 => mapping(address => CurrentAllowance))) public currentAllowances;

	event AllowanceUpdated(address vault, bytes32 circle, address token, uint256 amount, uint256 interval);

	// TODO add tap type checks
	function setAllowance(
		bytes32 _circle,
		address _token,
		uint256 _amount,
		uint256 _interval,
		uint256 _epochs
		) external {
		allowances[msg.sender][_circle][_token] = Allowance({
			maxAmount: _amount,
			maxInterval: _interval
		});

		currentAllowances[msg.sender][_circle][_token] = CurrentAllowance({
			debt: 0,
			intervalStart: block.timestamp,
			epochs: _epochs
		});
		emit AllowanceUpdated(msg.sender, _circle, _token, _amount, _interval);
	}

	function _isTapAllowed(
		address _vault,
		bytes32 _circle,
		address _token,
		uint256 _amount
		) internal {
		Allowance memory allowance = allowances[_vault][_circle][_token];
		CurrentAllowance storage currentAllowance = currentAllowances[_vault][_circle][_token];

		_updateInterval(currentAllowance, allowance);
		require(currentAllowance.debt + _amount <= allowance.maxAmount, "Circle does not have sufficient allowance");
		currentAllowance.debt += _amount;
	}

	function _updateInterval(CurrentAllowance storage _currentAllowance, Allowance memory _allowance) internal {
		uint256 elapsedTime = block.timestamp - _currentAllowance.intervalStart;
		if (elapsedTime > _allowance.maxInterval) {
			require(_currentAllowance.epochs > 0, "Circle cannot tap anymore");
			_currentAllowance.debt = 0;
			_currentAllowance.intervalStart += _allowance.maxInterval * (elapsedTime / _allowance.maxInterval);
			_currentAllowance.epochs--;
		}
	}
}