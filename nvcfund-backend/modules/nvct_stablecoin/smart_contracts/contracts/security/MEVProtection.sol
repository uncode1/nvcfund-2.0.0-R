// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title MEVProtection
 * @dev Advanced MEV (Maximal Extractable Value) protection system
 * Features:
 * - Transaction ordering protection
 * - Sandwich attack prevention
 * - Front-running detection
 * - Time-based transaction delays
 * - Priority fee analysis
 * - Commit-reveal schemes
 * - Batch transaction processing
 */
contract MEVProtection is AccessControl, ReentrancyGuard {
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MONITOR_ROLE = keccak256("MONITOR_ROLE");

    struct TransactionInfo {
        address sender;
        bytes32 txHash;
        uint256 blockNumber;
        uint256 gasPrice;
        uint256 priorityFee;
        uint256 timestamp;
        bool isSuspicious;
        uint256 mevScore;
    }

    struct UserProtection {
        uint256 lastTransactionBlock;
        uint256 transactionCount;
        uint256 suspiciousActivityCount;
        bool isProtected;
        uint256 protectionLevel; // 1-5 scale
        uint256 maxTransactionsPerBlock;
    }

    struct CommitRevealOrder {
        bytes32 commitment;
        address user;
        uint256 commitBlock;
        uint256 revealDeadline;
        bool revealed;
        bool executed;
        bytes orderData;
    }

    struct BatchTransaction {
        address[] targets;
        bytes[] data;
        uint256[] values;
        uint256 batchId;
        uint256 executionBlock;
        bool executed;
    }

    mapping(address => UserProtection) public userProtections;
    mapping(bytes32 => TransactionInfo) public transactionHistory;
    mapping(bytes32 => CommitRevealOrder) public commitRevealOrders;
    mapping(uint256 => BatchTransaction) public batchTransactions;
    mapping(address => bool) public protectedContracts;
    mapping(address => uint256) private nonces;

    uint256 public constant MIN_BLOCK_DELAY = 2;
    uint256 public constant MAX_BLOCK_DELAY = 10;
    uint256 public constant REVEAL_WINDOW = 5; // blocks
    uint256 public constant MEV_THRESHOLD = 80; // MEV score threshold
    uint256 public constant MAX_GAS_PRICE_DEVIATION = 150; // 150% of average

    uint256 public averageGasPrice;
    uint256 public averagePriorityFee;
    uint256 public totalTransactions;
    uint256 public suspiciousTransactions;
    uint256 public batchCounter;

    event MEVDetected(
        address indexed user,
        bytes32 indexed txHash,
        uint256 mevScore,
        string reason
    );
    event TransactionDelayed(
        address indexed user,
        uint256 delayBlocks,
        string reason
    );
    event CommitmentMade(
        bytes32 indexed commitment,
        address indexed user,
        uint256 revealDeadline
    );
    event OrderRevealed(
        bytes32 indexed commitment,
        address indexed user,
        bytes orderData
    );
    event BatchExecuted(
        uint256 indexed batchId,
        uint256 transactionCount,
        uint256 executionBlock
    );
    event ProtectionLevelUpdated(
        address indexed user,
        uint256 oldLevel,
        uint256 newLevel
    );

    modifier mevProtected() {
        _checkMEVProtection(msg.sender);
        _;
        _recordTransaction(msg.sender);
    }

    modifier onlyProtectedContract() {
        require(protectedContracts[msg.sender], "Contract not protected");
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(MONITOR_ROLE, msg.sender);
    }

    /**
     * @dev Enable MEV protection for a user
     */
    function enableProtection(uint256 _protectionLevel) external {
        require(_protectionLevel >= 1 && _protectionLevel <= 5, "Invalid protection level");
        
        UserProtection storage protection = userProtections[msg.sender];
        uint256 oldLevel = protection.protectionLevel;
        
        protection.isProtected = true;
        protection.protectionLevel = _protectionLevel;
        protection.maxTransactionsPerBlock = _getMaxTransactionsForLevel(_protectionLevel);
        
        emit ProtectionLevelUpdated(msg.sender, oldLevel, _protectionLevel);
    }

    /**
     * @dev Check MEV protection for a user
     */
    function _checkMEVProtection(address _user) internal {
        UserProtection storage protection = userProtections[_user];
        
        if (!protection.isProtected) return;

        // Check block-based rate limiting
        if (protection.lastTransactionBlock == block.number) {
            protection.transactionCount++;
            require(
                protection.transactionCount <= protection.maxTransactionsPerBlock,
                "Too many transactions in single block"
            );
        } else {
            protection.transactionCount = 1;
            protection.lastTransactionBlock = block.number;
        }

        // Check gas price manipulation
        uint256 currentGasPrice = tx.gasprice;
        if (averageGasPrice > 0) {
            uint256 maxAllowedGasPrice = averageGasPrice.mul(MAX_GAS_PRICE_DEVIATION).div(100);
            if (currentGasPrice > maxAllowedGasPrice) {
                protection.suspiciousActivityCount++;
                emit MEVDetected(
                    _user,
                    keccak256(abi.encodePacked(block.number, _user, nonces[_user])),
                    85,
                    "Excessive gas price"
                );
            }
        }

        // Apply protection level delays
        uint256 requiredDelay = _getRequiredDelay(protection.protectionLevel);
        if (requiredDelay > 0) {
            require(
                block.number >= protection.lastTransactionBlock + requiredDelay,
                "Transaction delay not satisfied"
            );
        }
    }

    /**
     * @dev Record transaction for MEV analysis
     */
    function _recordTransaction(address _user) internal {
        bytes32 txHash = keccak256(abi.encodePacked(
            block.number,
            _user,
            nonces[_user]++,
            tx.gasprice
        ));

        uint256 mevScore = _calculateMEVScore(_user, tx.gasprice);

        transactionHistory[txHash] = TransactionInfo({
            sender: _user,
            txHash: txHash,
            blockNumber: block.number,
            gasPrice: tx.gasprice,
            priorityFee: tx.gasprice, // Simplified
            timestamp: block.timestamp,
            isSuspicious: mevScore >= MEV_THRESHOLD,
            mevScore: mevScore
        });

        // Update global statistics
        totalTransactions++;
        averageGasPrice = averageGasPrice.mul(totalTransactions.sub(1)).add(tx.gasprice).div(totalTransactions);

        if (mevScore >= MEV_THRESHOLD) {
            suspiciousTransactions++;
            userProtections[_user].suspiciousActivityCount++;
            
            emit MEVDetected(_user, txHash, mevScore, "High MEV score detected");
        }
    }

    /**
     * @dev Calculate MEV score for a transaction
     */
    function _calculateMEVScore(address _user, uint256 _gasPrice) internal view returns (uint256) {
        uint256 score = 0;

        // Gas price analysis
        if (averageGasPrice > 0) {
            uint256 gasPriceRatio = _gasPrice.mul(100).div(averageGasPrice);
            if (gasPriceRatio > 120) score += 30; // 20% above average
            if (gasPriceRatio > 150) score += 20; // 50% above average
            if (gasPriceRatio > 200) score += 30; // 100% above average
        }

        // Transaction frequency analysis
        UserProtection storage protection = userProtections[_user];
        if (protection.transactionCount > 3) score += 25;
        if (protection.transactionCount > 5) score += 25;

        // Historical suspicious activity
        if (protection.suspiciousActivityCount > 5) score += 20;
        if (protection.suspiciousActivityCount > 10) score += 30;

        return score > 100 ? 100 : score;
    }

    /**
     * @dev Commit-reveal scheme for sensitive transactions
     */
    function commitOrder(bytes32 _commitment) external {
        require(_commitment != bytes32(0), "Invalid commitment");
        
        CommitRevealOrder storage order = commitRevealOrders[_commitment];
        require(order.user == address(0), "Commitment already exists");

        order.commitment = _commitment;
        order.user = msg.sender;
        order.commitBlock = block.number;
        order.revealDeadline = block.number.add(REVEAL_WINDOW);
        order.revealed = false;
        order.executed = false;

        emit CommitmentMade(_commitment, msg.sender, order.revealDeadline);
    }

    /**
     * @dev Reveal committed order
     */
    function revealOrder(
        bytes32 _commitment,
        bytes calldata _orderData,
        uint256 _nonce
    ) external {
        CommitRevealOrder storage order = commitRevealOrders[_commitment];
        require(order.user == msg.sender, "Not order owner");
        require(!order.revealed, "Order already revealed");
        require(block.number <= order.revealDeadline, "Reveal deadline passed");
        require(block.number > order.commitBlock, "Cannot reveal in same block");

        // Verify commitment
        bytes32 computedCommitment = keccak256(abi.encodePacked(_orderData, _nonce, msg.sender));
        require(computedCommitment == _commitment, "Invalid reveal");

        order.revealed = true;
        order.orderData = _orderData;

        emit OrderRevealed(_commitment, msg.sender, _orderData);
    }

    /**
     * @dev Execute revealed order
     */
    function executeRevealedOrder(bytes32 _commitment) external nonReentrant {
        CommitRevealOrder storage order = commitRevealOrders[_commitment];
        require(order.user == msg.sender, "Not order owner");
        require(order.revealed, "Order not revealed");
        require(!order.executed, "Order already executed");
        require(block.number > order.commitBlock.add(MIN_BLOCK_DELAY), "Minimum delay not met");

        order.executed = true;

        // Execute the order (implementation depends on order type)
        _executeOrderData(order.orderData);
    }

    /**
     * @dev Create batch transaction
     */
    function createBatch(
        address[] calldata _targets,
        bytes[] calldata _data,
        uint256[] calldata _values,
        uint256 _executionDelay
    ) external returns (uint256 batchId) {
        require(_targets.length == _data.length, "Array length mismatch");
        require(_targets.length == _values.length, "Array length mismatch");
        require(_targets.length <= 20, "Batch too large");
        require(_executionDelay >= MIN_BLOCK_DELAY, "Delay too small");
        require(_executionDelay <= MAX_BLOCK_DELAY, "Delay too large");

        batchId = batchCounter++;
        
        batchTransactions[batchId] = BatchTransaction({
            targets: _targets,
            data: _data,
            values: _values,
            batchId: batchId,
            executionBlock: block.number.add(_executionDelay),
            executed: false
        });

        return batchId;
    }

    /**
     * @dev Execute batch transaction
     */
    function executeBatch(uint256 _batchId) external nonReentrant {
        BatchTransaction storage batch = batchTransactions[_batchId];
        require(batch.batchId == _batchId, "Batch does not exist");
        require(!batch.executed, "Batch already executed");
        require(block.number >= batch.executionBlock, "Execution block not reached");

        batch.executed = true;

        for (uint256 i = 0; i < batch.targets.length; i++) {
            (bool success, ) = batch.targets[i].call{value: batch.values[i]}(batch.data[i]);
            require(success, "Batch transaction failed");
        }

        emit BatchExecuted(_batchId, batch.targets.length, block.number);
    }

    /**
     * @dev Get required delay for protection level
     */
    function _getRequiredDelay(uint256 _protectionLevel) internal pure returns (uint256) {
        if (_protectionLevel == 1) return 0;
        if (_protectionLevel == 2) return 1;
        if (_protectionLevel == 3) return 2;
        if (_protectionLevel == 4) return 3;
        if (_protectionLevel == 5) return 5;
        return 0;
    }

    /**
     * @dev Get max transactions per block for protection level
     */
    function _getMaxTransactionsForLevel(uint256 _protectionLevel) internal pure returns (uint256) {
        if (_protectionLevel == 1) return 10;
        if (_protectionLevel == 2) return 5;
        if (_protectionLevel == 3) return 3;
        if (_protectionLevel == 4) return 2;
        if (_protectionLevel == 5) return 1;
        return 10;
    }

    /**
     * @dev Execute order data (placeholder implementation)
     */
    function _executeOrderData(bytes memory _orderData) internal {
        // Implementation depends on the specific order type
        // This could involve calling other contracts, transferring tokens, etc.
    }

    /**
     * @dev Add protected contract
     */
    function addProtectedContract(address _contract) external onlyRole(ADMIN_ROLE) {
        protectedContracts[_contract] = true;
    }

    /**
     * @dev Remove protected contract
     */
    function removeProtectedContract(address _contract) external onlyRole(ADMIN_ROLE) {
        protectedContracts[_contract] = false;
    }

    /**
     * @dev Update user protection level (admin only)
     */
    function updateUserProtectionLevel(address _user, uint256 _level) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        require(_level >= 1 && _level <= 5, "Invalid protection level");
        
        UserProtection storage protection = userProtections[_user];
        uint256 oldLevel = protection.protectionLevel;
        
        protection.protectionLevel = _level;
        protection.maxTransactionsPerBlock = _getMaxTransactionsForLevel(_level);
        
        emit ProtectionLevelUpdated(_user, oldLevel, _level);
    }

    /**
     * @dev Get user protection info
     */
    function getUserProtection(address _user) external view returns (UserProtection memory) {
        return userProtections[_user];
    }

    /**
     * @dev Get transaction info
     */
    function getTransactionInfo(bytes32 _txHash) external view returns (TransactionInfo memory) {
        return transactionHistory[_txHash];
    }

    /**
     * @dev Get commit-reveal order info
     */
    function getCommitRevealOrder(bytes32 _commitment) external view returns (CommitRevealOrder memory) {
        return commitRevealOrders[_commitment];
    }

    /**
     * @dev Get batch transaction info
     */
    function getBatchTransaction(uint256 _batchId) external view returns (BatchTransaction memory) {
        return batchTransactions[_batchId];
    }

    /**
     * @dev Get MEV protection statistics
     */
    function getProtectionStats() external view returns (
        uint256 _totalTransactions,
        uint256 _suspiciousTransactions,
        uint256 _averageGasPrice,
        uint256 _mevDetectionRate
    ) {
        _totalTransactions = totalTransactions;
        _suspiciousTransactions = suspiciousTransactions;
        _averageGasPrice = averageGasPrice;
        _mevDetectionRate = totalTransactions > 0 ? 
            suspiciousTransactions.mul(10000).div(totalTransactions) : 0;
    }
}
