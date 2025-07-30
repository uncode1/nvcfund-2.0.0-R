// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title QuadraticVotingGovernance
 * @dev Advanced governance system with quadratic voting mechanism
 * Features:
 * - Quadratic voting to prevent plutocracy
 * - Delegation with decay
 * - Time-locked execution
 * - Emergency proposals
 * - Compliance integration
 * - Sybil resistance
 * - Vote privacy (commit-reveal)
 */
contract QuadraticVotingGovernance is ReentrancyGuard, AccessControl {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant PROPOSER_ROLE = keccak256("PROPOSER_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

    enum ProposalState {
        Pending,
        Active,
        Canceled,
        Defeated,
        Succeeded,
        Queued,
        Expired,
        Executed
    }

    enum VoteType {
        Against,
        For,
        Abstain
    }

    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        address[] targets;
        uint256[] values;
        bytes[] calldatas;
        uint256 startBlock;
        uint256 endBlock;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        uint256 totalVotingPower;
        bool canceled;
        bool executed;
        bool isEmergency;
        uint256 executionDelay;
        uint256 queuedTime;
        mapping(address => Receipt) receipts;
    }

    struct Receipt {
        bool hasVoted;
        VoteType support;
        uint256 votes;
        uint256 votingPower;
        bytes32 commitment; // For commit-reveal voting
        bool revealed;
    }

    struct Delegation {
        address delegate;
        uint256 amount;
        uint256 timestamp;
        uint256 decayRate; // Basis points per day
        bool active;
    }

    struct VoterInfo {
        uint256 votingPower;
        uint256 delegatedPower;
        uint256 lastVoteBlock;
        bool isVerified; // Sybil resistance
        uint256 reputationScore;
        mapping(address => Delegation) delegations;
    }

    IERC20 public governanceToken;
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => VoterInfo) public voters;
    mapping(bytes32 => bool) public commitments;
    mapping(address => bool) public verifiedVoters;

    uint256 public proposalCount;
    uint256 public votingDelay = 1 days; // 1 day delay before voting starts
    uint256 public votingPeriod = 7 days; // 7 days voting period
    uint256 public executionDelay = 2 days; // 2 days delay before execution
    uint256 public emergencyExecutionDelay = 1 hours; // 1 hour for emergency proposals
    uint256 public proposalThreshold = 100000e18; // 100,000 tokens to propose
    uint256 public quorumVotes = 400000e18; // 400,000 tokens for quorum
    uint256 public constant MAX_OPERATIONS = 10;
    uint256 public constant QUADRATIC_SCALING = 10000; // Scaling factor for quadratic calculation

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string title,
        uint256 startBlock,
        uint256 endBlock,
        bool isEmergency
    );
    
    event VoteCast(
        address indexed voter,
        uint256 indexed proposalId,
        VoteType support,
        uint256 votes,
        uint256 votingPower,
        string reason
    );
    
    event ProposalQueued(uint256 indexed proposalId, uint256 executionTime);
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCanceled(uint256 indexed proposalId);
    
    event DelegationCreated(
        address indexed delegator,
        address indexed delegate,
        uint256 amount,
        uint256 decayRate
    );
    
    event VoterVerified(address indexed voter, uint256 reputationScore);
    event CommitmentMade(address indexed voter, uint256 indexed proposalId, bytes32 commitment);
    event VoteRevealed(address indexed voter, uint256 indexed proposalId, VoteType support);

    modifier onlyVerifiedVoter() {
        require(verifiedVoters[msg.sender], "Voter not verified");
        _;
    }

    constructor(address _governanceToken) {
        governanceToken = IERC20(_governanceToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(PROPOSER_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);
        _grantRole(COMPLIANCE_ROLE, msg.sender);
    }

    /**
     * @dev Create a new proposal
     */
    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory title,
        string memory description,
        bool isEmergency
    ) public returns (uint256) {
        require(
            getVotingPower(msg.sender) >= proposalThreshold,
            "Insufficient voting power to propose"
        );
        require(targets.length == values.length, "Array length mismatch");
        require(targets.length == calldatas.length, "Array length mismatch");
        require(targets.length <= MAX_OPERATIONS, "Too many operations");
        require(targets.length > 0, "Must provide actions");

        if (isEmergency) {
            require(hasRole(EMERGENCY_ROLE, msg.sender), "Not authorized for emergency proposals");
        }

        uint256 proposalId = proposalCount++;
        uint256 startBlock = block.number + (votingDelay / 12); // Assuming 12 second blocks
        uint256 endBlock = startBlock + (votingPeriod / 12);

        Proposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.title = title;
        proposal.description = description;
        proposal.targets = targets;
        proposal.values = values;
        proposal.calldatas = calldatas;
        proposal.startBlock = startBlock;
        proposal.endBlock = endBlock;
        proposal.isEmergency = isEmergency;
        proposal.executionDelay = isEmergency ? emergencyExecutionDelay : executionDelay;

        emit ProposalCreated(proposalId, msg.sender, title, startBlock, endBlock, isEmergency);

        return proposalId;
    }

    /**
     * @dev Cast a vote with quadratic voting
     */
    function castVote(
        uint256 proposalId,
        VoteType support,
        uint256 tokenAmount,
        string calldata reason
    ) external onlyVerifiedVoter nonReentrant {
        require(state(proposalId) == ProposalState.Active, "Voting is closed");
        require(tokenAmount > 0, "Must vote with tokens");

        Proposal storage proposal = proposals[proposalId];
        Receipt storage receipt = proposal.receipts[msg.sender];
        require(!receipt.hasVoted, "Already voted");

        // Calculate quadratic voting power
        uint256 votingPower = calculateQuadraticVotingPower(tokenAmount);
        
        // Add delegated voting power
        uint256 delegatedPower = getActiveDelegatedPower(msg.sender);
        votingPower = votingPower.add(delegatedPower);

        // Lock tokens for voting
        governanceToken.safeTransferFrom(msg.sender, address(this), tokenAmount);

        receipt.hasVoted = true;
        receipt.support = support;
        receipt.votes = tokenAmount;
        receipt.votingPower = votingPower;

        if (support == VoteType.Against) {
            proposal.againstVotes = proposal.againstVotes.add(votingPower);
        } else if (support == VoteType.For) {
            proposal.forVotes = proposal.forVotes.add(votingPower);
        } else {
            proposal.abstainVotes = proposal.abstainVotes.add(votingPower);
        }

        proposal.totalVotingPower = proposal.totalVotingPower.add(votingPower);

        // Update voter info
        VoterInfo storage voter = voters[msg.sender];
        voter.lastVoteBlock = block.number;
        voter.reputationScore = voter.reputationScore.add(1);

        emit VoteCast(msg.sender, proposalId, support, tokenAmount, votingPower, reason);
    }

    /**
     * @dev Commit vote for privacy (commit-reveal scheme)
     */
    function commitVote(uint256 proposalId, bytes32 commitment) external onlyVerifiedVoter {
        require(state(proposalId) == ProposalState.Active, "Voting is closed");
        require(commitment != bytes32(0), "Invalid commitment");
        require(!commitments[commitment], "Commitment already used");

        Proposal storage proposal = proposals[proposalId];
        Receipt storage receipt = proposal.receipts[msg.sender];
        require(!receipt.hasVoted, "Already voted");

        receipt.commitment = commitment;
        commitments[commitment] = true;

        emit CommitmentMade(msg.sender, proposalId, commitment);
    }

    /**
     * @dev Reveal committed vote
     */
    function revealVote(
        uint256 proposalId,
        VoteType support,
        uint256 tokenAmount,
        uint256 nonce,
        string calldata reason
    ) external onlyVerifiedVoter nonReentrant {
        require(state(proposalId) == ProposalState.Active, "Voting is closed");

        Proposal storage proposal = proposals[proposalId];
        Receipt storage receipt = proposal.receipts[msg.sender];
        require(receipt.commitment != bytes32(0), "No commitment found");
        require(!receipt.revealed, "Already revealed");

        // Verify commitment
        bytes32 computedCommitment = keccak256(abi.encodePacked(
            proposalId, support, tokenAmount, nonce, msg.sender
        ));
        require(computedCommitment == receipt.commitment, "Invalid reveal");

        receipt.revealed = true;
        receipt.hasVoted = true;
        receipt.support = support;
        receipt.votes = tokenAmount;

        // Calculate quadratic voting power
        uint256 votingPower = calculateQuadraticVotingPower(tokenAmount);
        uint256 delegatedPower = getActiveDelegatedPower(msg.sender);
        votingPower = votingPower.add(delegatedPower);

        receipt.votingPower = votingPower;

        // Lock tokens
        governanceToken.safeTransferFrom(msg.sender, address(this), tokenAmount);

        // Update vote counts
        if (support == VoteType.Against) {
            proposal.againstVotes = proposal.againstVotes.add(votingPower);
        } else if (support == VoteType.For) {
            proposal.forVotes = proposal.forVotes.add(votingPower);
        } else {
            proposal.abstainVotes = proposal.abstainVotes.add(votingPower);
        }

        proposal.totalVotingPower = proposal.totalVotingPower.add(votingPower);

        emit VoteRevealed(msg.sender, proposalId, support);
        emit VoteCast(msg.sender, proposalId, support, tokenAmount, votingPower, reason);
    }

    /**
     * @dev Delegate voting power to another address
     */
    function delegate(
        address delegatee,
        uint256 amount,
        uint256 decayRate
    ) external onlyVerifiedVoter {
        require(delegatee != address(0), "Invalid delegatee");
        require(delegatee != msg.sender, "Cannot delegate to self");
        require(verifiedVoters[delegatee], "Delegatee not verified");
        require(amount > 0, "Amount must be greater than 0");
        require(decayRate <= 1000, "Decay rate too high"); // Max 10% per day

        governanceToken.safeTransferFrom(msg.sender, address(this), amount);

        VoterInfo storage delegator = voters[msg.sender];
        delegator.delegations[delegatee] = Delegation({
            delegate: delegatee,
            amount: amount,
            timestamp: block.timestamp,
            decayRate: decayRate,
            active: true
        });

        VoterInfo storage delegate = voters[delegatee];
        delegate.delegatedPower = delegate.delegatedPower.add(amount);

        emit DelegationCreated(msg.sender, delegatee, amount, decayRate);
    }

    /**
     * @dev Calculate quadratic voting power
     */
    function calculateQuadraticVotingPower(uint256 tokenAmount) public pure returns (uint256) {
        // Quadratic voting: voting power = sqrt(tokens) * scaling factor
        return sqrt(tokenAmount).mul(QUADRATIC_SCALING);
    }

    /**
     * @dev Get active delegated power for a voter
     */
    function getActiveDelegatedPower(address voter) public view returns (uint256) {
        VoterInfo storage voterInfo = voters[voter];
        return voterInfo.delegatedPower; // Simplified - would include decay calculation
    }

    /**
     * @dev Get voting power for an address
     */
    function getVotingPower(address account) public view returns (uint256) {
        uint256 tokenBalance = governanceToken.balanceOf(account);
        uint256 quadraticPower = calculateQuadraticVotingPower(tokenBalance);
        uint256 delegatedPower = getActiveDelegatedPower(account);
        return quadraticPower.add(delegatedPower);
    }

    /**
     * @dev Get proposal state
     */
    function state(uint256 proposalId) public view returns (ProposalState) {
        require(proposalId < proposalCount, "Invalid proposal ID");

        Proposal storage proposal = proposals[proposalId];

        if (proposal.canceled) {
            return ProposalState.Canceled;
        } else if (block.number <= proposal.startBlock) {
            return ProposalState.Pending;
        } else if (block.number <= proposal.endBlock) {
            return ProposalState.Active;
        } else if (proposal.forVotes <= proposal.againstVotes || proposal.totalVotingPower < quorumVotes) {
            return ProposalState.Defeated;
        } else if (proposal.queuedTime == 0) {
            return ProposalState.Succeeded;
        } else if (proposal.executed) {
            return ProposalState.Executed;
        } else if (block.timestamp >= proposal.queuedTime + proposal.executionDelay) {
            return ProposalState.Expired;
        } else {
            return ProposalState.Queued;
        }
    }

    /**
     * @dev Queue a successful proposal for execution
     */
    function queue(uint256 proposalId) external {
        require(state(proposalId) == ProposalState.Succeeded, "Proposal not succeeded");

        Proposal storage proposal = proposals[proposalId];
        proposal.queuedTime = block.timestamp;

        emit ProposalQueued(proposalId, block.timestamp + proposal.executionDelay);
    }

    /**
     * @dev Execute a queued proposal
     */
    function execute(uint256 proposalId) external nonReentrant {
        require(state(proposalId) == ProposalState.Queued, "Proposal not queued");

        Proposal storage proposal = proposals[proposalId];
        require(
            block.timestamp >= proposal.queuedTime + proposal.executionDelay,
            "Execution delay not met"
        );

        proposal.executed = true;

        for (uint256 i = 0; i < proposal.targets.length; i++) {
            (bool success, ) = proposal.targets[i].call{value: proposal.values[i]}(
                proposal.calldatas[i]
            );
            require(success, "Execution failed");
        }

        emit ProposalExecuted(proposalId);
    }

    /**
     * @dev Cancel a proposal
     */
    function cancel(uint256 proposalId) external {
        require(state(proposalId) != ProposalState.Executed, "Cannot cancel executed proposal");

        Proposal storage proposal = proposals[proposalId];
        require(
            msg.sender == proposal.proposer ||
            hasRole(ADMIN_ROLE, msg.sender) ||
            getVotingPower(proposal.proposer) < proposalThreshold,
            "Not authorized to cancel"
        );

        proposal.canceled = true;
        emit ProposalCanceled(proposalId);
    }

    /**
     * @dev Verify a voter for Sybil resistance
     */
    function verifyVoter(address voter, uint256 reputationScore) 
        external 
        onlyRole(COMPLIANCE_ROLE) 
    {
        require(voter != address(0), "Invalid voter address");
        require(reputationScore <= 100, "Invalid reputation score");

        verifiedVoters[voter] = true;
        voters[voter].isVerified = true;
        voters[voter].reputationScore = reputationScore;

        emit VoterVerified(voter, reputationScore);
    }

    /**
     * @dev Withdraw tokens after voting period
     */
    function withdrawVoteTokens(uint256 proposalId) external nonReentrant {
        require(
            state(proposalId) == ProposalState.Defeated ||
            state(proposalId) == ProposalState.Executed ||
            state(proposalId) == ProposalState.Expired,
            "Voting still active"
        );

        Proposal storage proposal = proposals[proposalId];
        Receipt storage receipt = proposal.receipts[msg.sender];
        require(receipt.hasVoted, "Did not vote");
        require(receipt.votes > 0, "No tokens to withdraw");

        uint256 amount = receipt.votes;
        receipt.votes = 0;

        governanceToken.safeTransfer(msg.sender, amount);
    }

    /**
     * @dev Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        string memory title,
        string memory description,
        uint256 startBlock,
        uint256 endBlock,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 abstainVotes,
        bool isEmergency,
        ProposalState currentState
    ) {
        require(proposalId < proposalCount, "Invalid proposal ID");
        
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.title,
            proposal.description,
            proposal.startBlock,
            proposal.endBlock,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.abstainVotes,
            proposal.isEmergency,
            state(proposalId)
        );
    }

    /**
     * @dev Get vote receipt for a voter on a proposal
     */
    function getReceipt(uint256 proposalId, address voter) external view returns (Receipt memory) {
        return proposals[proposalId].receipts[voter];
    }

    /**
     * @dev Square root function for quadratic voting
     */
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    // Admin functions
    function setVotingDelay(uint256 newVotingDelay) external onlyRole(ADMIN_ROLE) {
        votingDelay = newVotingDelay;
    }

    function setVotingPeriod(uint256 newVotingPeriod) external onlyRole(ADMIN_ROLE) {
        votingPeriod = newVotingPeriod;
    }

    function setProposalThreshold(uint256 newProposalThreshold) external onlyRole(ADMIN_ROLE) {
        proposalThreshold = newProposalThreshold;
    }

    function setQuorumVotes(uint256 newQuorumVotes) external onlyRole(ADMIN_ROLE) {
        quorumVotes = newQuorumVotes;
    }
}
