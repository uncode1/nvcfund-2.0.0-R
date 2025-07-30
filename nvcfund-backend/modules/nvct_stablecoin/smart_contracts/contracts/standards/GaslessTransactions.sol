// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title GaslessTransactions
 * @dev Enterprise-grade gasless transaction system with meta-transactions
 * Features:
 * - EIP-712 typed data signing
 * - Relay network integration
 * - Gas fee sponsorship
 * - Batch transaction processing
 * - Nonce management
 * - Fee token flexibility
 * - Anti-replay protection
 * - Compliance integration
 */
contract GaslessTransactions is ReentrancyGuard, AccessControl {
    using ECDSA for bytes32;
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant RELAYER_ROLE = keccak256("RELAYER_ROLE");
    bytes32 public constant SPONSOR_ROLE = keccak256("SPONSOR_ROLE");

    // EIP-712 Domain Separator
    bytes32 private constant DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    );

    // Meta-transaction typehash
    bytes32 private constant META_TRANSACTION_TYPEHASH = keccak256(
        "MetaTransaction(uint256 nonce,address from,bytes functionSignature,uint256 deadline,uint256 gasLimit,address feeToken,uint256 feeAmount)"
    );

    // Batch transaction typehash
    bytes32 private constant BATCH_TRANSACTION_TYPEHASH = keccak256(
        "BatchTransaction(uint256 nonce,address from,bytes[] functionSignatures,uint256 deadline,uint256 gasLimit,address feeToken,uint256 feeAmount)"
    );

    struct MetaTransaction {
        uint256 nonce;
        address from;
        bytes functionSignature;
        uint256 deadline;
        uint256 gasLimit;
        address feeToken;
        uint256 feeAmount;
        bytes signature;
    }

    struct BatchTransaction {
        uint256 nonce;
        address from;
        bytes[] functionSignatures;
        uint256 deadline;
        uint256 gasLimit;
        address feeToken;
        uint256 feeAmount;
        bytes signature;
    }

    struct RelayerInfo {
        address relayer;
        bool isActive;
        uint256 totalTransactions;
        uint256 successfulTransactions;
        uint256 totalGasUsed;
        uint256 totalFeesEarned;
        mapping(address => uint256) tokenBalances;
    }

    struct SponsorInfo {
        address sponsor;
        bool isActive;
        uint256 sponsorshipBudget;
        uint256 sponsorshipUsed;
        mapping(address => bool) sponsoredUsers;
        mapping(address => uint256) userLimits;
        mapping(address => uint256) userUsage;
    }

    struct UserGaslessInfo {
        uint256 nonce;
        uint256 totalTransactions;
        uint256 totalGasUsed;
        bool isWhitelisted;
        address preferredRelayer;
        address currentSponsor;
    }

    mapping(address => UserGaslessInfo) public userInfo;
    mapping(address => RelayerInfo) public relayers;
    mapping(address => SponsorInfo) public sponsors;
    mapping(bytes32 => bool) public executedTransactions;
    mapping(address => bool) public supportedFeeTokens;
    mapping(address => uint256) public feeTokenRates; // Rate per gas unit

    bytes32 public DOMAIN_SEPARATOR;
    string public constant NAME = "NVC Gasless Transactions";
    string public constant VERSION = "1.0.0";

    uint256 public constant MAX_DEADLINE = 1 hours;
    uint256 public constant MAX_BATCH_SIZE = 20;
    uint256 public constant BASE_GAS_COST = 21000;

    event MetaTransactionExecuted(
        address indexed user,
        address indexed relayer,
        bytes32 indexed txHash,
        bool success,
        uint256 gasUsed,
        uint256 feeAmount
    );

    event BatchTransactionExecuted(
        address indexed user,
        address indexed relayer,
        bytes32 indexed batchHash,
        uint256 successCount,
        uint256 totalGasUsed,
        uint256 feeAmount
    );

    event RelayerRegistered(address indexed relayer);
    event RelayerDeactivated(address indexed relayer);
    event SponsorRegistered(address indexed sponsor, uint256 budget);
    event SponsorshipUsed(address indexed sponsor, address indexed user, uint256 amount);
    event FeeTokenAdded(address indexed token, uint256 rate);
    event FeeTokenRemoved(address indexed token);

    modifier onlyActiveRelayer() {
        require(relayers[msg.sender].isActive, "Not an active relayer");
        _;
    }

    modifier onlyActiveSponsor() {
        require(sponsors[msg.sender].isActive, "Not an active sponsor");
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(RELAYER_ROLE, msg.sender);
        _grantRole(SPONSOR_ROLE, msg.sender);

        // Initialize domain separator
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                DOMAIN_TYPEHASH,
                keccak256(bytes(NAME)),
                keccak256(bytes(VERSION)),
                block.chainid,
                address(this)
            )
        );
    }

    /**
     * @dev Execute a meta-transaction
     */
    function executeMetaTransaction(
        MetaTransaction calldata metaTx
    ) external onlyActiveRelayer nonReentrant returns (bool success) {
        // Validate transaction
        require(block.timestamp <= metaTx.deadline, "Transaction expired");
        require(metaTx.gasLimit <= block.gaslimit, "Gas limit too high");
        
        // Generate transaction hash
        bytes32 txHash = _getMetaTransactionHash(metaTx);
        require(!executedTransactions[txHash], "Transaction already executed");

        // Verify signature
        require(_verifyMetaTransactionSignature(metaTx, txHash), "Invalid signature");

        // Check nonce
        UserGaslessInfo storage user = userInfo[metaTx.from];
        require(metaTx.nonce == user.nonce, "Invalid nonce");
        user.nonce = user.nonce.add(1);

        // Mark as executed
        executedTransactions[txHash] = true;

        // Record gas before execution
        uint256 gasStart = gasleft();

        // Execute the function call
        (success, ) = address(this).call{gas: metaTx.gasLimit}(
            abi.encodePacked(metaTx.functionSignature, metaTx.from)
        );

        // Calculate gas used
        uint256 gasUsed = gasStart.sub(gasleft()).add(BASE_GAS_COST);

        // Handle fee payment
        uint256 feeAmount = _handleFeePayment(metaTx.from, metaTx.feeToken, metaTx.feeAmount, gasUsed);

        // Update statistics
        _updateRelayerStats(msg.sender, gasUsed, feeAmount, success);
        _updateUserStats(metaTx.from, gasUsed);

        emit MetaTransactionExecuted(metaTx.from, msg.sender, txHash, success, gasUsed, feeAmount);

        return success;
    }

    /**
     * @dev Execute batch transactions
     */
    function executeBatchTransaction(
        BatchTransaction calldata batchTx
    ) external onlyActiveRelayer nonReentrant returns (uint256 successCount) {
        require(block.timestamp <= batchTx.deadline, "Batch expired");
        require(batchTx.functionSignatures.length <= MAX_BATCH_SIZE, "Batch too large");
        require(batchTx.functionSignatures.length > 0, "Empty batch");

        // Generate batch hash
        bytes32 batchHash = _getBatchTransactionHash(batchTx);
        require(!executedTransactions[batchHash], "Batch already executed");

        // Verify signature
        require(_verifyBatchTransactionSignature(batchTx, batchHash), "Invalid signature");

        // Check nonce
        UserGaslessInfo storage user = userInfo[batchTx.from];
        require(batchTx.nonce == user.nonce, "Invalid nonce");
        user.nonce = user.nonce.add(1);

        // Mark as executed
        executedTransactions[batchHash] = true;

        uint256 totalGasUsed = 0;
        successCount = 0;

        // Execute each transaction in the batch
        for (uint256 i = 0; i < batchTx.functionSignatures.length; i++) {
            uint256 gasStart = gasleft();
            
            (bool success, ) = address(this).call{gas: batchTx.gasLimit.div(batchTx.functionSignatures.length)}(
                abi.encodePacked(batchTx.functionSignatures[i], batchTx.from)
            );

            uint256 gasUsed = gasStart.sub(gasleft()).add(BASE_GAS_COST);
            totalGasUsed = totalGasUsed.add(gasUsed);

            if (success) {
                successCount = successCount.add(1);
            }
        }

        // Handle fee payment
        uint256 feeAmount = _handleFeePayment(batchTx.from, batchTx.feeToken, batchTx.feeAmount, totalGasUsed);

        // Update statistics
        _updateRelayerStats(msg.sender, totalGasUsed, feeAmount, successCount > 0);
        _updateUserStats(batchTx.from, totalGasUsed);

        emit BatchTransactionExecuted(batchTx.from, msg.sender, batchHash, successCount, totalGasUsed, feeAmount);

        return successCount;
    }

    /**
     * @dev Handle fee payment with sponsorship support
     */
    function _handleFeePayment(
        address user,
        address feeToken,
        uint256 feeAmount,
        uint256 gasUsed
    ) internal returns (uint256 actualFeeAmount) {
        UserGaslessInfo storage userGasless = userInfo[user];
        
        // Check for sponsorship
        if (userGasless.currentSponsor != address(0)) {
            SponsorInfo storage sponsor = sponsors[userGasless.currentSponsor];
            
            if (sponsor.isActive && sponsor.sponsoredUsers[user]) {
                uint256 userLimit = sponsor.userLimits[user];
                uint256 userUsage = sponsor.userUsage[user];
                
                if (userLimit == 0 || userUsage.add(feeAmount) <= userLimit) {
                    // Sponsor pays the fee
                    if (sponsor.sponsorshipUsed.add(feeAmount) <= sponsor.sponsorshipBudget) {
                        sponsor.sponsorshipUsed = sponsor.sponsorshipUsed.add(feeAmount);
                        sponsor.userUsage[user] = userUsage.add(feeAmount);
                        
                        emit SponsorshipUsed(userGasless.currentSponsor, user, feeAmount);
                        return feeAmount;
                    }
                }
            }
        }

        // User pays the fee
        if (feeToken == address(0)) {
            // ETH payment
            require(address(this).balance >= feeAmount, "Insufficient ETH for fee");
            payable(msg.sender).transfer(feeAmount);
        } else {
            // ERC20 token payment
            require(supportedFeeTokens[feeToken], "Unsupported fee token");
            IERC20(feeToken).safeTransferFrom(user, msg.sender, feeAmount);
        }

        return feeAmount;
    }

    /**
     * @dev Update relayer statistics
     */
    function _updateRelayerStats(
        address relayer,
        uint256 gasUsed,
        uint256 feeAmount,
        bool success
    ) internal {
        RelayerInfo storage relayerInfo = relayers[relayer];
        relayerInfo.totalTransactions = relayerInfo.totalTransactions.add(1);
        relayerInfo.totalGasUsed = relayerInfo.totalGasUsed.add(gasUsed);
        relayerInfo.totalFeesEarned = relayerInfo.totalFeesEarned.add(feeAmount);
        
        if (success) {
            relayerInfo.successfulTransactions = relayerInfo.successfulTransactions.add(1);
        }
    }

    /**
     * @dev Update user statistics
     */
    function _updateUserStats(address user, uint256 gasUsed) internal {
        UserGaslessInfo storage userGasless = userInfo[user];
        userGasless.totalTransactions = userGasless.totalTransactions.add(1);
        userGasless.totalGasUsed = userGasless.totalGasUsed.add(gasUsed);
    }

    /**
     * @dev Get meta-transaction hash
     */
    function _getMetaTransactionHash(MetaTransaction calldata metaTx) internal view returns (bytes32) {
        return keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        META_TRANSACTION_TYPEHASH,
                        metaTx.nonce,
                        metaTx.from,
                        keccak256(metaTx.functionSignature),
                        metaTx.deadline,
                        metaTx.gasLimit,
                        metaTx.feeToken,
                        metaTx.feeAmount
                    )
                )
            )
        );
    }

    /**
     * @dev Get batch transaction hash
     */
    function _getBatchTransactionHash(BatchTransaction calldata batchTx) internal view returns (bytes32) {
        bytes32[] memory functionHashes = new bytes32[](batchTx.functionSignatures.length);
        for (uint256 i = 0; i < batchTx.functionSignatures.length; i++) {
            functionHashes[i] = keccak256(batchTx.functionSignatures[i]);
        }

        return keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        BATCH_TRANSACTION_TYPEHASH,
                        batchTx.nonce,
                        batchTx.from,
                        keccak256(abi.encodePacked(functionHashes)),
                        batchTx.deadline,
                        batchTx.gasLimit,
                        batchTx.feeToken,
                        batchTx.feeAmount
                    )
                )
            )
        );
    }

    /**
     * @dev Verify meta-transaction signature
     */
    function _verifyMetaTransactionSignature(
        MetaTransaction calldata metaTx,
        bytes32 txHash
    ) internal pure returns (bool) {
        address signer = txHash.recover(metaTx.signature);
        return signer == metaTx.from;
    }

    /**
     * @dev Verify batch transaction signature
     */
    function _verifyBatchTransactionSignature(
        BatchTransaction calldata batchTx,
        bytes32 batchHash
    ) internal pure returns (bool) {
        address signer = batchHash.recover(batchTx.signature);
        return signer == batchTx.from;
    }

    /**
     * @dev Register a new relayer
     */
    function registerRelayer(address relayer) external onlyRole(ADMIN_ROLE) {
        require(relayer != address(0), "Invalid relayer address");
        require(!relayers[relayer].isActive, "Relayer already registered");

        RelayerInfo storage relayerInfo = relayers[relayer];
        relayerInfo.relayer = relayer;
        relayerInfo.isActive = true;

        _grantRole(RELAYER_ROLE, relayer);
        emit RelayerRegistered(relayer);
    }

    /**
     * @dev Deactivate a relayer
     */
    function deactivateRelayer(address relayer) external onlyRole(ADMIN_ROLE) {
        require(relayers[relayer].isActive, "Relayer not active");
        
        relayers[relayer].isActive = false;
        _revokeRole(RELAYER_ROLE, relayer);
        
        emit RelayerDeactivated(relayer);
    }

    /**
     * @dev Register a sponsor
     */
    function registerSponsor(
        address sponsor,
        uint256 budget
    ) external onlyRole(ADMIN_ROLE) {
        require(sponsor != address(0), "Invalid sponsor address");
        require(budget > 0, "Invalid budget");

        SponsorInfo storage sponsorInfo = sponsors[sponsor];
        sponsorInfo.sponsor = sponsor;
        sponsorInfo.isActive = true;
        sponsorInfo.sponsorshipBudget = budget;

        _grantRole(SPONSOR_ROLE, sponsor);
        emit SponsorRegistered(sponsor, budget);
    }

    /**
     * @dev Add sponsored user
     */
    function addSponsoredUser(
        address user,
        uint256 userLimit
    ) external onlyActiveSponsor {
        SponsorInfo storage sponsor = sponsors[msg.sender];
        sponsor.sponsoredUsers[user] = true;
        sponsor.userLimits[user] = userLimit;

        userInfo[user].currentSponsor = msg.sender;
    }

    /**
     * @dev Remove sponsored user
     */
    function removeSponsoredUser(address user) external onlyActiveSponsor {
        SponsorInfo storage sponsor = sponsors[msg.sender];
        sponsor.sponsoredUsers[user] = false;
        sponsor.userLimits[user] = 0;

        if (userInfo[user].currentSponsor == msg.sender) {
            userInfo[user].currentSponsor = address(0);
        }
    }

    /**
     * @dev Add supported fee token
     */
    function addFeeToken(address token, uint256 rate) external onlyRole(ADMIN_ROLE) {
        require(token != address(0), "Invalid token address");
        require(rate > 0, "Invalid rate");

        supportedFeeTokens[token] = true;
        feeTokenRates[token] = rate;

        emit FeeTokenAdded(token, rate);
    }

    /**
     * @dev Remove supported fee token
     */
    function removeFeeToken(address token) external onlyRole(ADMIN_ROLE) {
        supportedFeeTokens[token] = false;
        feeTokenRates[token] = 0;

        emit FeeTokenRemoved(token);
    }

    /**
     * @dev Set user preferred relayer
     */
    function setPreferredRelayer(address relayer) external {
        require(relayers[relayer].isActive, "Relayer not active");
        userInfo[msg.sender].preferredRelayer = relayer;
    }

    /**
     * @dev Whitelist user for gasless transactions
     */
    function whitelistUser(address user) external onlyRole(ADMIN_ROLE) {
        userInfo[user].isWhitelisted = true;
    }

    /**
     * @dev Remove user from whitelist
     */
    function removeFromWhitelist(address user) external onlyRole(ADMIN_ROLE) {
        userInfo[user].isWhitelisted = false;
    }

    /**
     * @dev Get user nonce
     */
    function getNonce(address user) external view returns (uint256) {
        return userInfo[user].nonce;
    }

    /**
     * @dev Get relayer info
     */
    function getRelayerInfo(address relayer) external view returns (
        bool isActive,
        uint256 totalTransactions,
        uint256 successfulTransactions,
        uint256 totalGasUsed,
        uint256 totalFeesEarned
    ) {
        RelayerInfo storage info = relayers[relayer];
        return (
            info.isActive,
            info.totalTransactions,
            info.successfulTransactions,
            info.totalGasUsed,
            info.totalFeesEarned
        );
    }

    /**
     * @dev Get sponsor info
     */
    function getSponsorInfo(address sponsor) external view returns (
        bool isActive,
        uint256 sponsorshipBudget,
        uint256 sponsorshipUsed
    ) {
        SponsorInfo storage info = sponsors[sponsor];
        return (
            info.isActive,
            info.sponsorshipBudget,
            info.sponsorshipUsed
        );
    }

    /**
     * @dev Check if user is sponsored
     */
    function isUserSponsored(address sponsor, address user) external view returns (bool) {
        return sponsors[sponsor].sponsoredUsers[user];
    }

    /**
     * @dev Get user sponsorship limit
     */
    function getUserSponsorshipLimit(address sponsor, address user) external view returns (uint256) {
        return sponsors[sponsor].userLimits[user];
    }

    /**
     * @dev Get user sponsorship usage
     */
    function getUserSponsorshipUsage(address sponsor, address user) external view returns (uint256) {
        return sponsors[sponsor].userUsage[user];
    }

    // Emergency functions
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    // Allow contract to receive ETH for fee payments
    receive() external payable {}
}
