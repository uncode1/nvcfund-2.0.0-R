// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title CircuitBreaker
 * @dev Advanced circuit breaker system for emergency controls
 * Features:
 * - Multi-level circuit breaking
 * - Automatic trigger conditions
 * - Manual emergency stops
 * - Gradual recovery mechanisms
 * - Risk assessment integration
 * - Compliance monitoring
 * - Automated incident response
 */
contract CircuitBreaker is AccessControl, ReentrancyGuard, Pausable {
    using SafeMath for uint256;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant MONITOR_ROLE = keccak256("MONITOR_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

    enum BreakerLevel {
        NONE,       // 0 - Normal operation
        YELLOW,     // 1 - Caution - monitoring increased
        ORANGE,     // 2 - Warning - some functions limited
        RED,        // 3 - Critical - major functions paused
        BLACK       // 4 - Emergency - all functions halted
    }

    enum TriggerType {
        MANUAL,
        VOLUME_SPIKE,
        PRICE_DEVIATION,
        LIQUIDITY_DRAIN,
        SUSPICIOUS_ACTIVITY,
        COMPLIANCE_VIOLATION,
        TECHNICAL_FAILURE,
        EXTERNAL_THREAT
    }

    struct BreakerConfig {
        bool enabled;
        uint256 volumeThreshold;        // Max volume per time period
        uint256 priceDeviationThreshold; // Max price deviation %
        uint256 liquidityThreshold;     // Min liquidity level
        uint256 suspiciousActivityThreshold; // Max suspicious transactions
        uint256 timeWindow;             // Time window for measurements
        uint256 cooldownPeriod;         // Cooldown before auto-recovery
    }

    struct BreakerState {
        BreakerLevel currentLevel;
        uint256 activatedTime;
        uint256 lastTriggerTime;
        TriggerType lastTriggerType;
        string lastTriggerReason;
        uint256 triggerCount;
        bool manualOverride;
        address triggeredBy;
    }

    struct RiskMetrics {
        uint256 currentVolume;
        uint256 priceDeviation;
        uint256 liquidityLevel;
        uint256 suspiciousTransactions;
        uint256 lastUpdateTime;
        uint256 riskScore; // 0-100 scale
    }

    struct IncidentReport {
        uint256 id;
        uint256 timestamp;
        BreakerLevel level;
        TriggerType triggerType;
        string description;
        address reporter;
        bool resolved;
        uint256 resolutionTime;
        string resolutionNotes;
    }

    mapping(BreakerLevel => BreakerConfig) public breakerConfigs;
    mapping(address => bool) public protectedContracts;
    mapping(address => bool) public emergencyResponders;
    
    BreakerState public currentState;
    RiskMetrics public riskMetrics;
    IncidentReport[] public incidentHistory;
    
    uint256 public incidentCounter;
    uint256 public constant MAX_RISK_SCORE = 100;
    uint256 public constant AUTO_RECOVERY_THRESHOLD = 30; // Risk score below which auto-recovery can occur

    // Function restrictions per breaker level
    mapping(BreakerLevel => mapping(bytes4 => bool)) public functionRestrictions;

    event CircuitBreakerTriggered(
        BreakerLevel indexed level,
        TriggerType indexed triggerType,
        address indexed triggeredBy,
        string reason
    );

    event CircuitBreakerRecovered(
        BreakerLevel indexed fromLevel,
        BreakerLevel indexed toLevel,
        address indexed recoveredBy,
        bool isAutomatic
    );

    event RiskMetricsUpdated(
        uint256 volume,
        uint256 priceDeviation,
        uint256 liquidityLevel,
        uint256 suspiciousTransactions,
        uint256 riskScore
    );

    event IncidentReported(
        uint256 indexed incidentId,
        BreakerLevel level,
        TriggerType triggerType,
        string description
    );

    event IncidentResolved(
        uint256 indexed incidentId,
        address resolver,
        string resolutionNotes
    );

    modifier onlyWhenNotBroken(bytes4 functionSelector) {
        require(!_isFunctionRestricted(functionSelector), "Function restricted by circuit breaker");
        _;
    }

    modifier onlyEmergencyResponder() {
        require(
            emergencyResponders[msg.sender] || hasRole(EMERGENCY_ROLE, msg.sender),
            "Not authorized emergency responder"
        );
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);
        _grantRole(MONITOR_ROLE, msg.sender);
        _grantRole(COMPLIANCE_ROLE, msg.sender);

        // Initialize default configurations
        _initializeDefaultConfigs();
        
        // Initialize state
        currentState = BreakerState({
            currentLevel: BreakerLevel.NONE,
            activatedTime: 0,
            lastTriggerTime: 0,
            lastTriggerType: TriggerType.MANUAL,
            lastTriggerReason: "",
            triggerCount: 0,
            manualOverride: false,
            triggeredBy: address(0)
        });

        riskMetrics = RiskMetrics({
            currentVolume: 0,
            priceDeviation: 0,
            liquidityLevel: 0,
            suspiciousTransactions: 0,
            lastUpdateTime: block.timestamp,
            riskScore: 0
        });
    }

    /**
     * @dev Initialize default breaker configurations
     */
    function _initializeDefaultConfigs() internal {
        // YELLOW level - Monitoring increased
        breakerConfigs[BreakerLevel.YELLOW] = BreakerConfig({
            enabled: true,
            volumeThreshold: 1000000e18,     // 1M tokens
            priceDeviationThreshold: 500,    // 5%
            liquidityThreshold: 100000e18,   // 100K tokens
            suspiciousActivityThreshold: 10,
            timeWindow: 1 hours,
            cooldownPeriod: 30 minutes
        });

        // ORANGE level - Some functions limited
        breakerConfigs[BreakerLevel.ORANGE] = BreakerConfig({
            enabled: true,
            volumeThreshold: 2000000e18,     // 2M tokens
            priceDeviationThreshold: 1000,   // 10%
            liquidityThreshold: 50000e18,    // 50K tokens
            suspiciousActivityThreshold: 20,
            timeWindow: 1 hours,
            cooldownPeriod: 1 hours
        });

        // RED level - Major functions paused
        breakerConfigs[BreakerLevel.RED] = BreakerConfig({
            enabled: true,
            volumeThreshold: 5000000e18,     // 5M tokens
            priceDeviationThreshold: 2000,   // 20%
            liquidityThreshold: 10000e18,    // 10K tokens
            suspiciousActivityThreshold: 50,
            timeWindow: 1 hours,
            cooldownPeriod: 4 hours
        });

        // BLACK level - All functions halted
        breakerConfigs[BreakerLevel.BLACK] = BreakerConfig({
            enabled: true,
            volumeThreshold: 10000000e18,    // 10M tokens
            priceDeviationThreshold: 5000,   // 50%
            liquidityThreshold: 1000e18,     // 1K tokens
            suspiciousActivityThreshold: 100,
            timeWindow: 1 hours,
            cooldownPeriod: 24 hours
        });
    }

    /**
     * @dev Manually trigger circuit breaker
     */
    function triggerCircuitBreaker(
        BreakerLevel level,
        TriggerType triggerType,
        string calldata reason
    ) external onlyEmergencyResponder {
        require(level > BreakerLevel.NONE, "Invalid breaker level");
        require(level > currentState.currentLevel, "Cannot downgrade manually");

        _activateCircuitBreaker(level, triggerType, reason, msg.sender, true);
    }

    /**
     * @dev Update risk metrics and check for automatic triggers
     */
    function updateRiskMetrics(
        uint256 volume,
        uint256 priceDeviation,
        uint256 liquidityLevel,
        uint256 suspiciousTransactions
    ) external onlyRole(MONITOR_ROLE) {
        riskMetrics.currentVolume = volume;
        riskMetrics.priceDeviation = priceDeviation;
        riskMetrics.liquidityLevel = liquidityLevel;
        riskMetrics.suspiciousTransactions = suspiciousTransactions;
        riskMetrics.lastUpdateTime = block.timestamp;

        // Calculate risk score
        uint256 riskScore = _calculateRiskScore();
        riskMetrics.riskScore = riskScore;

        emit RiskMetricsUpdated(volume, priceDeviation, liquidityLevel, suspiciousTransactions, riskScore);

        // Check for automatic triggers
        _checkAutomaticTriggers();
    }

    /**
     * @dev Calculate overall risk score
     */
    function _calculateRiskScore() internal view returns (uint256) {
        uint256 score = 0;

        // Volume risk (25% weight)
        BreakerConfig memory config = breakerConfigs[BreakerLevel.RED];
        if (riskMetrics.currentVolume > config.volumeThreshold) {
            score = score.add(25);
        } else if (riskMetrics.currentVolume > config.volumeThreshold.div(2)) {
            score = score.add(15);
        }

        // Price deviation risk (25% weight)
        if (riskMetrics.priceDeviation > config.priceDeviationThreshold) {
            score = score.add(25);
        } else if (riskMetrics.priceDeviation > config.priceDeviationThreshold.div(2)) {
            score = score.add(15);
        }

        // Liquidity risk (25% weight)
        if (riskMetrics.liquidityLevel < config.liquidityThreshold) {
            score = score.add(25);
        } else if (riskMetrics.liquidityLevel < config.liquidityThreshold.mul(2)) {
            score = score.add(15);
        }

        // Suspicious activity risk (25% weight)
        if (riskMetrics.suspiciousTransactions > config.suspiciousActivityThreshold) {
            score = score.add(25);
        } else if (riskMetrics.suspiciousTransactions > config.suspiciousActivityThreshold.div(2)) {
            score = score.add(15);
        }

        return score > MAX_RISK_SCORE ? MAX_RISK_SCORE : score;
    }

    /**
     * @dev Check for automatic circuit breaker triggers
     */
    function _checkAutomaticTriggers() internal {
        if (currentState.manualOverride) return;

        BreakerLevel newLevel = _determineRequiredLevel();
        
        if (newLevel > currentState.currentLevel) {
            TriggerType triggerType = _determineTriggerType();
            string memory reason = _generateTriggerReason(triggerType);
            
            _activateCircuitBreaker(newLevel, triggerType, reason, address(this), false);
        } else if (newLevel < currentState.currentLevel && _canAutoRecover()) {
            _recoverCircuitBreaker(newLevel, true);
        }
    }

    /**
     * @dev Determine required breaker level based on current metrics
     */
    function _determineRequiredLevel() internal view returns (BreakerLevel) {
        if (riskMetrics.riskScore >= 80) return BreakerLevel.BLACK;
        if (riskMetrics.riskScore >= 60) return BreakerLevel.RED;
        if (riskMetrics.riskScore >= 40) return BreakerLevel.ORANGE;
        if (riskMetrics.riskScore >= 20) return BreakerLevel.YELLOW;
        return BreakerLevel.NONE;
    }

    /**
     * @dev Determine trigger type based on metrics
     */
    function _determineTriggerType() internal view returns (TriggerType) {
        BreakerConfig memory config = breakerConfigs[BreakerLevel.RED];
        
        if (riskMetrics.currentVolume > config.volumeThreshold) return TriggerType.VOLUME_SPIKE;
        if (riskMetrics.priceDeviation > config.priceDeviationThreshold) return TriggerType.PRICE_DEVIATION;
        if (riskMetrics.liquidityLevel < config.liquidityThreshold) return TriggerType.LIQUIDITY_DRAIN;
        if (riskMetrics.suspiciousTransactions > config.suspiciousActivityThreshold) return TriggerType.SUSPICIOUS_ACTIVITY;
        
        return TriggerType.TECHNICAL_FAILURE;
    }

    /**
     * @dev Generate trigger reason string
     */
    function _generateTriggerReason(TriggerType triggerType) internal pure returns (string memory) {
        if (triggerType == TriggerType.VOLUME_SPIKE) return "Abnormal trading volume detected";
        if (triggerType == TriggerType.PRICE_DEVIATION) return "Excessive price deviation detected";
        if (triggerType == TriggerType.LIQUIDITY_DRAIN) return "Critical liquidity level reached";
        if (triggerType == TriggerType.SUSPICIOUS_ACTIVITY) return "High suspicious activity detected";
        return "Technical failure or unknown risk";
    }

    /**
     * @dev Activate circuit breaker
     */
    function _activateCircuitBreaker(
        BreakerLevel level,
        TriggerType triggerType,
        string memory reason,
        address triggeredBy,
        bool isManual
    ) internal {
        currentState.currentLevel = level;
        currentState.activatedTime = block.timestamp;
        currentState.lastTriggerTime = block.timestamp;
        currentState.lastTriggerType = triggerType;
        currentState.lastTriggerReason = reason;
        currentState.triggerCount = currentState.triggerCount.add(1);
        currentState.manualOverride = isManual;
        currentState.triggeredBy = triggeredBy;

        // Create incident report
        _createIncidentReport(level, triggerType, reason, triggeredBy);

        // Pause contract if at RED or BLACK level
        if (level >= BreakerLevel.RED && !paused()) {
            _pause();
        }

        emit CircuitBreakerTriggered(level, triggerType, triggeredBy, reason);
    }

    /**
     * @dev Recover from circuit breaker
     */
    function recoverCircuitBreaker(BreakerLevel newLevel) external onlyEmergencyResponder {
        require(newLevel < currentState.currentLevel, "Cannot upgrade level during recovery");
        _recoverCircuitBreaker(newLevel, false);
    }

    /**
     * @dev Internal recovery function
     */
    function _recoverCircuitBreaker(BreakerLevel newLevel, bool isAutomatic) internal {
        BreakerLevel fromLevel = currentState.currentLevel;
        
        currentState.currentLevel = newLevel;
        currentState.manualOverride = !isAutomatic;

        // Unpause if recovering from RED/BLACK to lower levels
        if (fromLevel >= BreakerLevel.RED && newLevel < BreakerLevel.RED && paused()) {
            _unpause();
        }

        emit CircuitBreakerRecovered(fromLevel, newLevel, msg.sender, isAutomatic);
    }

    /**
     * @dev Check if automatic recovery is possible
     */
    function _canAutoRecover() internal view returns (bool) {
        if (currentState.manualOverride) return false;
        if (riskMetrics.riskScore > AUTO_RECOVERY_THRESHOLD) return false;
        
        BreakerConfig memory config = breakerConfigs[currentState.currentLevel];
        return block.timestamp >= currentState.activatedTime.add(config.cooldownPeriod);
    }

    /**
     * @dev Create incident report
     */
    function _createIncidentReport(
        BreakerLevel level,
        TriggerType triggerType,
        string memory description,
        address reporter
    ) internal {
        uint256 incidentId = incidentCounter++;
        
        incidentHistory.push(IncidentReport({
            id: incidentId,
            timestamp: block.timestamp,
            level: level,
            triggerType: triggerType,
            description: description,
            reporter: reporter,
            resolved: false,
            resolutionTime: 0,
            resolutionNotes: ""
        }));

        emit IncidentReported(incidentId, level, triggerType, description);
    }

    /**
     * @dev Resolve incident
     */
    function resolveIncident(uint256 incidentId, string calldata resolutionNotes) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        require(incidentId < incidentHistory.length, "Invalid incident ID");
        
        IncidentReport storage incident = incidentHistory[incidentId];
        require(!incident.resolved, "Incident already resolved");

        incident.resolved = true;
        incident.resolutionTime = block.timestamp;
        incident.resolutionNotes = resolutionNotes;

        emit IncidentResolved(incidentId, msg.sender, resolutionNotes);
    }

    /**
     * @dev Check if function is restricted
     */
    function _isFunctionRestricted(bytes4 functionSelector) internal view returns (bool) {
        return functionRestrictions[currentState.currentLevel][functionSelector];
    }

    /**
     * @dev Set function restriction for a breaker level
     */
    function setFunctionRestriction(
        BreakerLevel level,
        bytes4 functionSelector,
        bool restricted
    ) external onlyRole(ADMIN_ROLE) {
        functionRestrictions[level][functionSelector] = restricted;
    }

    /**
     * @dev Add emergency responder
     */
    function addEmergencyResponder(address responder) external onlyRole(ADMIN_ROLE) {
        emergencyResponders[responder] = true;
    }

    /**
     * @dev Remove emergency responder
     */
    function removeEmergencyResponder(address responder) external onlyRole(ADMIN_ROLE) {
        emergencyResponders[responder] = false;
    }

    /**
     * @dev Get current circuit breaker status
     */
    function getCircuitBreakerStatus() external view returns (
        BreakerLevel currentLevel,
        uint256 riskScore,
        bool isPaused,
        uint256 activatedTime,
        string memory lastReason
    ) {
        return (
            currentState.currentLevel,
            riskMetrics.riskScore,
            paused(),
            currentState.activatedTime,
            currentState.lastTriggerReason
        );
    }

    /**
     * @dev Get incident history
     */
    function getIncidentHistory() external view returns (IncidentReport[] memory) {
        return incidentHistory;
    }

    /**
     * @dev Get risk metrics
     */
    function getRiskMetrics() external view returns (RiskMetrics memory) {
        return riskMetrics;
    }

    // Admin functions
    function updateBreakerConfig(
        BreakerLevel level,
        BreakerConfig calldata config
    ) external onlyRole(ADMIN_ROLE) {
        breakerConfigs[level] = config;
    }

    function addProtectedContract(address contractAddr) external onlyRole(ADMIN_ROLE) {
        protectedContracts[contractAddr] = true;
    }

    function removeProtectedContract(address contractAddr) external onlyRole(ADMIN_ROLE) {
        protectedContracts[contractAddr] = false;
    }
}
