pragma solidity ^0.8.2;

abstract contract ApeAllowanceModule {

	struct Allowance {
		uint256 maxAmount;
		uint256 maxInterval;
	}

	struct CurrentAllowance {
		uint256 debt;
		uint256 intervalStart;
	}

	// vault => circle => token => allowance
	mapping(address => mapping(address => mapping(address => Allowance))) public allowances;
	mapping(address => mapping(address => mapping(address => CurrentAllowance))) public currentAllowances;

	event AllowanceUpdated(address vault, address circle, address token, uint256 amount, uint256 interval);

	function setAllowance(
		address _circle,
		address _token,
		uint256 _amount,
		uint256 _interval
		) external {
		allowances[msg.sender][_circle][_token] = Allowance({
			maxAmount: _amount,
			maxInterval: _interval
		});

		currentAllowances[msg.sender][_circle][_token] = CurrentAllowance({
			debt: 0,
			intervalStart: block.timestamp
		});
		emit AllowanceUpdated(msg.sender, _circle, _token, _amount, _interval);
	}

	function _isTapAllowed(
		address _vault,
		address _circle,
		address _token,
		uint256 _amount
		) internal {
		Allowance memory allowance = allowances[_vault][_circle][_token];
		CurrentAllowance storage currentAllowance = currentAllowances[_vault][_circle][_token];

		_updateInterval(currentAllowance, allowance);
		require(currentAllowance.debt + _amount <= allowance.maxAmount, "Circle does not have sufficient allownace");
		currentAllowance.debt += _amount;
	}

	function _updateInterval(CurrentAllowance storage _currentAllowance, Allowance memory _allowance) internal {
		uint256 elapsedTime = block.timestamp - _currentAllowance.intervalStart;
		if (elapsedTime >= _allowance.maxInterval) {
			_currentAllowance.debt = 0;
			_currentAllowance.intervalStart += _currentAllowance.intervalStart * (elapsedTime / _allowance.maxInterval);
		}
	}
}