from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn
from datetime import datetime
import json
import uuid

# יבוא המודלים שלנו - עם relative imports
from models.scenario import Scenario, ScenarioSession, ScenarioCreate, ScenarioStatus
from scenarios.phishing_basic import BASIC_PHISHING_SCENARIO
from services.docker_service import DockerService
from services.scenario_engine import ScenarioEngine

# יצירת אפליקציית FastAPI
app = FastAPI(
    title="Incident Response Simulator API", 
    description="API for managing cybersecurity incident response simulations",
    version="1.0.0"
)

# הוספת CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# זיכרון זמני לתרחישים (בהמשך נחליף למסד נתונים)
scenarios_db = [BASIC_PHISHING_SCENARIO]  # התחלנו עם תרחיש אחד
active_scenarios = {}

# יצירת שירות Docker ומנגנון התרחישים
docker_service = DockerService()
scenario_engine = ScenarioEngine()

@app.get("/")
async def root():
    """נקודת הכניסה הראשית - בדיקה שה-API עובד"""
    return {
        "message": "Incident Response Simulator API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """בדיקת בריאות המערכת"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "not_implemented",
            "docker": "available" if docker_service.client else "unavailable"
        }
    }

@app.get("/scenarios")
async def get_scenarios():
    """קבלת רשימת כל התרחישים"""
    scenarios_list = []
    for i, scenario in enumerate(scenarios_db, 1):
        scenarios_list.append({
            "id": i,
            "name": scenario.name,
            "description": scenario.description,
            "type": scenario.type,
            "difficulty": scenario.difficulty,
            "estimated_duration": scenario.estimated_duration,
            "status": scenario.status
        })
    
    return {
        "scenarios": scenarios_list,
        "count": len(scenarios_db),
        "active_scenarios": len(active_scenarios)
    }

@app.post("/scenarios")
async def create_scenario(scenario_data: Dict[str, Any]):
    """יצירת תרחיש חדש"""
    # בדיקות בסיסיות
    if not scenario_data.get("name"):
        raise HTTPException(status_code=400, detail="Scenario name is required")
    
    # יצירת ID ייחודי
    scenario_id = len(scenarios_db) + 1
    
    # יצירת תרחיש
    new_scenario = {
        "id": scenario_id,
        "name": scenario_data["name"],
        "description": scenario_data.get("description", ""),
        "type": scenario_data.get("type", "basic"),
        "created_at": datetime.now().isoformat(),
        "status": "ready",
        "containers": scenario_data.get("containers", [])
    }
    
    return {
        "message": "Scenario created successfully",
        "scenario": new_scenario
    }

@app.post("/scenarios/{scenario_id}/run")
async def run_scenario(scenario_id: int):
    """הרצת תרחיש"""
    # חיפוש התרחיש
    if scenario_id < 1 or scenario_id > len(scenarios_db):
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    scenario = scenarios_db[scenario_id - 1]  # רשימה מתחילה מ-0
    
    # בדיקה שהתרחיש לא רץ כבר
    if scenario_id in active_scenarios:
        raise HTTPException(status_code=400, detail="Scenario already running")
    
    # יצירת session ID ייחודי
    session_id = str(uuid.uuid4())
    
    # יצירת session חדש
    session = ScenarioSession(
        session_id=session_id,
        scenario_id=scenario_id,
        started_at=datetime.now(),
        status=ScenarioStatus.RUNNING,
        current_step=0,
        logs=[],
        user_actions=[],
        alerts=[]
    )
    
    active_scenarios[scenario_id] = session
    
    # הפעלת containers אמיתיים
    docker_result = docker_service.start_scenario_containers(scenario_id)
    
    # הוספת לוג ראשוני
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": f"Starting scenario: {scenario.name}",
        "source": "orchestrator"
    })
    
    # הוספת לוג של הפעלת containers
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO" if docker_result["status"] == "success" else "ERROR",
        "message": f"Docker containers: {docker_result['message']}",
        "source": "docker_service",
        "details": docker_result
    })
    
    return {
        "message": f"Scenario '{scenario.name}' started successfully",
        "session_id": session_id,
        "scenario": {
            "name": scenario.name,
            "type": scenario.type,
            "estimated_duration": scenario.estimated_duration,
            "steps": len(scenario.steps)
        },
        "docker_status": docker_result,
        "status": session.status
    }

@app.get("/scenarios/{scenario_id}/status")
async def get_scenario_status(scenario_id: int):
    """בדיקת סטטוס תרחיש"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    return active_scenarios[scenario_id]

@app.post("/scenarios/{scenario_id}/stop")
async def stop_scenario(scenario_id: int):
    """עצירת תרחיש"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    # עצירת containers
    docker_result = docker_service.stop_scenario_containers()
    
    # עצירת התרחיש
    session = active_scenarios.pop(scenario_id)
    session.status = ScenarioStatus.STOPPED
    
    # הוספת לוג סיום
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO", 
        "message": "Scenario stopped by user",
        "source": "orchestrator"
    })
    
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO" if docker_result["status"] == "success" else "ERROR",
        "message": f"Docker containers: {docker_result['message']}",
        "source": "docker_service"
    })
    
    return {
        "message": "Scenario stopped successfully",
        "docker_status": docker_result,
        "session": session
    }

@app.get("/containers")
async def get_containers():
    """קבלת מידע על containers רצים"""
    containers = docker_service.get_running_containers()
    return {
        "containers": containers,
        "count": len(containers),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/containers/{container_name}/logs")
async def get_container_logs(container_name: str, lines: int = 50):
    """קבלת לוגים מcontainer ספציפי"""
    result = docker_service.get_container_logs(container_name, lines)
    return result

@app.post("/scenarios/{scenario_id}/attack")
async def simulate_attack(scenario_id: int):
    """הרצת סימולציית התקפה"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    session = active_scenarios[scenario_id]
    
    # הרצת סימולציית דיוג
    attack_steps = docker_service.simulate_phishing_attack()
    
    # הוספת התקפה ללוגים
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "WARNING",
        "message": "Phishing attack simulation started",
        "source": "attack_simulator",
        "details": attack_steps
    })
    
    return {
        "message": "Attack simulation completed",
        "scenario_id": scenario_id,
        "attack_steps": attack_steps,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/scenarios/{scenario_id}/response")
async def submit_response(scenario_id: int, response_data: Dict[str, Any]):
    """קבלת תגובת התלמיד והחזרת משוב"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    session = active_scenarios[scenario_id]
    action = response_data.get("action")
    response_time = response_data.get("response_time", 0)
    
    # הגדרת תגובות נכונות לפי התרחיש
    correct_responses = {
        "phishing": ["isolate", "block_ip"],  # תגובות מתאימות לדיוג
        "malware": ["isolate", "escalate"],
        "basic": ["monitor", "isolate"]
    }
    
    scenario_type = "phishing"  # כרגע יש לנו רק תרחיש אחד
    is_correct = action in correct_responses.get(scenario_type, [])
    
    # חישוב ציון לפי זמן תגובה ונכונות
    score = 0
    feedback = []
    
    if is_correct:
        score += 50  # נקודות על תגובה נכונה
        feedback.append(f"בחירה טובה! '{action}' היא תגובה מתאימה למתקפת דיוג.")
    else:
        feedback.append(f"'{action}' אינה התגובה האופטימלית למתקפת דיוג.")
    
    # ציון לפי זמן תגובה
    if response_time <= 60:  # תגובה מהירה
        score += 30
        feedback.append("זמן תגובה מצוין - מתחת לדקה!")
    elif response_time <= 120:  # תגובה סבירה
        score += 20
        feedback.append("זמן תגובה סביר - 1-2 דקות.")
    elif response_time <= 300:  # תגובה איטית
        score += 10
        feedback.append("זמן תגובה איטי - במקרה אמיתי זה עלול להיות קריטי.")
    else:
        feedback.append("זמן תגובה איטי מדי - יש לשפר זמני תגובה.")
    
    # הוספת המלצות ספציפיות
    recommendations = []
    if action == "monitor":
        if scenario_type == "phishing":
            recommendations.append("במקרה של דיוג מתקדם, ניטור לבד אינו מספיק - כדאי לשקול בידוד.")
    elif action == "escalate":
        if response_time > 120:
            recommendations.append("הסלמה טובה, אבל כדאי לעשות צעדי חירום קודם.")
    elif action == "isolate":
        recommendations.append("בידוד הוא צעד טוב כדי למנוע התפשטות נוספת.")
    elif action == "block_ip":
        recommendations.append("חסימת IP מתאימה למניעת גישה למקור התקיפה.")
    
    # רישום התגובה בsession
    session.user_actions.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "response_time": response_time,
        "score": score,
        "is_correct": is_correct
    })
    
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": f"Student response: {action} (response time: {response_time}s)",
        "source": "student_interface"
    })
    
    return {
        "message": "Response received successfully",
        "evaluation": {
            "action": action,
            "is_correct": is_correct,
            "score": score,
            "max_score": 80,
            "response_time": response_time,
            "feedback": feedback,
            "recommendations": recommendations
        },
        "scenario_status": "completed" if action in ["isolate", "escalate"] else "ongoing",
        "timestamp": datetime.now().isoformat()
    }

# ===== התרחישים המורכבים החדשים =====

@app.post("/scenarios/complex/{scenario_id}/start")
async def start_complex_scenario(scenario_id: str):
    """התחלת תרחיש מורכב"""
    session_id = str(uuid.uuid4())
    
    result = await scenario_engine.start_scenario(session_id, scenario_id)
    
    if result["status"] == "success":
        return {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "scenario_name": result["scenario_name"],
            "total_events": result["total_events"],
            "message": "Complex scenario started successfully"
        }
    else:
        raise HTTPException(status_code=404, detail=result["message"])

@app.get("/scenarios/complex/{session_id}/events")
async def get_scenario_events(session_id: str):
    """קבלת אירועים עדכניים מהתרחיש"""
    events = scenario_engine.get_session_events(session_id)
    
    return {
        "session_id": session_id,
        "events": events,
        "count": len(events),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/scenarios/complex/{session_id}/respond")
async def respond_to_event(session_id: str, response_data: Dict[str, Any]):
    """תגובת התלמיד לאירוע ספציפי"""
    event_id = response_data.get("event_id")
    action = response_data.get("action")
    is_suspicious = response_data.get("is_suspicious", False)
    
    if not event_id or not action:
        raise HTTPException(status_code=400, detail="event_id and action are required")
    
    result = scenario_engine.submit_student_response(session_id, event_id, action, is_suspicious)
    
    if result["status"] == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])

@app.get("/scenarios/complex/{session_id}/summary")
async def get_scenario_summary(session_id: str):
    """סיכום ביצועי התלמיד"""
    summary = scenario_engine.get_session_summary(session_id)
    
    if "status" in summary and summary["status"] == "error":
        raise HTTPException(status_code=404, detail=summary["message"])
    
    return summary

@app.get("/scenarios/complex/available")
async def get_available_complex_scenarios():
    """רשימת תרחישים מורכבים זמינים"""
    return {
        "scenarios": [
            {
                "scenario_id": "advanced_phishing",
                "name": "Advanced Multi-Stage Attack",
                "description": "Complex phishing attack that escalates to lateral movement and data exfiltration",
                "total_events": 16,
                "difficulty": "intermediate"
            }
        ],
        "count": 1
    }

if __name__ == "__main__":
    # הרצת השרת
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # אפשר hot reload בזמן פיתוח
    )
