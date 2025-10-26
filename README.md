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


---

## Labs & Exercises (added)

This project includes interactive learning labs and attack exercises implemented in the `frontend/public` pages and in the `containers/` images. I inspected the repository and found the following practical exercises and attacker pages — they are ready-to-use and documented briefly here so users can run them and learn safely.

### 1) Password Cracking Lab (`frontend/public/password_cracking.html`, `hashcrack_lab` service)
**What it is:** a hands-on lab that demonstrates password hashing and cracking techniques. The lab contains sample hash files and a wordlist (e.g. `rockyou.txt`) mounted into the `hashcrack_lab` container.  
**Learning goals:**
- Understand common hash algorithms (MD5, SHA1, SHA256) and why salts matter.
- Practice using wordlists and offline cracking tools (e.g., `john`, `hashcat`) to recover weak passwords.
- Learn defensive lessons: password policies, hashing with salt & stretching.

**How to use:**
1. Start the environment (see *Run the simulator* below).
2. Open the Password Cracking page in your browser — the frontend HTML file is `frontend/public/password_cracking.html`. The project may serve the frontend statically; if using the provided `package.json` dev script it can also be served with `python3 -m http.server 3000` from the `frontend` directory.
3. Inside the container `hashcrack_lab` you will find `/wordlists/rockyou.txt` and sample hashes under `/hashes/`. Try cracking with your preferred tool or follow the on-page instructions.

> Note: The lab is intentionally educational — it uses sample, non-sensitive data.

---

### 2) Privilege Escalation Lab (`frontend/public/privilege_escalation.html`, `privesc_lab` service)
**What it is:** a simulated Linux victim that contains intentional misconfigurations (SUID binaries, weak sudo rules, leftover credentials) to teach privilege escalation techniques.  
**Learning goals:**
- Identify common privilege escalation vectors on Linux.
- Practice safe exploitation in a containerized lab environment.
- Learn to remediate issues (remove SUID bits, tighten sudoers, update packages).

**How to use:**
1. Start the environment (see *Run the simulator* below).
2. Access the Privilege Escalation page: `frontend/public/privilege_escalation.html`.
3. Connect to the `privesc_lab` container (e.g., `docker exec -it <privesc_container> bash`) and follow the steps on the page to practice enumerating the system and exploiting misconfigurations.

---

### 3) Phishing / Attacker Pages (`containers/attacker/web/*.html`)
**What it is:** small static pages used to demonstrate phishing tactics and credential-harvesting techniques (fake login pages). These files are in `containers/attacker/web/` and are intentionally simple educational examples (e.g. `fake_login.html`).  
**Learning goals:**
- Recognize social-engineering patterns in phishing pages (urgency, spoofed UI).
- Learn how credential harvesting works and how logs may show attempted credential submissions.
- Understand defenses: email filtering, URL inspection, 2FA, user training.

**Important:** These pages are for training only. Do **not** use them against real targets or on public-facing systems without authorization.

---

## Learning Pages (`frontend/public/learning.html`)

A self-contained learning center page (`frontend/public/learning.html`) provides written background on key topics such as:
- Incident response process and playbooks.
- Common attack techniques (reconnaissance, exploitation, persistence).
- Defensive controls and mitigation best practices.
- Career paths and how to progress from SOC analyst → pentester etc.

These pages are best viewed in a browser. They are static React-based pages bundled in `frontend/public/`.

---

## How to run the simulator (recommended)

This repository includes a `docker-compose.yml` that builds and runs the simulated environment (victim, attacker, labs, logging). The project assumes you have Docker and Docker Compose installed.

1. Clone the repo (or extract the provided ZIP) and change directory:
```bash
cd incident-response-simulator.-main
```

2. Build and run all services:
```bash
docker-compose up --build
```
This command will create the containers defined in `docker-compose.yml` (for example: `victim_workstation`, `hashcrack_lab`, `privesc_lab`, `attacker_server`, `log_collector`). The compose file also declares a bridge network `ir_network` so containers can communicate.

3. Check ports and endpoints:
- The victim workstation web UI is typically mapped to port **8080** (see `docker-compose.yml` for exact mappings).
- A static frontend or attacker web server may be mapped to other ports (check the `ports:` sections in `docker-compose.yml`). You can confirm actual host ports with:
```bash
docker-compose ps
```
or
```bash
docker ps --format "table {.Names}\t{.Ports}"
```

4. Access the learning pages and labs:
- Open the Password Cracking lab page: `frontend/public/password_cracking.html` served from the frontend host or via `http://localhost:8080/password_cracking.html` depending on your configuration.
- Open the Privilege Escalation lab page: `frontend/public/privilege_escalation.html`.
- Open the Learning Center: `frontend/public/learning.html`.

If you prefer to serve the frontend locally without Docker:
```bash
cd frontend
# quick static server (already included in package.json)
python3 -m http.server 3000
# then browse http://localhost:3000/password_cracking.html
```

---

## Security & Usage Notice

This repository is meant for **learning in a controlled environment** only. Never run these labs in a production environment or against systems you do not own/are not authorized to test. Always follow institutional and legal rules when performing security exercises.

---

## Troubleshooting tips

- If Docker fails to start a service, inspect logs:
```bash
docker-compose logs <service_name>
```
- If a page doesn't load, confirm host port mappings with `docker ps`.
- If wordlists or sample hashes are missing, inspect the container volumes and the `hashes/` and `wordlists/` folders.

---

## Short GitHub description (for "About" / repo short description)

**Incident Response Simulator — hands-on cybersecurity training platform with password‑cracking, privilege‑escalation and phishing exercises, designed for safe learning and teaching.**
