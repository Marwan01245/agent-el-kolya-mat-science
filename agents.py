import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.memory import ConversationTokenBufferMemory
from langchain.agents.agent import AgentExecutor
from classes import DynamoDBChatMessageHistoryNew
from retrievers import *
from tools import get_tool
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
# from dotenv import load_dotenv
from tools import AgentTool
from langchain.document_loaders import AmazonTextractPDFLoader

def _init_(session_id):
    llm_chat = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo-16k-0613")
    tools = [
        get_tool("retriever")(
            syllabus_vectorstore(),
            name="syllabus_database",
            description="send the same user question to the syllabus content database."
        ),
        # get_tool(AgentTool.TELEGRAM)(
        #     description="used to send a message to the teacher in case the user wanted a human to answer him or ask the nerd in your class if"
        #                 "you needed a zionist to answer you."
        # )
    ]

    sys_message = SystemMessage(
        content="You are a phd level industrial engineer with years of experiance and you are explainging material science to college students YOU ALWAYS TAKE THE WHOLE USER QUESTION AS YOUR QUERY TO THE DATABASE AND DO NOT CUT CORNERS .\n"
                "You always lookup questions in the syllabus database before answering anything. (send to the syllabus data base the same user question, don't comeup with a query)\n"
                "You NEVER answer questions outside the syllabus, and never come up with answers.\n"
                "You always say the chapter number of your answer.\n"
                "Begin the conversation with offering help in the course content."
    )

    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=sys_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
    )

    reminder = "Always refer to the syllabus and in which chapter the answer is ."

    memory = AgentTokenBufferMemory(max_token_limit=11000, memory_key="chat_history", llm=llm_chat,
                                    chat_memory=DynamoDBChatMessageHistoryNew(table_name="langchain-agents",
                                                                              session_id=session_id, reminder=reminder))

    agent = OpenAIFunctionsAgent(llm=llm_chat, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True
    )

    return agent_executor
# enum Agent
class Agent(str, Enum):
    JEWELRY = "jewelry"
    BIZNIS_CLINICS = "biznis-clinics"
    CRYPTO = "crypto"
    ECOM = "ecom"
    BEAUTY_CLINICS = "beauty-clinics"
    DIAMONDS = "diamonds"
    TEST = "test"
    WELCH_LAW = "welch-law"


agents_dict = {
    Agent.TEST: _init_,
}

def get_agent(name, session_id):
    return agents_dict[name](session_id=session_id)
