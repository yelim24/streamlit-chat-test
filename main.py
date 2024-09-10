import streamlit as st
from streamlit_option_menu import option_menu
import os
import re
import time
import pandas as pd
import numpy as np
from openai import OpenAI


instructions = """
SYSTEM:
당신은 정신 건강 상담사입니다.
먼저 당신은 대화 단계를 파악하고 그 단계에 맞는 대답을 제공해야합니다.
다음, 당신은 괄호 안에 있는 사용자 지시사항을 명심해야합니다.
그리고 친절한 말투로 사용자에게 응원, 공감, 안정, 조언을 해주세요.
마지막으로 절대 괄호 안에 있는 사용자 지시사항을 직접적으로 말하지 마세요

대화 단계는 종료와 진행이 있습니다.
- 종료: 대화가 충분히 진행 된 이후 사용자가 대화를 마무리하고 싶어할 때 단계
- 진행: 종료 이외의 모든 단계

[INST]
위에 주어진 가이드라인을 따라서,
먼저 사용자 메세지로부터 대화의 단계를 구분합니다.
사용자 메세지에 어떻게 답변을 할지 생각합니다.
그리고 괄호 안의 지시사항을 따라 사용자의 감정 표현을 이끌어낼 수 있는 답변을 생성해주세요.
답변은 답변: 뒤에 작성합니다.
한국어 존댓말로만 답변합니다.

<example>
user: 안녕하세요.
you: 단계: 진행
답변: 안녕하세요! 오늘 하루는 어떤 일들이 있으셨나요?
----
user: 안녕
you: 단계: 진행
답변: 안녕하세요! 지금 기분은 어떠신가요?
----
user: 안녕
you: 단계: 진행
답변: 안녕하세요! 오늘 하루 잘 보내고 계신가요? 기분은 어떠세요?
</example>
"""

questions = [
    "Q1. 첫 번째 질문",
    "Q2. 두 번째 질문",
    "Q3. 세 번째 질문",
]

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

menu_list = option_menu(None, ["Chat", "BDI-II", "Result", 'Database'], 
    icons=['chat-left-dots', 'clipboard-check', "file-earmark-bar-graph", 'database'],
    # https://icons.getbootstrap.com/
    menu_icon="cast", default_index=0, orientation="horizontal")

if menu_list == "Chat":

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "ft:gpt-3.5-turbo-0125:turingbio::92xTWUco"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("당신의 고민을 말씀해주세요"):
        user_instruction = ''
        if st.session_state.messages != []:
            user_instruction = "(사용자가 적극적으로 표현할 수 있도록 대화를 진행해주세요)"
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            messages.insert(0, {"role": "system", "content": instructions})
            
            messages[-1] = {"role": "user", "content": prompt + user_instruction}
            
            response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages,
                temperature=0.2,        # .5
                frequency_penalty=.7,  # .5
                # presence_penalty=.2,   # .3
            )
            bot_response = response.choices[0].message.content
            bot_response_list = re.split(r'답변:\s', bot_response)
            if len(bot_response_list)>1:
                dialog_step = bot_response_list[0].split(':')[-1].strip()
                bot_response = bot_response_list[1]
            
            chars = ''
            for char in bot_response:
                time.sleep(0.001)
                chars += char
                message_placeholder.markdown(chars + "▌")

            message_placeholder.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
elif menu_list == "BDI-II":

    st.write("BDI-II는 우울 정도를 측정하는 데 사용되는 21개의 객관식 질문으로 구성된 자가보고 설문지입니다.")
    st.write("지난 2주 동안의 기분과 상태를 생각해 보시고, 이를 가장 잘 설명하는 문장의 번호에 표시해주세요.")
    
    options = ["1: 거의 그렇지 않거나 아니다", "2: 가끔 그렇다", "3: 자주 그렇다", "4: 항상 그렇다"]
    responses = [st.radio(question, options, key=f"question_{i+1}") for i, question in enumerate(questions)]
    
elif menu_list == "Result":
    st.write("지금까지의 감정 그래프를 보여드리겠습니다.")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.line_chart(chart_data)
    st.bar_chart(chart_data)
    
elif menu_list == "Database":
    st.write("Database 페이지")
