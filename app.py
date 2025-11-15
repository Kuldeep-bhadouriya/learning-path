"""
Streamlit Web Interface for the Personalized Learning Path Generator.
This wraps the existing main.py logic in a simple web UI.
"""
import streamlit as st
import asyncio
import ast
import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Import the agent factory functions
from curriculum_agent import create_curriculum_agent
from resource_finder_agent import create_resource_finder_agent
from project_planner_agent import create_project_planner_agent
from tools import google_search

# Load environment variables
load_dotenv()

# Try to load from Streamlit secrets if available (for Streamlit Cloud deployment)
if not os.getenv('GOOGLE_API_KEY') and hasattr(st, 'secrets'):
    try:
        os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']
    except:
        pass


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


async def generate_learning_plan(topic_to_learn: str):
    """
    Main function to generate a complete learning plan.
    Returns a tuple of (full_learning_plan, final_project_idea, modules)
    """
    
    # This list will hold our final, structured data
    full_learning_plan = []
    
    # --- STEP 1: Call CurriculumAgent ---
    st.write("### 📚 Step 1: Generating Curriculum Modules...")
    
    try:
        # Run the curriculum agent with the user's topic
        module_list_str = await run_agent_query(
            create_curriculum_agent,
            topic_to_learn
        )
        
        # Parse the Python list string
        modules = ast.literal_eval(module_list_str)
        st.success(f"✓ Generated {len(modules)} modules")
        
        if not modules:
            st.error("✗ Error: CurriculumAgent returned no modules.")
            return None, None, None

    except Exception as e:
        st.error(f"✗ Error in Step 1: {e}")
        return None, None, None

    # --- STEP 2: Call ResourceFinderAgent (in a loop) ---
    st.write("### 🔍 Step 2: Finding Resources for Each Module...")
    
    plan_for_project_agent = []  # To format for the next agent
    progress_bar = st.progress(0)
    
    for i, module in enumerate(modules, 1):
        try:
            st.write(f"  **Module {i}/{len(modules)}:** {module}")
            
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
                    st.success(f"  ✓ Found {len(resources)} resources")
                else:
                    # If no markdown, try to parse the whole string
                    resources = json.loads(resources_json_str)
                    st.success(f"  ✓ Found {len(resources)} resources")
            except json.JSONDecodeError:
                st.warning(f"  ⚠ Warning: Could not parse resources JSON")
                resources = []
            
            # Store the structured data
            full_learning_plan.append({
                "module": module,
                "resources": resources
            })
            plan_for_project_agent.append(f"Module: {module}")
            
            # Update progress
            progress_bar.progress(i / len(modules))

        except Exception as e:
            st.warning(f"  ⚠ Error finding resources for '{module}': {e}")
            # Add with empty resources so we can continue
            full_learning_plan.append({
                "module": module,
                "resources": []
            })

    # --- STEP 3: Call ProjectPlannerAgent ---
    st.write("### 🎯 Step 3: Generating Capstone Project Idea...")
    
    try:
        # Create a simple string representation of the plan for the agent
        plan_str_for_agent = "\n".join(plan_for_project_agent)
        
        # Run the project planner agent with the full plan
        final_project_idea = await run_agent_query(
            create_project_planner_agent,
            plan_str_for_agent
        )
        
        st.success("✓ Project idea generated")

    except Exception as e:
        st.error(f"✗ Error in Step 3: {e}")
        final_project_idea = "Could not generate project idea."

    return full_learning_plan, final_project_idea, modules


def main():
    """
    Main Streamlit application.
    """
    st.set_page_config(
        page_title="Learning Path Generator",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🤖 Personalized Learning Path Generator")
    st.markdown("---")
    
    # Sidebar for API key configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.success("✓ API Key loaded from .env")
        else:
            st.error("✗ GOOGLE_API_KEY not found in .env file")
            st.info("Please add your Google AI API key to the .env file")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app generates a complete personalized learning plan using three AI agents:
        - **CurriculumAgent**: Creates learning modules
        - **ResourceFinderAgent**: Finds web resources
        - **ProjectPlannerAgent**: Suggests capstone projects
        """)
    
    # Main input area
    st.header("What do you want to learn?")
    
    # Example topics
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Python for Data Analysis"):
            st.session_state.topic = "Learn Python for Data Analysis"
    with col2:
        if st.button("🌐 Web Development"):
            st.session_state.topic = "Learn Web Development with React and Node.js"
    with col3:
        if st.button("🤖 Machine Learning"):
            st.session_state.topic = "Learn Machine Learning Fundamentals"
    
    # Text input
    topic_input = st.text_input(
        "Enter your learning topic:",
        value=st.session_state.get('topic', ''),
        placeholder="e.g., Learn Python for Data Analysis, Master Digital Marketing, etc."
    )
    
    # Generate button
    if st.button("🚀 Generate Learning Plan", type="primary"):
        if not topic_input:
            st.warning("⚠ Please enter a topic to learn")
        elif not os.getenv('GOOGLE_API_KEY'):
            st.error("✗ Please configure your GOOGLE_API_KEY in the .env file")
        else:
            # Show loading state
            with st.spinner("Generating your personalized learning plan..."):
                # Run the async function
                full_learning_plan, final_project_idea, modules = asyncio.run(
                    generate_learning_plan(topic_input)
                )
            
            if full_learning_plan:
                # Display the results
                st.markdown("---")
                st.header("✅ Your Personalized Learning Plan")
                st.subheader(f"Topic: {topic_input}")
                st.markdown("---")
                
                # Display modules and resources
                for i, item in enumerate(full_learning_plan, 1):
                    with st.expander(f"📚 Module {i}: {item['module']}", expanded=True):
                        if item['resources']:
                            for res in item['resources']:
                                st.markdown(f"**• {res.get('title', 'Untitled')}**")
                                st.markdown(f"  [{res.get('url', 'No URL')}]({res.get('url', '#')})")
                                if res.get('snippet'):
                                    st.markdown(f"  _{res.get('snippet', '')}_")
                                st.markdown("")
                        else:
                            st.info("No resources found for this module")
                
                # Display capstone project
                st.markdown("---")
                st.header("🎯 Recommended Capstone Project")
                st.markdown(final_project_idea)
                
                # Download option
                st.markdown("---")
                
                # Create downloadable text version
                download_content = f"PERSONALIZED LEARNING PLAN\n"
                download_content += f"Topic: {topic_input}\n"
                download_content += "=" * 60 + "\n\n"
                
                for i, item in enumerate(full_learning_plan, 1):
                    download_content += f"MODULE {i}: {item['module']}\n"
                    if item['resources']:
                        for res in item['resources']:
                            download_content += f"  • {res.get('title', 'Untitled')}\n"
                            download_content += f"    {res.get('url', 'No URL')}\n"
                    else:
                        download_content += "  • (No resources found)\n"
                    download_content += "\n"
                
                download_content += "=" * 60 + "\n"
                download_content += "RECOMMENDED CAPSTONE PROJECT:\n"
                download_content += "=" * 60 + "\n"
                download_content += final_project_idea + "\n"
                
                st.download_button(
                    label="📥 Download Learning Plan",
                    data=download_content,
                    file_name=f"learning_plan_{topic_input.replace(' ', '_')}.txt",
                    mime="text/plain"
                )


if __name__ == "__main__":
    main()
