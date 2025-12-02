"""
Main agent module demonstrating dynamic instruction injection based on session state.
"""

import asyncio
from typing import Union, Awaitable, Dict, Any
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

load_dotenv()


def memory_writer_tool(key: str, value: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Use this tool to save specific information
        about the user (like their name) into the session state.

    Args:
        key (str): The state variable name.
        value (str): The value to store.
        tool_context (ToolContext): The context of the tool (injected automatically).

    Returns:
        Dict[str, Any]: Status message.
    """

    tool_context.state[key] = value

    return {
        "status": "success",
        "message": f"Successfully saved '{value}' to state key '{key}'."
    }

memory_writer_tool = FunctionTool(
    func=memory_writer_tool
)

def dynamic_state_instruction_provider(context: ReadonlyContext) -> Union[str, Awaitable[str]]:
    """Dynamically generates the system instruction based on session state.

    Args:
        context (ReadonlyContext): ReadonlyContext object providing access to state.

    Returns:
        Union[str, Awaitable[str]]: The dynamically generated instruction.
    """

    user_name = context.state.get("user_name", "Mentor")

    instruction_template = (
        f"You are helpful assistant. "
        f"You are currently speaking with '{user_name}'. "
        f"If the user asks you to remember their name or save information, "
        f"Use the 'MemoryWriterTool'. "
        f"Always greet the user by the name you currently know them as. "
    )

    return instruction_template

root_agent: LlmAgent = LlmAgent(
    name="UserStateAgent",
    model="gemini-2.5-flash",
    instruction=dynamic_state_instruction_provider,
    description="Agent demonstrating dynamic instructions based on session state.",
    tools=[memory_writer_tool]
)


if __name__=="__main__":
    async def run_demo():
        """
        Demonstrates the agent lifecycle using InMemoryRunner with manual state injection.
        """
        runner = InMemoryRunner(agent=root_agent, app_name="StateApp")
        user_id = "user_001"
        session_id = "session_write_demo"

        await runner.session_service.create_session(
            app_name="StateApp",
            user_id=user_id,
            session_id=session_id,
            state={}
        )

        messages = [
            "Hey",
            "Use tool MemoryWriterTool to save key='user_name' and value='Sarah'",
            "Hey, again"
        ]

        print("--- Start Demo MemoryWriter ---")

        for msg_text in messages:
            print(f"\nYOU: {msg_text}")
            user_message = Content(parts=[Part(text=msg_text)])

            print("AGENT: ", end="", flush=True)
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.function_call:
                            func_name = part.function_call.name
                            args = part.function_call.args
                            print(f"\n[🛠️ TOOL CALL: {func_name}({args})]", end="", flush=True)
                        elif part.text:
                            print(part.text, end="", flush=True)
            print()

    asyncio.run(run_demo())
