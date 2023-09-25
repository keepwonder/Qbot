import pandas as pd
import streamlit as st
from configs import *
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)

st.set_page_config(
    page_title="Welcome to Qbot!",
    page_icon="👋",
)

chat = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0

if 'max_tokens' not in st.session_state:
    st.session_state['max_tokens'] = MAX_TOKEN

if 'history_len' not in st.session_state:
    st.session_state['history_len'] = HISTORY_LEN
    print('history_len1111:', st.session_state['history_len'])
 
if 'responses' not in st.session_state:
    st.session_state['responses'] = []

if 'requests' not in st.session_state:
    st.session_state['requests'] = []


if 'OPENAI_API_KEY' not in st.session_state:
    st.session_state['OPENAI_API_KEY'] = ''

elif st.session_state["OPENAI_API_KEY"] != "":

    if 'buffer_memory' not in st.session_state:
        print('history_len222:', st.session_state['history_len'])
        st.session_state['buffer_memory']= ConversationBufferWindowMemory(k=st.session_state['history_len'])

    # with no history 
    chat = ChatOpenAI(openai_api_key=st.session_state["OPENAI_API_KEY"], temperature=st.session_state['temperature'], max_tokens=st.session_state['max_tokens'])

    # with chat history
    conversation = ConversationChain(
        llm=chat,
        memory=st.session_state['buffer_memory'],
        verbose=True
    )
    

chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter "
prompt = st.chat_input(chat_input_placeholder, key='prompt')
# print(f'prompt:{prompt}')
# print(f'temperature:{st.session_state["temperature"]}')
# print(f'max tokens:{st.session_state["max_tokens"]}')
# print(f'API key: {st.session_state["OPENAI_API_KEY"]}')
print(f'history_len:{st.session_state["history_len"]}')


if chat:
    with st.container():
        st.caption(f'<p align="center">{MODEL_NAME}<p>', unsafe_allow_html=True)
        for message in st.session_state["messages"]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)
        if prompt:
            st.session_state["messages"].append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)

            # 1. no memory   
            # ai_message = chat([HumanMessage(content=prompt)])
            # st.session_state["messages"].append(ai_message)

            # 2. with memory
            ai_message = conversation(prompt)
            st.session_state['messages'].append(AIMessage(content=ai_message['response']))

            st.session_state.requests.append(prompt)
            st.session_state.responses.append(ai_message['response'])

            with st.chat_message("assistant"):
                print(ai_message)
                # st.markdown(ai_message.content)
                st.markdown(ai_message['response'])
else:
    with st.container():
        st.warning('Please set your OpenAI API key first!')


def reset_history():
    """清空历史对话信息"""
    st.session_state['messages'] = []

def export_records():
    """导出当前对话记录"""
    with open('records.txt', 'w') as f:
        for msg in st.session_state['messages']:
            f.write(msg.content)


def get_messages_df():
    msgs = []
    messages = st.session_state['messages']
    print(f'messages:{messages}')
    for i in range(0, len(messages), 2):
        msg = []
        msg.append(messages[i].content)
        msg.append(messages[i+1].content)
        msgs.append(msg) 

    print('msgs：', msgs)
    return pd.DataFrame(msgs, columns=['HumanMessage', 'AIMessage'])


@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv_file = convert_df(get_messages_df())


with st.sidebar:
    st.write('# Welcome to Qbot! 👋')
    st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
    
    openai_api_key = st.text_input('OpenAI API KEY: ', value=st.session_state['OPENAI_API_KEY'], max_chars=None, key=None, type='password')
    if openai_api_key:
        st.session_state['OPENAI_API_KEY'] = openai_api_key

    temperature = st.slider("Temperature: ", 0.0, 1.0, 0.2, 0.01)
    if temperature:
        st.session_state['temperature'] = temperature

    max_tokens = st.slider("Max tokens: ", 0, 8197, 1024, 1)
    if max_tokens:
        st.session_state['max_tokens'] = max_tokens

    history_len = st.number_input("历史对话轮数：", 0, 10, 3) 
    if history_len:
        st.session_state['history_len'] = history_len

    col1, col2 = st.columns(2)
    with col1:
        with open('records.txt', 'w+') as f:
            for msg in st.session_state['messages']:
                f.write(msg.content)
            st.download_button('Export Records',data=csv_file, file_name='records.csv', use_container_width=True)
    with col2:
        clear = st.button('Clear History', use_container_width=True, type='primary', on_click=reset_history)