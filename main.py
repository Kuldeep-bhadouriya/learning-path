"""
Main orchestrator for the Personalized Learning Path Generator.
This script coordinates three agents to create a complete learning plan:
1. CurriculumAgent - generates learning modules
2. ResourceFinderAgent - finds web resources for each module
3. ProjectPlannerAgent - creates a capstone project idea
"""
import asyncio
import ast
import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
from tools import google_search

# Import the agent factory functions
from curriculum_agent import create_curriculum_agent
from resource_finder_agent import create_resource_finder_agent
from project_planner_agent import create_project_planner_agent

# Load environment variables from .env file
load_dotenv()


async def run_agent_query(agent_creator, user_input: str) -> str:
    """
    Helper function to run an agent and get its text response, handling tool calls.
    """
    agent = agent_creator()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(agent['model'])

    full_prompt = f"{agent['instruction']}\n\nUser request: {user_input}"
    
    tools = agent.get('tools')

    if not tools:
        response = await model.generate_content_async(full_prompt)
        return response.text

    # First API call: may return a function call
    response = await model.generate_content_async(full_prompt, tools=tools)
    
    # Check for function call and execute
    if response.candidates and response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        
        if function_call.name == "google_search":
            tool_result = google_search(**function_call.args)
            
            response = await model.generate_content_async(
                [
                    types.Content(parts=[types.Part.from_function_call(function_call)]),
                    types.Content(
                        parts=[
                            types.Part.from_function_response(
                                name=function_call.name,
                                response={"content": tool_result},
                            )
                        ]
                    ),
                ]
            )

    return response.text


async def main():
    """
    Main orchestrator for the Personalized Learning Path Generator.
    This script manually controls the flow of information between agents
    to demonstrate state management.
    """
    
    # --- CONFIGURATION ---
    # This is the topic the user wants to learn.
    # You can change this to test different topics.
    topic_to_learn = "Learn Python for Data Analysis"
    
    print("=" * 60)
    print("🤖 PERSONALIZED LEARNING PATH GENERATOR")
    print("=" * 60)
    print(f"Topic: {topic_to_learn}")
    print("=" * 60)

    # This list will hold our final, structured data
    full_learning_plan = []
    
    # --- STEP 1: Call CurriculumAgent ---
    print("\n[STEP 1] Generating curriculum modules...")
    print("-" * 60)
    
    try:
        # Run the curriculum agent with the user's topic
        module_list_str = await run_agent_query(
            create_curriculum_agent,
            topic_to_learn
        )
        
        print(f"✓ Raw response: {module_list_str[:200]}...")
        
        # Parse the Python list string
        modules = ast.literal_eval(module_list_str)
        print(f"✓ Generated {len(modules)} modules")
        
        if not modules:
            print("✗ Error: CurriculumAgent returned no modules.")
            return

    except Exception as e:
        print(f"✗ Error in Step 1: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- STEP 2: Call ResourceFinderAgent (in a loop) ---
    print(f"\n[STEP 2] Finding resources for each module...")
    print("-" * 60)
    
    plan_for_project_agent = []  # To format for the next agent
    
    for i, module in enumerate(modules, 1):
        try:
            print(f"\n  Module {i}/{len(modules)}: {module}")
            
            # Run the resource finder agent with the module topic
            resources_json_str = await run_agent_query(
                create_resource_finder_agent,
                module
            )
            
            # Extract the JSON from the markdown
            try:
                match = re.search(r"```json\n(.*?)\n```", resources_json_str, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    resources = json.loads(json_str)
                    print(f"  ✓ Found {len(resources)} resources")
                else:
                    # If no markdown, try to parse the whole string
                    resources = json.loads(resources_json_str)
                    print(f"  ✓ Found {len(resources)} resources")
            except json.JSONDecodeError:
                print(f"  ✗ Warning: Could not parse resources JSON")
                resources = []
            
            # Store the structured data
            full_learning_plan.append({
                "module": module,
                "resources": resources
            })
            plan_for_project_agent.append(f"Module: {module}")

        except Exception as e:
            print(f"  ✗ Error finding resources for '{module}': {e}")
            # Add with empty resources so we can continue
            full_learning_plan.append({
                "module": module,
                "resources": []
            })

    # --- STEP 3: Call ProjectPlannerAgent ---
    print(f"\n[STEP 3] Generating capstone project idea...")
    print("-" * 60)
    
    try:
        # Create a simple string representation of the plan for the agent
        plan_str_for_agent = "\n".join(plan_for_project_agent)
        
        # Run the project planner agent with the full plan
        final_project_idea = await run_agent_query(
            create_project_planner_agent,
            plan_str_for_agent
        )
        
        print(f"✓ Project idea generated")

    except Exception as e:
        print(f"✗ Error in Step 3: {e}")
        import traceback
        traceback.print_exc()
        final_project_idea = "Could not generate project idea."


    # --- STEP 4: Format and Print the Final Plan ---
    print("\n\n" + "=" * 60)
    print("✅ YOUR PERSONALIZED LEARNING PLAN")
    print("=" * 60)
    print(f"TOPIC: {topic_to_learn}")
    print("=" * 60)
    
    for i, item in enumerate(full_learning_plan, 1):
        print(f"\n📚 MODULE {i}: {item['module']}")
        if item['resources']:
            for res in item['resources']:
                print(f"  • {res.get('title', 'Untitled')}")
                print(f"    {res.get('url', 'No URL')}")
        else:
            print("  • (No resources found)")
            
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED PROJECT:")
    print("=" * 60)
    print(final_project_idea)
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()