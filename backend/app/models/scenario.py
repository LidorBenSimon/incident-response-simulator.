from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ScenarioType(str, Enum):
    PHISHING = "phishing"
    MALWARE = "malware"
    PORT_SCAN = "port_scan"
    RANSOMWARE = "ransomware"
    DDoS = "ddos"

class ScenarioStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class ContainerConfig(BaseModel):
    name: str
    image: str
    ports: Optional[Dict[str, int]] = {}
    environment: Optional[Dict[str, str]] = {}
    commands: Optional[List[str]] = []

class ScenarioStep(BaseModel):
    step_id: int
    name: str
    description: str
    duration_seconds: int
    commands: List[str]
    expected_logs: List[str]

class Scenario(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    type: ScenarioType
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    estimated_duration: int = 300  # seconds
    containers: List[ContainerConfig] = []
    steps: List[ScenarioStep] = []
    learning_objectives: List[str] = []
    created_at: Optional[datetime] = None
    status: ScenarioStatus = ScenarioStatus.READY

class ScenarioSession(BaseModel):
    session_id: str
    scenario_id: int
    started_at: datetime
    status: ScenarioStatus
    current_step: int = 0
    logs: List[Dict[str, Any]] = []
    user_actions: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    
class ScenarioCreate(BaseModel):
    name: str
    description: str
    type: ScenarioType
    difficulty: str = "beginner"
    containers: List[ContainerConfig] = []
    steps: List[ScenarioStep] = []
    learning_objectives: List[str] = []
