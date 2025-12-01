"""
Main agent module demonstrating dynamic instruction injection based on session state.
"""

import asyncio
from typing import Union, Awaitable

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part


def dynamic_state_instruction_provider(context: ReadonlyContext) -> Union[str, Awaitable[str]]:
    """Dynamically generates the system instruction based on session state.

    Args:
        context (ReadonlyContext): ReadonlyContext object providing access to state.

    Returns:
        Union[str, Awaitable[str]]: The dynamically generated instruction.
    """

    user_name = context.state.get("user_name", "Mentor")
    instruction_template = (
        f"You are street technical mentor and AI Solution Architect. "
        f"You are currently assisting user '{user_name}'. "
        f"Always greet the user by their name and explicitly state that "
        f"the current topic is Module 1, Lesson 1: State Management. "
        f"Your response must be concise, professional, and technical."
    )

    return instruction_template

root_agent: LlmAgent = LlmAgent(
    name="UserStateAgent",
    model="gemini-2.5-flash",
    instruction=dynamic_state_instruction_provider,
    description="Agent demonstrating dynamic instructions based on session state.",
    tools=[]
)


if __name__=="__main__":
    async def run_demo():
        """
        Demonstrates the agent lifecycle using InMemoryRunner with manual state injection.
        """
        runner = InMemoryRunner(agent=root_agent, app_name="StateApp")
        user_id = "user_001"
        session_id = "session_state_demo"

        initial_state = {
            "user_name": "Alex",
            "module": 1,
            "lesson": 1
        }

        await runner.session_service.create_session(
            app_name="StateApp",
            user_id=user_id,
            session_id=session_id,
            state=initial_state
        )

        user_message = Content(parts=[Part(text="Hey, who are you?")])
        print("--- Launching with State: user_name='Alex' ---")
        print(f"YOU: {user_message.parts[0].text}")

        print("AGENT: ", end="", flush=True)

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                print()

    asyncio.run(run_demo())
