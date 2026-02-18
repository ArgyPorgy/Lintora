pragma solidity ^0.8.0;
contract Token {
    address owner;
    function withdraw() public { selfdestruct(payable(owner)); }
    function mint(address to, uint256 amt) external { /* no access control */ }
}
