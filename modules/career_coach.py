import google.generativeai as genai
import datetime
from typing import Dict, List, Optional
import json
import os

class CareerCoach:
    def __init__(self, api_key: str):
        """Initialize the career coach with Gemini API key."""
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def generate_daily_motivation(self, user_profile: Dict) -> Dict:
        """Generate personalized daily motivation message."""
        try:
            prompt = f"""
            Create a motivational message for a {user_profile['job_role']} professional.
            Consider their goals: {user_profile['goals']}
            Recent achievements: {user_profile['achievements']}
            Areas of improvement: {user_profile['improvement_areas']}
            
            Return the response in this JSON format:
            {{
                "message": "The motivational message",
                "focus_area": "Today's focus area",
                "quick_tip": "A practical tip for today",
                "quote": "An inspiring quote",
                "action_item": "One specific action to take today"
            }}
            """
            
            response = self.model.generate_content(prompt)
            # Clean the response text to ensure it's valid JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                # Fallback to a structured response if JSON parsing fails
                return {
                    "message": response_text,
                    "focus_area": "General Development",
                    "quick_tip": "Stay focused on your goals",
                    "quote": "Success is not final, failure is not fatal",
                    "action_item": "Review your goals for today"
                }
        except Exception as e:
            print(f"Error generating motivation: {str(e)}")
            return None
    
    def generate_weekly_challenge(self, user_profile: Dict) -> Dict:
        """Generate personalized weekly skill challenge."""
        try:
            prompt = f"""
            Create a weekly skill challenge for a {user_profile['job_role']} professional.
            Current skill level: {user_profile['skill_level']}
            Available time: {user_profile['available_time']} hours per week
            Goals: {user_profile['goals']}
            Current skills: {user_profile['skills']}
            
            Return the response in this JSON format:
            {{
                "challenge_name": "Name of the challenge",
                "description": "Description of the challenge",
                "daily_tasks": [
                    {{
                        "day": "Day of the week",
                        "task": "Task description",
                        "time_required": "Estimated time",
                        "resources": "Helpful resources"
                    }}
                ],
                "success_criteria": "How to measure success",
                "bonus_challenge": "Additional optional challenge",
                "expected_outcome": "What to expect after completion"
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                return {
                    "challenge_name": "Weekly Skill Development",
                    "description": response_text,
                    "daily_tasks": [
                        {
                            "day": "Monday",
                            "task": "Review your goals",
                            "time_required": "1 hour",
                            "resources": "Your career goals document"
                        }
                    ],
                    "success_criteria": "Complete all daily tasks",
                    "bonus_challenge": "Share your progress with a mentor",
                    "expected_outcome": "Improved skills and knowledge"
                }
        except Exception as e:
            print(f"Error generating weekly challenge: {str(e)}")
            return None
    
    def generate_monthly_review(self, user_profile: Dict, monthly_data: Dict) -> Dict:
        """Generate monthly progress review."""
        try:
            prompt = f"""
            Create a monthly progress review for a {user_profile['job_role']} professional.
            
            Monthly Data:
            Completed challenges: {monthly_data['completed_challenges']}
            Achievements: {monthly_data['achievements']}
            Skills improved: {monthly_data['skills_improved']}
            Time invested: {monthly_data['time_invested']} hours
            
            Return the response in this JSON format:
            {{
                "summary": "Overall progress summary",
                "key_achievements": ["List of key achievements"],
                "areas_of_growth": [
                    {{
                        "skill": "Skill name",
                        "progress": "Progress made",
                        "next_steps": "Recommended next steps"
                    }}
                ],
                "insights": ["List of insights"],
                "next_month_focus": {{
                    "primary_goal": "Main goal for next month",
                    "action_items": ["List of action items"]
                }}
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                return {
                    "summary": response_text,
                    "key_achievements": monthly_data['achievements'],
                    "areas_of_growth": [
                        {
                            "skill": "General Development",
                            "progress": "In Progress",
                            "next_steps": "Continue with current learning path"
                        }
                    ],
                    "insights": ["Keep up the good work!"],
                    "next_month_focus": {
                        "primary_goal": "Continue skill development",
                        "action_items": ["Review monthly goals", "Plan next steps"]
                    }
                }
        except Exception as e:
            print(f"Error generating monthly review: {str(e)}")
            return None
    
    def generate_action_plan(self, user_profile: Dict, goals: List[str]) -> Dict:
        """Generate personalized action plan."""
        try:
            prompt = f"""
            Create an action plan for a {user_profile['job_role']} professional.
            Goals: {goals}
            Current skills: {user_profile['skills']}
            Available time: {user_profile['available_time']} hours per week
            
            Return the response in this JSON format:
            {{
                "plan_name": "Name of the action plan",
                "overview": "Plan overview",
                "milestones": [
                    {{
                        "name": "Milestone name",
                        "timeframe": "Expected duration",
                        "tasks": [
                            {{
                                "task": "Task description",
                                "priority": "High/Medium/Low",
                                "resources": "Helpful resources",
                                "success_criteria": "How to measure completion"
                            }}
                        ]
                    }}
                ],
                "success_metrics": ["List of success metrics"],
                "potential_challenges": [
                    {{
                        "challenge": "Potential challenge",
                        "solution": "Proposed solution"
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                return {
                    "plan_name": "Career Development Plan",
                    "overview": response_text,
                    "milestones": [
                        {
                            "name": "Initial Milestone",
                            "timeframe": "1 month",
                            "tasks": [
                                {
                                    "task": "Review and set goals",
                                    "priority": "High",
                                    "resources": "Career planning tools",
                                    "success_criteria": "Clear goals defined"
                                }
                            ]
                        }
                    ],
                    "success_metrics": ["Goal completion", "Skill improvement"],
                    "potential_challenges": [
                        {
                            "challenge": "Time management",
                            "solution": "Create a detailed schedule"
                        }
                    ]
                }
        except Exception as e:
            print(f"Error generating action plan: {str(e)}")
            return None
    
    def generate_progress_feedback(self, user_profile: Dict, progress_data: Dict) -> Dict:
        """Generate progress feedback."""
        try:
            prompt = f"""
            Provide progress feedback for a {user_profile['job_role']} professional.
            
            Progress Data:
            Recent progress: {progress_data['recent_progress']}
            Completed tasks: {progress_data['completed_tasks']}
            Challenges faced: {progress_data['challenges']}
            Time spent: {progress_data['time_spent']} hours
            
            Return the response in this JSON format:
            {{
                "overall_assessment": "Overall progress assessment",
                "key_observations": [
                    {{
                        "observation": "Key observation",
                        "impact": "Impact on progress",
                        "recommendation": "Recommendation"
                    }}
                ],
                "strengths": [
                    {{
                        "strength": "Identified strength",
                        "how_to_leverage": "How to leverage this strength"
                    }}
                ],
                "improvement_areas": [
                    {{
                        "area": "Area for improvement",
                        "why_important": "Why this matters",
                        "how_to_improve": "How to improve"
                    }}
                ],
                "next_steps": ["List of next steps"],
                "motivation": "Motivational message"
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                return {
                    "overall_assessment": response_text,
                    "key_observations": [
                        {
                            "observation": "Progress tracking",
                            "impact": "Positive",
                            "recommendation": "Continue current approach"
                        }
                    ],
                    "strengths": [
                        {
                            "strength": "Dedication",
                            "how_to_leverage": "Maintain consistent effort"
                        }
                    ],
                    "improvement_areas": [
                        {
                            "area": "Time management",
                            "why_important": "Efficiency",
                            "how_to_improve": "Create detailed schedule"
                        }
                    ],
                    "next_steps": ["Review feedback", "Update goals"],
                    "motivation": "Keep up the great work!"
                }
        except Exception as e:
            print(f"Error generating progress feedback: {str(e)}")
            return None
