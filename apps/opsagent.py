import streamlit as st
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

from apps.utils import generate_shell, execute_shell, user_prompt, admin_prompt

'''
这个文件负责搭建智能体工作流。
注意不要轻易改动streamlit注解或者代码位置（除非不再使用streamlit），否则可能会无法达到预期效果！！
这是因为streamlit的底层原理及缓存更新机制导致的！！！
'''


@st.cache_resource
def get_memory():
    memory = InMemorySaver()
    return memory


config = {"configurable": {"thread_id": "abc123"}}
shared_memory = get_memory()


@st.cache_resource
def create_agent(prompt: str):
    tools = [generate_shell, execute_shell]
    llm = ChatTongyi(model_name="qwen-plus", temperature=0.5, max_retries=10000).bind_tools(tools,
                                                                                            parallel_tool_calls=False)
    sys_prompt = prompt

    agent = create_react_agent(llm, tools=tools, checkpointer=shared_memory, prompt=sys_prompt)

    return agent


def ops_agent(query: str, permission="超级管理员"):
    logger.info("当前权限：" + permission)
    if permission.strip() == "超级管理员":
        agent = create_agent(admin_prompt)
    else:
        agent = create_agent(user_prompt)

    for text_chunk in agent.stream({"messages": [HumanMessage(content=query)]}, config=config,
                                   stream_mode="messages"):
        yield text_chunk


if __name__ == '__main__':
    user_query = "你好呀"

    print("🤖 AI 回复：", end="", flush=True)

    for chunk in ops_agent(user_query):
        # chunk 格式：(消息对象, 元信息)，只提取AI回复的文本内容
        message, meta = chunk
        # 过滤：只打印AI的回答内容，排除系统/工具消息
        if hasattr(message, "content") and message.content:
            print(message.content, end="", flush=True)
