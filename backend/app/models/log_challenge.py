from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ThreatType(str, Enum):
    BRUTE_FORCE = "brute_force"
    PORT_SCAN = "port_scan"
    MALWARE = "malware"
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_PROCESS = "suspicious_process"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DNS_TUNNELING = "dns_tunneling"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PHISHING = "phishing"

class LogLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ThreatIndicator(BaseModel):
    line_number: int
    threat_type: ThreatType
    severity: str  # low, medium, high, critical
    description: str
    evidence: str
    mitigation: str

class LogChallenge(BaseModel):
    level: LogLevel
    title: str
    description: str
    total_lines: int
    total_threats: int
    threat_indicators: List[ThreatIndicator]
    time_limit_minutes: int
    passing_score: int  # percentage

class UserFinding(BaseModel):
    line_number: int
    threat_type: ThreatType
    confidence: str  # low, medium, high
    notes: Optional[str] = None

class LogSubmission(BaseModel):
    level: LogLevel
    findings: List[UserFinding]
    time_taken_seconds: int

class FindingEvaluation(BaseModel):
    line_number: int
    user_threat_type: ThreatType
    is_correct: bool
    is_false_positive: bool
    actual_threat_type: Optional[ThreatType]
    points_earned: int
    feedback: str

class LogChallengeResult(BaseModel):
    level: LogLevel
    total_threats: int
    threats_found: int
    threats_missed: int
    false_positives: int
    accuracy_percentage: float
    score: int
    max_score: int
    time_taken: str
    passed: bool
    evaluations: List[FindingEvaluation]
    missed_threats: List[ThreatIndicator]
    summary_feedback: str
    recommendations: List[str]
