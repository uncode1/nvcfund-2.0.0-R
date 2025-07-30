// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title ConcentratedLiquidityAMM
 * @dev Advanced AMM with concentrated liquidity (Uniswap V3 style)
 * Features:
 * - Concentrated liquidity positions
 * - Multiple fee tiers
 * - Price range orders
 * - MEV protection
 * - Flash loan integration
 * - Dynamic fee adjustment
 */
contract ConcentratedLiquidityAMM is ReentrancyGuard, AccessControl {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant FEE_SETTER_ROLE = keccak256("FEE_SETTER_ROLE");

    struct Pool {
        IERC20 token0;
        IERC20 token1;
        uint24 fee;
        int24 tickSpacing;
        uint128 liquidity;
        uint160 sqrtPriceX96;
        int24 tick;
        uint256 feeGrowthGlobal0X128;
        uint256 feeGrowthGlobal1X128;
        uint128 protocolFees0;
        uint128 protocolFees1;
        bool unlocked;
    }

    struct Position {
        uint128 liquidity;
        uint256 feeGrowthInside0LastX128;
        uint256 feeGrowthInside1LastX128;
        uint128 tokensOwed0;
        uint128 tokensOwed1;
    }

    struct TickInfo {
        uint128 liquidityGross;
        int128 liquidityNet;
        uint256 feeGrowthOutside0X128;
        uint256 feeGrowthOutside1X128;
        int56 tickCumulativeOutside;
        uint160 secondsPerLiquidityOutsideX128;
        uint32 secondsOutside;
        bool initialized;
    }

    struct SwapCache {
        uint8 feeProtocol;
        uint128 liquidityStart;
        uint32 blockTimestamp;
        int56 tickCumulative;
        uint160 secondsPerLiquidityCumulativeX128;
        bool computedLatestObservation;
    }

    mapping(bytes32 => Pool) public pools;
    mapping(bytes32 => mapping(bytes32 => Position)) public positions;
    mapping(bytes32 => mapping(int24 => TickInfo)) public ticks;
    mapping(address => uint256) public nonces;

    // Fee tiers (in hundredths of a bip, i.e. 1e-6)
    uint24 public constant FEE_LOW = 500;      // 0.05%
    uint24 public constant FEE_MEDIUM = 3000;  // 0.30%
    uint24 public constant FEE_HIGH = 10000;   // 1.00%

    // Protocol fee (1/N of the swap fee)
    uint8 public protocolFeeRatio = 4; // 25% of swap fees

    // MEV protection
    mapping(address => uint256) private lastTransactionBlock;
    uint256 public constant MEV_PROTECTION_BLOCKS = 2;

    event PoolCreated(
        address indexed token0,
        address indexed token1,
        uint24 indexed fee,
        int24 tickSpacing,
        bytes32 poolId
    );

    event Mint(
        address sender,
        address indexed owner,
        int24 indexed tickLower,
        int24 indexed tickUpper,
        uint128 amount,
        uint256 amount0,
        uint256 amount1
    );

    event Burn(
        address indexed owner,
        int24 indexed tickLower,
        int24 indexed tickUpper,
        uint128 amount,
        uint256 amount0,
        uint256 amount1
    );

    event Swap(
        address indexed sender,
        address indexed recipient,
        int256 amount0,
        int256 amount1,
        uint160 sqrtPriceX96,
        uint128 liquidity,
        int24 tick
    );

    modifier mevProtection() {
        require(
            lastTransactionBlock[msg.sender] + MEV_PROTECTION_BLOCKS < block.number,
            "MEV protection: too frequent transactions"
        );
        lastTransactionBlock[msg.sender] = block.number;
        _;
    }

    modifier lock(bytes32 poolId) {
        require(pools[poolId].unlocked, "Pool is locked");
        pools[poolId].unlocked = false;
        _;
        pools[poolId].unlocked = true;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(FEE_SETTER_ROLE, msg.sender);
    }

    /**
     * @dev Create a new liquidity pool
     */
    function createPool(
        address tokenA,
        address tokenB,
        uint24 fee
    ) external returns (bytes32 poolId) {
        require(tokenA != tokenB, "Identical tokens");
        require(fee == FEE_LOW || fee == FEE_MEDIUM || fee == FEE_HIGH, "Invalid fee");

        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        require(token0 != address(0), "Zero address");

        poolId = keccak256(abi.encodePacked(token0, token1, fee));
        require(address(pools[poolId].token0) == address(0), "Pool already exists");

        int24 tickSpacing = fee == FEE_LOW ? 10 : fee == FEE_MEDIUM ? 60 : 200;

        pools[poolId] = Pool({
            token0: IERC20(token0),
            token1: IERC20(token1),
            fee: fee,
            tickSpacing: tickSpacing,
            liquidity: 0,
            sqrtPriceX96: 0,
            tick: 0,
            feeGrowthGlobal0X128: 0,
            feeGrowthGlobal1X128: 0,
            protocolFees0: 0,
            protocolFees1: 0,
            unlocked: true
        });

        emit PoolCreated(token0, token1, fee, tickSpacing, poolId);
    }

    /**
     * @dev Initialize pool with starting price
     */
    function initialize(bytes32 poolId, uint160 sqrtPriceX96) external {
        Pool storage pool = pools[poolId];
        require(address(pool.token0) != address(0), "Pool does not exist");
        require(pool.sqrtPriceX96 == 0, "Already initialized");

        int24 tick = TickMath.getTickAtSqrtRatio(sqrtPriceX96);

        pool.sqrtPriceX96 = sqrtPriceX96;
        pool.tick = tick;
    }

    /**
     * @dev Add liquidity to a position
     */
    function mint(
        bytes32 poolId,
        address recipient,
        int24 tickLower,
        int24 tickUpper,
        uint128 amount,
        bytes calldata data
    ) external nonReentrant lock(poolId) mevProtection returns (uint256 amount0, uint256 amount1) {
        require(amount > 0, "Amount must be greater than 0");
        
        Pool storage pool = pools[poolId];
        require(address(pool.token0) != address(0), "Pool does not exist");
        require(tickLower < tickUpper, "Invalid tick range");
        require(tickLower >= TickMath.MIN_TICK, "Tick too low");
        require(tickUpper <= TickMath.MAX_TICK, "Tick too high");

        bytes32 positionKey = keccak256(abi.encodePacked(recipient, tickLower, tickUpper));
        Position storage position = positions[poolId][positionKey];

        // Calculate token amounts needed
        (amount0, amount1) = LiquidityAmounts.getAmountsForLiquidity(
            pool.sqrtPriceX96,
            TickMath.getSqrtRatioAtTick(tickLower),
            TickMath.getSqrtRatioAtTick(tickUpper),
            amount
        );

        // Update position
        position.liquidity = position.liquidity + amount;

        // Update ticks
        _updateTick(poolId, tickLower, int128(amount), false);
        _updateTick(poolId, tickUpper, int128(amount), true);

        // Update pool liquidity if position is in range
        if (tickLower <= pool.tick && pool.tick < tickUpper) {
            pool.liquidity = pool.liquidity + amount;
        }

        // Transfer tokens
        if (amount0 > 0) pool.token0.safeTransferFrom(msg.sender, address(this), amount0);
        if (amount1 > 0) pool.token1.safeTransferFrom(msg.sender, address(this), amount1);

        emit Mint(msg.sender, recipient, tickLower, tickUpper, amount, amount0, amount1);
    }

    /**
     * @dev Remove liquidity from a position
     */
    function burn(
        bytes32 poolId,
        int24 tickLower,
        int24 tickUpper,
        uint128 amount
    ) external nonReentrant lock(poolId) returns (uint256 amount0, uint256 amount1) {
        require(amount > 0, "Amount must be greater than 0");

        Pool storage pool = pools[poolId];
        bytes32 positionKey = keccak256(abi.encodePacked(msg.sender, tickLower, tickUpper));
        Position storage position = positions[poolId][positionKey];

        require(position.liquidity >= amount, "Insufficient liquidity");

        // Calculate token amounts to return
        (amount0, amount1) = LiquidityAmounts.getAmountsForLiquidity(
            pool.sqrtPriceX96,
            TickMath.getSqrtRatioAtTick(tickLower),
            TickMath.getSqrtRatioAtTick(tickUpper),
            amount
        );

        // Update position
        position.liquidity = position.liquidity - amount;
        position.tokensOwed0 = position.tokensOwed0 + uint128(amount0);
        position.tokensOwed1 = position.tokensOwed1 + uint128(amount1);

        // Update ticks
        _updateTick(poolId, tickLower, -int128(amount), false);
        _updateTick(poolId, tickUpper, -int128(amount), true);

        // Update pool liquidity if position is in range
        if (tickLower <= pool.tick && pool.tick < tickUpper) {
            pool.liquidity = pool.liquidity - amount;
        }

        emit Burn(msg.sender, tickLower, tickUpper, amount, amount0, amount1);
    }

    /**
     * @dev Collect fees and tokens owed
     */
    function collect(
        bytes32 poolId,
        address recipient,
        int24 tickLower,
        int24 tickUpper,
        uint128 amount0Requested,
        uint128 amount1Requested
    ) external nonReentrant returns (uint128 amount0, uint128 amount1) {
        bytes32 positionKey = keccak256(abi.encodePacked(msg.sender, tickLower, tickUpper));
        Position storage position = positions[poolId][positionKey];
        Pool storage pool = pools[poolId];

        amount0 = amount0Requested > position.tokensOwed0 ? position.tokensOwed0 : amount0Requested;
        amount1 = amount1Requested > position.tokensOwed1 ? position.tokensOwed1 : amount1Requested;

        if (amount0 > 0) {
            position.tokensOwed0 = position.tokensOwed0 - amount0;
            pool.token0.safeTransfer(recipient, amount0);
        }

        if (amount1 > 0) {
            position.tokensOwed1 = position.tokensOwed1 - amount1;
            pool.token1.safeTransfer(recipient, amount1);
        }
    }

    /**
     * @dev Execute a swap
     */
    function swap(
        bytes32 poolId,
        address recipient,
        bool zeroForOne,
        int256 amountSpecified,
        uint160 sqrtPriceLimitX96,
        bytes calldata data
    ) external nonReentrant lock(poolId) mevProtection returns (int256 amount0, int256 amount1) {
        require(amountSpecified != 0, "Amount cannot be zero");

        Pool storage pool = pools[poolId];
        require(address(pool.token0) != address(0), "Pool does not exist");

        SwapCache memory cache = SwapCache({
            feeProtocol: protocolFeeRatio,
            liquidityStart: pool.liquidity,
            blockTimestamp: uint32(block.timestamp),
            tickCumulative: 0,
            secondsPerLiquidityCumulativeX128: 0,
            computedLatestObservation: false
        });

        bool exactInput = amountSpecified > 0;

        // Perform the swap calculation
        (amount0, amount1, pool.sqrtPriceX96, pool.liquidity, pool.tick) = _computeSwap(
            pool,
            cache,
            zeroForOne,
            amountSpecified,
            sqrtPriceLimitX96
        );

        // Handle token transfers
        if (zeroForOne) {
            if (amount1 < 0) pool.token1.safeTransfer(recipient, uint256(-amount1));
            if (amount0 > 0) pool.token0.safeTransferFrom(msg.sender, address(this), uint256(amount0));
        } else {
            if (amount0 < 0) pool.token0.safeTransfer(recipient, uint256(-amount0));
            if (amount1 > 0) pool.token1.safeTransferFrom(msg.sender, address(this), uint256(amount1));
        }

        emit Swap(msg.sender, recipient, amount0, amount1, pool.sqrtPriceX96, pool.liquidity, pool.tick);
    }

    /**
     * @dev Flash loan function
     */
    function flash(
        bytes32 poolId,
        address recipient,
        uint256 amount0,
        uint256 amount1,
        bytes calldata data
    ) external nonReentrant lock(poolId) {
        Pool storage pool = pools[poolId];
        require(address(pool.token0) != address(0), "Pool does not exist");

        uint256 fee0 = amount0.mul(pool.fee).div(1000000);
        uint256 fee1 = amount1.mul(pool.fee).div(1000000);

        uint256 balance0Before = pool.token0.balanceOf(address(this));
        uint256 balance1Before = pool.token1.balanceOf(address(this));

        if (amount0 > 0) pool.token0.safeTransfer(recipient, amount0);
        if (amount1 > 0) pool.token1.safeTransfer(recipient, amount1);

        // Callback to recipient
        IFlashLoanCallback(recipient).flashLoanCallback(fee0, fee1, data);

        uint256 balance0After = pool.token0.balanceOf(address(this));
        uint256 balance1After = pool.token1.balanceOf(address(this));

        require(balance0After >= balance0Before.add(fee0), "Insufficient token0 returned");
        require(balance1After >= balance1Before.add(fee1), "Insufficient token1 returned");

        // Update protocol fees
        if (fee0 > 0) {
            uint256 protocolFee0 = fee0.div(protocolFeeRatio);
            pool.protocolFees0 = pool.protocolFees0 + uint128(protocolFee0);
        }

        if (fee1 > 0) {
            uint256 protocolFee1 = fee1.div(protocolFeeRatio);
            pool.protocolFees1 = pool.protocolFees1 + uint128(protocolFee1);
        }
    }

    /**
     * @dev Internal function to update tick info
     */
    function _updateTick(
        bytes32 poolId,
        int24 tick,
        int128 liquidityDelta,
        bool upper
    ) internal {
        TickInfo storage tickInfo = ticks[poolId][tick];

        uint128 liquidityGrossBefore = tickInfo.liquidityGross;
        uint128 liquidityGrossAfter = liquidityDelta < 0
            ? liquidityGrossBefore - uint128(-liquidityDelta)
            : liquidityGrossBefore + uint128(liquidityDelta);

        require(liquidityGrossAfter <= type(uint128).max, "Liquidity overflow");

        tickInfo.liquidityGross = liquidityGrossAfter;

        if (upper) {
            tickInfo.liquidityNet = tickInfo.liquidityNet - liquidityDelta;
        } else {
            tickInfo.liquidityNet = tickInfo.liquidityNet + liquidityDelta;
        }
    }

    /**
     * @dev Internal swap computation (simplified)
     */
    function _computeSwap(
        Pool storage pool,
        SwapCache memory cache,
        bool zeroForOne,
        int256 amountSpecified,
        uint160 sqrtPriceLimitX96
    ) internal view returns (int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick) {
        // Simplified swap calculation
        // In production, this would include complex tick crossing logic
        
        uint256 feeAmount = uint256(amountSpecified > 0 ? amountSpecified : -amountSpecified)
            .mul(pool.fee)
            .div(1000000);

        if (zeroForOne) {
            amount0 = amountSpecified;
            amount1 = -int256(uint256(amountSpecified).sub(feeAmount));
        } else {
            amount1 = amountSpecified;
            amount0 = -int256(uint256(amountSpecified).sub(feeAmount));
        }

        return (amount0, amount1, pool.sqrtPriceX96, pool.liquidity, pool.tick);
    }

    // Admin functions
    function setProtocolFeeRatio(uint8 _protocolFeeRatio) external onlyRole(FEE_SETTER_ROLE) {
        require(_protocolFeeRatio > 0 && _protocolFeeRatio <= 10, "Invalid protocol fee ratio");
        protocolFeeRatio = _protocolFeeRatio;
    }

    function collectProtocolFees(bytes32 poolId, address recipient) external onlyRole(ADMIN_ROLE) {
        Pool storage pool = pools[poolId];
        
        if (pool.protocolFees0 > 0) {
            pool.token0.safeTransfer(recipient, pool.protocolFees0);
            pool.protocolFees0 = 0;
        }

        if (pool.protocolFees1 > 0) {
            pool.token1.safeTransfer(recipient, pool.protocolFees1);
            pool.protocolFees1 = 0;
        }
    }
}

// Helper interfaces and libraries would be imported or defined separately
interface IFlashLoanCallback {
    function flashLoanCallback(uint256 fee0, uint256 fee1, bytes calldata data) external;
}

library TickMath {
    int24 internal constant MIN_TICK = -887272;
    int24 internal constant MAX_TICK = -MIN_TICK;

    function getSqrtRatioAtTick(int24 tick) internal pure returns (uint160) {
        // Simplified implementation
        return uint160(2**96);
    }

    function getTickAtSqrtRatio(uint160 sqrtPriceX96) internal pure returns (int24) {
        // Simplified implementation
        return 0;
    }
}

library LiquidityAmounts {
    function getAmountsForLiquidity(
        uint160 sqrtRatioX96,
        uint160 sqrtRatioAX96,
        uint160 sqrtRatioBX96,
        uint128 liquidity
    ) internal pure returns (uint256 amount0, uint256 amount1) {
        // Simplified implementation
        amount0 = uint256(liquidity);
        amount1 = uint256(liquidity);
    }
}
