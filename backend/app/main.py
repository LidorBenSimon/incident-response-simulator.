from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn
from datetime import datetime
import json
import uuid
import os
import docker
import subprocess
from typing import Dict, Any

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









@app.post("/privilege-escalation/start")
async def start_privesc_lab():
    """Start the privilege escalation lab container"""
    try:
        client = docker.from_env()
        
        try:
            container = client.containers.get("privesc_lab")
            if container.status == "running":
                # Container already running - restart it
                container.restart()
                # Wait for services to start
                import time
                time.sleep(5)
                return {
                    "status": "success",
                    "message": "Lab restarted for fresh session",
                    "container_id": container.id,
                    "username": "lowpriv",
                    "password": "student123",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                container.start()
                import time
                time.sleep(5)
                return {
                    "status": "success",
                    "message": "Privilege Escalation Lab started",
                    "container_id": container.id,
                    "username": "lowpriv",
                    "password": "student123",
                    "timestamp": datetime.now().isoformat()
                }
        except docker.errors.NotFound:
            # Container doesn't exist, start with docker-compose
            result = subprocess.run(
                ['docker-compose', 'up', '-d', 'privesc_lab'],
                cwd='/root/incident-response-simulator',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                import time
                time.sleep(8)  # Wait longer for initial setup
                
                container = client.containers.get("privesc_lab")
                return {
                    "status": "success",
                    "message": "Lab container created and started",
                    "container_id": container.id,
                    "username": "lowpriv",
                    "password": "student123",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start container: {result.stderr}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error starting lab: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/privilege-escalation/execute")
async def execute_command(command_data: Dict[str, Any]):
    """Execute command in privilege escalation lab - FIXED VERSION"""
    try:
        client = docker.from_env()
        container = client.containers.get("privesc_lab")
        
        if container.status != "running":
            return {
                "status": "error",
                "message": "Lab container is not running. Please start the lab first.",
                "timestamp": datetime.now().isoformat()
            }
        
        command = command_data.get("command", "")
        
        if not command:
            return {
                "status": "error",
                "message": "No command provided"
            }
        
        # Security: Block dangerous commands
        blocked_commands = ["rm -rf /", "mkfs", "dd if=/dev/zero"]
        if any(blocked in command for blocked in blocked_commands):
            return {
                "status": "error",
                "output": "Command blocked for safety reasons",
                "timestamp": datetime.now().isoformat()
            }
        
        # FIXED: Use proper shell script for su command
        # Create a temporary script file and execute it
        script_content = f"""#!/bin/bash
su - lowpriv << 'EOFSU'
{command}
EOFSU
"""
        
        # Write script to container
        script_name = f"/tmp/cmd_{datetime.now().timestamp()}.sh"
        create_script = container.exec_run(
            f"bash -c \"cat > {script_name} << 'EOFSCRIPT'\n{script_content}\nEOFSCRIPT\"",
            stdout=True,
            stderr=True
        )
        
        # Make script executable
        container.exec_run(f"chmod +x {script_name}")
        
        # Execute the script
        exec_result = container.exec_run(
            f"bash {script_name}",
            stdout=True,
            stderr=True,
            demux=False
        )
        
        # Clean up script
        container.exec_run(f"rm -f {script_name}")
        
        output = exec_result.output.decode('utf-8', errors='replace')
        exit_code = exec_result.exit_code
        
        # Check if flag was found
        flag_found = "FLAG{" in output
        is_root = "root@" in output or "uid=0" in output
        
        return {
            "status": "success",
            "output": output,
            "exit_code": exit_code,
            "flag_found": flag_found,
            "is_root": is_root,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
    except docker.errors.NotFound:
        return {
            "status": "error",
            "message": "Lab container not found. Please start the lab first.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing command: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/privilege-escalation/hint/{hint_number}")
async def get_hint(hint_number: int):
    """Get progressive hints for the challenge"""
    hints = {
        1: {
            "title": "Reconnaissance",
            "hint": "Start by exploring the system. Check what commands you can run and what files you have access to.",
            "commands": ["whoami", "id", "ls -la", "pwd", "uname -a"]
        },
        2: {
            "title": "SUID Binaries",
            "hint": "Look for files with the SUID bit set. These run with the owner's privileges (usually root).",
            "commands": ["find / -perm -4000 -type f 2>/dev/null", "ls -la /usr/local/bin/"]
        },
        3: {
            "title": "Sudo Permissions",
            "hint": "Check what commands you can run with sudo. Sometimes misconfigured sudo can lead to privilege escalation.",
            "commands": ["sudo -l"]
        },
        4: {
            "title": "SUID Exploitation",
            "hint": "Found /usr/local/bin/backup? It has SUID bit and runs as root. Execute it directly.",
            "commands": ["/usr/local/bin/backup", "# This will give you root shell!"]
        },
        5: {
            "title": "Alternative: Sudo Find",
            "hint": "If you have sudo access to 'find', you can use it to execute commands as root using -exec flag.",
            "commands": ["sudo find /home -exec /bin/bash \\;"]
        },
        6: {
            "title": "Getting the Flag",
            "hint": "Once you have root shell, read the flag from /root/flag.txt",
            "commands": ["whoami", "cat /root/flag.txt"]
        }
    }
    
    if hint_number not in hints:
        return {
            "status": "error",
            "message": "Invalid hint number. Available hints: 1-6"
        }
    
    return {
        "status": "success",
        "hint": hints[hint_number],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/privilege-escalation/submit-flag")
async def submit_flag(flag_data: Dict[str, Any]):
    """Submit flag and calculate score"""
    submitted_flag = flag_data.get("flag", "").strip()
    time_taken = flag_data.get("time_taken", 0)
    hints_used = flag_data.get("hints_used", 0)
    
    correct_flag = "FLAG{pr1v3sc_m4st3r_2024}"
    
    if submitted_flag == correct_flag:
        # Calculate score
        base_score = 100
        time_bonus = max(0, 50 - (int(time_taken) // 60))  # Bonus for speed
        hint_penalty = hints_used * 5  # -5 points per hint
        
        final_score = max(0, min(150, base_score + time_bonus - hint_penalty))
        
        return {
            "status": "success",
            "correct": True,
            "score": final_score,
            "base_score": base_score,
            "time_bonus": time_bonus,
            "hint_penalty": hint_penalty,
            "message": "Congratulations! You've successfully escalated privileges to root!",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "success",
            "correct": False,
            "message": "Incorrect flag. Keep trying!",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/privilege-escalation/stop")
async def stop_privesc_lab():
    """Stop the privilege escalation lab"""
    try:
        client = docker.from_env()
        container = client.containers.get("privesc_lab")
        container.stop()
        
        return {
            "status": "success",
            "message": "Lab stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        return {
            "status": "error",
            "message": "Lab container not found",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error stopping lab: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/privilege-escalation/status")
async def get_lab_status():
    """Get current lab status"""
    try:
        client = docker.from_env()
        container = client.containers.get("privesc_lab")
        
        return {
            "status": "success",
            "running": container.status == "running",
            "container_status": container.status,
            "created": container.attrs['Created'],
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        return {
            "status": "success",
            "running": False,
            "message": "Lab not created yet",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# ============================================
# PASSWORD CRACKING LAB - FIXED ENDPOINTS
# ============================================

@app.post("/hashcrack/start")
async def start_hashcrack_lab():
    """Start the password cracking lab container"""
    try:
        client = docker.from_env()
        
        try:
            container = client.containers.get("hashcrack_lab")
            if container.status == "running":
                container.restart()
                import time
                time.sleep(5)
                return {
                    "status": "success",
                    "message": "Lab restarted for fresh session",
                    "container_id": container.id,
                    "username": "pentester",
                    "password": "cracker123",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                container.start()
                import time
                time.sleep(5)
                return {
                    "status": "success",
                    "message": "Password Cracking Lab started",
                    "container_id": container.id,
                    "username": "pentester",
                    "password": "cracker123",
                    "timestamp": datetime.now().isoformat()
                }
        except docker.errors.NotFound:
            result = subprocess.run(
                ['docker-compose', 'up', '-d', 'hashcrack_lab'],
                cwd='/root/incident-response-simulator',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                import time
                time.sleep(8)
                
                container = client.containers.get("hashcrack_lab")
                return {
                    "status": "success",
                    "message": "Lab container created and started",
                    "container_id": container.id,
                    "username": "pentester",
                    "password": "cracker123",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start container: {result.stderr}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error starting lab: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/hashcrack/execute")
async def execute_hashcrack_command(command_data: Dict[str, Any]):
    """Execute command in password cracking lab - FIXED VERSION"""
    try:
        client = docker.from_env()
        container = client.containers.get("hashcrack_lab")
        
        if container.status != "running":
            return {
                "status": "error",
                "message": "Lab container is not running. Please start the lab first.",
                "timestamp": datetime.now().isoformat()
            }
        
        command = command_data.get("command", "")
        
        if not command:
            return {
                "status": "error",
                "message": "No command provided"
            }
        
        # FIXED: Use proper shell script for su command
        script_content = f"""#!/bin/bash
su - pentester << 'EOFSU'
{command}
EOFSU
"""
        
        # Write script to container
        script_name = f"/tmp/cmd_{datetime.now().timestamp()}.sh"
        create_script = container.exec_run(
            f"bash -c \"cat > {script_name} << 'EOFSCRIPT'\n{script_content}\nEOFSCRIPT\"",
            stdout=True,
            stderr=True
        )
        
        # Make script executable
        container.exec_run(f"chmod +x {script_name}")
        
        # Execute the script
        exec_result = container.exec_run(
            f"bash {script_name}",
            stdout=True,
            stderr=True,
            demux=False
        )
        
        # Clean up script
        container.exec_run(f"rm -f {script_name}")
        
        output = exec_result.output.decode('utf-8', errors='replace')
        exit_code = exec_result.exit_code
        
        # Check for cracked passwords
        cracked_found = "Cracked" in output or ("password" in output.lower() and ":" in output)
        
        return {
            "status": "success",
            "output": output,
            "exit_code": exit_code,
            "cracked_found": cracked_found,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
    except docker.errors.NotFound:
        return {
            "status": "error",
            "message": "Lab container not found. Please start the lab first.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing command: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/hashcrack/files")
async def list_hashcrack_files():
    """List available hash files and wordlists"""
    try:
        client = docker.from_env()
        container = client.containers.get("hashcrack_lab")
        
        # List hash files
        hash_result = container.exec_run("ls -la /hashes/", stdout=True, stderr=True)
        hash_files = hash_result.output.decode('utf-8', errors='replace')
        
        # List wordlists
        wordlist_result = container.exec_run("ls -lh /wordlists/", stdout=True, stderr=True)
        wordlists = wordlist_result.output.decode('utf-8', errors='replace')
        
        return {
            "status": "success",
            "hash_files": hash_files,
            "wordlists": wordlists,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing files: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/hashcrack/hint/{hint_number}")
async def get_hashcrack_hint(hint_number: int):
    """Get progressive hints for password cracking"""
    hints = {
        1: {
            "title": "Getting Started",
            "hint": "Start by exploring what files are available. Check /hashes/ directory for hash dumps.",
            "commands": ["ls -la /hashes/", "cat /hashes/README.txt"]
        },
        2: {
            "title": "Hash Identification",
            "hint": "You need to identify the hash type before cracking. Look at hash length and format.",
            "commands": [
                "cat /hashes/company_dump_md5.txt",
                "# MD5 = 32 chars hex",
                "# SHA-1 = 40 chars hex"
            ]
        },
        3: {
            "title": "Choose Your Tool",
            "hint": "You have two main tools: john (simple) and hashcat (powerful). Start with john for learning.",
            "commands": ["john --help", "hashcat --help"]
        },
        4: {
            "title": "Select Wordlist",
            "hint": "Check available wordlists. Start with rockyou.txt (fastest for this lab).",
            "commands": ["ls -lh /wordlists/", "wc -l /wordlists/rockyou.txt"]
        },
        5: {
            "title": "Cracking MD5 with John",
            "hint": "Use john with format and wordlist. IMPORTANT: Use lowercase 'raw-md5' for the format.",
            "commands": [
                "john --format=raw-md5 --wordlist=/wordlists/rockyou.txt /hashes/company_dump_md5.txt",
                "john --format=raw-md5 --show /hashes/company_dump_md5.txt"
            ]
        },
        6: {
            "title": "Using Hashcat",
            "hint": "Hashcat is faster. MD5=0, SHA1=100. Use --force to bypass warnings.",
            "commands": [
                "hashcat -m 0 /hashes/company_dump_md5.txt /wordlists/rockyou.txt --force",
                "hashcat -m 0 /hashes/company_dump_md5.txt --show"
            ]
        },
        7: {
            "title": "View Results",
            "hint": "After cracking, view your results with --show flag",
            "commands": [
                "john --format=raw-md5 --show /hashes/company_dump_md5.txt",
                "hashcat -m 0 /hashes/company_dump_md5.txt --show"
            ]
        }
    }
    
    if hint_number not in hints:
        return {
            "status": "error",
            "message": "Invalid hint number. Available hints: 1-7"
        }
    
    return {
        "status": "success",
        "hint": hints[hint_number],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/hashcrack/submit-results")
async def submit_hashcrack_results(results_data: Dict[str, Any]):
    """Submit cracked passwords and calculate score"""
    cracked_passwords = results_data.get("cracked_passwords", [])
    time_taken = results_data.get("time_taken", 0)
    hints_used = results_data.get("hints_used", 0)
    tool_used = results_data.get("tool_used", "unknown")
    
    # Expected passwords (what can be cracked with rockyou.txt)
    expected_cracks = {
        "5f4dcc3b5aa765d61d8327deb882cf99": "password",
        "e10adc3949ba59abbe56e057f20f883e": "123456",
        "25d55ad283aa400af464c76d713c07ad": "12345678",
        "fcea920f7412b5da7be0cf42b8c93759": "pass123",
        "1a1dc91c907325c69271ddf0c944bc72": "Password123",
        "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8": "password",
        "8cb2237d0679ca88db6464eac60da96345513964": "qwerty",
        "209c6174da490caeb422f3fa5a7ae634": "password",
        "32ed87bdb5fdc5e9cba88547376818d4": "Password123"
    }
    
    total_crackable = len(expected_cracks)
    correct_cracks = len(cracked_passwords)
    
    # Calculate score
    base_score = (correct_cracks / total_crackable) * 100
    time_bonus = max(0, 30 - (int(time_taken) // 60))
    hint_penalty = hints_used * 3
    tool_bonus = 10 if tool_used == "hashcat" else 5 if tool_used == "john" else 0
    
    final_score = max(0, min(150, base_score + time_bonus - hint_penalty + tool_bonus))
    
    # Grade
    if final_score >= 90:
        grade = "A"
    elif final_score >= 75:
        grade = "B"
    elif final_score >= 60:
        grade = "C"
    elif final_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return {
        "status": "success",
        "score": round(final_score, 1),
        "grade": grade,
        "base_score": round(base_score, 1),
        "time_bonus": time_bonus,
        "hint_penalty": hint_penalty,
        "tool_bonus": tool_bonus,
        "cracked_count": correct_cracks,
        "total_crackable": total_crackable,
        "success_rate": round((correct_cracks / total_crackable) * 100, 1),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/hashcrack/stop")
async def stop_hashcrack_lab():
    """Stop the password cracking lab"""
    try:
        client = docker.from_env()
        container = client.containers.get("hashcrack_lab")
        container.stop()
        
        return {
            "status": "success",
            "message": "Lab stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        return {
            "status": "error",
            "message": "Lab container not found",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error stopping lab: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/hashcrack/status")
async def get_hashcrack_status():
    """Get current lab status"""
    try:
        client = docker.from_env()
        container = client.containers.get("hashcrack_lab")
        
        return {
            "status": "success",
            "running": container.status == "running",
            "container_status": container.status,
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        return {
            "status": "success",
            "running": False,
            "message": "Lab not created yet",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }














if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
