# Incident Response Simulator

A comprehensive cybersecurity training platform for practicing incident response in a safe, controlled environment. This platform provides interactive simulations, educational materials, and real-time security system demonstrations.

![Platform Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![Docker](https://img.shields.io/badge/docker-required-2496ED)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Training Modules](#training-modules)
- [System Demos](#system-demos)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Incident Response Simulator is an educational platform designed for cybersecurity students and professionals to develop critical incident response skills. The platform combines theoretical learning with hands-on practice through realistic attack simulations.

**Key Objectives:**
- Practice threat identification and response
- Analyze security logs and network traffic
- Make decisions under pressure
- Receive instant feedback and scoring
- Visualize security tools in action

---

## Features

### Training Modules
- **Live Simulations** - Real-time attack scenarios with scoring
- **Knowledge Quizzes** - Test cybersecurity knowledge
- **Log Analysis** - Practice identifying threats in logs
- **Advanced Scenarios** - Multi-stage attack simulations

### System Demonstrations
- **SIEM Dashboard** - Security Information and Event Management visualization
- **Network Traffic Analyzer** - Live packet capture and analysis

### Educational Content
- Comprehensive learning materials
- Threat identification guides
- Best practice documentation
- Incident response procedures

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┬─────────────────┬────────────────────┐   │
│  │   Learning   │  Training Center │   System Demos     │   │
│  │   Materials  │   (Interactive)  │  (Visualization)   │   │
│  └──────────────┴─────────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────┬─────────────────┬────────────────────┐   │
│  │   Scenario   │  Docker Service │   Scenario Engine  │   │
│  │   Manager    │  (Containers)   │   (Events/Scoring) │   │
│  └──────────────┴─────────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              Docker Containers (Simulated Network)           │
│  ┌──────────────┬─────────────────┬────────────────────┐   │
│  │   Victim     │    Attacker     │   Log Collector    │   │
│  │  Workstation │     Server      │   (SIEM-like)      │   │
│  └──────────────┴─────────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18 (via CDN)
- Tailwind CSS
- Vanilla JavaScript

**Backend:**
- Python 3.8+
- FastAPI
- Docker SDK for Python
- Pydantic (data validation)

**Infrastructure:**
- Docker & Docker Compose
- Ubuntu 20.04 containers
- Virtual network (172.20.0.0/16)

---

## Project Structure

```
incident-response-simulator/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI application
│   │   ├── models/
│   │   │   └── scenario.py              # Data models
│   │   ├── scenarios/
│   │   │   └── phishing_basic.py        # Scenario definitions
│   │   ├── services/
│   │   │   ├── docker_service.py        # Container management
│   │   │   └── scenario_engine.py       # Event/scoring engine
│   │   ├── data/                        # Training data
│   │   └── utils/                       # Helper functions
│   ├── requirements.txt                 # Python dependencies
│   └── tests/                           # Unit tests
│
├── frontend/
│   └── public/
│       ├── index.html                   # Homepage
│       ├── learning.html                # Learning materials
│       ├── simulator.html               # Training hub
│       ├── system_demos.html            # Demo hub
│       ├── simulation_dashboard.html    # Live simulation
│       ├── quiz.html                    # Quiz interface
│       ├── log_analyzer.html            # Log analysis
│       ├── siem_dashboard.html          # SIEM demo
│       └── network_traffic.html         # Network traffic demo
│
├── containers/
│   ├── attacker/                        # Attacker container files
│   │   ├── web/                         # Phishing pages
│   │   └── logs/
│   ├── victim/                          # Victim container files
│   │   ├── scripts/                     # Simulation scripts
│   │   └── logs/
│   └── siem/                            # Log collector files
│       ├── scripts/
│       └── logs/
│
├── docker-compose.yml                   # Container orchestration
├── logs/                                # Collected logs
├── docs/                                # Documentation
└── README.md                            # This file
```

---

## Installation

### Prerequisites

- **Operating System:** Ubuntu 20.04+ (or similar Linux)
- **Docker:** 20.10+
- **Docker Compose:** 1.29+
- **Python:** 3.8+
- **Git:** Latest version

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/incident-response-simulator.git
cd incident-response-simulator
```

### Step 2: Install Docker (if not installed)

```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER

# Restart session or run
newgrp docker
```

### Step 3: Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Start Docker Containers

```bash
# Return to project root
cd ..

# Start containers
docker-compose up -d

# Verify containers are running
docker ps
```

You should see 3 containers:
- `victim_workstation`
- `attacker_server`
- `log_collector`

### Step 5: Start Backend API

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: `http://localhost:8000`

### Step 6: Access Frontend

Open your browser and navigate to:
```
http://localhost:8000/
```

Or serve frontend separately:
```bash
cd frontend/public
python3 -m http.server 3000
```

Then visit: `http://localhost:3000`

---

## Usage

### Starting a Training Session

1. **Visit Homepage** - Navigate to `index.html`
2. **Choose Module:**
   - **Learning Materials** - Study before practicing
   - **Training Center** - Interactive exercises with scoring
   - **System Demos** - Visualize security tools

### Training Center Options

#### 1. Live Simulation
- Real-time incident response scenario
- Make decisions and receive instant feedback
- Scored based on correctness and response time

#### 2. Knowledge Quiz
- Multiple choice questions
- Covers various security topics
- Immediate scoring and explanations

#### 3. Log Analysis
- Analyze security logs
- Identify suspicious activity
- Practice pattern recognition

#### 4. Advanced Scenarios
- Multi-stage attack simulations
- Events appear gradually
- Comprehensive performance report

### System Demos

#### SIEM Dashboard
```
1. Click "Start Monitoring"
2. Observe security events in real-time
3. Filter by severity/source
4. Click events for details
```

#### Network Traffic Analyzer
```
1. Click "Start Capture"
2. Watch live packet capture
3. Filter by protocol
4. Inspect suspicious packets
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Core Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "services": {
    "api": "running",
    "docker": "available"
  }
}
```

#### List Scenarios
```http
GET /scenarios
```

Response:
```json
{
  "scenarios": [
    {
      "id": 1,
      "name": "Basic Phishing Attack",
      "type": "phishing",
      "difficulty": "beginner",
      "estimated_duration": 120
    }
  ],
  "count": 1
}
```

#### Start Scenario
```http
POST /scenarios/{scenario_id}/run
```

Response:
```json
{
  "session_id": "abc-123-def",
  "message": "Scenario started successfully",
  "status": "running"
}
```

#### Get Scenario Status
```http
GET /scenarios/{scenario_id}/status
```

#### Stop Scenario
```http
POST /scenarios/{scenario_id}/stop
```

#### Submit Response
```http
POST /scenarios/{scenario_id}/response
Content-Type: application/json

{
  "action": "isolate",
  "response_time": 45
}
```

Response:
```json
{
  "evaluation": {
    "is_correct": true,
    "score": 80,
    "feedback": ["Good choice!"],
    "recommendations": ["Consider faster response time"]
  }
}
```

### Advanced Scenario Endpoints

#### Start Complex Scenario
```http
POST /scenarios/complex/advanced_phishing/start
```

#### Get Events
```http
GET /scenarios/complex/{session_id}/events
```

#### Respond to Event
```http
POST /scenarios/complex/{session_id}/respond
Content-Type: application/json

{
  "event_id": "evt_001",
  "action": "isolate",
  "is_suspicious": true
}
```

#### Get Summary
```http
GET /scenarios/complex/{session_id}/summary
```

### Container Management

#### List Running Containers
```http
GET /containers
```

#### Get Container Logs
```http
GET /containers/{container_name}/logs?lines=50
```

#### Simulate Attack
```http
POST /scenarios/{scenario_id}/attack
```

---

## Training Modules

### 1. Basic Phishing Scenario

**Learning Objectives:**
- Identify phishing indicators
- Monitor suspicious network traffic
- Respond to credential theft
- Analyze security logs

**Scenario Flow:**
1. Victim receives phishing email
2. User clicks malicious link
3. Credentials harvested
4. Security alerts generated
5. Student responds to incident

**Evaluation Criteria:**
- Response correctness (50%)
- Response time (30%)
- Decision quality (20%)

### 2. Advanced Multi-Stage Attack

**Features:**
- 16 security events (mix of normal and suspicious)
- Events appear gradually (every 3-7 seconds)
- Student identifies and responds to each
- Comprehensive scoring report

**Event Types:**
- Normal operations (backups, logins)
- Port scanning
- DNS tunneling
- C2 beaconing
- Lateral movement
- Data exfiltration
- Ransomware

**Scoring:**
- Each event worth 50 points (25 for suspicion detection + 25 for correct action)
- Letter grade (A-F) based on overall accuracy
- Detailed feedback per event

---

## System Demos

### SIEM Dashboard Features
- Live event stream simulation
- Severity classification (Critical, High, Medium, Low, Info)
- Event statistics dashboard
- Search and filtering
- Event detail inspection

### Network Traffic Analyzer Features
- Live packet capture simulation
- Protocol filtering (TCP, UDP, HTTP, HTTPS, DNS)
- Automatic threat detection
- Packet inspection
- Traffic statistics

**Note:** Demos are visualization-only. For interactive training with scoring, use Training Center.

---

## Development

### Running in Development Mode

```bash
# Backend with hot reload
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (simple HTTP server)
cd frontend/public
python3 -m http.server 3000
```

### Adding New Scenarios

1. Create scenario file in `backend/app/scenarios/`
```python
from models.scenario import Scenario, ScenarioStep

def create_my_scenario() -> Scenario:
    # Define containers, steps, etc.
    pass
```

2. Register in `backend/app/main.py`
```python
from scenarios.my_scenario import MY_SCENARIO
scenarios_db.append(MY_SCENARIO)
```

### Testing

```bash
cd backend
pytest tests/
```

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Stop containers
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Clean up
docker-compose down -v
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Docker
DOCKER_NETWORK=ir_network
VICTIM_SSH_PORT=2222
ATTACKER_HTTP_PORT=9090
```

### CORS Configuration

Edit `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Containers Not Starting

```bash
# Check Docker status
sudo systemctl status docker

# View container logs
docker-compose logs

# Restart Docker service
sudo systemctl restart docker
```

### API Connection Errors

```bash
# Check if API is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status

# Allow port if needed
sudo ufw allow 8000
```

### Frontend Not Loading

```bash
# Check CORS settings in backend
# Verify frontend URL matches allowed origins

# Clear browser cache
# Try incognito/private window
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python:** Follow PEP 8
- **JavaScript:** Use ES6+ syntax
- **HTML/CSS:** Use Tailwind utility classes

### Commit Messages

```
feat: Add new scenario type
fix: Resolve container startup issue
docs: Update API documentation
style: Format code with black
refactor: Simplify scenario engine
test: Add unit tests for scoring
```

---

## Roadmap

- [ ] User authentication and progress tracking
- [ ] More attack scenarios (ransomware, DDoS, etc.)
- [ ] Leaderboard and achievements
- [ ] Export training reports (PDF)
- [ ] Multi-language support
- [ ] Mobile-responsive design improvements
- [ ] Integration with real SIEM tools
- [ ] CTF-style challenges

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with FastAPI and React
- Inspired by real-world incident response procedures
- Educational use only - not for production security

---

## Support

For questions or issues:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [docs/](docs/)

---

## Authors

- **Your Name** - Initial development

---

**⚠️ Disclaimer:** This platform is for educational purposes only. Do not use techniques learned here for unauthorized access to systems. Always practice ethical hacking and obtain proper authorization before testing security systems.
