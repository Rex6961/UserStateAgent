# Module 1, Lesson 1: State Management & Dynamic Instructions

This project demonstrates how to implement **Session State** within the Google ADK framework to create dynamic, context-aware agents. It moves beyond static system prompts by using an `InstructionProvider` that alters the agent's persona based on real-time data stored in the session state.

## 🧠 Logic & Visualization

To understand how the components interact, consider the **Restaurant Analogy**:

  * **Agent (The Waiter):** Interacts directly with the user.
  * **Runner (The Floor Manager):** Orchestrates the workflow and manages the lifecycle.
  * **Session (The Visit):** The current dialogue from start to finish.
  * **State (The Notebook):** A key-value dictionary the waiter keeps in their pocket. It stores short-term, "sticky" facts (e.g., User's Name, Diet, Current Module) specific to this session.
  * **Memory (The Archive):** Long-term storage (past visits). *Not covered in this specific example.*
  * **InstructionProvider (Dynamic Job Description):** Instead of a static role ("You are a helper"), this is a function that reads the **State** and rewrites the instructions in real-time (e.g., "You are a helper for Alex").

### Data Flow Diagram

```text
graph TD
    A[User Message] --> R(Runner);
    R --> S[Session Service];
    S -- Store/Load --> St{State: {user_name}};
    St --> C(ReadonlyContext);
    C --> IP[InstructionProvider Function];
    IP -- Dynamic System Prompt --> LLM(LLM Agent);
    LLM --> Response;
```

## 📂 Project Structure

The project assumes the following structure within the `adk-expert` root:

```text
src/
├── .env                  # Contains GOOGLE_API_KEY
├── .venv/                # Virtual Environment
└── user_state_agent/     # Renamed from 'greeting_agent'
    ├── __init__.py
    └── agent.py          # Main logic and InstructionProvider
```

## ⚙️ Setup & Installation

1.  **Prerequisites**: Ensure you have Python installed and a Google Cloud Project with the Gemini API enabled.
2.  **Environment**:
    ```bash
    # Activate virtual environment
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows

    # Ensure dependencies are installed
    pip install google-adk
    ```

## 🚀 Usage

The `agent.py` file contains a self-standing demo using `InMemoryRunner`. It manually injects a state (`user_name="Alex"`) to demonstrate how the agent adapts.

Run the agent:

```bash
python -m user_state_agent.agent
```

### Expected Output

Because the state contains `user_name: "Alex"`, the `InstructionProvider` dynamically inserts this into the system prompt.

```text
--- Starting with State: user_name='Alex' ---
YOU: Hey, who are you?
AGENT: Hello Alex. I am your strict technical mentor and AI Solutions Architect.
We are currently discussing Module 1, Lesson 1: State Management.
```

## 💻 Code Highlights

### The Instruction Provider

This is the core of the lesson. Instead of a string, we define a function that accepts `ReadonlyContext`.

```python
def dynamic_state_instruction_provider(context: ReadonlyContext) -> Union[str, Awaitable[str]]:
    # Retrieve data from the "Notebook" (State)
    user_name = context.state.get("user_name", "Mentor")

    # Inject data into the System Prompt
    return (
        f"You are a strict technical mentor... "
        f"You are currently assisting user '{user_name}'..."
    )
```

### The Agent Definition

We bind the provider to the agent:

```python
root_agent = LlmAgent(
    name="UserStateAgent",
    model="gemini-2.5-flash",
    instruction=dynamic_state_instruction_provider, # Dynamic function, not static string
    tools=[]
)
```
