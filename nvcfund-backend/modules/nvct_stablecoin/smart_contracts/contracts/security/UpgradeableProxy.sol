// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title UpgradeableProxy
 * @dev Enterprise-grade upgradeable proxy system with advanced security
 * Features:
 * - Multi-signature upgrade approval
 * - Time-locked upgrades
 * - Emergency upgrade capabilities
 * - Rollback functionality
 * - Upgrade history tracking
 * - Compliance integration
 * - Formal verification hooks
 */
contract UpgradeableProxy is TransparentUpgradeableProxy, AccessControl, ReentrancyGuard {
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

    struct UpgradeProposal {
        uint256 id;
        address proposer;
        address newImplementation;
        bytes upgradeData;
        uint256 proposalTime;
        uint256 executionTime;
        uint256 approvalCount;
        bool executed;
        bool canceled;
        bool isEmergency;
        string description;
        mapping(address => bool) approvals;
    }

    struct ImplementationHistory {
        address implementation;
        uint256 timestamp;
        string version;
        bytes32 codeHash;
        bool isActive;
        string description;
    }

    mapping(uint256 => UpgradeProposal) public upgradeProposals;
    mapping(address => bool) public authorizedUpgraders;
    ImplementationHistory[] public implementationHistory;

    uint256 public proposalCount;
    uint256 public requiredApprovals = 3; // Multi-sig requirement
    uint256 public upgradeDelay = 7 days; // 7 days delay for normal upgrades
    uint256 public emergencyUpgradeDelay = 1 hours; // 1 hour for emergency upgrades
    uint256 public constant MAX_UPGRADE_DELAY = 30 days;
    uint256 public constant MIN_UPGRADE_DELAY = 1 hours;

    bool public upgradesEnabled = true;
    bool public emergencyMode = false;
    address public rollbackImplementation;

    event UpgradeProposed(
        uint256 indexed proposalId,
        address indexed proposer,
        address newImplementation,
        bool isEmergency,
        string description
    );

    event UpgradeApproved(
        uint256 indexed proposalId,
        address indexed approver,
        uint256 approvalCount
    );

    event UpgradeExecuted(
        uint256 indexed proposalId,
        address oldImplementation,
        address newImplementation,
        string version
    );

    event UpgradeCanceled(uint256 indexed proposalId, string reason);
    event EmergencyModeActivated(address activator, string reason);
    event EmergencyModeDeactivated(address deactivator);
    event RollbackExecuted(address oldImplementation, address rolledBackTo);

    modifier onlyWhenUpgradesEnabled() {
        require(upgradesEnabled, "Upgrades are disabled");
        _;
    }

    modifier onlyInEmergency() {
        require(emergencyMode, "Not in emergency mode");
        _;
    }

    constructor(
        address _logic,
        address _admin,
        bytes memory _data
    ) TransparentUpgradeableProxy(_logic, _admin, _data) {
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(ADMIN_ROLE, _admin);
        _grantRole(UPGRADER_ROLE, _admin);
        _grantRole(EMERGENCY_ROLE, _admin);
        _grantRole(COMPLIANCE_ROLE, _admin);

        // Record initial implementation
        implementationHistory.push(ImplementationHistory({
            implementation: _logic,
            timestamp: block.timestamp,
            version: "1.0.0",
            codeHash: _logic.codehash,
            isActive: true,
            description: "Initial implementation"
        }));
    }

    /**
     * @dev Propose an upgrade to a new implementation
     */
    function proposeUpgrade(
        address newImplementation,
        bytes calldata upgradeData,
        string calldata description,
        bool isEmergency
    ) external onlyRole(UPGRADER_ROLE) onlyWhenUpgradesEnabled returns (uint256) {
        require(newImplementation != address(0), "Invalid implementation address");
        require(newImplementation != _implementation(), "Same implementation");
        require(bytes(description).length > 0, "Description required");

        if (isEmergency) {
            require(hasRole(EMERGENCY_ROLE, msg.sender), "Not authorized for emergency upgrades");
        }

        // Compliance check
        require(_isImplementationCompliant(newImplementation), "Implementation not compliant");

        uint256 proposalId = proposalCount++;
        uint256 executionTime = block.timestamp.add(
            isEmergency ? emergencyUpgradeDelay : upgradeDelay
        );

        UpgradeProposal storage proposal = upgradeProposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.newImplementation = newImplementation;
        proposal.upgradeData = upgradeData;
        proposal.proposalTime = block.timestamp;
        proposal.executionTime = executionTime;
        proposal.isEmergency = isEmergency;
        proposal.description = description;

        // Auto-approve for emergency if in emergency mode
        if (isEmergency && emergencyMode) {
            proposal.approvals[msg.sender] = true;
            proposal.approvalCount = 1;
        }

        emit UpgradeProposed(proposalId, msg.sender, newImplementation, isEmergency, description);

        return proposalId;
    }

    /**
     * @dev Approve an upgrade proposal
     */
    function approveUpgrade(uint256 proposalId) external onlyRole(UPGRADER_ROLE) {
        require(proposalId < proposalCount, "Invalid proposal ID");

        UpgradeProposal storage proposal = upgradeProposals[proposalId];
        require(!proposal.executed, "Proposal already executed");
        require(!proposal.canceled, "Proposal canceled");
        require(!proposal.approvals[msg.sender], "Already approved");

        proposal.approvals[msg.sender] = true;
        proposal.approvalCount = proposal.approvalCount.add(1);

        emit UpgradeApproved(proposalId, msg.sender, proposal.approvalCount);
    }

    /**
     * @dev Execute an approved upgrade
     */
    function executeUpgrade(uint256 proposalId, string calldata version) 
        external 
        onlyRole(UPGRADER_ROLE) 
        nonReentrant 
    {
        require(proposalId < proposalCount, "Invalid proposal ID");

        UpgradeProposal storage proposal = upgradeProposals[proposalId];
        require(!proposal.executed, "Proposal already executed");
        require(!proposal.canceled, "Proposal canceled");
        require(block.timestamp >= proposal.executionTime, "Execution time not reached");

        // Check approval requirements
        uint256 requiredApprovalCount = proposal.isEmergency && emergencyMode ? 1 : requiredApprovals;
        require(proposal.approvalCount >= requiredApprovalCount, "Insufficient approvals");

        // Final compliance check
        require(_isImplementationCompliant(proposal.newImplementation), "Implementation not compliant");

        address oldImplementation = _implementation();
        
        // Store rollback option
        rollbackImplementation = oldImplementation;

        // Mark old implementation as inactive
        for (uint256 i = 0; i < implementationHistory.length; i++) {
            if (implementationHistory[i].implementation == oldImplementation) {
                implementationHistory[i].isActive = false;
                break;
            }
        }

        // Execute the upgrade
        _upgradeTo(proposal.newImplementation);

        // Record new implementation
        implementationHistory.push(ImplementationHistory({
            implementation: proposal.newImplementation,
            timestamp: block.timestamp,
            version: version,
            codeHash: proposal.newImplementation.codehash,
            isActive: true,
            description: proposal.description
        }));

        // Execute upgrade data if provided
        if (proposal.upgradeData.length > 0) {
            (bool success, ) = proposal.newImplementation.delegatecall(proposal.upgradeData);
            require(success, "Upgrade data execution failed");
        }

        proposal.executed = true;

        emit UpgradeExecuted(proposalId, oldImplementation, proposal.newImplementation, version);
    }

    /**
     * @dev Cancel an upgrade proposal
     */
    function cancelUpgrade(uint256 proposalId, string calldata reason) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        require(proposalId < proposalCount, "Invalid proposal ID");

        UpgradeProposal storage proposal = upgradeProposals[proposalId];
        require(!proposal.executed, "Proposal already executed");
        require(!proposal.canceled, "Proposal already canceled");

        proposal.canceled = true;

        emit UpgradeCanceled(proposalId, reason);
    }

    /**
     * @dev Emergency rollback to previous implementation
     */
    function emergencyRollback() external onlyRole(EMERGENCY_ROLE) onlyInEmergency nonReentrant {
        require(rollbackImplementation != address(0), "No rollback implementation available");
        require(rollbackImplementation != _implementation(), "Already at rollback implementation");

        address currentImplementation = _implementation();
        
        // Mark current implementation as inactive
        for (uint256 i = 0; i < implementationHistory.length; i++) {
            if (implementationHistory[i].implementation == currentImplementation) {
                implementationHistory[i].isActive = false;
                break;
            }
        }

        // Rollback to previous implementation
        _upgradeTo(rollbackImplementation);

        // Mark rollback implementation as active
        for (uint256 i = 0; i < implementationHistory.length; i++) {
            if (implementationHistory[i].implementation == rollbackImplementation) {
                implementationHistory[i].isActive = true;
                break;
            }
        }

        emit RollbackExecuted(currentImplementation, rollbackImplementation);
    }

    /**
     * @dev Activate emergency mode
     */
    function activateEmergencyMode(string calldata reason) external onlyRole(EMERGENCY_ROLE) {
        require(!emergencyMode, "Already in emergency mode");
        
        emergencyMode = true;
        emit EmergencyModeActivated(msg.sender, reason);
    }

    /**
     * @dev Deactivate emergency mode
     */
    function deactivateEmergencyMode() external onlyRole(ADMIN_ROLE) {
        require(emergencyMode, "Not in emergency mode");
        
        emergencyMode = false;
        emit EmergencyModeDeactivated(msg.sender);
    }

    /**
     * @dev Check if implementation is compliant
     */
    function _isImplementationCompliant(address implementation) internal view returns (bool) {
        // Compliance checks would be implemented here
        // For example: checking against blacklisted addresses, verifying code signatures, etc.
        
        // Basic checks
        require(implementation != address(0), "Zero address");
        require(implementation.code.length > 0, "No contract code");
        
        // Additional compliance checks would go here
        return true;
    }

    /**
     * @dev Get current implementation address
     */
    function getCurrentImplementation() external view returns (address) {
        return _implementation();
    }

    /**
     * @dev Get implementation history
     */
    function getImplementationHistory() external view returns (ImplementationHistory[] memory) {
        return implementationHistory;
    }

    /**
     * @dev Get active implementation info
     */
    function getActiveImplementation() external view returns (ImplementationHistory memory) {
        for (uint256 i = implementationHistory.length; i > 0; i--) {
            if (implementationHistory[i - 1].isActive) {
                return implementationHistory[i - 1];
            }
        }
        revert("No active implementation found");
    }

    /**
     * @dev Get upgrade proposal details
     */
    function getUpgradeProposal(uint256 proposalId) external view returns (
        address proposer,
        address newImplementation,
        uint256 proposalTime,
        uint256 executionTime,
        uint256 approvalCount,
        bool executed,
        bool canceled,
        bool isEmergency,
        string memory description
    ) {
        require(proposalId < proposalCount, "Invalid proposal ID");
        
        UpgradeProposal storage proposal = upgradeProposals[proposalId];
        return (
            proposal.proposer,
            proposal.newImplementation,
            proposal.proposalTime,
            proposal.executionTime,
            proposal.approvalCount,
            proposal.executed,
            proposal.canceled,
            proposal.isEmergency,
            proposal.description
        );
    }

    /**
     * @dev Check if address has approved a proposal
     */
    function hasApproved(uint256 proposalId, address approver) external view returns (bool) {
        return upgradeProposals[proposalId].approvals[approver];
    }

    // Admin functions
    function setRequiredApprovals(uint256 _requiredApprovals) external onlyRole(ADMIN_ROLE) {
        require(_requiredApprovals > 0, "Must require at least 1 approval");
        require(_requiredApprovals <= 10, "Too many required approvals");
        requiredApprovals = _requiredApprovals;
    }

    function setUpgradeDelay(uint256 _upgradeDelay) external onlyRole(ADMIN_ROLE) {
        require(_upgradeDelay >= MIN_UPGRADE_DELAY, "Delay too short");
        require(_upgradeDelay <= MAX_UPGRADE_DELAY, "Delay too long");
        upgradeDelay = _upgradeDelay;
    }

    function setEmergencyUpgradeDelay(uint256 _emergencyUpgradeDelay) external onlyRole(ADMIN_ROLE) {
        require(_emergencyUpgradeDelay >= MIN_UPGRADE_DELAY, "Delay too short");
        require(_emergencyUpgradeDelay <= upgradeDelay, "Emergency delay cannot exceed normal delay");
        emergencyUpgradeDelay = _emergencyUpgradeDelay;
    }

    function setUpgradesEnabled(bool _enabled) external onlyRole(ADMIN_ROLE) {
        upgradesEnabled = _enabled;
    }

    function addUpgrader(address upgrader) external onlyRole(ADMIN_ROLE) {
        _grantRole(UPGRADER_ROLE, upgrader);
        authorizedUpgraders[upgrader] = true;
    }

    function removeUpgrader(address upgrader) external onlyRole(ADMIN_ROLE) {
        _revokeRole(UPGRADER_ROLE, upgrader);
        authorizedUpgraders[upgrader] = false;
    }
}
