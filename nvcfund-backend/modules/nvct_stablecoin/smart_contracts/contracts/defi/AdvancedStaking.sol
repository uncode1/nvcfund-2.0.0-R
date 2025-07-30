// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title AdvancedStaking
 * @dev Enterprise-grade staking protocol with advanced features
 * Features:
 * - Flexible staking periods with different APY rates
 * - Compound staking rewards
 * - Slashing protection
 * - Validator delegation
 * - Governance token rewards
 * - Emergency unstaking with penalties
 */
contract AdvancedStaking is ReentrancyGuard, Pausable, AccessControl {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant SLASHER_ROLE = keccak256("SLASHER_ROLE");

    struct StakingTier {
        uint256 minAmount;
        uint256 maxAmount;
        uint256 apyRate; // Basis points (10000 = 100%)
        uint256 lockPeriod;
        uint256 penaltyRate; // Early withdrawal penalty
        bool active;
    }

    struct StakeInfo {
        uint256 amount;
        uint256 tier;
        uint256 startTime;
        uint256 lastRewardTime;
        uint256 accumulatedRewards;
        address delegatedValidator;
        bool isCompounding;
        bool isSlashed;
        uint256 slashAmount;
    }

    struct Validator {
        address validatorAddress;
        uint256 totalDelegated;
        uint256 commissionRate; // Basis points
        uint256 slashCount;
        bool isActive;
        bool isJailed;
        uint256 jailReleaseTime;
    }

    IERC20 public stakingToken;
    IERC20 public rewardToken;
    IERC20 public governanceToken;

    mapping(uint256 => StakingTier) public stakingTiers;
    mapping(address => StakeInfo[]) public userStakes;
    mapping(address => Validator) public validators;
    mapping(address => bool) public authorizedSlashers;

    uint256 public tierCount;
    uint256 public totalStaked;
    uint256 public totalRewardsDistributed;
    uint256 public constant MAX_COMMISSION_RATE = 2000; // 20%
    uint256 public constant SLASHING_THRESHOLD = 3;
    uint256 public constant JAIL_PERIOD = 7 days;

    event Staked(address indexed user, uint256 amount, uint256 tier);
    event Unstaked(address indexed user, uint256 amount, uint256 penalty);
    event RewardsClaimed(address indexed user, uint256 amount);
    event ValidatorRegistered(address indexed validator, uint256 commissionRate);
    event Delegated(address indexed user, address indexed validator, uint256 amount);
    event Slashed(address indexed user, uint256 amount, string reason);
    event ValidatorJailed(address indexed validator, uint256 releaseTime);

    constructor(
        address _stakingToken,
        address _rewardToken,
        address _governanceToken
    ) {
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
        governanceToken = IERC20(_governanceToken);

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(SLASHER_ROLE, msg.sender);
    }

    /**
     * @dev Create a new staking tier
     */
    function createStakingTier(
        uint256 _minAmount,
        uint256 _maxAmount,
        uint256 _apyRate,
        uint256 _lockPeriod,
        uint256 _penaltyRate
    ) external onlyRole(ADMIN_ROLE) {
        require(_minAmount < _maxAmount, "Invalid amount range");
        require(_apyRate <= 50000, "APY rate too high"); // Max 500%
        require(_penaltyRate <= 5000, "Penalty rate too high"); // Max 50%

        stakingTiers[tierCount] = StakingTier({
            minAmount: _minAmount,
            maxAmount: _maxAmount,
            apyRate: _apyRate,
            lockPeriod: _lockPeriod,
            penaltyRate: _penaltyRate,
            active: true
        });

        tierCount++;
    }

    /**
     * @dev Stake tokens in a specific tier
     */
    function stake(
        uint256 _amount,
        uint256 _tier,
        bool _compound,
        address _validator
    ) external nonReentrant whenNotPaused {
        require(_tier < tierCount, "Invalid tier");
        require(_amount > 0, "Amount must be greater than 0");

        StakingTier storage tier = stakingTiers[_tier];
        require(tier.active, "Tier is not active");
        require(_amount >= tier.minAmount, "Amount below minimum");
        require(_amount <= tier.maxAmount, "Amount above maximum");

        if (_validator != address(0)) {
            require(validators[_validator].isActive, "Validator not active");
            require(!validators[_validator].isJailed, "Validator is jailed");
        }

        stakingToken.safeTransferFrom(msg.sender, address(this), _amount);

        StakeInfo memory newStake = StakeInfo({
            amount: _amount,
            tier: _tier,
            startTime: block.timestamp,
            lastRewardTime: block.timestamp,
            accumulatedRewards: 0,
            delegatedValidator: _validator,
            isCompounding: _compound,
            isSlashed: false,
            slashAmount: 0
        });

        userStakes[msg.sender].push(newStake);
        totalStaked = totalStaked.add(_amount);

        if (_validator != address(0)) {
            validators[_validator].totalDelegated = validators[_validator].totalDelegated.add(_amount);
            emit Delegated(msg.sender, _validator, _amount);
        }

        emit Staked(msg.sender, _amount, _tier);
    }

    /**
     * @dev Unstake tokens with penalty calculation
     */
    function unstake(uint256 _stakeIndex) external nonReentrant {
        require(_stakeIndex < userStakes[msg.sender].length, "Invalid stake index");

        StakeInfo storage stakeInfo = userStakes[msg.sender][_stakeIndex];
        require(stakeInfo.amount > 0, "Stake already withdrawn");

        uint256 amount = stakeInfo.amount;
        uint256 penalty = 0;

        // Calculate penalty for early withdrawal
        StakingTier storage tier = stakingTiers[stakeInfo.tier];
        if (block.timestamp < stakeInfo.startTime.add(tier.lockPeriod)) {
            penalty = amount.mul(tier.penaltyRate).div(10000);
        }

        // Apply slashing if applicable
        if (stakeInfo.isSlashed) {
            penalty = penalty.add(stakeInfo.slashAmount);
        }

        uint256 withdrawAmount = amount.sub(penalty);

        // Update validator delegation
        if (stakeInfo.delegatedValidator != address(0)) {
            validators[stakeInfo.delegatedValidator].totalDelegated = 
                validators[stakeInfo.delegatedValidator].totalDelegated.sub(amount);
        }

        // Claim pending rewards
        _claimRewards(_stakeIndex);

        // Remove stake
        stakeInfo.amount = 0;
        totalStaked = totalStaked.sub(amount);

        stakingToken.safeTransfer(msg.sender, withdrawAmount);

        if (penalty > 0) {
            // Send penalty to treasury or burn
            stakingToken.safeTransfer(address(this), penalty);
        }

        emit Unstaked(msg.sender, withdrawAmount, penalty);
    }

    /**
     * @dev Claim staking rewards
     */
    function claimRewards(uint256 _stakeIndex) external nonReentrant {
        require(_stakeIndex < userStakes[msg.sender].length, "Invalid stake index");
        _claimRewards(_stakeIndex);
    }

    /**
     * @dev Internal function to claim rewards
     */
    function _claimRewards(uint256 _stakeIndex) internal {
        StakeInfo storage stakeInfo = userStakes[msg.sender][_stakeIndex];
        require(stakeInfo.amount > 0, "No active stake");

        uint256 rewards = calculateRewards(msg.sender, _stakeIndex);
        
        if (rewards > 0) {
            stakeInfo.accumulatedRewards = stakeInfo.accumulatedRewards.add(rewards);
            stakeInfo.lastRewardTime = block.timestamp;

            if (stakeInfo.isCompounding) {
                // Compound rewards back into stake
                stakeInfo.amount = stakeInfo.amount.add(rewards);
                totalStaked = totalStaked.add(rewards);
            } else {
                // Pay out rewards
                rewardToken.safeTransfer(msg.sender, rewards);
                totalRewardsDistributed = totalRewardsDistributed.add(rewards);
            }

            // Distribute governance tokens
            uint256 govRewards = rewards.div(10); // 10% of rewards in governance tokens
            governanceToken.safeTransfer(msg.sender, govRewards);

            emit RewardsClaimed(msg.sender, rewards);
        }
    }

    /**
     * @dev Calculate pending rewards for a stake
     */
    function calculateRewards(address _user, uint256 _stakeIndex) public view returns (uint256) {
        StakeInfo storage stakeInfo = userStakes[_user][_stakeIndex];
        if (stakeInfo.amount == 0) return 0;

        StakingTier storage tier = stakingTiers[stakeInfo.tier];
        uint256 stakingDuration = block.timestamp.sub(stakeInfo.lastRewardTime);
        
        uint256 baseRewards = stakeInfo.amount
            .mul(tier.apyRate)
            .mul(stakingDuration)
            .div(365 days)
            .div(10000);

        // Apply validator commission if delegated
        if (stakeInfo.delegatedValidator != address(0)) {
            Validator storage validator = validators[stakeInfo.delegatedValidator];
            uint256 commission = baseRewards.mul(validator.commissionRate).div(10000);
            baseRewards = baseRewards.sub(commission);
        }

        return baseRewards;
    }

    /**
     * @dev Register as a validator
     */
    function registerValidator(uint256 _commissionRate) external {
        require(_commissionRate <= MAX_COMMISSION_RATE, "Commission rate too high");
        require(!validators[msg.sender].isActive, "Already registered");

        validators[msg.sender] = Validator({
            validatorAddress: msg.sender,
            totalDelegated: 0,
            commissionRate: _commissionRate,
            slashCount: 0,
            isActive: true,
            isJailed: false,
            jailReleaseTime: 0
        });

        _grantRole(VALIDATOR_ROLE, msg.sender);
        emit ValidatorRegistered(msg.sender, _commissionRate);
    }

    /**
     * @dev Slash a validator and their delegators
     */
    function slashValidator(
        address _validator,
        uint256 _slashPercentage,
        string calldata _reason
    ) external onlyRole(SLASHER_ROLE) {
        require(validators[_validator].isActive, "Validator not active");
        require(_slashPercentage <= 10000, "Invalid slash percentage");

        Validator storage validator = validators[_validator];
        validator.slashCount++;

        // Jail validator if slashed too many times
        if (validator.slashCount >= SLASHING_THRESHOLD) {
            validator.isJailed = true;
            validator.jailReleaseTime = block.timestamp.add(JAIL_PERIOD);
            emit ValidatorJailed(_validator, validator.jailReleaseTime);
        }

        // Apply slashing to all delegated stakes
        // Note: In production, this would require iterating through all stakes
        // which might be gas-intensive. Consider using events and off-chain processing.
        
        emit Slashed(_validator, _slashPercentage, _reason);
    }

    /**
     * @dev Release validator from jail
     */
    function releaseFromJail(address _validator) external onlyRole(ADMIN_ROLE) {
        require(validators[_validator].isJailed, "Validator not jailed");
        require(block.timestamp >= validators[_validator].jailReleaseTime, "Jail period not expired");

        validators[_validator].isJailed = false;
        validators[_validator].jailReleaseTime = 0;
    }

    /**
     * @dev Get user's stake count
     */
    function getUserStakeCount(address _user) external view returns (uint256) {
        return userStakes[_user].length;
    }

    /**
     * @dev Get user's stake info
     */
    function getUserStake(address _user, uint256 _index) external view returns (StakeInfo memory) {
        require(_index < userStakes[_user].length, "Invalid stake index");
        return userStakes[_user][_index];
    }

    // Admin functions
    function setTierActive(uint256 _tier, bool _active) external onlyRole(ADMIN_ROLE) {
        require(_tier < tierCount, "Invalid tier");
        stakingTiers[_tier].active = _active;
    }

    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    function emergencyWithdraw(address _token, uint256 _amount) external onlyRole(ADMIN_ROLE) {
        IERC20(_token).safeTransfer(msg.sender, _amount);
    }
}
