import streamlit as st
import time
import uuid
import os
import json
from openai import OpenAI

# --- Streamlit Config ---
st.set_page_config(
    page_title="Cognify",
    page_icon="🧠",
    layout="centered"
)

# --- API Key Setup ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


# --- AI Agent Functions ---

def clarify_vague_input(task_title: str) -> dict:
    """Uses an LLM to turn a vague user input into a specific, actionable goal."""
    if not client: return {"error": "API key not found."}
    prompt = f"""You are a helpful assistant. A user has a vague task: "{task_title}". Rephrase it into a more specific, concrete, and actionable goal. Respond with ONLY the rephrased task string.
    Example 1: User input: "clean up" -> Your response: "Organize and clean the kitchen"
    Example 2: User input: "work" -> Your response: "Finish the quarterly report for work"
    """
    try:
        response = client.chat.completions.create(model="gpt-4.1-nano", messages=[{"role": "user", "content": prompt}],
                                                  temperature=0.6)
        return {"clarified_task": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": f"An error occurred while clarifying the task: {e}"}


def get_decomposition_plan(task_title: str) -> dict:
    """Calls an LLM to break down a specific task into a JSON plan."""
    if not client: return {"error": "API key not found."}
    prompt = f"""You are a compassionate productivity and friendly life coach. The user's task is: "{task_title}". Create a gentle, 4-5 step plan.
        Rules: 1. Calm the user and comfort them that you are there for them. 2. Make steps concrete and physical. 3. Include at least one break. 4. Keep the tone gentle. 5. You MUST respond with ONLY a valid JSON object.
        The JSON structure: {{ "title": "User's Task Title", "steps": [ {{"text": "..."}} ] }}
        """
    st.info(f"🤖 **AI Agent:** Thinking about how to break down '{task_title}'...")
    try:
        response = client.chat.completions.create(model="gpt-4.1-nano", messages=[{"role": "user", "content": prompt}],
                                                  temperature=0.7, response_format={"type": "json_object"})
        plan = json.loads(response.choices[0].message.content.strip())
        return plan if 'title' in plan and 'steps' in plan else {"error": "The AI returned an invalid plan format."}
    except Exception as e:
        return {"error": f"An error occurred while creating the plan: {e}"}


def refine_plan_with_chat(current_plan: dict, user_request: str) -> dict:
    """Takes an existing plan and a user's chat request to refine the plan."""
    if not client: return {"error": "API key not found."}
    plan_str = json.dumps(current_plan, indent=2)
    prompt = f"""You are a plan editor. A user wants to modify their current task plan based on their request.
    Current Plan (in JSON format): {plan_str}
    User's Request: "{user_request}"
    Your task is to modify the 'steps' in the JSON based on the user's request. Maintain the gentle tone. You MUST respond with ONLY the updated, valid JSON object, including the original 'title'.
    """
    st.info(f"🤖 **AI Agent:** Refining the plan based on your request...")
    try:
        response = client.chat.completions.create(model="gpt-4.1-nano", messages=[{"role": "user", "content": prompt}],
                                                  temperature=0.7, response_format={"type": "json_object"})
        plan = json.loads(response.choices[0].message.content.strip())
        return plan if 'title' in plan and 'steps' in plan else {"error": "The AI returned an invalid plan format."}
    except Exception as e:
        return {"error": f"An error occurred while refining the plan: {e}"}


# --- Callback and Helper Functions ---

def start_clarification(user_input):
    """Starts the clarification process if input is provided."""
    if user_input:
        with st.spinner("Thinking of a clearer goal..."):
            st.session_state.original_input = user_input
            result = clarify_vague_input(user_input)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.clarified_task = result["clarified_task"]
                st.rerun()


def reset_app_state():
    """Clears all session state variables to start fresh."""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()


# --- App UI ---

# Initialize session state
for key in ['task_plan', 'clarified_task', 'original_input', 'show_chat']:
    if key not in st.session_state:
        st.session_state[key] = False if key == 'show_chat' else None

st.title("🧠 Cognify")

# State 1: No plan exists yet (The Landing Page)
if st.session_state.task_plan is None:

    st.markdown("##### Clarity for the overwhelmed mind.")
    st.markdown("---")

    # --- SUB-STATE: After clarification, show choices ---
    if st.session_state.clarified_task:
        with st.container(border=True):
            st.markdown("#### Is this goal clearer?")
            st.write("Here's the AI's suggestion. Feel free to edit it before creating a plan.")
            clarified_input = st.text_input("Suggested Goal:", value=st.session_state.clarified_task,
                                            label_visibility="collapsed")
            if st.button(f"✅ Create Plan with This Goal", use_container_width=True, type="primary"):
                with st.spinner("Our friendly AI is creating your plan..."):
                    result = get_decomposition_plan(clarified_input)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.task_plan = result
                        st.session_state.clarified_task = None
                        st.rerun()

        st.markdown("**Or, choose another option:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💡 Use My Original Input",
                         help=f"Your original input was: '{st.session_state.original_input}'",
                         use_container_width=True):
                with st.spinner("Got it! Creating a plan for your original goal..."):
                    result = get_decomposition_plan(st.session_state.original_input)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.task_plan = result
                        st.session_state.clarified_task = None
                        st.rerun()
        with col2:
            if st.button("❌ Start Over Completely", use_container_width=True):
                reset_app_state()

    # --- SUB-STATE: Initial input screen (Streamlined UI) ---
    else:
        with st.container(border=True):
            st.markdown("#### What's on your mind today?")
            st.write(
                "Feeling stuck? Enter a task that feels too big, and our AI assistant will work with you to break it down into a calm, step-by-step plan.")

            with st.form(key='task_input_form'):
                user_input = st.text_input("Enter a task:", placeholder="e.g., plan my weekend",
                                           label_visibility="collapsed")
                submit_button = st.form_submit_button(label="✨ Create My Gentle Plan", use_container_width=True,
                                                      type="primary")

                if submit_button:
                    if not api_key:
                        st.error("Please add your OpenAI API Key to proceed.")
                    else:
                        start_clarification(user_input)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: left; color: #A0AEC0;'>— or try one of these options —</p>",
                    unsafe_allow_html=True)

        cols = st.columns(5, gap="small")
        starters = ["Organize my emails", "Plan my study session", "Clean my kitchen"]

        if cols[0].button(starters[0]):
            if not api_key:
                st.error("Please add your OpenAI API Key to proceed.")
            else:
                start_clarification(starters[0])
        if cols[1].button(starters[1]):
            if not api_key:
                st.error("Please add your OpenAI API Key to proceed.")
            else:
                start_clarification(starters[1])
        if cols[2].button(starters[2]):
            if not api_key:
                st.error("Please add your OpenAI API Key to proceed.")
            else:
                start_clarification(starters[2])


# State 2: A plan has been created and is being displayed
else:
    plan = st.session_state.task_plan
    st.subheader(f"Your Gentle Plan for: *{plan['title']}*")
   # st.markdown("---")

    for i, step in enumerate(plan['steps']):
        with st.container(border=True):
            st.markdown(f"**Step {i + 1}:** {step['text']}")

    #st.markdown("---")

    if not st.session_state.show_chat:
        if st.button("💬 Refine Plan with Chat", use_container_width=True):
            st.session_state.show_chat = True
            st.rerun()
    else:
        st.subheader("Refine Your Plan")
        with st.form(key="refinement_form"):
            refinement_request = st.text_input("How would you like to change the plan?",
                                               placeholder="e.g., Make step 3 shorter")
            submit_refinement = st.form_submit_button("Update Plan")

            if submit_refinement and refinement_request:
                with st.spinner("Updating your plan..."):
                    result = refine_plan_with_chat(st.session_state.task_plan, refinement_request)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.task_plan = result
                        st.rerun()

    if st.button("Start a New Plan", use_container_width=True):
        reset_app_state()

if not client and st.session_state.task_plan is None:
    st.warning(
        "No OpenAI API key found! Please add your `OPENAI_API_KEY` to `.streamlit/secrets.toml` to enable AI features.")

