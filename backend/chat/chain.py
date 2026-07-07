
import os
from dotenv import load_dotenv

load_dotenv()

import logging

logger = logging.getLogger(__name__)

from datetime import date

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from langchain_community.tools import DuckDuckGoSearchResults

from chat.models import Message


class Model:
    def __init__(self):
        self.llm = ChatOllama(
            model = os.getenv("OLLAMA_MODEL_NAME", ""),
            base_url = os.getenv("OLLAMA_URL", "http://localhost:11434"),
            temperature = 0,
        )

        # self.tools = [DuckDuckGoSearchResults()]
        # self.tools_by_name = {tool.name: tool for tool in self.tools}
        # self.llm_with_tools = self.llm.bind_tools(self.tools)

    def create_chat_context(self, context: list[Message]):
        today = date.today().strftime("%d.%m.%Y")
        messages = [
            SystemMessage(
                content = (
                    f"Текущая дата: {today}. "
                    "You should use only english language when calling tools and answering to user in Russian."
                )
            )
        ]

        for msg in context:
            if msg.is_assistant:
                messages.append(
                    AIMessage(
                        content = msg.text
                    )
                )

            elif msg.is_user:
                messages.append(
                    HumanMessage(
                        content = msg.text
                    )
                )

        return messages

    # def generate(self, context):
    #     logger.info("Starting generation")
    #
    #     response = self.llm_with_tools.invoke(context)
    #     context.append(response)
    #
    #     logger.info(f"TOOL CALLS: {response.tool_calls}")
    #     logger.info(f"CONTENT: {response.content}")
    #
    #     if not response.tool_calls:
    #         return str(response.content)
    #
    #     for tool_call in response.tool_calls:
    #         tool = self.tools_by_name[tool_call["name"]]
    #         result = tool.invoke(tool_call["args"])
    #
    #         context.append(
    #             ToolMessage(
    #                 content = str(result),
    #                 tool_call_id = tool_call["id"],
    #             )
    #         )
    #
    #     logger.info(f"TOOL CALLS: {response.tool_calls}")
    #     logger.info(f"CONTENT: {response.content}")
    #
    #     final_response = self.llm_with_tools.invoke(context)
    #     return str(final_response.content)

    def stream_generate(self, context):
        for chunk in self.llm.stream(context):
            if chunk.content:
                yield str(chunk.content)


def get_llm() -> Model:
    return Model()
