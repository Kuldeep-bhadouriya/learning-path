"""
ResourceFinderAgent: Finds high-quality web resources for a learning module.
This agent uses Google Search to find 2-3 articles or videos for each module.
"""

from google.generativeai.types import FunctionDeclaration, Tool

RESOURCE_FINDER_INSTRUCTION = """
You are an expert research assistant. A user will provide you with a
single, specific learning module. Your job is to use the `google_search`
tool to find 2-3 high-quality, free articles or video tutorials for that topic.

RULES:
- You *must* use the `google_search` tool.
- Focus on well-known, free sources like official documentation, popular tutorial sites, or YouTube.
- Return *only* a valid JSON string representing a list of objects.
- Do not add any other text, explanation, or conversational phrases.
- Each object in the list must have two keys: "title" and "url".

Example user topic: "React Hooks (useState, useEffect)"

Your response:
[{"title": "Introducing Hooks – React", "url": "https://react.dev/reference/react/hooks"}, {"title": "React Hooks Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=..."}, {"title": "A Simple Introduction to React Hooks", "url": "https://www.freecodecamp.org/news/simple-introduction-to-react-hooks/"}]
"""

def create_resource_finder_agent():
    """
    Creates and returns a ResourceFinderAgent instance.
    This agent finds web resources for a single learning module using Google Search.
    """
    return {
        "name": "resource_finder_agent",
        "model": "gemini-2.0-flash",
        "instruction": RESOURCE_FINDER_INSTRUCTION,
        "tools": [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="google_search",
                        description="Performs a Google search.",
                        parameters={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The search query."}
                            },
                            "required": ["query"],
                        },
                    )
                ]
            )
        ],
    }
