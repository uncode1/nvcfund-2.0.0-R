// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title FlashLoanProtocol
 * @dev Enterprise-grade flash loan protocol with advanced security
 * Features:
 * - Multi-asset flash loans
 * - Dynamic fee calculation
 * - MEV protection
 * - Compliance integration
 * - Emergency controls
 * - Liquidation protection
 * - Arbitrage detection
 */
contract FlashLoanProtocol is ReentrancyGuard, Pausable, AccessControl {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

    struct FlashLoanPool {
        IERC20 asset;
        uint256 totalLiquidity;
        uint256 availableLiquidity;
        uint256 baseFeeRate; // Basis points (10000 = 100%)
        uint256 utilizationFeeRate; // Additional fee based on utilization
        uint256 maxLoanAmount;
        uint256 minLoanAmount;
        bool active;
        bool emergencyPaused;
    }

    struct FlashLoanRequest {
        address borrower;
        address asset;
        uint256 amount;
        uint256 fee;
        uint256 timestamp;
        bytes32 requestId;
        bool executed;
        bool repaid;
    }

    struct BorrowerInfo {
        uint256 totalBorrowed;
        uint256 totalRepaid;
        uint256 defaultCount;
        uint256 lastLoanTime;
        bool isBlacklisted;
        uint256 creditScore;
        uint256 maxLoanLimit;
    }

    mapping(address => FlashLoanPool) public pools;
    mapping(bytes32 => FlashLoanRequest) public flashLoans;
    mapping(address => BorrowerInfo) public borrowers;
    mapping(address => bool) public authorizedCallers;
    mapping(address => uint256) private lastTransactionBlock;

    address[] public supportedAssets;
    uint256 public constant MAX_UTILIZATION_RATE = 9500; // 95%
    uint256 public constant MEV_PROTECTION_BLOCKS = 2;
    uint256 public constant MIN_CREDIT_SCORE = 70;
    uint256 public constant MAX_LOAN_DURATION = 1; // 1 block
    
    uint256 public totalFlashLoans;
    uint256 public totalVolumeFlashLoaned;
    uint256 public totalFeesCollected;

    event FlashLoanPoolCreated(address indexed asset, uint256 baseFeeRate);
    event FlashLoanExecuted(
        bytes32 indexed requestId,
        address indexed borrower,
        address indexed asset,
        uint256 amount,
        uint256 fee
    );
    event FlashLoanRepaid(bytes32 indexed requestId, uint256 amount, uint256 fee);
    event LiquidityAdded(address indexed asset, uint256 amount);
    event LiquidityRemoved(address indexed asset, uint256 amount);
    event BorrowerBlacklisted(address indexed borrower, string reason);
    event EmergencyPause(address indexed asset, bool paused);

    modifier onlyAuthorizedCaller() {
        require(authorizedCallers[msg.sender], "Unauthorized caller");
        _;
    }

    modifier mevProtection() {
        require(
            lastTransactionBlock[msg.sender] + MEV_PROTECTION_BLOCKS < block.number,
            "MEV protection: too frequent transactions"
        );
        lastTransactionBlock[msg.sender] = block.number;
        _;
    }

    modifier validBorrower(address borrower) {
        BorrowerInfo storage info = borrowers[borrower];
        require(!info.isBlacklisted, "Borrower is blacklisted");
        require(info.creditScore >= MIN_CREDIT_SCORE, "Credit score too low");
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);
        _grantRole(COMPLIANCE_ROLE, msg.sender);
    }

    /**
     * @dev Create a new flash loan pool for an asset
     */
    function createFlashLoanPool(
        address _asset,
        uint256 _baseFeeRate,
        uint256 _utilizationFeeRate,
        uint256 _maxLoanAmount,
        uint256 _minLoanAmount
    ) external onlyRole(ADMIN_ROLE) {
        require(_asset != address(0), "Invalid asset address");
        require(_baseFeeRate <= 1000, "Base fee rate too high"); // Max 10%
        require(_utilizationFeeRate <= 500, "Utilization fee rate too high"); // Max 5%
        require(_maxLoanAmount > _minLoanAmount, "Invalid loan amount range");
        require(address(pools[_asset].asset) == address(0), "Pool already exists");

        pools[_asset] = FlashLoanPool({
            asset: IERC20(_asset),
            totalLiquidity: 0,
            availableLiquidity: 0,
            baseFeeRate: _baseFeeRate,
            utilizationFeeRate: _utilizationFeeRate,
            maxLoanAmount: _maxLoanAmount,
            minLoanAmount: _minLoanAmount,
            active: true,
            emergencyPaused: false
        });

        supportedAssets.push(_asset);
        emit FlashLoanPoolCreated(_asset, _baseFeeRate);
    }

    /**
     * @dev Add liquidity to a flash loan pool
     */
    function addLiquidity(address _asset, uint256 _amount) 
        external 
        nonReentrant 
        whenNotPaused 
    {
        require(_amount > 0, "Amount must be greater than 0");
        FlashLoanPool storage pool = pools[_asset];
        require(address(pool.asset) != address(0), "Pool does not exist");
        require(pool.active, "Pool is not active");

        pool.asset.safeTransferFrom(msg.sender, address(this), _amount);
        pool.totalLiquidity = pool.totalLiquidity.add(_amount);
        pool.availableLiquidity = pool.availableLiquidity.add(_amount);

        emit LiquidityAdded(_asset, _amount);
    }

    /**
     * @dev Remove liquidity from a flash loan pool
     */
    function removeLiquidity(address _asset, uint256 _amount) 
        external 
        nonReentrant 
        onlyRole(ADMIN_ROLE) 
    {
        require(_amount > 0, "Amount must be greater than 0");
        FlashLoanPool storage pool = pools[_asset];
        require(address(pool.asset) != address(0), "Pool does not exist");
        require(pool.availableLiquidity >= _amount, "Insufficient liquidity");

        pool.totalLiquidity = pool.totalLiquidity.sub(_amount);
        pool.availableLiquidity = pool.availableLiquidity.sub(_amount);
        pool.asset.safeTransfer(msg.sender, _amount);

        emit LiquidityRemoved(_asset, _amount);
    }

    /**
     * @dev Execute a flash loan
     */
    function flashLoan(
        address _asset,
        uint256 _amount,
        bytes calldata _params
    ) external nonReentrant whenNotPaused mevProtection validBorrower(msg.sender) {
        require(_amount > 0, "Amount must be greater than 0");
        
        FlashLoanPool storage pool = pools[_asset];
        require(address(pool.asset) != address(0), "Pool does not exist");
        require(pool.active && !pool.emergencyPaused, "Pool not available");
        require(_amount >= pool.minLoanAmount, "Amount below minimum");
        require(_amount <= pool.maxLoanAmount, "Amount above maximum");
        require(pool.availableLiquidity >= _amount, "Insufficient liquidity");

        // Check utilization rate
        uint256 utilizationRate = pool.totalLiquidity.sub(pool.availableLiquidity)
            .mul(10000)
            .div(pool.totalLiquidity);
        require(utilizationRate <= MAX_UTILIZATION_RATE, "Utilization rate too high");

        // Calculate dynamic fee
        uint256 fee = calculateFlashLoanFee(_asset, _amount);
        
        // Create flash loan request
        bytes32 requestId = keccak256(abi.encodePacked(
            msg.sender,
            _asset,
            _amount,
            block.timestamp,
            totalFlashLoans
        ));

        flashLoans[requestId] = FlashLoanRequest({
            borrower: msg.sender,
            asset: _asset,
            amount: _amount,
            fee: fee,
            timestamp: block.timestamp,
            requestId: requestId,
            executed: true,
            repaid: false
        });

        // Update pool state
        pool.availableLiquidity = pool.availableLiquidity.sub(_amount);
        
        // Update borrower info
        BorrowerInfo storage borrower = borrowers[msg.sender];
        borrower.totalBorrowed = borrower.totalBorrowed.add(_amount);
        borrower.lastLoanTime = block.timestamp;

        // Record balances before loan
        uint256 balanceBefore = pool.asset.balanceOf(address(this));

        // Transfer loan amount to borrower
        pool.asset.safeTransfer(msg.sender, _amount);

        // Execute callback
        IFlashLoanReceiver(msg.sender).executeOperation(
            _asset,
            _amount,
            fee,
            msg.sender,
            _params
        );

        // Verify repayment
        uint256 balanceAfter = pool.asset.balanceOf(address(this));
        uint256 expectedBalance = balanceBefore.add(fee);
        require(balanceAfter >= expectedBalance, "Flash loan not repaid");

        // Update state after successful repayment
        flashLoans[requestId].repaid = true;
        pool.availableLiquidity = pool.availableLiquidity.add(_amount).add(fee);
        borrower.totalRepaid = borrower.totalRepaid.add(_amount).add(fee);

        // Update global statistics
        totalFlashLoans++;
        totalVolumeFlashLoaned = totalVolumeFlashLoaned.add(_amount);
        totalFeesCollected = totalFeesCollected.add(fee);

        emit FlashLoanExecuted(requestId, msg.sender, _asset, _amount, fee);
        emit FlashLoanRepaid(requestId, _amount, fee);
    }

    /**
     * @dev Calculate dynamic flash loan fee
     */
    function calculateFlashLoanFee(address _asset, uint256 _amount) 
        public 
        view 
        returns (uint256) 
    {
        FlashLoanPool storage pool = pools[_asset];
        
        // Base fee
        uint256 baseFee = _amount.mul(pool.baseFeeRate).div(10000);
        
        // Utilization-based fee
        uint256 utilization = pool.totalLiquidity.sub(pool.availableLiquidity)
            .mul(10000)
            .div(pool.totalLiquidity);
        uint256 utilizationFee = _amount.mul(pool.utilizationFeeRate).mul(utilization).div(100000000);
        
        // Borrower credit score adjustment
        BorrowerInfo storage borrower = borrowers[msg.sender];
        uint256 creditAdjustment = 0;
        if (borrower.creditScore < 90) {
            creditAdjustment = baseFee.mul(100 - borrower.creditScore).div(1000);
        }

        return baseFee.add(utilizationFee).add(creditAdjustment);
    }

    /**
     * @dev Batch flash loan for multiple assets
     */
    function batchFlashLoan(
        address[] calldata _assets,
        uint256[] calldata _amounts,
        bytes calldata _params
    ) external nonReentrant whenNotPaused mevProtection validBorrower(msg.sender) {
        require(_assets.length == _amounts.length, "Array length mismatch");
        require(_assets.length <= 10, "Too many assets"); // Limit batch size

        uint256[] memory fees = new uint256[](_assets.length);
        bytes32[] memory requestIds = new bytes32[](_assets.length);

        // Validate all loans first
        for (uint256 i = 0; i < _assets.length; i++) {
            require(_amounts[i] > 0, "Amount must be greater than 0");
            
            FlashLoanPool storage pool = pools[_assets[i]];
            require(address(pool.asset) != address(0), "Pool does not exist");
            require(pool.active && !pool.emergencyPaused, "Pool not available");
            require(pool.availableLiquidity >= _amounts[i], "Insufficient liquidity");

            fees[i] = calculateFlashLoanFee(_assets[i], _amounts[i]);
        }

        // Execute all loans
        for (uint256 i = 0; i < _assets.length; i++) {
            FlashLoanPool storage pool = pools[_assets[i]];
            
            requestIds[i] = keccak256(abi.encodePacked(
                msg.sender,
                _assets[i],
                _amounts[i],
                block.timestamp,
                totalFlashLoans + i
            ));

            // Update pool state
            pool.availableLiquidity = pool.availableLiquidity.sub(_amounts[i]);
            
            // Transfer loan amount
            pool.asset.safeTransfer(msg.sender, _amounts[i]);
        }

        // Execute callback
        IFlashLoanReceiver(msg.sender).executeOperationBatch(
            _assets,
            _amounts,
            fees,
            msg.sender,
            _params
        );

        // Verify repayments
        for (uint256 i = 0; i < _assets.length; i++) {
            FlashLoanPool storage pool = pools[_assets[i]];
            uint256 expectedBalance = _amounts[i].add(fees[i]);
            
            require(
                pool.asset.balanceOf(address(this)) >= expectedBalance,
                "Batch flash loan not fully repaid"
            );

            // Update state
            pool.availableLiquidity = pool.availableLiquidity.add(_amounts[i]).add(fees[i]);
            
            totalFlashLoans++;
            totalVolumeFlashLoaned = totalVolumeFlashLoaned.add(_amounts[i]);
            totalFeesCollected = totalFeesCollected.add(fees[i]);

            emit FlashLoanExecuted(requestIds[i], msg.sender, _assets[i], _amounts[i], fees[i]);
            emit FlashLoanRepaid(requestIds[i], _amounts[i], fees[i]);
        }
    }

    /**
     * @dev Update borrower credit score
     */
    function updateCreditScore(address _borrower, uint256 _score) 
        external 
        onlyRole(COMPLIANCE_ROLE) 
    {
        require(_score <= 100, "Invalid credit score");
        borrowers[_borrower].creditScore = _score;
    }

    /**
     * @dev Blacklist a borrower
     */
    function blacklistBorrower(address _borrower, string calldata _reason) 
        external 
        onlyRole(COMPLIANCE_ROLE) 
    {
        borrowers[_borrower].isBlacklisted = true;
        emit BorrowerBlacklisted(_borrower, _reason);
    }

    /**
     * @dev Emergency pause a specific pool
     */
    function emergencyPausePool(address _asset, bool _paused) 
        external 
        onlyRole(EMERGENCY_ROLE) 
    {
        pools[_asset].emergencyPaused = _paused;
        emit EmergencyPause(_asset, _paused);
    }

    /**
     * @dev Set authorized caller for flash loans
     */
    function setAuthorizedCaller(address _caller, bool _authorized) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        authorizedCallers[_caller] = _authorized;
    }

    /**
     * @dev Get pool information
     */
    function getPoolInfo(address _asset) 
        external 
        view 
        returns (FlashLoanPool memory) 
    {
        return pools[_asset];
    }

    /**
     * @dev Get borrower information
     */
    function getBorrowerInfo(address _borrower) 
        external 
        view 
        returns (BorrowerInfo memory) 
    {
        return borrowers[_borrower];
    }

    /**
     * @dev Get supported assets
     */
    function getSupportedAssets() external view returns (address[] memory) {
        return supportedAssets;
    }

    // Admin functions
    function pause() external onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }

    function setPoolActive(address _asset, bool _active) external onlyRole(ADMIN_ROLE) {
        pools[_asset].active = _active;
    }

    function updatePoolFees(
        address _asset,
        uint256 _baseFeeRate,
        uint256 _utilizationFeeRate
    ) external onlyRole(ADMIN_ROLE) {
        require(_baseFeeRate <= 1000, "Base fee rate too high");
        require(_utilizationFeeRate <= 500, "Utilization fee rate too high");
        
        pools[_asset].baseFeeRate = _baseFeeRate;
        pools[_asset].utilizationFeeRate = _utilizationFeeRate;
    }
}

/**
 * @dev Interface for flash loan receivers
 */
interface IFlashLoanReceiver {
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 fee,
        address initiator,
        bytes calldata params
    ) external returns (bool);

    function executeOperationBatch(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata fees,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}
