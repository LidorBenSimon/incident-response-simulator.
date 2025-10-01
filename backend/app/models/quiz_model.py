from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuizOption(BaseModel):
    option_id: str  # A, B, C, D
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    question_id: int
    question_text: str
    options: List[QuizOption]
    explanation: str
    category: str  # phishing, malware, incident_response, forensics

class QuizAnswer(BaseModel):
    question_id: int
    selected_option: str  # A, B, C, D

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    question_id: int
    question_text: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: str
    category: str

class QuizSummary(BaseModel):
    total_questions: int
    correct_answers: int
    score_percentage: float
    letter_grade: str
    results: List[QuizResult]
    category_breakdown: Dict[str, Dict[str, int]]  # category -> {correct: x, total: y}
    recommendations: List[str]
