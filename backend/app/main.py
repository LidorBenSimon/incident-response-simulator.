from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn
from datetime import datetime
import json
import uuid
import os

# Existing imports
from models.scenario import Scenario, ScenarioSession, ScenarioCreate, ScenarioStatus
from scenarios.phishing_basic import BASIC_PHISHING_SCENARIO
from services.docker_service import DockerService
from services.scenario_engine import ScenarioEngine

# Quiz imports
from models.quiz_model import QuizSubmission, QuizSummary, QuizResult
from data.quiz_questions import get_all_quiz_questions, get_question_by_id

# NEW: Log Challenge imports
from models.log_challenge import LogLevel, LogSubmission, LogChallengeResult, FindingEvaluation, UserFinding, ThreatType
from data.logs.log_challenges_data import get_challenge_by_level

# Create FastAPI app
app = FastAPI(
    title="Incident Response Simulator API", 
    description="API for managing cybersecurity incident response simulations, quizzes, and log analysis",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage
scenarios_db = [BASIC_PHISHING_SCENARIO]
active_scenarios = {}
quiz_sessions = {}
log_sessions = {}

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
        "version": "3.0.0",
        "features": ["simulations", "quizzes", "log_analysis"]
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

# ===== SCENARIO ENDPOINTS (existing) =====

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

# ===== QUIZ ENDPOINTS (existing) =====

@app.get("/quiz/questions")
async def get_quiz_questions():
    """Get all quiz questions (without showing correct answers)"""
    questions = get_all_quiz_questions()
    
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "question_id": q.question_id,
            "question_text": q.question_text,
            "options": [
                {
                    "option_id": opt.option_id,
                    "text": opt.text
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
    
    for answer in submission.answers:
        question = get_question_by_id(answer.question_id)
        
        if not question:
            continue
        
        correct_option = None
        for opt in question.options:
            if opt.is_correct:
                correct_option = opt.option_id
                break
        
        is_correct = (answer.selected_option == correct_option)
        if is_correct:
            correct_count += 1
        
        if question.category not in category_stats:
            category_stats[question.category] = {"correct": 0, "total": 0}
        
        category_stats[question.category]["total"] += 1
        if is_correct:
            category_stats[question.category]["correct"] += 1
        
        results.append(QuizResult(
            question_id=question.question_id,
            question_text=question.question_text,
            selected_option=answer.selected_option,
            correct_option=correct_option,
            is_correct=is_correct,
            explanation=question.explanation,
            category=question.category
        ))
    
    total_questions = len(submission.answers)
    score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
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

# ===== NEW: LOG ANALYSIS CHALLENGE ENDPOINTS =====

@app.get("/log-challenge/levels")
async def get_log_challenge_levels():
    """Get available log challenge levels"""
    return {
        "levels": [
            {
                "level": "basic",
                "title": "Basic Log Analysis",
                "description": "Introduction to threat detection with clear attack patterns",
                "total_lines": 200,
                "total_threats": 8,
                "time_limit_minutes": 15,
                "difficulty": "Beginner",
                "recommended_for": "New SOC analysts and students"
            },
            {
                "level": "intermediate",
                "title": "Intermediate Log Analysis",
                "description": "Mixed traffic with subtle threats requiring pattern analysis",
                "total_lines": 500,
                "total_threats": 12,
                "time_limit_minutes": 25,
                "difficulty": "Intermediate",
                "recommended_for": "Analysts with basic experience"
            },
            {
                "level": "advanced",
                "title": "Advanced APT Detection",
                "description": "Enterprise logs with APT campaign and false positives",
                "total_lines": 1000,
                "total_threats": 18,
                "time_limit_minutes": 40,
                "difficulty": "Advanced",
                "recommended_for": "Senior analysts and threat hunters"
            }
        ]
    }

@app.get("/log-challenge/{level}/logs")
async def get_log_file(level: str):
    """Get log file content for a specific level"""
    try:
        log_level = LogLevel(level.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid level. Use: basic, intermediate, or advanced")
    
    # Get challenge info
    challenge = get_challenge_by_level(log_level)
    
    # Get absolute path to log file
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    level_num = 1 if log_level == LogLevel.BASIC else 2 if log_level == LogLevel.INTERMEDIATE else 3
    log_file_path = os.path.join(base_dir, "data", "logs", f"level{level_num}_{level.lower()}.log")
    
    try:
        with open(log_file_path, 'r') as f:
            log_content = f.read()
        
        lines = log_content.strip().split('\n')
        
        return {
            "level": level,
            "title": challenge.title,
            "description": challenge.description,
            "total_lines": len(lines),
            "total_threats": challenge.total_threats,
            "time_limit_minutes": challenge.time_limit_minutes,
            "passing_score": challenge.passing_score,
            "lines": lines,
            "timestamp": datetime.now().isoformat()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Log file not found at: {log_file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")
@app.post("/log-challenge/submit")
async def submit_log_analysis(submission: LogSubmission):
    """Submit log analysis findings and get detailed feedback"""
    
    # Get challenge configuration
    challenge = get_challenge_by_level(submission.level)
    
    if not challenge:
        raise HTTPException(status_code=400, detail="Invalid challenge level")
    
    # Create a map of actual threats by line number
    actual_threats_map = {threat.line_number: threat for threat in challenge.threat_indicators}
    
    evaluations = []
    threats_found = 0
    threats_missed = 0
    false_positives = 0
    total_points = 0
    max_points = challenge.total_threats * 10  # 10 points per threat
    
    # Track which threats were found
    found_threat_lines = set()
    
    # Evaluate each user finding
    for finding in submission.findings:
        line_num = finding.line_number
        user_threat_type = finding.threat_type
        
        if line_num in actual_threats_map:
            # This line has an actual threat
            actual_threat = actual_threats_map[line_num]
            
            if user_threat_type == actual_threat.threat_type:
                # Correct identification
                is_correct = True
                points = 10
                threats_found += 1
                found_threat_lines.add(line_num)
                feedback = f"✓ Correct! {actual_threat.description}. {actual_threat.mitigation}"
            else:
                # Wrong threat type
                is_correct = False
                points = 3  # Partial credit for finding the right line
                feedback = f"Partially correct. You identified a threat on this line, but classified it as {user_threat_type.value} instead of {actual_threat.threat_type.value}. {actual_threat.description}"
            
            evaluations.append(FindingEvaluation(
                line_number=line_num,
                user_threat_type=user_threat_type,
                is_correct=is_correct,
                is_false_positive=False,
                actual_threat_type=actual_threat.threat_type,
                points_earned=points,
                feedback=feedback
            ))
            total_points += points
        else:
            # False positive - no threat on this line
            false_positives += 1
            evaluations.append(FindingEvaluation(
                line_number=line_num,
                user_threat_type=user_threat_type,
                is_correct=False,
                is_false_positive=True,
                actual_threat_type=None,
                points_earned=-2,  # Penalty for false positive
                feedback=f"✗ False positive. This line contains normal activity, not a {user_threat_type.value} threat. Be more careful with threat identification to avoid alert fatigue."
            ))
            total_points -= 2
    
    # Identify missed threats
    missed_threats = []
    for threat in challenge.threat_indicators:
        if threat.line_number not in found_threat_lines:
            threats_missed += 1
            missed_threats.append(threat)
    
    # Calculate accuracy
    if challenge.total_threats > 0:
        accuracy = (threats_found / challenge.total_threats) * 100
    else:
        accuracy = 0
    
    # Calculate final score (0-100)
    score = max(0, min(100, (total_points / max_points) * 100))
    
    # Determine if passed
    passed = score >= challenge.passing_score
    
    # Generate summary feedback
    if score >= 90:
        summary_feedback = "Outstanding performance! You demonstrated expert-level log analysis skills and identified threats with high accuracy."
    elif score >= 80:
        summary_feedback = "Excellent work! You showed strong threat detection capabilities with good attention to detail."
    elif score >= 70:
        summary_feedback = "Good job! You identified most threats correctly, but review the missed items to improve your analysis."
    elif score >= 60:
        summary_feedback = "Fair performance. You need more practice with threat patterns and reducing false positives."
    else:
        summary_feedback = "More training needed. Focus on learning common threat indicators and improving pattern recognition."
    
    # Generate recommendations
    recommendations = []
    
    if threats_missed > challenge.total_threats * 0.3:
        recommendations.append("You missed several threats. Review common attack patterns like brute force, port scans, and data exfiltration indicators.")
    
    if false_positives > 3:
        recommendations.append("Too many false positives detected. Learn to distinguish between normal operations and actual threats to avoid alert fatigue.")
    
    if threats_found > 0 and threats_found < challenge.total_threats * 0.5:
        recommendations.append("Focus on improving threat detection rate. Study SIEM rules and common IOCs (Indicators of Compromise).")
    
    # Format time taken
    minutes = submission.time_taken_seconds // 60
    seconds = submission.time_taken_seconds % 60
    time_taken_str = f"{minutes}m {seconds}s"
    
    if submission.time_taken_seconds < challenge.time_limit_minutes * 60:
        recommendations.append(f"Good time management! Completed in {time_taken_str}.")
    else:
        recommendations.append(f"Consider improving analysis speed. Took {time_taken_str}, over the {challenge.time_limit_minutes} minute target.")
    
    if passed and submission.level == LogLevel.BASIC:
        recommendations.append("Ready for the next level! Try the Intermediate challenge to test advanced skills.")
    elif passed and submission.level == LogLevel.INTERMEDIATE:
        recommendations.append("Impressive! You're ready for the Advanced APT detection challenge.")
    elif passed:
        recommendations.append("Expert level achieved! Consider pursuing SOC analyst certifications.")
    
    result = LogChallengeResult(
        level=submission.level,
        total_threats=challenge.total_threats,
        threats_found=threats_found,
        threats_missed=threats_missed,
        false_positives=false_positives,
        accuracy_percentage=round(accuracy, 1),
        score=round(score, 1),
        max_score=100,
        time_taken=time_taken_str,
        passed=passed,
        evaluations=evaluations,
        missed_threats=missed_threats,
        summary_feedback=summary_feedback,
        recommendations=recommendations
    )
    
    return result

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
