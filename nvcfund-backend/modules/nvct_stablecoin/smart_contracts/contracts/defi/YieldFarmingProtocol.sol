// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title YieldFarmingProtocol
 * @dev Enterprise-grade yield farming protocol with advanced security features
 * Implements modern DeFi 2.0 yield farming with:
 * - Multi-token staking pools
 * - Dynamic reward distribution
 * - Emergency controls
 * - MEV protection
 * - Compliance integration
 */
contract YieldFarmingProtocol is ReentrancyGuard, Pausable, AccessControl {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

    struct Pool {
        IERC20 stakingToken;
        IERC20 rewardToken;
        uint256 totalStaked;
        uint256 rewardRate;
        uint256 lastUpdateTime;
        uint256 rewardPerTokenStored;
        uint256 minimumStake;
        uint256 lockPeriod;
        bool active;
        bool emergencyWithdrawEnabled;
    }

    struct UserInfo {
        uint256 stakedAmount;
        uint256 rewardPerTokenPaid;
        uint256 rewards;
        uint256 lastStakeTime;
        bool isCompliant;
        uint256 complianceScore;
    }

    mapping(uint256 => Pool) public pools;
    mapping(uint256 => mapping(address => UserInfo)) public userInfo;
    mapping(address => bool) public blacklistedUsers;
    
    uint256 public poolCount;
    uint256 public constant MAX_POOLS = 100;
    uint256 public constant COMPLIANCE_THRESHOLD = 80;
    
    // MEV Protection
    mapping(address => uint256) private lastTransactionBlock;
    uint256 public constant MEV_PROTECTION_BLOCKS = 2;

    event PoolCreated(uint256 indexed poolId, address stakingToken, address rewardToken);
    event Staked(address indexed user, uint256 indexed poolId, uint256 amount);
    event Withdrawn(address indexed user, uint256 indexed poolId, uint256 amount);
    event RewardClaimed(address indexed user, uint256 indexed poolId, uint256 reward);
    event EmergencyWithdraw(address indexed user, uint256 indexed poolId, uint256 amount);
    event ComplianceViolation(address indexed user, uint256 complianceScore);

    modifier onlyCompliant(address user) {
        require(!blacklistedUsers[user], "User is blacklisted");
        require(userInfo[0][user].complianceScore >= COMPLIANCE_THRESHOLD, "Compliance score too low");
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

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);
        _grantRole(COMPLIANCE_ROLE, msg.sender);
    }

    /**
     * @dev Create a new yield farming pool
     */
    function createPool(
        address _stakingToken,
        address _rewardToken,
        uint256 _rewardRate,
        uint256 _minimumStake,
        uint256 _lockPeriod
    ) external onlyRole(ADMIN_ROLE) {
        require(poolCount < MAX_POOLS, "Maximum pools reached");
        require(_stakingToken != address(0), "Invalid staking token");
        require(_rewardToken != address(0), "Invalid reward token");
        require(_rewardRate > 0, "Invalid reward rate");

        pools[poolCount] = Pool({
            stakingToken: IERC20(_stakingToken),
            rewardToken: IERC20(_rewardToken),
            totalStaked: 0,
            rewardRate: _rewardRate,
            lastUpdateTime: block.timestamp,
            rewardPerTokenStored: 0,
            minimumStake: _minimumStake,
            lockPeriod: _lockPeriod,
            active: true,
            emergencyWithdrawEnabled: false
        });

        emit PoolCreated(poolCount, _stakingToken, _rewardToken);
        poolCount++;
    }

    /**
     * @dev Stake tokens in a pool with compliance checks
     */
    function stake(uint256 _poolId, uint256 _amount) 
        external 
        nonReentrant 
        whenNotPaused 
        onlyCompliant(msg.sender)
        mevProtection
    {
        require(_poolId < poolCount, "Invalid pool ID");
        require(_amount > 0, "Amount must be greater than 0");
        
        Pool storage pool = pools[_poolId];
        require(pool.active, "Pool is not active");
        require(_amount >= pool.minimumStake, "Amount below minimum stake");

        updateReward(_poolId, msg.sender);

        UserInfo storage user = userInfo[_poolId][msg.sender];
        user.stakedAmount = user.stakedAmount.add(_amount);
        user.lastStakeTime = block.timestamp;
        pool.totalStaked = pool.totalStaked.add(_amount);

        pool.stakingToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _poolId, _amount);
    }

    /**
     * @dev Withdraw staked tokens with lock period check
     */
    function withdraw(uint256 _poolId, uint256 _amount) 
        external 
        nonReentrant 
        onlyCompliant(msg.sender)
        mevProtection
    {
        require(_poolId < poolCount, "Invalid pool ID");
        require(_amount > 0, "Amount must be greater than 0");

        Pool storage pool = pools[_poolId];
        UserInfo storage user = userInfo[_poolId][msg.sender];
        
        require(user.stakedAmount >= _amount, "Insufficient staked amount");
        require(
            block.timestamp >= user.lastStakeTime.add(pool.lockPeriod) || 
            pool.emergencyWithdrawEnabled,
            "Lock period not expired"
        );

        updateReward(_poolId, msg.sender);

        user.stakedAmount = user.stakedAmount.sub(_amount);
        pool.totalStaked = pool.totalStaked.sub(_amount);

        pool.stakingToken.safeTransfer(msg.sender, _amount);

        emit Withdrawn(msg.sender, _poolId, _amount);
    }

    /**
     * @dev Claim accumulated rewards
     */
    function claimReward(uint256 _poolId) 
        external 
        nonReentrant 
        onlyCompliant(msg.sender)
        mevProtection
    {
        require(_poolId < poolCount, "Invalid pool ID");

        updateReward(_poolId, msg.sender);

        UserInfo storage user = userInfo[_poolId][msg.sender];
        uint256 reward = user.rewards;
        
        if (reward > 0) {
            user.rewards = 0;
            pools[_poolId].rewardToken.safeTransfer(msg.sender, reward);
            emit RewardClaimed(msg.sender, _poolId, reward);
        }
    }

    /**
     * @dev Emergency withdraw without rewards (compliance override)
     */
    function emergencyWithdraw(uint256 _poolId) 
        external 
        nonReentrant 
        onlyRole(EMERGENCY_ROLE)
    {
        require(_poolId < poolCount, "Invalid pool ID");
        
        Pool storage pool = pools[_poolId];
        UserInfo storage user = userInfo[_poolId][msg.sender];
        
        uint256 amount = user.stakedAmount;
        require(amount > 0, "No staked amount");

        user.stakedAmount = 0;
        user.rewards = 0;
        pool.totalStaked = pool.totalStaked.sub(amount);

        pool.stakingToken.safeTransfer(msg.sender, amount);

        emit EmergencyWithdraw(msg.sender, _poolId, amount);
    }

    /**
     * @dev Update reward calculations for a user
     */
    function updateReward(uint256 _poolId, address _user) internal {
        Pool storage pool = pools[_poolId];
        pool.rewardPerTokenStored = rewardPerToken(_poolId);
        pool.lastUpdateTime = block.timestamp;

        if (_user != address(0)) {
            UserInfo storage user = userInfo[_poolId][_user];
            user.rewards = earned(_poolId, _user);
            user.rewardPerTokenPaid = pool.rewardPerTokenStored;
        }
    }

    /**
     * @dev Calculate reward per token
     */
    function rewardPerToken(uint256 _poolId) public view returns (uint256) {
        Pool storage pool = pools[_poolId];
        if (pool.totalStaked == 0) {
            return pool.rewardPerTokenStored;
        }
        
        return pool.rewardPerTokenStored.add(
            block.timestamp
                .sub(pool.lastUpdateTime)
                .mul(pool.rewardRate)
                .mul(1e18)
                .div(pool.totalStaked)
        );
    }

    /**
     * @dev Calculate earned rewards for a user
     */
    function earned(uint256 _poolId, address _user) public view returns (uint256) {
        UserInfo storage user = userInfo[_poolId][_user];
        return user.stakedAmount
            .mul(rewardPerToken(_poolId).sub(user.rewardPerTokenPaid))
            .div(1e18)
            .add(user.rewards);
    }

    // Admin functions
    function setPoolActive(uint256 _poolId, bool _active) external onlyRole(ADMIN_ROLE) {
        require(_poolId < poolCount, "Invalid pool ID");
        pools[_poolId].active = _active;
    }

    function setEmergencyWithdraw(uint256 _poolId, bool _enabled) external onlyRole(EMERGENCY_ROLE) {
        require(_poolId < poolCount, "Invalid pool ID");
        pools[_poolId].emergencyWithdrawEnabled = _enabled;
    }

    function updateComplianceScore(address _user, uint256 _score) external onlyRole(COMPLIANCE_ROLE) {
        require(_score <= 100, "Invalid compliance score");
        userInfo[0][_user].complianceScore = _score;
        
        if (_score < COMPLIANCE_THRESHOLD) {
            emit ComplianceViolation(_user, _score);
        }
    }

    function blacklistUser(address _user, bool _blacklisted) external onlyRole(COMPLIANCE_ROLE) {
        blacklistedUsers[_user] = _blacklisted;
    }

    function pause() external onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }
}
