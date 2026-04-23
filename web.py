import requests
import streamlit as st

st.set_page_config(layout="wide")

from apps.opsagent import ops_agent


# 这个文件是项目入口，搭建的简单可视化页面。
# 注意不要轻易改动streamlit注解或者代码位置（除非不再使用streamlit），否则可能会无法达到预期效果！！
# 这是因为streamlit的底层原理及缓存更新机制导致的！！！


def clear_history():
    st.session_state.history = []
    st.cache_resource.clear()


# 向后端发请求
def get_llm_response(query, files, permission):
    try:
        for chunk in ops_agent(query, permission):
            # chunk 格式：(消息对象, 元信息)，只提取AI回复的文本内容
            message, meta = chunk
            # 过滤：只打印AI的回答内容，排除系统/工具消息
            if hasattr(message, "content") and message.content:
                yield message.content
    except requests.exceptions.RequestException as e:
        yield "API请求错误:{}".format(e)


# 构建对话页面
def main():
    st.title("Ubuntu Ops Agent👋")
    st.badge("Warning：请谨慎使用超级管理员，这个权限可以执行危险命令", icon=":material/check:",
             color="orange")
    st.sidebar.button("清空聊天记录", type="primary", on_click=clear_history, use_container_width=True)
    st.sidebar.warning("当前仅能使用固定语言模型")
    model = st.sidebar.selectbox(
        "使用的语言模型：",
        ("Qwen3-Plus", "DeepSeek-v4")
    )
    permission = st.sidebar.selectbox(
        "操作权限等级：",
        ("普通用户", "超级管理员")
    )

    # 增加会话状态，history保存历史记录
    if "history" not in st.session_state:
        st.session_state.history = []

    # 打印历史记录
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 如果用户输入了信息
    if user_input := st.chat_input("Chat with Alex: ", accept_file=True, file_type=["txt", "pdf"]):
        message = user_input.text
        files = user_input.files
        if not message:
            st.warning('你必须输入文本信息，否则不会执行任何操作!', icon="⚠️")
            return

        with st.chat_message("user"):
            st.markdown(message)

        with st.chat_message("assistant"):
            full_response = st.write_stream(get_llm_response(message, files, permission))

        # 将用户和模型内容放入历史状态
        st.session_state.history.append({"role": "user", "content": message})
        st.session_state.history.append({"role": "assistant", "content": full_response})


if __name__ == '__main__':
    main()
