import docker
import subprocess
import json
from typing import Dict, List, Any
from datetime import datetime

class DockerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Warning: Could not connect to Docker: {e}")
            self.client = None
    
    def start_scenario_containers(self, scenario_id: int) -> Dict[str, Any]:
        """הפעלת containers לתרחיש"""
        try:
            # הפעלת docker-compose
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd='/root/incident-response-simulator',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # קבלת סטטוס containers
                containers = self.get_running_containers()
                return {
                    "status": "success",
                    "message": "Containers started successfully",
                    "containers": containers,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Failed to start containers: {result.stderr}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Docker service error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def stop_scenario_containers(self) -> Dict[str, Any]:
        """עצירת containers של התרחיש"""
        try:
            result = subprocess.run(
                ['docker-compose', 'down'],
                cwd='/root/incident-response-simulator',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Containers stopped successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to stop containers: {result.stderr}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Docker service error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_running_containers(self) -> List[Dict[str, Any]]:
        """קבלת רשימת containers רצים"""
        containers = []
        try:
            if self.client:
                for container in self.client.containers.list():
                    if container.name in ['victim_workstation', 'attacker_server', 'log_collector']:
                        containers.append({
                            "name": container.name,
                            "status": container.status,
                            "image": container.image.tags[0] if container.image.tags else "unknown",
                            "ports": container.ports,
                            "created": container.attrs['Created']
                        })
        except Exception as e:
            print(f"Error getting containers: {e}")
        
        return containers
    
    def get_container_logs(self, container_name: str, lines: int = 50) -> Dict[str, Any]:
        """קבלת לוגים מcontainer ספציפי"""
        try:
            if self.client:
                container = self.client.containers.get(container_name)
                logs = container.logs(tail=lines).decode('utf-8')
                return {
                    "status": "success",
                    "container": container_name,
                    "logs": logs.split('\n'),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not get logs from {container_name}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_command_in_container(self, container_name: str, command: str) -> Dict[str, Any]:
        """הרצת פקודה בcontainer"""
        try:
            if self.client:
                container = self.client.containers.get(container_name)
                result = container.exec_run(command)
                return {
                    "status": "success",
                    "container": container_name,
                    "command": command,
                    "output": result.output.decode('utf-8'),
                    "exit_code": result.exit_code,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not execute command in {container_name}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def simulate_phishing_attack(self) -> List[Dict[str, Any]]:
        """סימולציה של מתקפת דיוג"""
        steps = []
        
        # שלב 1: משתמש גולש לאתר הדיוג
        step1 = self.execute_command_in_container(
            "victim_workstation",
            "curl -s http://attacker_server > /dev/null && echo 'User accessed phishing site' >> /var/log/custom/activity.log"
        )
        steps.append({
            "step": 1,
            "description": "User clicks phishing link",
            "result": step1
        })
        
        # שלב 2: רישום פעילות חשודה
        step2 = self.execute_command_in_container(
            "attacker_server", 
            "echo 'PHISHING_ATTEMPT: Victim accessed fake login page' >> /var/log/custom/attack.log"
        )
        steps.append({
            "step": 2,
            "description": "Attacker logs phishing attempt",
            "result": step2
        })
        
        # שלב 3: התרעת אבטחה
        step3 = self.execute_command_in_container(
            "log_collector",
            "echo 'SECURITY_ALERT: Suspicious web activity detected' >> /var/log/collected/alerts.log"
        )
        steps.append({
            "step": 3, 
            "description": "Security system generates alert",
            "result": step3
        })
        
        return steps
