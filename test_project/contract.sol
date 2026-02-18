pragma solidity ^0.8.0;

contract Vault {
    address public owner;
    
    function withdrawAll() public {
        require(msg.sender == owner);
        payable(owner).transfer(address(this).balance);
    }
    
    function mint(address to, uint256 amount) external {
        // No access control!
    }
    
    function destroy() public {
        selfdestruct(payable(owner));
    }
}
