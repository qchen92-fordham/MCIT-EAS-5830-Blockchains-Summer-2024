// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
	mapping( address => address) public underlying_tokens;
	mapping( address => address) public wrapped_tokens;
	address[] public tokens;

	event Creation( address indexed underlying_token, address indexed wrapped_token );
	event Wrap( address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount );
	event Unwrap( address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

	function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        require(wrapped_tokens[_underlying_token] != address(0), "Token not registered1");
        require(_recipient != address(0), "Recipient cannot be zero address");
        require(_amount > 0, "Amt needs to be greater than zero");

        // Mint wrapped tokens to the recipient
        BridgeToken wrappedToken = BridgeToken(wrapped_tokens[_underlying_token]);
	    wrappedToken.mint(_recipient, _amount);

        emit Wrap(_underlying_token,address(wrappedToken), _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        address underlying_token = underlying_tokens[_wrapped_token];
        require(underlying_tokens[_wrapped_token] != address(0), "Token not registered2");
        require(_amount > 0, "Unwrap token amt needs to be greater than 0 ");
        require(_recipient != address(0), "Recipient cannot be zero address");

        //buring wrapped token
        BridgeToken wrappedToken = BridgeToken(_wrapped_token);
	    wrappedToken.burnFrom(msg.sender, _amount);
		
        emit Unwrap(underlying_token, _wrapped_token, msg.sender, _recipient, _amount);
    }

    function createToken(address _underlying_token, string memory name, string memory symbol) public onlyRole(CREATOR_ROLE) returns (address) {
        require(wrapped_tokens[_underlying_token] == address(0), "Wrapped asset already registered");

        BridgeToken WrappedToken = new BridgeToken(_underlying_token, name, symbol, address(this));
        address WrappedTokenAddress = address(WrappedToken);

        wrapped_tokens[_underlying_token] = WrappedTokenAddress;
        underlying_tokens[WrappedTokenAddress] = _underlying_token;
        tokens.push(_underlying_token);
        emit Creation(_underlying_token, WrappedTokenAddress);

        return WrappedTokenAddress;
    }


	}
