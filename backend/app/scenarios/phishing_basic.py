from models.scenario import Scenario, ContainerConfig, ScenarioStep, ScenarioType

def create_basic_phishing_scenario() -> Scenario:
    """יצירת תרחיש דיוג בסיסי"""
    
    # הגדרת containers שנצטרך
    containers = [
        ContainerConfig(
            name="victim_workstation",
            image="ubuntu:20.04",
            ports={"22": 2222, "80": 8080},
            environment={
                "USER": "john_doe",
                "HOSTNAME": "DESKTOP-VICTIM01"
            },
            commands=[
                "apt update && apt install -y openssh-server apache2 curl",
                "service ssh start",
                "service apache2 start",
                "echo 'Victim workstation is ready' > /var/log/setup.log"
            ]
        ),
        ContainerConfig(
            name="attacker_server",
            image="ubuntu:20.04", 
            ports={"80": 9090, "443": 9443},
            environment={
                "ATTACK_TYPE": "phishing",
                "TARGET": "victim_workstation"
            },
            commands=[
                "apt update && apt install -y apache2 python3 python3-pip",
                "service apache2 start",
                "echo 'Attacker server ready' > /var/log/attacker.log"
            ]
        )
    ]
    
    # שלבי התרחיש
    steps = [
        ScenarioStep(
            step_id=1,
            name="Initial Setup",
            description="הכנת הסביבה - הרצת מחשב הקורבן ושרת התוקף",
            duration_seconds=30,
            commands=[
                "docker-compose up -d victim_workstation attacker_server"
            ],
            expected_logs=[
                "Victim workstation is ready",
                "Attacker server ready"
            ]
        ),
        ScenarioStep(
            step_id=2,
            name="Phishing Email Simulation",
            description="שליחת מייל דיוג מדומה (סימולציה)",
            duration_seconds=10,
            commands=[
                "echo 'PHISHING_EMAIL: Urgent! Click here to verify your account: http://evil-bank.com/login' >> /tmp/email_log.txt"
            ],
            expected_logs=[
                "PHISHING_EMAIL sent to john_doe@company.com"
            ]
        ),
        ScenarioStep(
            step_id=3,
            name="User Clicks Malicious Link",
            description="המשתמש לוחץ על הקישור החשוד (סימולציה)",
            duration_seconds=15,
            commands=[
                "curl -s http://attacker_server:80/fake_login > /dev/null",
                "echo 'WEB_ACCESS: User accessed suspicious URL http://evil-bank.com/login' >> /tmp/web_log.txt"
            ],
            expected_logs=[
                "WEB_ACCESS: suspicious domain accessed",
                "HTTP_REQUEST to known malicious IP"
            ]
        ),
        ScenarioStep(
            step_id=4,
            name="Credential Harvesting",
            description="שרת התוקף אוסף את פרטי הכניסה (סימולציה)",
            duration_seconds=20,
            commands=[
                "echo 'CREDENTIAL_STOLEN: username=john_doe, password=******' >> /tmp/attacker_log.txt",
                "echo 'DATA_EXFIL: Sending stolen credentials to C&C server' >> /tmp/attacker_log.txt"
            ],
            expected_logs=[
                "CREDENTIAL_STOLEN: sensitive data harvested",
                "DATA_EXFIL: outbound connection detected"
            ]
        ),
        ScenarioStep(
            step_id=5,
            name="Alert Generation",
            description="מערכת האבטחה מזהה פעילות חשודה",
            duration_seconds=10,
            commands=[
                "echo 'SECURITY_ALERT: Suspicious web activity detected from DESKTOP-VICTIM01' >> /tmp/security_log.txt",
                "echo 'SECURITY_ALERT: Possible credential theft detected' >> /tmp/security_log.txt"
            ],
            expected_logs=[
                "SECURITY_ALERT: Suspicious activity",
                "SECURITY_ALERT: Credential theft"
            ]
        )
    ]
    
    # יצירת התרחיש המלא
    scenario = Scenario(
        name="Basic Phishing Attack",
        description="תרחיש דיוג בסיסי שמדמה מתקפת דיוג ואיסוף פרטי כניסה",
        type=ScenarioType.PHISHING,
        difficulty="beginner",
        estimated_duration=120,  # 2 דקות
        containers=containers,
        steps=steps,
        learning_objectives=[
            "זיהוי סימני דיוג במיילים",
            "ניטור תעבורת רשת חשודה", 
            "תגובה מהירה לאיסוף פרטי כניסה",
            "ניתוח לוגי אבטחה"
        ]
    )
    
    return scenario

# התרחיש המוכן לשימוש
BASIC_PHISHING_SCENARIO = create_basic_phishing_scenario()
