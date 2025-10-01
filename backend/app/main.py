from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn
from datetime import datetime
import json
import uuid

# Import existing models and services
from models.scenario import Scenario, ScenarioSession, ScenarioCreate, ScenarioStatus
from scenarios.phishing_basic import BASIC_PHISHING_SCENARIO
from services.docker_service import DockerService
from services.scenario_engine import ScenarioEngine

# Import new quiz models and data
from models.quiz_model import QuizSubmission, QuizSummary, QuizResult
from data.quiz_questions import get_all_quiz_questions, get_question_by_id

# Create FastAPI app
app = FastAPI(
    title="Incident Response Simulator API", 
    description="API for managing cybersecurity incident response simulations and quizzes",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500", "*"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage (later replace with database)
scenarios_db = [BASIC_PHISHING_SCENARIO]
active_scenarios = {}
quiz_sessions = {}  # Store quiz session data

# Services
docker_service = DockerService()
scenario_engine = ScenarioEngine()

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Incident Response Simulator API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": ["simulations", "quizzes", "learning"]
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "not_implemented",
            "docker": "available" if docker_service.client else "unavailable"
        }
    }

# ===== EXISTING SCENARIO ENDPOINTS =====

@app.get("/scenarios")
async def get_scenarios():
    """Get all available scenarios"""
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

@app.post("/scenarios/{scenario_id}/run")
async def run_scenario(scenario_id: int):
    """Start a scenario simulation"""
    if scenario_id < 1 or scenario_id > len(scenarios_db):
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    scenario = scenarios_db[scenario_id - 1]
    
    if scenario_id in active_scenarios:
        raise HTTPException(status_code=400, detail="Scenario already running")
    
    session_id = str(uuid.uuid4())
    
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
    
    docker_result = docker_service.start_scenario_containers(scenario_id)
    
    session.logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": f"Starting scenario: {scenario.name}",
        "source": "orchestrator"
    })
    
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
    """Get scenario status"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    return active_scenarios[scenario_id]

@app.post("/scenarios/{scenario_id}/stop")
async def stop_scenario(scenario_id: int):
    """Stop a running scenario"""
    if scenario_id not in active_scenarios:
        raise HTTPException(status_code=404, detail="Scenario not running")
    
    docker_result = docker_service.stop_scenario_containers()
    
    session = active_scenarios.pop(scenario_id)
    session.status = ScenarioStatus.STOPPED
    
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

# ===== COMPLEX SCENARIO ENDPOINTS =====

@app.post("/scenarios/complex/{scenario_id}/start")
async def start_complex_scenario(scenario_id: str):
    """Start a complex scenario"""
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
    """Get current events from scenario"""
    events = scenario_engine.get_session_events(session_id)
    
    return {
        "session_id": session_id,
        "events": events,
        "count": len(events),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/scenarios/complex/{session_id}/respond")
async def respond_to_event(session_id: str, response_data: Dict[str, Any]):
    """Submit student response to an event"""
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
    """Get scenario performance summary"""
    summary = scenario_engine.get_session_summary(session_id)
    
    if "status" in summary and summary["status"] == "error":
        raise HTTPException(status_code=404, detail=summary["message"])
    
    return summary

@app.get("/scenarios/complex/available")
async def get_available_complex_scenarios():
    """Get list of available complex scenarios"""
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

# ===== NEW QUIZ ENDPOINTS =====

@app.get("/quiz/questions")
async def get_quiz_questions():
    """Get all quiz questions (without showing correct answers)"""
    questions = get_all_quiz_questions()
    
    # Format questions for frontend (hide correct answer info)
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "question_id": q.question_id,
            "question_text": q.question_text,
            "options": [
                {
                    "option_id": opt.option_id,
                    "text": opt.text
                    # Don't include is_correct field
                }
                for opt in q.options
            ],
            "category": q.category
        })
    
    return {
        "questions": formatted_questions,
        "total": len(formatted_questions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/quiz/submit")
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results with feedback"""
    
    results = []
    correct_count = 0
    category_stats = {}
    
    # Evaluate each answer
    for answer in submission.answers:
        question = get_question_by_id(answer.question_id)
        
        if not question:
            continue
        
        # Find correct option
        correct_option = None
        for opt in question.options:
            if opt.is_correct:
                correct_option = opt.option_id
                break
        
        # Check if answer is correct
        is_correct = (answer.selected_option == correct_option)
        if is_correct:
            correct_count += 1
        
        # Track category statistics
        if question.category not in category_stats:
            category_stats[question.category] = {"correct": 0, "total": 0}
        
        category_stats[question.category]["total"] += 1
        if is_correct:
            category_stats[question.category]["correct"] += 1
        
        # Add to results
        results.append(QuizResult(
            question_id=question.question_id,
            question_text=question.question_text,
            selected_option=answer.selected_option,
            correct_option=correct_option,
            is_correct=is_correct,
            explanation=question.explanation,
            category=question.category
        ))
    
    # Calculate score
    total_questions = len(submission.answers)
    score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # Determine letter grade
    if score_percentage >= 90:
        letter_grade = "A"
    elif score_percentage >= 80:
        letter_grade = "B"
    elif score_percentage >= 70:
        letter_grade = "C"
    elif score_percentage >= 60:
        letter_grade = "D"
    else:
        letter_grade = "F"
    
    # Generate recommendations
    recommendations = []
    
    if score_percentage >= 90:
        recommendations.append("Excellent performance! You have a strong understanding of incident response concepts.")
        recommendations.append("Consider trying the advanced simulation scenarios to further challenge your skills.")
    elif score_percentage >= 70:
        recommendations.append("Good job! You have a solid foundation in incident response.")
        recommendations.append("Review the topics where you had incorrect answers to strengthen your knowledge.")
    else:
        recommendations.append("We recommend reviewing the learning materials in the Learning Center.")
        recommendations.append("Focus especially on the topics where you had the most difficulty.")
    
    # Category-specific recommendations
    for category, stats in category_stats.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        if accuracy < 70:
            category_names = {
                "phishing": "Phishing Attacks",
                "malware": "Malware Detection",
                "incident_response": "Incident Response Procedures",
                "forensics": "Digital Forensics"
            }
            recommendations.append(
                f"Consider reviewing the '{category_names.get(category, category)}' topic in the Learning Center."
            )
    
    # Create summary
    summary = QuizSummary(
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=round(score_percentage, 1),
        letter_grade=letter_grade,
        results=results,
        category_breakdown=category_stats,
        recommendations=recommendations
    )
    
    return summary

@app.get("/quiz/categories")
async def get_quiz_categories():
    """Get quiz question categories and their counts"""
    questions = get_all_quiz_questions()
    
    categories = {}
    for q in questions:
        if q.category not in categories:
            categories[q.category] = 0
        categories[q.category] += 1
    
    return {
        "categories": categories,
        "total_questions": len(questions)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
