// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "../contracts/Destination.sol";
import "../contracts/BridgeToken.sol";

contract DestinationTest is Test {
    Destination destination;
    BridgeToken bridgeToken;
    address admin = address(1);
    address warden = address(2);
    address user = address(3);
    address s_recipient = address(4);
    address underlyingToken = address(5);
    uint256 amount = 1000;

    function setUp() public {
        destination = new Destination(admin);
        bridgeToken = new BridgeToken(underlyingToken, "Wrapped Token", "WTKN", address(destination));
        destination.grantRole(destination.CREATOR_ROLE(), admin);
        destination.grantRole(destination.WARDEN_ROLE(), warden);

        // Register the wrapped token
        vm.prank(admin);
        destination.createToken(underlyingToken, "Wrapped Token", "WTKN");
    }

    function testWrap() public {
        // Test wrap function
        vm.prank(warden);
        destination.wrap(underlyingToken, user, amount);
    }

    function testUnwrap() public {
        // Test unwrap function
        vm.prank(warden);
        destination.wrap(underlyingToken, user, amount);

        vm.prank(user);
        destination.unwrap(address(bridgeToken), amount); // Updated to match the new signature
    }
}
