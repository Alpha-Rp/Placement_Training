import os
import tempfile
import subprocess
import openai
import random
import json
from typing import Dict, List, Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import black
from datetime import datetime
from io import StringIO
from pylint.reporters.text import TextReporter
import google.generativeai as genai

# Try to import pylint, but don't fail if it's not available
try:
    from pylint.lint import Run as pylint_run
except ImportError:
    pylint_run = None

try:
    import black
except ImportError:
    black = None

class CodeExecutionEnvironment:
    def __init__(self):
        pass

    def execute_code(self, code, language="python"):
        results = {
            "output": "",
            "error": "",
            "execution_time": 0
        }
        
        if language != "python":
            results["error"] = "Only Python language is supported at the moment"
            return results

        start_time = datetime.now()
        
        try:
            # Execute code in a safe way using subprocess
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                file_path = f.name
            
            try:
                process = subprocess.run(
                    ["python", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                results["output"] = process.stdout
                if process.stderr:
                    results["error"] = process.stderr
            finally:
                os.remove(file_path)
                
        except subprocess.TimeoutExpired:
            results["error"] = "Code execution timed out"
        except Exception as e:
            results["error"] = str(e)
        
        end_time = datetime.now()
        results["execution_time"] = (end_time - start_time).total_seconds()
        
        return results

    def analyze_code(self, code, language="python"):
        results = {
            "issues": [],
            "style": [],
            "metrics": {}
        }
        
        if language != "python":
            results["error"] = "Only Python language is supported at the moment"
            return results

        # Run code analysis
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                file_path = f.name
            
            try:
                # Try to use pylint for analysis
                if pylint_run:
                    pylint_run([file_path], do_exit=False)
                else:
                    results["issues"].append("Pylint not available, skipping analysis")
                
                # Count lines of code
                with open(file_path, 'r') as f:
                    code_lines = f.readlines()
                results["metrics"]["lines_of_code"] = len(code_lines)
                
                # Basic style checks
                if not code.strip():
                    results["issues"].append("Code is empty")
                if "    " not in code and "\t" not in code:
                    results["style"].append("Consider using proper indentation")
                if not code.endswith('\n'):
                    results["style"].append("Add a newline at the end of the file")
                
            finally:
                os.remove(file_path)
                
        except Exception as e:
            results["issues"].append(str(e))
        
        return results

class CodeEditor:
    def __init__(self):
        self.execution_env = CodeExecutionEnvironment()

    def format_code(self, code, language="python"):
        if language != "python":
            return code
        try:
            if black:
                return black.format_str(code, mode=black.FileMode())
            else:
                return code
        except:
            return code

    def highlight_code(self, code, language="python"):
        try:
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(style="monokai")
            return highlight(code, lexer, formatter)
        except:
            return code

    def execute_code(self, code, language="python"):
        return self.execution_env.execute_code(code, language)

    def analyze_code(self, code, language="python"):
        return self.execution_env.analyze_code(code, language)

class InterviewGame:
    def __init__(self, api_key: str):
        """Initialize the interview game with Gemini API key."""
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.code_editor = CodeEditor()
        
        # Version control for solutions
        self.solution_history = {}
        
        # Game modes - Updated to match the 5 types
        self.GAME_MODES = {
            "quiz": "Quick Quiz Challenge",
            "scenario": "Real-world Scenario Solver",
            "rapid": "Rapid Fire Round",
            "coding": "Coding Challenge",
            "system_design": "System Design Challenge"
        }
        
        # Supported programming languages
        self.SUPPORTED_LANGUAGES = {
            "python": "Python",
            "javascript": "JavaScript",
            "java": "Java",
            "cpp": "C++"
        }
        
        # Difficulty levels
        self.DIFFICULTY_LEVELS = {
            "beginner": "Beginner",
            "intermediate": "Intermediate",
            "advanced": "Advanced",
            "expert": "Expert"
        }

    def get_game_modes(self) -> Dict[str, str]:
        """Return available game modes."""
        return self.GAME_MODES

    def get_difficulty_levels(self) -> Dict[str, str]:
        """Return available difficulty levels."""
        return self.DIFFICULTY_LEVELS

    def generate_company_context(self, company: str) -> str:
        """Generate company-specific context for interview questions."""
        try:
            prompt = f"""Generate a comprehensive context about {company}'s:
            1. Technical stack and preferred technologies
            2. Company culture and values
            3. Interview process and focus areas
            4. Common interview questions and patterns
            5. Coding style preferences
            
            Format as a detailed paragraph that can be used to make interview questions more company-specific."""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"Error generating company context: {str(e)}")
            return ""

    def generate_quiz_questions(self, job_role: str, difficulty: str = "intermediate", company: str = None) -> List[Dict]:
        """Generate quiz questions with optional company-specific focus."""
        try:
            company_context = ""
            if company:
                company_context = f"""Consider this company context:
                {self.generate_company_context(company)}
                
                Generate questions that are particularly relevant to {company}'s technical stack, 
                interview style, and company values."""

            prompt = f"""Generate 5 multiple-choice interview questions for a {job_role} position at {difficulty} level.
            {company_context}
            
            Format as JSON array:
            [{{
                "question": "question text",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_answer": "correct option",
                "explanation": "detailed explanation"
            }}]"""

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
                return []

        except Exception as e:
            print(f"Error generating quiz questions: {str(e)}")
            return []

    def generate_rapid_fire(self, job_role: str, difficulty: str = "intermediate", num_questions: int = 10) -> List[Dict]:
        """Generate rapid-fire questions for quick responses."""
        prompt = f"""Create {num_questions} rapid-fire technical questions for a {job_role} position at {difficulty} level.
        For each question, format exactly as follows:

        Q1: [Question text]
        Answer: [Correct answer]
        Keywords: [Key terms or concepts that should be in the answer]
        Time: [Time in seconds to answer]

        Q2: [...]
        [and so on...]"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Process the response into a structured format
            questions = []
            raw_questions = response_text.split("\n\n")
            
            for raw_q in raw_questions:
                if not raw_q.strip().startswith("Q"):
                    continue
                
                lines = raw_q.strip().split("\n")
                question = {
                    "id": len(questions) + 1,
                    "question": "",
                    "answer": "",
                    "keywords": [],
                    "time_limit": 30  # Default 30 seconds
                }
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Q"):
                        question["question"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Answer:"):
                        question["answer"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Keywords:"):
                        question["keywords"] = [
                            k.strip() 
                            for k in line.split(":", 1)[1].strip().split(",")
                        ]
                    elif line.startswith("Time:"):
                        try:
                            time_str = line.split(":", 1)[1].strip()
                            question["time_limit"] = int(time_str.split()[0])
                        except:
                            question["time_limit"] = 30
                
                if question["question"] and question["answer"]:
                    questions.append(question)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating rapid-fire questions: {str(e)}")
            return []

    def generate_scenario_challenge(self, job_role: str, difficulty: str = "intermediate") -> Dict:
        """Generate a scenario-based challenge."""
        try:
            prompt = f"""Create a realistic technical scenario for a {job_role} interview at {difficulty} level.
            
            Include:
            1. A detailed scenario description
            2. Clear requirements
            3. Technical constraints
            4. Evaluation criteria
            5. A sample solution that would score 100%
            6. Key points that should be covered in a good answer
            
            Format the response as a JSON object with the following structure:
            {{
                "scenario": "detailed scenario description",
                "requirements": ["req1", "req2", ...],
                "constraints": ["constraint1", "constraint2", ...],
                "evaluation_criteria": ["criterion1", "criterion2", ...],
                "sample_solution": "detailed ideal solution",
                "key_points": ["point1", "point2", ...]
            }}"""

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
                return None

        except Exception as e:
            print(f"Error generating scenario challenge: {str(e)}")
            return None

    def generate_coding_challenge(self, job_role: str, difficulty: str = "intermediate", language: str = "python") -> Dict:
        """Generate a coding challenge with test cases."""
        try:
            prompt = f"""Create a coding challenge for a {job_role} position at {difficulty} level in {language}.
            
            Include:
            1. Problem description
            2. Input/Output format
            3. Constraints
            4. Example test cases
            5. Hidden test cases (for evaluation)
            6. Function signature/template
            7. Sample solution
            
            Format the response as a JSON object with the following structure:
            {{
                "title": "challenge title",
                "description": "detailed problem description",
                "input_format": "description of input format",
                "output_format": "description of output format",
                "constraints": ["constraint1", "constraint2"],
                "example_cases": [
                    {{"input": "example input 1", "output": "expected output 1"}},
                    {{"input": "example input 2", "output": "expected output 2"}}
                ],
                "hidden_cases": [
                    {{"input": "hidden input 1", "output": "expected output 1"}},
                    {{"input": "hidden input 2", "output": "expected output 2"}}
                ],
                "function_template": "code template to start with",
                "sample_solution": "complete working solution",
                "time_limit": "time limit in seconds",
                "memory_limit": "memory limit in MB"
            }}"""

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
                return None

        except Exception as e:
            print(f"Error generating coding challenge: {str(e)}")
            return None

    def generate_system_design_challenge(self, job_role: str, difficulty: str, company: str = None) -> Dict:
        """Generate a system design challenge with optional company focus."""
        try:
            company_context = ""
            if company:
                company_context = f"""Consider this company context:
                {self.generate_company_context(company)}
                
                Generate a system design challenge that reflects {company}'s:
                - Scale and infrastructure preferences
                - Common architectural patterns
                - Technical priorities and trade-offs"""

            prompt = f"""Create a system design challenge for a {job_role} position at {difficulty} level.
            {company_context}
            
            Include:
            1. A real-world system design problem
            2. Clear requirements
            3. Constraints and scale considerations
            4. Evaluation criteria
            5. Sample solution with architecture diagram description
            
            Format as JSON:
            {{
                "description": "detailed problem description",
                "requirements": ["req1", "req2"],
                "constraints": ["constraint1", "constraint2"],
                "evaluation_criteria": ["criterion1", "criterion2"],
                "time_limit": "time in minutes",
                "sample_solution": "detailed solution"
            }}"""

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
                return None

        except Exception as e:
            print(f"Error generating system design challenge: {str(e)}")
            return None

    def evaluate_scenario_solution(self, scenario: Dict, user_solution: str) -> Dict:
        """Evaluate a scenario solution."""
        if not scenario or not user_solution:
            print("Missing scenario or user solution")
            return None

        try:
            # Create a detailed prompt for evaluation
            requirements_text = "\n".join([f"- {req}" for req in scenario.get('requirements', [])])
            constraints_text = "\n".join([f"- {con}" for con in scenario.get('constraints', [])])
            criteria_text = "\n".join([f"- {crit}" for crit in scenario.get('evaluation_criteria', [])])
            key_points_text = "\n".join([f"- {point}" for point in scenario.get('key_points', [])])
            
            prompt = f"""Evaluate this technical solution based on the following scenario and criteria:

SCENARIO:
{scenario['scenario']}

REQUIREMENTS:
{requirements_text}

CONSTRAINTS:
{constraints_text}

EVALUATION CRITERIA:
{criteria_text}

KEY POINTS THAT SHOULD BE COVERED:
{key_points_text}

SAMPLE SOLUTION:
{scenario.get('sample_solution', 'Not provided')}

USER'S SOLUTION:
{user_solution}

Evaluate the solution strictly and provide:
1. A score out of 100 (be strict, only give high scores for truly excellent solutions)
2. Detailed feedback explaining the strengths and weaknesses
3. A score for each evaluation criterion (out of 100)
4. Specific suggestions for improvement
5. Technical accuracy assessment
6. Key points missed by the user
7. Comparison with the sample solution

Format your response exactly as follows:
SCORE: [number 0-100]
FEEDBACK: [detailed feedback]
CRITERION_SCORES:
[criterion1]: [score1]
[criterion2]: [score2]
...
IMPROVEMENTS:
1. [improvement1]
2. [improvement2]
...
TECHNICAL_ACCURACY: [assessment]
MISSED_POINTS:
1. [missed_point1]
2. [missed_point2]
...
SAMPLE_SOLUTION_COMPARISON: [comparison with ideal solution]"""

            print("Sending evaluation prompt to Gemini...")
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            print("Received response from Gemini:", content[:100] + "...")
            
            result = {
                "score": 0,
                "feedback": "",
                "criteria_scores": {},
                "improvements": [],
                "technical_accuracy": "",
                "missed_points": [],
                "sample_solution_comparison": "",
                "sample_solution": scenario.get('sample_solution', '')
            }
            
            # Split content into sections
            sections = content.split("\n\n")
            
            for section in sections:
                section = section.strip()
                if section.startswith("SCORE:"):
                    try:
                        result["score"] = float(section.replace("SCORE:", "").strip())
                    except ValueError as e:
                        print(f"Error parsing score: {e}")
                        result["score"] = 0
                elif section.startswith("FEEDBACK:"):
                    result["feedback"] = section.replace("FEEDBACK:", "").strip()
                elif section.startswith("CRITERION_SCORES:"):
                    scores_section = section.split("\n")[1:]
                    for line in scores_section:
                        if ":" in line:
                            criterion, score = line.split(":", 1)
                            try:
                                result["criteria_scores"][criterion.strip()] = float(score.strip())
                            except ValueError as e:
                                print(f"Error parsing criterion score: {e}")
                                result["criteria_scores"][criterion.strip()] = 0
                elif section.startswith("IMPROVEMENTS:"):
                    improvements = section.split("\n")[1:]
                    result["improvements"] = [
                        imp.strip()[2:].strip() if imp.strip().startswith(("- ", "* ", "1. ")) else imp.strip()
                        for imp in improvements
                        if imp.strip()
                    ]
                elif section.startswith("TECHNICAL_ACCURACY:"):
                    result["technical_accuracy"] = section.replace("TECHNICAL_ACCURACY:", "").strip()
                elif section.startswith("MISSED_POINTS:"):
                    missed_points = section.split("\n")[1:]
                    result["missed_points"] = [
                        point.strip()[2:].strip() if point.strip().startswith(("- ", "* ", "1. ")) else point.strip()
                        for point in missed_points
                        if point.strip()
                    ]
                elif section.startswith("SAMPLE_SOLUTION_COMPARISON:"):
                    result["sample_solution_comparison"] = section.replace("SAMPLE_SOLUTION_COMPARISON:", "").strip()
            
            return result

        except Exception as e:
            print(f"Error evaluating scenario solution: {str(e)}")
            return None

    def evaluate_system_design(self, challenge: Dict, user_solution: str) -> Dict:
        """Evaluate a system design solution."""
        if not challenge or not user_solution:
            return {
                "score": 0,
                "feedback": "No solution provided",
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }

        try:
            # Create evaluation prompt
            prompt = f"""Evaluate this system design solution based on the following criteria:

CHALLENGE TITLE: {challenge.get('title', '')}

SCENARIO: {challenge.get('scenario', '')}

REQUIREMENTS:
{chr(10).join(f"{i+1}. {req}" for i, req in enumerate(challenge.get('requirements', [])))}

CONSTRAINTS:
{chr(10).join(f"{i+1}. {con}" for i, con in enumerate(challenge.get('constraints', [])))}

EVALUATION_CRITERIA:
{chr(10).join(f"{i+1}. {crit}" for i, crit in enumerate(challenge.get('evaluation_criteria', [])))}

USER'S SOLUTION:
{user_solution}

Evaluate thoroughly and provide:
1. A score out of 100 (be strict, consider all requirements and constraints)
2. Detailed feedback on the solution
3. Key strengths of the design
4. Areas that need improvement
5. Specific suggestions for making it better

Format your response exactly as follows:
SCORE: [number 0-100]
FEEDBACK: [detailed feedback]
STRENGTHS:
1. [strength1]
2. [strength2]
...
WEAKNESSES:
1. [weakness1]
2. [weakness2]
...
SUGGESTIONS:
1. [suggestion1]
2. [suggestion2]
..."""

            response = self.model.generate_content(prompt)
            content = response.text.strip()
            sections = content.split("\n\n")
            
            result = {
                "score": 0,
                "feedback": "",
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
            
            current_section = None
            for section in sections:
                if section.startswith("SCORE:"):
                    try:
                        result["score"] = float(section.replace("SCORE:", "").strip())
                    except:
                        result["score"] = 0
                elif section.startswith("FEEDBACK:"):
                    result["feedback"] = section.replace("FEEDBACK:", "").strip()
                elif section.startswith("STRENGTHS:"):
                    result["strengths"] = [
                        line.strip()[2:].strip() 
                        for line in section.split("\n")[1:]
                        if line.strip() and line.strip()[0].isdigit()
                    ]
                elif section.startswith("WEAKNESSES:"):
                    result["weaknesses"] = [
                        line.strip()[2:].strip() 
                        for line in section.split("\n")[1:]
                        if line.strip() and line.strip()[0].isdigit()
                    ]
                elif section.startswith("SUGGESTIONS:"):
                    result["suggestions"] = [
                        line.strip()[2:].strip() 
                        for line in section.split("\n")[1:]
                        if line.strip() and line.strip()[0].isdigit()
                    ]
            
            return result

        except Exception as e:
            print(f"Error evaluating system design: {str(e)}")
            return {
                "score": 0,
                "feedback": "Error evaluating solution",
                "strengths": [],
                "weaknesses": ["Could not evaluate solution"],
                "suggestions": ["Please try again"]
            }

    def evaluate_quiz_answer(self, question: Dict, user_answer: str) -> Dict:
        """Evaluate a quiz answer."""
        is_correct = user_answer.lower() == question['correct_answer'].lower()
        return {
            "is_correct": is_correct,
            "correct_answer": question['correct_answer'],
            "explanation": "Correct!" if is_correct else f"The correct answer is: {question['correct_answer']}"
        }

    def evaluate_rapid_fire(self, question: Dict, user_answer: str) -> Dict:
        """Evaluate a rapid-fire answer."""
        try:
            prompt = f"""Question: {question['question']}
            Answer: {user_answer}
            
            Evaluate if this answer is correct and provide a brief explanation."""
            
            response = self.model.generate_content(prompt)
            evaluation = response.text.strip()
            is_correct = "correct" in evaluation.lower()
            
            return {
                "is_correct": is_correct,
                "score": 100 if is_correct else 50,
                "feedback": evaluation
            }
            
        except Exception as e:
            print(f"Error evaluating rapid-fire answer: {str(e)}")
            return {
                "is_correct": False,
                "score": 0,
                "feedback": "Error evaluating answer"
            }

    def evaluate_debug_solution(self, challenge: Dict, user_solution: str) -> Dict:
        """Evaluate a debugging solution."""
        if not challenge or not user_solution:
            return {
                "score": 0,
                "is_correct": False,
                "feedback": "No solution provided",
                "execution_result": "No code to execute",
                "analysis_result": "No code to analyze",
                "best_practices": []
            }

        try:
            # First, check if the solution is valid Python code
            try:
                compile(user_solution, '<string>', 'exec')
            except Exception as e:
                return {
                    "score": 0,
                    "is_correct": False,
                    "feedback": "Your solution contains syntax errors",
                    "execution_result": f"Syntax Error: {str(e)}",
                    "analysis_result": "Cannot analyze code with syntax errors",
                    "best_practices": ["Fix the syntax errors in your code"]
                }

            # Create a temporary file with the user's solution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(user_solution)
                temp_file = f.name

            results = {
                "passed": 0,
                "total": 0,
                "test_results": [],
                "execution_time": 0,
                "memory_usage": 0,
                "errors": [],
                "style_issues": [],
                "optimization_tips": []
            }

            # Run test cases
            all_test_cases = challenge.get('example_cases', []) + challenge.get('hidden_cases', [])
            results['total'] = len(all_test_cases)

            for test_case in all_test_cases:
                try:
                    # Execute code with test input
                    start_time = datetime.now()
                    process = subprocess.run(
                        ['python', temp_file],
                        input=str(test_case['input']).encode(),
                        capture_output=True,
                        timeout=float(challenge.get('time_limit', 2))
                    )
                    execution_time = (datetime.now() - start_time).total_seconds()

                    output = process.stdout.decode().strip()
                    expected = str(test_case['output']).strip()

                    test_result = {
                        "input": test_case['input'],
                        "expected": expected,
                        "actual": output,
                        "passed": output == expected,
                        "execution_time": execution_time
                    }

                    if test_result['passed']:
                        results['passed'] += 1

                    results['test_results'].append(test_result)
                    results['execution_time'] = max(results['execution_time'], execution_time)

                except subprocess.TimeoutExpired:
                    results['errors'].append(f"Time limit exceeded for input: {test_case['input']}")
                except Exception as e:
                    results['errors'].append(f"Runtime error: {str(e)}")

            # Code style analysis
            if language == "python":
                try:
                    # Run pylint for style checking
                    if pylint_run:
                        pylint_output = StringIO()
                        reporter = TextReporter(pylint_output)
                        pylint_run([temp_file], reporter=reporter, do_exit=False)
                        style_issues = pylint_output.getvalue().split('\n')
                        results['style_issues'] = [issue for issue in style_issues if issue.strip()]
                except Exception as e:
                    print(f"Error in style analysis: {str(e)}")

            # Code optimization suggestions
            prompt = f"""Analyze this code and suggest optimizations:

CODE:
{user_solution}

Provide specific suggestions for:
1. Time complexity improvements
2. Space complexity improvements
3. Code readability
4. Best practices

Format suggestions as a list."""

            try:
                optimization_response = self.model.generate_content(prompt)
                results['optimization_tips'] = optimization_response.text.strip().split('\n')
            except Exception as e:
                print(f"Error getting optimization tips: {str(e)}")

            # Cleanup
            try:
                os.remove(temp_file)
            except:
                pass

            return results

        except Exception as e:
            print(f"Error evaluating debug solution: {str(e)}")
            return {
                "score": 0,
                "is_correct": False,
                "feedback": "Error evaluating solution",
                "execution_result": str(e),
                "analysis_result": "Could not analyze solution",
                "best_practices": ["Ensure your code is valid Python"]
            }

    def evaluate_code_solution(self, challenge: Dict, user_code: str, language: str = "python") -> Dict:
        """Evaluate a coding solution with test cases."""
        if not challenge or not user_code:
            return None

        try:
            # Create a temporary file with the user's code
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                f.write(user_code)
                code_file = f.name

            results = {
                "passed": 0,
                "total": 0,
                "test_results": [],
                "execution_time": 0,
                "memory_usage": 0,
                "errors": [],
                "style_issues": [],
                "optimization_tips": []
            }

            # Run test cases
            all_test_cases = challenge.get('example_cases', []) + challenge.get('hidden_cases', [])
            results['total'] = len(all_test_cases)

            for test_case in all_test_cases:
                try:
                    # Execute code with test input
                    start_time = datetime.now()
                    process = subprocess.run(
                        ["python", code_file],
                        input=str(test_case['input']).encode(),
                        capture_output=True,
                        timeout=float(challenge.get('time_limit', 2))
                    )
                    execution_time = (datetime.now() - start_time).total_seconds()

                    output = process.stdout.decode().strip()
                    expected = str(test_case['output']).strip()

                    test_result = {
                        "input": test_case['input'],
                        "expected": expected,
                        "actual": output,
                        "passed": output == expected,
                        "execution_time": execution_time
                    }

                    if test_result['passed']:
                        results['passed'] += 1

                    results['test_results'].append(test_result)
                    results['execution_time'] = max(results['execution_time'], execution_time)

                except subprocess.TimeoutExpired:
                    results['errors'].append(f"Time limit exceeded for input: {test_case['input']}")
                except Exception as e:
                    results['errors'].append(f"Runtime error: {str(e)}")

            # Code style analysis
            if language == "python":
                try:
                    # Run pylint for style checking
                    if pylint_run:
                        pylint_output = StringIO()
                        reporter = TextReporter(pylint_output)
                        pylint_run([code_file], reporter=reporter, do_exit=False)
                        style_issues = pylint_output.getvalue().split('\n')
                        results['style_issues'] = [issue for issue in style_issues if issue.strip()]
                except Exception as e:
                    print(f"Error in style analysis: {str(e)}")

            # Code optimization suggestions
            prompt = f"""Analyze this code and suggest optimizations:

CODE:
{user_code}

Provide specific suggestions for:
1. Time complexity improvements
2. Space complexity improvements
3. Code readability
4. Best practices

Format suggestions as a list."""

            try:
                optimization_response = self.model.generate_content(prompt)
                results['optimization_tips'] = optimization_response.text.strip().split('\n')
            except Exception as e:
                print(f"Error getting optimization tips: {str(e)}")

            # Cleanup
            try:
                os.remove(code_file)
            except:
                pass

            return results

        except Exception as e:
            print(f"Error evaluating code solution: {str(e)}")
            return None

    def get_practice_websites(self, job_role: str) -> Dict:
        """Get relevant practice websites based on job role."""
        # Define website categories and their descriptions
        websites_by_role = {
            # DevOps and Infrastructure
            "docker": {
                "hands_on_practice": [
                    {"name": "Play with Docker", "url": "https://labs.play-with-docker.com/", "description": "Free Docker playground for learning"},
                    {"name": "Katacoda Docker", "url": "https://www.katacoda.com/courses/docker", "description": "Interactive Docker scenarios"},
                    {"name": "Docker Labs", "url": "https://github.com/docker/labs", "description": "Official Docker tutorials and labs"}
                ],
                "learning_resources": [
                    {"name": "Docker Documentation", "url": "https://docs.docker.com/get-started/", "description": "Official Docker documentation and tutorials"},
                    {"name": "Docker Hub", "url": "https://hub.docker.com/", "description": "Docker container registry and resources"}
                ],
                "certification_prep": [
                    {"name": "Docker Certified Associate", "url": "https://training.mirantis.com/dca-certification-exam/", "description": "Official Docker certification preparation"}
                ]
            },
            "devops engineer": {
                "hands_on_practice": [
                    {"name": "KodeKloud", "url": "https://kodekloud.com/", "description": "DevOps tools and practices"},
                    {"name": "Katacoda", "url": "https://www.katacoda.com/", "description": "Interactive DevOps scenarios"},
                    {"name": "Linux Academy", "url": "https://linuxacademy.com/", "description": "Cloud and DevOps hands-on labs"}
                ],
                "cloud_platforms": [
                    {"name": "AWS Training", "url": "https://aws.amazon.com/training/", "description": "AWS certification and training"},
                    {"name": "Google Cloud Training", "url": "https://cloud.google.com/training", "description": "GCP learning resources"},
                    {"name": "Azure Learn", "url": "https://docs.microsoft.com/learn/azure/", "description": "Microsoft Azure training"}
                ],
                "automation_tools": [
                    {"name": "Ansible Workshops", "url": "https://ansible.github.io/workshops/", "description": "Learn Ansible automation"},
                    {"name": "Jenkins Tutorial", "url": "https://www.jenkins.io/doc/tutorials/", "description": "CI/CD with Jenkins"}
                ]
            },
            "kubernetes": {
                "hands_on_practice": [
                    {"name": "Play with Kubernetes", "url": "https://labs.play-with-k8s.com/", "description": "Interactive K8s environment"},
                    {"name": "Katacoda Kubernetes", "url": "https://www.katacoda.com/courses/kubernetes", "description": "Learn K8s through scenarios"}
                ],
                "learning_resources": [
                    {"name": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/tutorials/", "description": "Official K8s tutorials"},
                    {"name": "K8s the Hard Way", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way", "description": "Deep dive into K8s"}
                ],
                "certification_prep": [
                    {"name": "CKAD Exercises", "url": "https://github.com/dgkanatsios/CKAD-exercises", "description": "Kubernetes certification prep"},
                    {"name": "CKA Course", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/", "description": "Official CKA certification"}
                ]
            },
            # Development and Programming
            "python developer": {
                "coding_practice": [
                    {"name": "HackerRank - Python", "url": "https://www.hackerrank.com/domains/python", "description": "Practice Python fundamentals and algorithms"},
                    {"name": "CodeSignal", "url": "https://app.codesignal.com/", "description": "Python coding challenges used by top companies"},
                    {"name": "LeetCode", "url": "https://leetcode.com/", "description": "Advanced algorithmic challenges in Python"}
                ],
                "learning_resources": [
                    {"name": "Real Python", "url": "https://realpython.com/", "description": "Hands-on Python tutorials and projects"},
                    {"name": "Python.org", "url": "https://www.python.org/", "description": "Official Python documentation and tutorials"},
                    {"name": "PyBites", "url": "https://codechalleng.es/", "description": "Python code challenges and learning paths"}
                ]
            },
            # Data Engineering and Analytics
            "data engineer": {
                "big_data_tools": [
                    {"name": "Databricks Academy", "url": "https://academy.databricks.com/", "description": "Learn Spark and big data processing"},
                    {"name": "Snowflake University", "url": "https://training.snowflake.com/", "description": "Data warehouse training"}
                ],
                "etl_practice": [
                    {"name": "Apache Airflow", "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html", "description": "Learn data pipeline orchestration"},
                    {"name": "dbt Learn", "url": "https://courses.getdbt.com/", "description": "Data transformation tutorials"}
                ],
                "certification_prep": [
                    {"name": "GCP Data Engineer", "url": "https://cloud.google.com/certification/data-engineer", "description": "Google Cloud data engineering certification"},
                    {"name": "Azure Data Engineer", "url": "https://docs.microsoft.com/learn/certifications/azure-data-engineer", "description": "Microsoft Azure data engineering path"}
                ]
            }
        }

        # Add general resources for any role
        general_resources = {
            "learning_platforms": [
                {"name": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "description": "Professional courses for all fields"},
                {"name": "Coursera", "url": "https://www.coursera.org/", "description": "University-level courses in various domains"},
                {"name": "Udemy", "url": "https://www.udemy.com/", "description": "Practical courses in business and technology"}
            ],
            "career_resources": [
                {"name": "Indeed Career Guide", "url": "https://www.indeed.com/career-advice", "description": "Career advice and interview prep"},
                {"name": "Glassdoor", "url": "https://www.glassdoor.com/", "description": "Company reviews and interview experiences"}
            ]
        }

        # Clean and standardize the job role input
        job_role = job_role.lower().strip()
        
        # Common variations and aliases
        role_aliases = {
            "docker": ["docker engineer", "docker developer", "container engineer"],
            "kubernetes": ["k8s", "k8s engineer", "kubernetes engineer", "kubernetes administrator"],
            "devops engineer": ["devops", "site reliability engineer", "sre", "platform engineer"],
            "data engineer": ["data engineering", "etl developer", "data pipeline engineer"]
        }
        
        # Check for exact matches first
        if job_role in websites_by_role:
            return {
                "found": True,
                "websites": {**websites_by_role[job_role], **general_resources},
                "matched_role": job_role
            }
            
        # Check aliases
        for main_role, aliases in role_aliases.items():
            if job_role in aliases:
                return {
                    "found": True,
                    "websites": {**websites_by_role[main_role], **general_resources},
                    "matched_role": main_role
                }
        
        # If no exact match, try fuzzy matching
        highest_similarity = 0
        best_match = None
        
        for role in websites_by_role.keys():
            # Simple similarity check
            similarity = sum(1 for a, b in zip(role, job_role) if a == b) / max(len(role), len(job_role))
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = role
                
        # If we found a reasonably close match
        if highest_similarity > 0.5:
            return {
                "found": True,
                "websites": {**websites_by_role[best_match], **general_resources},
                "matched_role": best_match
            }
            
        # If no good match found, return general resources
        return {
            "found": False,
            "websites": general_resources,
            "message": f"Showing recommended resources for {job_role}"
        }
