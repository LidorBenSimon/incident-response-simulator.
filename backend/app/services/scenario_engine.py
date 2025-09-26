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
        """יצירת בריכות אירועים מעורבים"""
        
        # אירועים רגילים
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
        
        # אירועים חשודים
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
        """התחלת תרחיש מורכב"""
        
        # יצירת רצף מעורב של אירועים
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
        
        # התחלת שליחת אירועים הדרגתית
        asyncio.create_task(self._deliver_events_gradually(session_id))
        
        return {
            "status": "success",
            "session_id": session_id,
            "scenario_name": "Advanced Multi-Stage Attack Simulation",
            "total_events": len(mixed_events),
            "message": "Scenario started - events will appear gradually"
        }
    
    def _create_mixed_sequence(self) -> List[ScenarioEvent]:
        """יצירת רצף מעורב ואקראי של אירועים"""
        normal_pool = self.event_pools["normal"].copy()
        suspicious_pool = self.event_pools["suspicious"].copy()
        
        # עירבוב האירועים
        random.shuffle(normal_pool)
        random.shuffle(suspicious_pool)
        
        # יצירת רצף מעורב: בערך 60% רגילים, 40% חשודים
        sequence = []
        normal_idx = 0
        suspicious_idx = 0
        
        for i in range(16):  # סה"כ 16 אירועים
            if random.random() < 0.6 and normal_idx < len(normal_pool):
                # אירוע רגיל
                event = normal_pool[normal_idx]
                event.event_id = f"evt_{i+1:03d}"
                sequence.append(event)
                normal_idx += 1
            elif suspicious_idx < len(suspicious_pool):
                # אירוע חשוד
                event = suspicious_pool[suspicious_idx]
                event.event_id = f"evt_{i+1:03d}"
                sequence.append(event)
                suspicious_idx += 1
            else:
                # אם נגמרו החשודים, הוסף רגיל
                if normal_idx < len(normal_pool):
                    event = normal_pool[normal_idx]
                    event.event_id = f"evt_{i+1:03d}"
                    sequence.append(event)
                    normal_idx += 1
        
        return sequence
    
    async def _deliver_events_gradually(self, session_id: str):
        """שליחת אירועים בהדרגה - אחד כל 3-7 שניות"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        while (session_id in self.active_sessions and 
               session["next_event_index"] < len(session["event_sequence"])):
            
            # המתנה אקראית בין 3-7 שניות
            delay = random.uniform(3, 7)
            await asyncio.sleep(delay)
            
            # בדיקה שהsession עדיין פעיל
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            event_idx = session["next_event_index"]
            
            if event_idx < len(session["event_sequence"]):
                event = session["event_sequence"][event_idx]
                event.timestamp = datetime.now()  # עדכון זמן אמיתי
                
                session["events_delivered"].append(event)
                session["next_event_index"] += 1
                session["last_event_time"] = datetime.now()
    
    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """קבלת כל האירועים שנשלחו עד כה"""
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
                "is_suspicious": event.is_suspicious,  # זה לא יוצג לmשתמש
                "event_type": event.event_type
            })
        
        return events
    
    def submit_student_response(self, session_id: str, event_id: str, 
                               action: str, is_suspicious_marked: bool) -> Dict[str, Any]:
        """קבלת תגובת התלמיד לאירוע ספציפי"""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # חיפוש האירוע
        event = None
        for e in session["events_delivered"]:
            if e.event_id == event_id:
                event = e
                break
        
        if not event:
            return {"status": "error", "message": "Event not found"}
        
        # הערכת התגובה
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
        """הערכת נכונות הפעולה"""
        if event.is_suspicious:
            # פעולות נכונות לאירועים חשודים
            if event.level == "CRITICAL":
                return action in ["isolate", "escalate", "shutdown"]
            else:  # WARNING
                return action in ["monitor", "isolate", "block_ip"]
        else:
            # פעולות נכונות לאירועים רגילים
            return action in ["monitor"]
    
    def _generate_feedback(self, event: ScenarioEvent, response: Dict[str, Any]) -> Dict[str, Any]:
        """יצירת משוב מפורט"""
        feedback = {
            "suspicion_feedback": "",
            "action_feedback": "",
            "recommendations": []
        }
        
        # משוב על זיהוי החשדנות
        if response["correct_suspicion"]:
            if event.is_suspicious:
                feedback["suspicion_feedback"] = "זיהוי מעולה! זה אכן אירוע חשוד."
            else:
                feedback["suspicion_feedback"] = "נכון - זה אירוע רגיל."
        else:
            if event.is_suspicious:
                feedback["suspicion_feedback"] = "פספסת איום! זה היה אירוע חשוד."
                feedback["recommendations"].append("שים לב למילים כמו 'suspicious', 'unusual', 'multiple failed attempts'")
            else:
                feedback["suspicion_feedback"] = "זה היה אירוע רגיל, לא חשוד."
                feedback["recommendations"].append("פעילות כמו backup, updates, login/logout רגילים הם לא חשודים")
        
        # משוב על הפעולה
        if response["correct_action"]:
            feedback["action_feedback"] = "בחירת פעולה נכונה!"
        else:
            if event.is_suspicious and event.level == "CRITICAL":
                feedback["action_feedback"] = "אירוע קריטי דורש פעולה חזקה יותר (isolate/escalate/shutdown)"
            elif event.is_suspicious:
                feedback["action_feedback"] = "אירוע חשוד דורש תגובה (monitor/isolate/block_ip)"
            else:
                feedback["action_feedback"] = "לאירוע רגיל מספיק ניטור"
        
        return feedback
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """סיכום ביצועי התלמיד"""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.active_sessions[session_id]
        responses = session["student_responses"]
        total_events = len(session["events_delivered"])
        suspicious_events = len([e for e in session["events_delivered"] if e.is_suspicious])
        
        total_responses = len(responses)
        correct_suspicions = len([r for r in responses if r["correct_suspicion"]])
        correct_actions = len([r for r in responses if r["correct_action"]])
        total_score = sum([r["score"] for r in responses])
        
        return {
            "session_id": session_id,
            "scenario_name": "Advanced Multi-Stage Attack",
            "total_events": total_events,
            "total_suspicious_events": suspicious_events,
            "events_responded_to": total_responses,
            "correct_suspicions": correct_suspicions,
            "correct_actions": correct_actions,
            "total_score": total_score,
            "max_possible_score": total_responses * 50,
            "suspicion_accuracy": (correct_suspicions / total_responses) * 100 if total_responses > 0 else 0,
            "action_accuracy": (correct_actions / total_responses) * 100 if total_responses > 0 else 0
        }
