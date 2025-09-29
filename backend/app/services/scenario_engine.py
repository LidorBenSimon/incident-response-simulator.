import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.scenario import ScenarioStatus

class ScenarioEvent:
    def __init__(self, event_id: str, timestamp: datetime, event_type: str, 
                 level: str, message: str, source: str, is_suspicious: bool = False):
        self.event_id = event_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.level = level
        self.message = message
        self.source = source
        self.is_suspicious = is_suspicious

class ScenarioEngine:
    def __init__(self):
        self.active_sessions = {}
        self.event_pools = self._create_event_pools()
    
    def _create_event_pools(self) -> Dict[str, List[ScenarioEvent]]:
        """Create event pools (normal + suspicious)"""
        
        # Normal events
        normal_events = [
            ScenarioEvent("norm_001", datetime.now(), "normal", "INFO", 
                         "User alice.smith logged into workstation WS-MARKETING-01", "Active Directory"),
            ScenarioEvent("norm_002", datetime.now(), "normal", "INFO",
                         "Scheduled backup completed successfully on SERVER-FILE-01", "Backup System"),
            ScenarioEvent("norm_003", datetime.now(), "normal", "INFO",
                         "User bob.jones accessed shared folder /marketing/campaigns", "File Server"),
            ScenarioEvent("norm_004", datetime.now(), "normal", "INFO",
                         "Print job completed on PRINTER-02", "Print Server"),
            ScenarioEvent("norm_005", datetime.now(), "normal", "INFO",
                         "Routine system update installed on WS-HR-03", "WSUS"),
            ScenarioEvent("norm_006", datetime.now(), "normal", "INFO",
                         "User charlie.brown logged out from WS-SALES-02", "Active Directory"),
            ScenarioEvent("norm_007", datetime.now(), "normal", "INFO",
                         "Daily antivirus scan completed on WS-RECEPTION-01", "Antivirus"),
            ScenarioEvent("norm_008", datetime.now(), "normal", "INFO",
                         "Scheduled database maintenance started", "SQL Server"),
            ScenarioEvent("norm_009", datetime.now(), "normal", "INFO",
                         "Email sync completed for user@company.com", "Exchange Server"),
            ScenarioEvent("norm_010", datetime.now(), "normal", "INFO",
                         "Firewall rule updated: Allow port 443", "Network Security"),
        ]
        
        # Suspicious events
        suspicious_events = [
            ScenarioEvent("susp_001", datetime.now(), "attack", "WARNING",
                         "Suspicious email attachment opened on WS-MARKETING-01", "Email Gateway", True),
            ScenarioEvent("susp_002", datetime.now(), "attack", "WARNING",
                         "Outbound connection to suspicious domain: secure-bank-login.com", "Firewall", True),
            ScenarioEvent("susp_003", datetime.now(), "attack", "CRITICAL",
                         "Unusual PowerShell execution detected on WS-MARKETING-01", "EDR System", True),
            ScenarioEvent("susp_004", datetime.now(), "attack", "WARNING",
                         "Multiple failed login attempts for admin account", "Domain Controller", True),
            ScenarioEvent("susp_005", datetime.now(), "attack", "CRITICAL",
                         "Lateral movement detected: WS-MARKETING-01 -> SERVER-FILE-01", "Network Monitor", True),
            ScenarioEvent("susp_006", datetime.now(), "attack", "CRITICAL",
                         "Large data transfer detected: SERVER-FILE-01 -> external IP", "DLP System", True),
            ScenarioEvent("susp_007", datetime.now(), "attack", "CRITICAL",
                         "Encrypted files detected on multiple workstations", "File System Monitor", True),
            ScenarioEvent("susp_008", datetime.now(), "attack", "CRITICAL",
                         "Ransom note file created: README_DECRYPT.txt", "File System Monitor", True),
        ]
        
        return {
            "normal": normal_events,
            "suspicious": suspicious_events
        }
    
    async def start_scenario(self, session_id: str, scenario_id: str) -> Dict[str, Any]:
        """Start a complex scenario"""
        
        # Create a mixed sequence of events
        mixed_events = self._create_mixed_sequence()
        
        session = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "start_time": datetime.now(),
            "event_sequence": mixed_events,
            "events_delivered": [],
            "next_event_index": 0,
            "student_responses": [],
            "status": "active",
            "last_event_time": datetime.now()
        }
        
        self.active_sessions[session_id] = session
        
        # Start gradual event delivery
        asyncio.create_task(self._deliver_events_gradually(session_id))
        
        return {
            "status": "success",
            "session_id": session_id,
            "scenario_name": "Advanced Multi-Stage Attack Simulation",
            "total_events": len(mixed_events),
            "message": "Scenario started - events will appear gradually"
        }
    
    def _create_mixed_sequence(self) -> List[ScenarioEvent]:
        """Create a random mixed sequence of events"""
        normal_pool = self.event_pools["normal"].copy()
        suspicious_pool = self.event_pools["suspicious"].copy()
        
        # Shuffle events
        random.shuffle(normal_pool)
        random.shuffle(suspicious_pool)
        
        # Create a sequence: ~60% normal, ~40% suspicious
        sequence = []
        normal_idx = 0
        suspicious_idx = 0
        
        for i in range(16):  # Total 16 events
            if random.random() < 0.6 and normal_idx < len(normal_pool):
                # Normal event
                event = normal_pool[normal_idx]
                event.event_id = f"evt_{i+1:03d}"
                sequence.append(event)
                normal_idx += 1
            elif suspicious_idx < len(suspicious_pool):
                # Suspicious event
                event = suspicious_pool[suspicious_idx]
                event.event_id = f"evt_{i+1:03d}"
                sequence.append(event)
                suspicious_idx += 1
            else:
                # If suspicious pool is empty, add normal
                if normal_idx < len(normal_pool):
                    event = normal_pool[normal_idx]
                    event.event_id = f"evt_{i+1:03d}"
                    sequence.append(event)
                    normal_idx += 1
        
        return sequence
    
    async def _deliver_events_gradually(self, session_id: str):
        """Deliver events gradually - one every 3-7 seconds"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        while (session_id in self.active_sessions and 
               session["next_event_index"] < len(session["event_sequence"])):
            
            # Wait randomly between 3-7 seconds
            delay = random.uniform(3, 7)
            await asyncio.sleep(delay)
            
            # Check session is still active
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            event_idx = session["next_event_index"]
            
            if event_idx < len(session["event_sequence"]):
                event = session["event_sequence"][event_idx]
                event.timestamp = datetime.now()  # Update real time
                
                session["events_delivered"].append(event)
                session["next_event_index"] += 1
                session["last_event_time"] = datetime.now()
    
    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events delivered so far"""
        if session_id not in self.active_sessions:
            return []
        
        session = self.active_sessions[session_id]
        events = []
        
        for event in session["events_delivered"]:
            events.append({
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "level": event.level,
                "message": event.message,
                "source": event.source,
                "is_suspicious": event.is_suspicious,
                "event_type": event.event_type
            })
        
        return events
    
    def submit_student_response(self, session_id: str, event_id: str, 
                               action: str, is_suspicious_marked: bool) -> Dict[str, Any]:
        """Receive student's response to a specific event"""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Find the event
        event = None
        for e in session["events_delivered"]:
            if e.event_id == event_id:
                event = e
                break
        
        if not event:
            return {"status": "error", "message": "Event not found"}
        
        # Evaluate response
        correct_suspicion = event.is_suspicious == is_suspicious_marked
        correct_action = self._evaluate_action(event, action)
        
        response_data = {
            "event_id": event_id,
            "action": action,
            "is_suspicious_marked": is_suspicious_marked,
            "timestamp": datetime.now().isoformat(),
            "correct_suspicion": correct_suspicion,
            "correct_action": correct_action,
            "score": (25 if correct_suspicion else 0) + (25 if correct_action else 0)
        }
        
        session["student_responses"].append(response_data)
        
        return {
            "status": "success",
            "evaluation": response_data,
            "feedback": self._generate_feedback(event, response_data)
        }
    
    def _evaluate_action(self, event: ScenarioEvent, action: str) -> bool:
        """Evaluate correctness of the action"""
        if event.is_suspicious:
            # Correct actions for suspicious events
            if event.level == "CRITICAL":
                return action in ["isolate", "escalate", "shutdown"]
            else:  # WARNING
                return action in ["monitor", "isolate", "block_ip"]
        else:
            # Correct actions for normal events
            return action in ["monitor"]
    
    def _generate_feedback(self, event: ScenarioEvent, response: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed feedback"""
        feedback = {
            "suspicion_feedback": "",
            "action_feedback": "",
            "recommendations": []
        }
        
        # Feedback on suspicion detection
        if response["correct_suspicion"]:
            if event.is_suspicious:
                feedback["suspicion_feedback"] = "Great detection! This is indeed a suspicious event."
            else:
                feedback["suspicion_feedback"] = "Correct - this is a normal event."
        else:
            if event.is_suspicious:
                feedback["suspicion_feedback"] = "You missed a threat! This was a suspicious event."
                feedback["recommendations"].append("Pay attention to words like 'suspicious', 'unusual', 'multiple failed attempts'")
            else:
                feedback["suspicion_feedback"] = "This was a normal event, not suspicious."
                feedback["recommendations"].append("Activities like backup, updates, regular login/logout are not suspicious")
        
        # Feedback on action
        if response["correct_action"]:
            feedback["action_feedback"] = "Correct action choice!"
        else:
            if event.is_suspicious and event.level == "CRITICAL":
                feedback["action_feedback"] = "Critical events require stronger actions (isolate/escalate/shutdown)"
            elif event.is_suspicious:
                feedback["action_feedback"] = "Suspicious events require a response (monitor/isolate/block_ip)"
            else:
                feedback["action_feedback"] = "For a normal event, monitoring is sufficient"
        
        return feedback
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Summarize student's performance with score across all events"""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.active_sessions[session_id]
        responses = session["student_responses"]
        
        # All events delivered
        total_events = len(session["events_delivered"])
        suspicious_events = [e for e in session["events_delivered"] if e.is_suspicious]
        normal_events = [e for e in session["events_delivered"] if not e.is_suspicious]
        
        # Responses
        total_responses = len(responses)
        correct_suspicions = len([r for r in responses if r["correct_suspicion"]])
        correct_actions = len([r for r in responses if r["correct_action"]])
        total_score = sum([r["score"] for r in responses])
        
        # Max score
        max_possible_score = total_events * 50  # each event worth 50 points
        unanswered_events = total_events - total_responses
        
        # Detailed breakdown
        all_events_details = []
        for event in session["events_delivered"]:
            # Find response for this event
            response = None
            for r in responses:
                if r["event_id"] == event.event_id:
                    response = r
                    break
            
            event_detail = {
                "event_id": event.event_id,
                "message": event.message,
                "actual_suspicion": event.is_suspicious,
                "correct_action_options": self._get_correct_actions_for_event(event),
                "explanation": self._get_event_explanation(event)
            }
            
            if response:
                event_detail.update({
                    "responded": True,
                    "student_marked_suspicious": response["is_suspicious_marked"],
                    "student_action": response["action"],
                    "suspicion_correct": response["correct_suspicion"],
                    "action_correct": response["correct_action"],
                    "points_earned": response["score"]
                })
            else:
                event_detail.update({
                    "responded": False,
                    "student_marked_suspicious": None,
                    "student_action": None,
                    "suspicion_correct": False,
                    "action_correct": False,
                    "points_earned": 0
                })
            
            all_events_details.append(event_detail)
        
        # Calculate percentages
        if total_events > 0:
            overall_accuracy = (total_score / max_possible_score) * 100
            response_rate = (total_responses / total_events) * 100
        else:
            overall_accuracy = 0
            response_rate = 0
            
        suspicion_accuracy = (correct_suspicions / total_responses) * 100 if total_responses > 0 else 0
        action_accuracy = (correct_actions / total_responses) * 100 if total_responses > 0 else 0
        
        return {
            "session_id": session_id,
            "scenario_name": "Advanced Multi-Stage Attack",
            "overall_performance": {
                "total_score": total_score,
                "max_possible_score": max_possible_score,
                "overall_accuracy": round(overall_accuracy, 1),
                "letter_grade": self._calculate_letter_grade(overall_accuracy)
            },
            "event_statistics": {
                "total_events": total_events,
                "total_suspicious_events": len(suspicious_events),
                "total_normal_events": len(normal_events),
                "events_responded_to": total_responses,
                "unanswered_events": unanswered_events,
                "response_rate": round(response_rate, 1)
            },
            "accuracy_breakdown": {
                "correct_suspicions": correct_suspicions,
                "correct_actions": correct_actions,
                "suspicion_accuracy": round(suspicion_accuracy, 1),
                "action_accuracy": round(action_accuracy, 1)
            },
            "detailed_results": all_events_details,
            "recommendations": self._generate_recommendations(overall_accuracy, response_rate, suspicion_accuracy, action_accuracy)
        }
    
    def _get_correct_actions_for_event(self, event) -> List[str]:
        """Return correct actions for the event"""
        if event.is_suspicious:
            if event.level == "CRITICAL":
                return ["isolate", "escalate", "shutdown"]
            else:  # WARNING
                return ["monitor", "isolate", "block_ip"]
        else:
            return ["monitor"]
    
    def _get_event_explanation(self, event) -> str:
        """Explain why the event is suspicious or not"""
        if event.is_suspicious:
            explanations = {
                "Suspicious email attachment opened": "Opening a suspicious attachment may lead to malware installation",
                "Outbound connection to suspicious domain": "Connection to a suspicious domain may indicate malware activity or data exfiltration",
                "Unusual PowerShell execution": "Unusual PowerShell usage is a strong indicator of malicious activity",
                "Multiple failed login attempts": "Multiple failed logins may indicate a brute force attack",
                "Lateral movement detected": "Lateral movement indicates attacker spreading post-initial compromise",
                "Large data transfer": "Large outbound data transfer may indicate data theft",
                "Encrypted files detected": "File encryption is a typical ransomware sign",
                "Ransom note file created": "Creation of ransom note confirms ransomware attack"
            }
            
            for key, explanation in explanations.items():
                if key.lower() in event.message.lower():
                    return explanation
            return "This activity shows suspicious behavior patterns typical of cyberattacks"
        else:
            return "This is normal routine activity in the system and not suspicious"
    
    def _calculate_letter_grade(self, accuracy: float) -> str:
        """Calculate letter grade"""
        if accuracy >= 90:
            return "A"
        elif accuracy >= 80:
            return "B"
        elif accuracy >= 70:
            return "C"
        elif accuracy >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, overall_acc: float, response_rate: float, 
                                suspicion_acc: float, action_acc: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if response_rate < 70:
            recommendations.append("Try to identify and respond to more events - unanswered events may escalate issues")
        
        if suspicion_acc < 70:
            recommendations.append("Focus on learning indicators of suspicious activity like unknown domains and unusual command executions")
        
        if action_acc < 70:
            recommendations.append("Learn the appropriate responses for each severity level - critical events require stronger actions")
        
        if overall_acc >= 90:
            recommendations.append("Excellent performance! Try more advanced scenarios")
        elif overall_acc >= 70:
            recommendations.append("Good performance. Continue practicing similar scenarios to strengthen skills")
        else:
            recommendations.append("Recommended to review study material and practice more basic scenarios")
        
        return recommendations
