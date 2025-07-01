# cognify_crewai.py

# --- Core Libraries ---
import streamlit as st  # The web framework used to build the user interface
import os               # Used to interact with the operating system, primarily for API keys
import json             # Used to parse the JSON output from the AI agents
import time             # Used for creating artificial delays to improve user experience

# --- CrewAI Imports ---
# These are the fundamental building blocks for creating AI agent crews
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI # This provides the connection to OpenAI's models

# Fix for ChromaDB/SQLite3 compatibility issue
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# --- Streamlit Page Configuration ---
# Sets the title, icon, and layout for the web application page
st.set_page_config(
    page_title="Cognify",
    page_icon="🧠",
    layout="centered"
)

# --- API Key and LLM (Large Language Model) Setup ---
# Tries to get the OpenAI API key first from Streamlit's secrets manager (for deployment)
# and then falls back to an environment variable (for local development).
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

# Check if an API key was found and configure the LLM
if api_key:
    # Set environment variables required by CrewAI and LangChain
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4.1-nano"  # Specify a cost-effective and capable model

    # Initialize the LLM that all agents in this application will use.
    # 'temperature=0.7' makes the output creative but not overly random.
    llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.7)
else:
    # If no API key is found, set the llm to None. The app will show a warning.
    llm = None


# --- CrewAI Agent & Task Functions ---
# Each function below defines a specialized crew to handle a specific part of the workflow.

def run_clarification_crew(task_title: str) -> dict:
    """
    This function assembles and runs a CrewAI crew with a single agent
    to refine a user's vague input into a clear, actionable goal.
    """
    # Abort if the LLM wasn't initialized (no API key).
    if not llm: return {"error": "API key not found."}

    # 1. Define the Agent
    clarifier_agent = Agent(
        role='Expert Task Clarifier',
        goal='Rephrase a vague user task into a single, specific, concrete, and actionable goal. Your response must be ONLY the rephrased task string.',
        backstory='You are a world-class productivity coach who excels at taking ambiguous ideas and turning them into crystal-clear objectives.',
        verbose=False,  # Set to True to see the agent's thinking process in the terminal
        llm=llm         # Assign the pre-configured LLM to this agent
    )

    # 2. Define the Task
    clarification_task = Task(
        description=f'Analyze the user\'s vague task: "{task_title}".',
        expected_output='A single string containing the rephrased, clear, and actionable task.',
        agent=clarifier_agent # Assign the task to our clarifier agent
    )

    # 3. Assemble the Crew
    clarification_crew = Crew(
        agents=[clarifier_agent],
        tasks=[clarification_task],
        process=Process.sequential, # Tasks will be executed one after another
        verbose=False
    )

    # 4. Kickoff the Crew's work and process the result
    try:
        result = clarification_crew.kickoff()
        # Clean up the raw output from the LLM
        clarified_text = result.strip() if isinstance(result, str) else result.raw.strip()
        return {"clarified_task": clarified_text}
    except Exception as e:
        st.error(f"An error occurred in the clarification crew: {e}")
        return {"error": f"An error occurred in the clarification crew: {e}"}


def run_planning_crew(task_title: str) -> dict:
    """
    This function runs a CrewAI crew to break down a specific task
    into a structured, multi-step plan in JSON format.
    """
    if not llm: return {"error": "API key not found."}

    # 1. Define the Planner Agent
    planner_agent = Agent(
        role='Compassionate ADHD & Productivity Coach',
        goal='Create a gentle, 4-5 step plan in a valid JSON format for a given task.',
        backstory='You are a friendly life coach who specializes in helping people who feel overwhelmed.',
        verbose=False,
        llm=llm,
        allow_delegation=False # This agent works alone and cannot delegate tasks
    )

    # 2. Define the Planning Task
    planning_task = Task(
        description=f'Create a plan for the task: "{task_title}". Rules: 1. Your response MUST be ONLY a valid JSON object. 2. Make steps concrete and physical. 3. Include at least one break.',
        # The expected_output is crucial for guiding the LLM to produce a clean, parsable JSON.
        expected_output='A single, valid JSON object following this structure: { "title": "User\'s Task Title", "steps": [ {"text": "..."} ] }',
        agent=planner_agent
    )

    # 3. Assemble the Crew
    planning_crew = Crew(
        agents=[planner_agent],
        tasks=[planning_task],
        process=Process.sequential,
        verbose=False
    )

    # 4. Kickoff the Crew and handle UI feedback
    with st.spinner("Creating your plan..."):
        st.info(f"🤖 **Planner Agent:** Creating a gentle, step-by-step plan...")
        time.sleep(2)  # A small delay for a better user experience
        try:
            result = planning_crew.kickoff()
            # The raw output from the LLM is expected to be a JSON string
            raw_output = result.strip() if isinstance(result, str) else result.raw
            # Parse the JSON string into a Python dictionary
            plan = json.loads(raw_output)
            # Basic validation to ensure the plan has the expected keys
            if 'title' in plan and 'steps' in plan:
                return plan
            return {"error": f"The AI returned an invalid plan format: {plan}"}
        except Exception as e:
            # Handle potential errors, like the LLM returning malformed JSON
            st.error(f"An error occurred in the planning crew: {e}")
            return {"error": f"An error occurred in the planning crew: {e}"}


def run_refinement_crew(current_plan: dict, user_request: str) -> dict:
    """
    Uses a CrewAI agent to modify an existing plan based on user feedback.
    """
    if not llm: return {"error": "API key not found."}

    # 1. Define the Refiner Agent
    refiner_agent = Agent(
        role='Helpful Plan Editor',
        goal='Modify an existing JSON task plan based on a user\'s specific request.',
        backstory='You are an assistant to the Compassionate Coach. Your job is to listen carefully to user feedback and make precise edits to their plan.',
        verbose=False,
        llm=llm,
        allow_delegation=False
    )

    # Convert the current plan dictionary back into a string to provide as context to the agent
    plan_str = json.dumps(current_plan, indent=2)

    # 2. Define the Refinement Task
    refinement_task = Task(
        description=f'A user wants to modify their plan. Current Plan: {plan_str}. User\'s Request: "{user_request}".',
        expected_output="The complete, updated, and valid JSON object. Your response MUST be ONLY the valid JSON object.",
        agent=refiner_agent
    )

    # 3. Assemble the Crew
    refinement_crew = Crew(
        agents=[refiner_agent],
        tasks=[refinement_task],
        process=Process.sequential,
        verbose=False
    )

    # 4. Kickoff the Crew and process the refined plan
    with st.spinner("Updating your plan..."):
        st.info(f"🤖 **Refiner Agent:** Refining the plan based on your request...")
        time.sleep(2)  # Demo delay
        try:
            result = refinement_crew.kickoff()
            raw_output = result.strip() if isinstance(result, str) else result.raw
            plan = json.loads(raw_output) # Parse the updated JSON
            if 'title' in plan and 'steps' in plan:
                return plan
            return {"error": f"The AI returned an invalid plan format during refinement: {plan}"}
        except Exception as e:
            st.error(f"An error occurred in the refinement crew: {e}")
            return {"error": f"An error occurred in the refinement crew: {e}"}


# --- Callback and Helper Functions for Streamlit ---

def start_clarification(user_input):
    """
    This is a callback function that is triggered when the user submits their initial task.
    It runs the first crew and updates the application's state.
    """
    if user_input:
        with st.spinner("Analyzing your goal..."):
            st.info("🤖 **Clarifier Agent:** Thinking of a clearer goal for you...")
            time.sleep(2)  # Demo delay
            # Store the user's original input in the session state
            st.session_state.original_input = user_input
            # Run the clarification crew
            result = run_clarification_crew(user_input)
            if "error" not in result:
                # If successful, store the clarified task and rerun the script to update the UI
                st.session_state.clarified_task = result["clarified_task"]
                st.rerun()


def reset_app_state():
    """Clears all session state variables to reset the app to its initial screen."""
    st.session_state.clear()
    st.rerun()


# --- Main Application UI ---

# Function to initialize the Streamlit session state.
# This ensures that variables persist across user interactions.
def init_session_state():
    """Initializes session state variables if they don't exist."""
    defaults = {
        'task_plan': None,        # Stores the generated plan (a dictionary)
        'clarified_task': None,   # Stores the output from the clarification crew
        'original_input': None,   # Stores the user's very first input
        'show_chat': False        # Controls visibility of the refinement chat box
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize the state when the app starts
init_session_state()

st.title("🧠 Cognify")

# --- UI State 1: No plan exists yet (The Landing Page) ---
# This is the main "if" block that controls what the user sees.
if st.session_state.task_plan is None:
    st.markdown("##### Clarity for the overwhelmed mind.")
    st.markdown("---")

    # --- SUB-STATE: Show clarification options ---
    # If a clarified task exists in the session state, show this UI block.
    if st.session_state.clarified_task:
        with st.container(border=True):
            st.markdown("#### Is this goal clearer?")
            st.write("Here's the AI agent's suggestion. Feel free to edit it before creating a plan.")
            clarified_input = st.text_area("Suggested Goal:", value=st.session_state.clarified_task,
                                           label_visibility="collapsed", height=85)
            # Button to proceed with the AI's suggestion (or the user's edit of it)
            if st.button(f"✅ Create Plan with This Goal", use_container_width=True, type="primary"):
                result = run_planning_crew(clarified_input)
                if "error" not in result:
                    st.session_state.task_plan = result # Store the final plan
                    st.session_state.clarified_task = None # Clear the clarified task
                    st.rerun() # Rerun to display the plan

        st.markdown("**Or, choose another option:**")
        col1, col2 = st.columns(2)
        with col1:
            # Button to bypass the suggestion and use the original input
            if st.button(f"💡 Use My Original Input",
                         help=f"Your original input was: '{st.session_state.original_input}'",
                         use_container_width=True):
                result = run_planning_crew(st.session_state.original_input)
                if "error" not in result:
                    st.session_state.task_plan = result
                    st.session_state.clarified_task = None
                    st.rerun()
        with col2:
            # Button to restart the entire process
            if st.button("❌ Start Over Completely", use_container_width=True):
                reset_app_state()

    # --- SUB-STATE: Initial input screen ---
    # This is the very first screen the user sees.
    else:
        with st.container(border=True):
            st.markdown("#### What's on your mind today?")
            st.write(
                "Feeling stuck? Enter a task that feels too big, and our AI crew will work with you to break it down into a calm, step-by-step plan.")

            # Use a form to prevent the app from rerunning on every key press in the text input
            with st.form(key='task_input_form'):
                user_input = st.text_input("Enter a task:", placeholder="e.g., plan my weekend",
                                           label_visibility="collapsed")
                submit_button = st.form_submit_button(label="✨ Create My Gentle Plan", use_container_width=True,
                                                      type="primary")

                if submit_button:
                    # Check for API key before starting
                    if not llm:
                        st.error("Please add your OpenAI API Key to proceed.")
                    else:
                        # Trigger the first step of the process
                        start_clarification(user_input)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: left; color: #A0AEC0;'>— or try one of these options —</p>",
                    unsafe_allow_html=True)

        # Pre-defined starter prompts for the user
        cols = st.columns(5, gap="small")
        starters = ["Organize my emails", "Plan my study session", "Clean my kitchen"]
        if cols[0].button(starters[0], use_container_width=True):
            if not llm: st.error("Please add your OpenAI API Key to proceed.")
            else: start_clarification(starters[0])
        if cols[1].button(starters[1], use_container_width=True):
            if not llm: st.error("Please add your OpenAI API Key to proceed.")
            else: start_clarification(starters[1])
        if cols[2].button(starters[2], use_container_width=True):
            if not llm: st.error("Please add your OpenAI API Key to proceed.")
            else: start_clarification(starters[2])


# --- UI State 2: A plan has been created and is being displayed ---
else:
    plan = st.session_state.task_plan
    st.subheader(f"Your Gentle Plan for: *{plan['title']}*")

    # Loop through the steps in the plan and display each one
    for i, step in enumerate(plan['steps']):
        with st.container(border=True):
            st.markdown(f"**Step {i + 1}:** {step['text']}")

    # Option to show the refinement chat interface
    if not st.session_state.show_chat:
        if st.button("💬 Refine Plan with Chat", use_container_width=True):
            st.session_state.show_chat = True
            st.rerun()
    else:
        # The refinement form
        st.subheader("Refine Your Plan")
        with st.form(key="refinement_form"):
            refinement_request = st.text_input("How would you like to change the plan?",
                                               placeholder="e.g., Make step 3 shorter")
            submit_refinement = st.form_submit_button("Update Plan")

            if submit_refinement and refinement_request:
                # Call the refinement crew with the current plan and the new request
                result = run_refinement_crew(st.session_state.task_plan, refinement_request)

                if "error" not in result:
                    # If successful, update the plan in the session state
                    st.session_state.task_plan = result
                    st.toast("✅ Plan updated successfully!", icon="📝")
                    time.sleep(1)
                    st.rerun() # Rerun to show the updated plan

    # Final button to reset the app
    if st.button("Start a New Plan", use_container_width=True):
        reset_app_state()

# A persistent warning at the bottom if the API key is missing.
if not llm and st.session_state.task_plan is None:
    st.warning(
        "No OpenAI API key found! Please add your `OPENAI_API_KEY` to `.streamlit/secrets.toml` to enable AI features.")
