# 🧠 Cognify

### Clarity for the overwhelmed mind.

Cognify is an intelligent web application that acts as an AI-powered executive function assistant. It's designed for anyone who has ever felt stuck or overwhelmed by a large task. By using a multi-step agentic workflow, Cognify works with the user to transform vague goals into clear, actionable, and gentle step-by-step plans.

**Live Demo:** [Link to your Deployed Streamlit App]

---

### Key Features & Agentic Workflow

Cognify uses a unique, three-step agentic workflow that feels like a natural conversation:

1.  **Clarify:** The agent first interprets a user's vague input (e.g., "deal with my messy room") and proposes a more concrete, actionable goal ("Organize the desk and closet in your bedroom").
2.  **Decompose:** Once a goal is agreed upon, the agent breaks it down into a series of small, gentle sub-tasks, including built-in breaks and warm-up activities.
3.  **Refine:** The agent maintains the context of the generated plan, allowing users to provide feedback in natural language (e.g., "make step 4 shorter"), and intelligently edits the plan in response.

### Tech Stack

* **Language:** Python
* **Framework:** Streamlit
* **AI:** OpenAI API (gpt-4o-mini)
* **Core Logic:** Custom stateful agentic workflow

### Running the App Locally

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd cognify-app
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your API key:**
    Create a file at `.streamlit/secrets.toml` and add your OpenAI API key:
    ```toml
    OPENAI_API_KEY = "your-key-here"
    ```
5.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

### Future Vision

This MVP was built with Streamlit to prove the core concept. The next phase of development will involve migrating the application to a more robust, production-grade architecture, such as a FastAPI backend with a modern frontend framework.


