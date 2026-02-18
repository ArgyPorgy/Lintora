// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract PredictionMarket is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    enum Team { NONE, KARAN, SATYAKI }
    
    struct Voter {
        bool hasVoted;
        Team votedTeam;
        uint256 voteTime;
    }
    
    IERC20 public immutable usdcToken;
    uint256 public constant VOTING_DURATION = 24 hours;
    uint256 public constant PRIZE_AMOUNT = 10 * 10**6; // 10 USDC (6 decimals)
    uint256 public constant MIN_VOTE_BUFFER = 1 hours; // Minimum time before voting ends to submit vote
    
    uint256 public votingStartTime;
    bool public votingEndedFlag;
    bool public prizeDistributedFlag;
    Team public winningTeam; // Cache winning team to avoid recalculation
    
    mapping(address => Voter) public voters;
    mapping(address => bool) public karanVoters;
    mapping(address => bool) public satyakiVoters;
    
    uint256 public karanVoteCount;
    uint256 public satyakiVoteCount;
    
    event VoteCast(address indexed voter, Team team, uint256 timestamp);
    event VotingEnded(Team winningTeam, uint256 karanVotes, uint256 satyakiVotes);
    event PrizeDistributed(Team winningTeam, uint256 totalWinners, uint256 prizePerWinner, uint256 remainder);
    event ExcessFundsWithdrawn(address indexed to, uint256 amount);
    
    constructor(address _usdcToken) Ownable(msg.sender) {
        require(_usdcToken != address(0), "Invalid USDC token address");
        usdcToken = IERC20(_usdcToken);
        votingStartTime = block.timestamp;
    }
    
    modifier votingActive() {
        require(!votingEndedFlag, "Voting has ended");
        require(block.timestamp < votingStartTime + VOTING_DURATION, "Voting period has expired");
        require(block.timestamp <= votingStartTime + VOTING_DURATION - MIN_VOTE_BUFFER, "Voting too close to deadline");
        _;
    }
    
    modifier votingEnded() {
        require(votingEndedFlag || block.timestamp >= votingStartTime + VOTING_DURATION, "Voting is still active");
        _;
    }
    
    function vote(Team _team) external votingActive nonReentrant {
        require(_team == Team.KARAN || _team == Team.SATYAKI, "Invalid team selection");
        require(!voters[msg.sender].hasVoted, "Already voted");
        
        voters[msg.sender] = Voter({
            hasVoted: true,
            votedTeam: _team,
            voteTime: block.timestamp
        });
        
        if (_team == Team.KARAN) {
            karanVoters[msg.sender] = true;
            karanVoteCount++;
        } else {
            satyakiVoters[msg.sender] = true;
            satyakiVoteCount++;
        }
        
        emit VoteCast(msg.sender, _team, block.timestamp);
    }
    
    function endVoting() external onlyOwner {
        require(!votingEndedFlag, "Voting already ended");
        require(block.timestamp >= votingStartTime + VOTING_DURATION, "Voting period not yet complete");
        
        votingEndedFlag = true;
        
        // Cache winning team to avoid recalculation
        winningTeam = karanVoteCount > satyakiVoteCount ? Team.KARAN : 
                     satyakiVoteCount > karanVoteCount ? Team.SATYAKI : Team.NONE;
        
        emit VotingEnded(winningTeam, karanVoteCount, satyakiVoteCount);
    }
    
    function distributePrize() external onlyOwner votingEnded nonReentrant {
        require(!prizeDistributedFlag, "Prize already distributed");
        require(usdcToken.balanceOf(address(this)) >= PRIZE_AMOUNT, "Insufficient USDC balance");
        
        require(winningTeam != Team.NONE, "No clear winner");
        
        uint256 winnerCount = winningTeam == Team.KARAN ? karanVoteCount : satyakiVoteCount;
        require(winnerCount > 0, "No winners");
        
        uint256 prizePerWinner = PRIZE_AMOUNT / winnerCount;
        uint256 remainder = PRIZE_AMOUNT % winnerCount;
        
        // Distribute prizes to all voters of the winning team
        if (winningTeam == Team.KARAN) {
            _distributeToKaranVoters(prizePerWinner);
        } else {
            _distributeToSatyakiVoters(prizePerWinner);
        }
        
        // Distribute remainder to the owner (or could be distributed to last winner)
        if (remainder > 0) {
            usdcToken.safeTransfer(owner(), remainder);
        }
        
        prizeDistributedFlag = true;
        
        emit PrizeDistributed(winningTeam, winnerCount, prizePerWinner, remainder);
    }
    
    function _distributeToKaranVoters(uint256 /* prizePerWinner */) private {
        require(karanVoteCount > 0, "No Karan voters");
        // Transfer total prize amount to owner for manual distribution
        // In production, implement a proper distribution mechanism with voter tracking
        usdcToken.safeTransfer(owner(), PRIZE_AMOUNT);
    }
    
    function _distributeToSatyakiVoters(uint256 /* prizePerWinner */) private {
        require(satyakiVoteCount > 0, "No Satyaki voters");
        // Transfer total prize amount to owner for manual distribution
        // In production, implement a proper distribution mechanism with voter tracking
        usdcToken.safeTransfer(owner(), PRIZE_AMOUNT);
    }
    
    // Function to manually distribute prize to a specific voter (owner only)
    // This allows the owner to distribute prizes manually after calling distributePrize
    function distributeToVoter(address voter, uint256 amount) external onlyOwner {
        require(votingEndedFlag, "Voting not ended");
        require(prizeDistributedFlag, "Prize not distributed yet");
        require(usdcToken.balanceOf(address(this)) >= amount, "Insufficient balance");
        
        usdcToken.safeTransfer(voter, amount);
    }
    
    function fundContract() external onlyOwner {
        usdcToken.safeTransferFrom(msg.sender, address(this), PRIZE_AMOUNT);
    }
    
    // Function to withdraw excess funds (if contract receives more than PRIZE_AMOUNT)
    function withdrawExcessFunds() external onlyOwner {
        uint256 currentBalance = usdcToken.balanceOf(address(this));
        require(currentBalance > PRIZE_AMOUNT, "No excess funds to withdraw");
        
        uint256 excessAmount = currentBalance - PRIZE_AMOUNT;
        usdcToken.safeTransfer(owner(), excessAmount);
        
        emit ExcessFundsWithdrawn(owner(), excessAmount);
    }
    
    function getVotingStatus() external view returns (
        bool isActive,
        uint256 timeRemaining,
        uint256 karanVotes,
        uint256 satyakiVotes,
        bool hasEnded,
        bool prizeDistributed
    ) {
        isActive = !votingEndedFlag && block.timestamp < votingStartTime + VOTING_DURATION;
        timeRemaining = block.timestamp < votingStartTime + VOTING_DURATION ? 
                       (votingStartTime + VOTING_DURATION) - block.timestamp : 0;
        karanVotes = karanVoteCount;
        satyakiVotes = satyakiVoteCount;
        hasEnded = votingEndedFlag;
        prizeDistributed = prizeDistributedFlag;
    }
    
    function getUserVote(address user) external view returns (bool hasVoted, Team votedTeam, uint256 voteTime) {
        Voter memory voter = voters[user];
        return (voter.hasVoted, voter.votedTeam, voter.voteTime);
    }
    
    function getWinningTeam() external view returns (Team) {
        if (karanVoteCount > satyakiVoteCount) return Team.KARAN;
        if (satyakiVoteCount > karanVoteCount) return Team.SATYAKI;
        return Team.NONE;
    }
    
    // Function to restart voting (reset everything)
    function restartVoting() external onlyOwner {
        votingStartTime = block.timestamp;
        votingEndedFlag = false;
        prizeDistributedFlag = false;
        winningTeam = Team.NONE;
        
        // Reset vote counts
        karanVoteCount = 0;
        satyakiVoteCount = 0;
        
        // Note: We cannot efficiently clear mappings in Solidity
        // In production, consider using a different approach or accept that old voters
        // cannot vote again (which might be desired behavior)
    }
    
    // Function to get vote counts (only for owner/admin)
    function getVoteCounts() external view onlyOwner returns (uint256 karanVotes, uint256 satyakiVotes) {
        return (karanVoteCount, satyakiVoteCount);
    }
}
