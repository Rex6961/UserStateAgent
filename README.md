# Module 1, Lesson 1: Read/Write State & Dynamic Instructions

This project demonstrates the full cycle of **Session State** management within the Google ADK framework. It covers not only **reading** state to create dynamic system prompts but also **writing** to the state using a `FunctionTool`.

## 🧠 Logic & Visualization

To understand how the components interact, let's upgrade our **Restaurant Analogy**:

  * **Agent (The Waiter):** Interacts directly with the user.
  * **State (The Notebook):** A key-value dictionary where the waiter keeps sticky facts (e.g., "User's Name").
  * **InstructionProvider (Dynamic Job Description):** A function that reads the **Notebook** before every turn to remind the waiter of the context (e.g., "You are speaking with Sarah").
  * **MemoryWriterTool (The Pen):** **(New!)** A tool that allows the waiter to *write* new information into the **Notebook** during the conversation.

### The Feedback Loop

1.  **Read:** At the start of a turn, the Agent reads the State via the `InstructionProvider`.
2.  **Act:** The Agent chats with the user.
3.  **Write:** If the user shares new info, the Agent uses the **Tool** to save it to the State.
4.  **Adapt:** On the *next* turn, the Instruction changes because the State has changed.

### Data Flow Diagram

```text
graph TD
    A[User Message] --> R(Runner);
    R --> S[Session Service];
    S -- Load State --> St{State Dictionary};
    St --> IP[InstructionProvider];
    IP -- "You are talking to {name}" --> LLM(LLM Agent);
    LLM -- Decide to Save --> Tool[MemoryWriterTool];
    Tool -- Update Key/Value --> St;
    LLM --> Response;
````

## 📂 Project Structure

The project structure includes environment management:

```text
src/
├── .env                  # Contains GOOGLE_API_KEY (Loaded via dotenv)
├── .venv/                # Virtual Environment
└── user_state_agent/
    ├── __init__.py
    └── agent.py          # Logic for Provider, Tool, and Agent
```

## ⚙️ Setup & Installation

1.  **Prerequisites**: Python installed, Google Cloud Project with Gemini API enabled.
2.  **Environment**:
    ```bash
    # Activate virtual environment
    source .venv/bin/activate

    # Install dependencies (including python-dotenv)
    pip install google-adk python-dotenv
    ```
3.  **Configuration**:
    Create a `.env` file in the `src/` directory:
    ```text
    GOOGLE_API_KEY=your_api_key_here
    ```

## 🚀 Usage

The `agent.py` file contains a simulation of a 3-turn conversation to demonstrate the state memory lifecycle.

Run the agent:

```bash
python -m user_state_agent.agent
```

### Expected Output

Notice how the output explicitly logs when the tool is used and adapts the greeting in the final turn.

1.  **Turn 1:** State is empty -\> Agent sees "Mentor".
2.  **Turn 2:** User says save "Sarah" -\> Agent calls `MemoryWriterTool` (Logged).
3.  **Turn 3:** State has "Sarah" -\> Instruction updates -\> Agent greets "Sarah".

<!-- end list -->

```text
--- Start Demo MemoryWriter ---

YOU: Hey
AGENT: Hello! How can I help you today?

YOU: Use tool MemoryWriterTool to save key='user_name' and value='Sarah'
AGENT:
[🛠️ TOOL CALL: MemoryWriterTool({'key': 'user_name', 'value': 'Sarah'})]
Hello Sarah! I've saved your name.

YOU: Hey, again
AGENT: Hello Sarah! Good to see you again.
```

## 💻 Code Highlights

### 1\. The Writer (The Tool)

We define a function and wrap it in `FunctionTool`. Note the use of `ToolContext` to access the session state.

```python
def memory_writer_tool(key: str, value: str, tool_context: ToolContext) -> Dict[str, Any]:
    # WRITING to the "Notebook"
    tool_context.state[key] = value
    return {"status": "success", "message": f"Successfully saved '{value}' to state key '{key}'."}

memory_writer_tool = FunctionTool(func=memory_writer_tool)
```

### 2\. The Reader (The Instruction)

The instruction dynamically pulls the value we just wrote.

```python
def dynamic_state_instruction_provider(context: ReadonlyContext) -> Union[str, Awaitable[str]]:
    # READING from the "Notebook"
    user_name = context.state.get("user_name", "Mentor")
    return f"You are currently speaking with '{user_name}'..."
```

### 3\. Handling Tool Calls & Visualization

To properly handle the response structure (avoiding SDK warnings about non-text parts) and visualize the tool execution, we implement **Type Guarding** in the runner loop. We explicitly check if a response part is a `function_call` or `text`.

```python
if part.function_call:
    # Log the tool usage nicely
    func_name = part.function_call.name
    args = part.function_call.args
    print(f"\n[🛠️ TOOL CALL: {func_name}({args})]", end="", flush=True)
elif part.text:
    # Print the standard text response
    print(part.text, end="", flush=True)
```
