from models.quiz_model import QuizQuestion, QuizOption

# Quiz questions database
QUIZ_QUESTIONS = [
    QuizQuestion(
        question_id=1,
        question_text="You receive an email claiming to be from your bank, asking you to verify your account by clicking a link. The email uses urgent language like 'Your account will be suspended in 24 hours!' What should be your FIRST action?",
        options=[
            QuizOption(option_id="A", text="Click the link to verify your account immediately", is_correct=False),
            QuizOption(option_id="B", text="Reply to the email asking for more information", is_correct=False),
            QuizOption(option_id="C", text="Report the email to your security team and delete it", is_correct=True),
            QuizOption(option_id="D", text="Forward the email to your colleagues to warn them", is_correct=False)
        ],
        explanation="The correct action is to report the email to your security team and delete it. This is a classic phishing attempt using urgency and fear tactics. Never click links in suspicious emails, don't reply (confirms your email is active), and don't forward (spreads the threat). Always verify through official channels.",
        category="phishing"
    ),
    
    QuizQuestion(
        question_id=2,
        question_text="You notice a workstation is making unusually high amounts of outbound network connections to an unknown IP address. What type of activity does this MOST likely indicate?",
        options=[
            QuizOption(option_id="A", text="Normal software update process", is_correct=False),
            QuizOption(option_id="B", text="Data exfiltration or command and control (C2) communication", is_correct=True),
            QuizOption(option_id="C", text="User downloading large files", is_correct=False),
            QuizOption(option_id="D", text="Network configuration error", is_correct=False)
        ],
        explanation="High volumes of outbound connections to unknown IPs typically indicate data exfiltration or C2 communication with an attacker's server. This is a critical indicator of compromise (IoC) that requires immediate investigation and likely system isolation.",
        category="malware"
    ),
    
    QuizQuestion(
        question_id=3,
        question_text="During incident response, you discover an attacker has gained access to one workstation. What is the PRIMARY reason you should isolate this system from the network?",
        options=[
            QuizOption(option_id="A", text="To preserve evidence for forensic analysis", is_correct=False),
            QuizOption(option_id="B", text="To prevent the attacker from moving laterally to other systems", is_correct=True),
            QuizOption(option_id="C", text="To stop the user from working on the system", is_correct=False),
            QuizOption(option_id="D", text="To force the attacker to reveal their identity", is_correct=False)
        ],
        explanation="The primary reason for isolation is containment - preventing lateral movement to other systems. While preserving evidence is important, stopping the spread of the attack takes priority. Isolation limits the attacker's ability to access additional resources and cause further damage.",
        category="incident_response"
    ),
    
    QuizQuestion(
        question_id=4,
        question_text="You detect multiple failed login attempts for an administrator account from different IP addresses within a short time period. What attack is this MOST likely?",
        options=[
            QuizOption(option_id="A", text="Phishing attack", is_correct=False),
            QuizOption(option_id="B", text="Distributed brute force attack", is_correct=True),
            QuizOption(option_id="C", text="SQL injection", is_correct=False),
            QuizOption(option_id="D", text="Man-in-the-middle attack", is_correct=False)
        ],
        explanation="Multiple failed logins from different IPs indicates a distributed brute force attack, where attackers try many password combinations across multiple sources to avoid detection. This requires immediate action: account lockout, IP blocking, and password reset.",
        category="incident_response"
    ),
    
    QuizQuestion(
        question_id=5,
        question_text="A user reports that all their files have been encrypted and there's a file called 'README_DECRYPT.txt' on their desktop. What type of malware is this?",
        options=[
            QuizOption(option_id="A", text="Trojan horse", is_correct=False),
            QuizOption(option_id="B", text="Spyware", is_correct=False),
            QuizOption(option_id="C", text="Ransomware", is_correct=True),
            QuizOption(option_id="D", text="Rootkit", is_correct=False)
        ],
        explanation="File encryption with a ransom note is the hallmark of ransomware. Immediate actions: isolate the system, don't pay the ransom, check backups, and report to security team. Ransomware can spread rapidly across networks if not contained quickly.",
        category="malware"
    ),
    
    QuizQuestion(
        question_id=6,
        question_text="In digital forensics, why is it critical to create a bit-by-bit copy of a hard drive before analysis?",
        options=[
            QuizOption(option_id="A", text="To make the analysis faster", is_correct=False),
            QuizOption(option_id="B", text="To preserve the original evidence and maintain chain of custody", is_correct=True),
            QuizOption(option_id="C", text="To reduce storage costs", is_correct=False),
            QuizOption(option_id="D", text="To make the data easier to read", is_correct=False)
        ],
        explanation="Creating a forensic image preserves the original evidence in its exact state, maintaining integrity and chain of custody for potential legal proceedings. Any analysis should be done on the copy, never the original, to prevent accidental modification of evidence.",
        category="forensics"
    ),
    
    QuizQuestion(
        question_id=7,
        question_text="You observe an employee account accessing servers and files they've never accessed before, outside of normal business hours. What should you do FIRST?",
        options=[
            QuizOption(option_id="A", text="Immediately disable the account", is_correct=False),
            QuizOption(option_id="B", text="Call the employee to ask what they're doing", is_correct=False),
            QuizOption(option_id="C", text="Monitor the activity and gather more information while alerting security team", is_correct=True),
            QuizOption(option_id="D", text="Ignore it as the employee may be working overtime", is_correct=False)
        ],
        explanation="While monitoring and alerting security is the best first step, this allows you to gather critical intelligence about what's being accessed and how. Immediately disabling might tip off the attacker if the account is compromised. Never ignore unusual access patterns.",
        category="incident_response"
    ),
    
    QuizQuestion(
        question_id=8,
        question_text="Which of the following is the BEST indicator that an email might be a phishing attempt?",
        options=[
            QuizOption(option_id="A", text="The email is from someone you don't know", is_correct=False),
            QuizOption(option_id="B", text="The sender's email address doesn't match the claimed organization's domain", is_correct=True),
            QuizOption(option_id="C", text="The email contains spelling errors", is_correct=False),
            QuizOption(option_id="D", text="The email was sent late at night", is_correct=False)
        ],
        explanation="A mismatched sender domain is the strongest technical indicator of phishing. For example, an email claiming to be from PayPal but sent from 'paypa1-security@gmail.com' is clearly fraudulent. While spelling errors are suspicious, domain spoofing is a definitive red flag.",
        category="phishing"
    ),
    
    QuizQuestion(
        question_id=9,
        question_text="What is the PRIMARY purpose of the 'Lessons Learned' phase in the incident response lifecycle?",
        options=[
            QuizOption(option_id="A", text="To assign blame for the incident", is_correct=False),
            QuizOption(option_id="B", text="To improve future incident response and prevent similar incidents", is_correct=True),
            QuizOption(option_id="C", text="To document incidents for compliance requirements only", is_correct=False),
            QuizOption(option_id="D", text="To calculate the financial cost of the incident", is_correct=False)
        ],
        explanation="Lessons Learned focuses on continuous improvement - identifying what worked, what didn't, and how to prevent similar incidents. This isn't about blame but about strengthening security posture and response capabilities. Documentation and cost analysis are byproducts, not the primary goal.",
        category="incident_response"
    ),
    
    QuizQuestion(
        question_id=10,
        question_text="You find a suspicious PowerShell script running on a workstation. What information is MOST valuable to collect first for investigation?",
        options=[
            QuizOption(option_id="A", text="The script's execution time and command line arguments", is_correct=True),
            QuizOption(option_id="B", text="The workstation's IP address", is_correct=False),
            QuizOption(option_id="C", text="The user's email address", is_correct=False),
            QuizOption(option_id="D", text="The workstation's operating system version", is_correct=False)
        ],
        explanation="Command line arguments and execution context reveal what the script does and how it was launched. This helps determine if it's malicious, part of an attack chain, or legitimate automation. This forensic data is time-sensitive and should be captured immediately before it's lost.",
        category="forensics"
    )
]

def get_all_quiz_questions():
    """Return all quiz questions"""
    return QUIZ_QUESTIONS

def get_question_by_id(question_id: int):
    """Get a specific question by ID"""
    for question in QUIZ_QUESTIONS:
        if question.question_id == question_id:
            return question
    return None
