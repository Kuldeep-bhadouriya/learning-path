"""
CurriculumAgent: Generates a structured list of learning modules for a given topic.
This agent takes a user's learning topic and breaks it down into 5-7 core modules.
"""

# This system prompt is crucial. It forces the LLM to return *only*
# a parseable Python list as a string.
CURRICULUM_AGENT_INSTRUCTION = """
You are an expert curriculum designer. A user will provide you with a topic
they want to learn. Your job is to break that topic down into a
logical, step-by-step list of 5-7 core learning modules.

RULES:
- Only output a valid Python list of strings.
- Do not add any other text, explanation, or conversational phrases.
- Each string in the list should be a single, concise learning module.

Example user topic: "Learn Python"

Your response:
["1. Python Basics (Syntax, Variables, Data Types)", "2. Control Flow (Loops, Conditionals)", "3. Functions and Scope", "4. Data Structures (Lists, Dictionaries, Tuples)", "5. Object-Oriented Programming (Classes, Inheritance)", "6. Error Handling and File I/O"]
"""

def create_curriculum_agent():
    """
    Creates and returns a CurriculumAgent instance.
    This agent generates a list of learning modules for any topic.
    """
    return {
        "name": "curriculum_agent",
        "model": "gemini-2.0-flash",
        "instruction": CURRICULUM_AGENT_INSTRUCTION
    }
