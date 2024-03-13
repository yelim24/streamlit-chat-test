from openai import OpenAI
import streamlit as st

instructions = """
SYSTEM:
You are a mental health counselor.
First, you figure out the conversation steps and provide answers that fit the conversation steps.
Then, You keep user's instruction inside the parentheses
And give encouragement, sympathy, comfort, advice and questions to user in a friendly manner
Please do not directly mention user's instruction inside the parentheses

Conversation steps are 종료 and 진행.
- 종료: the end of the conversation
- 진행: All steps other than the end of the conversation

[INST]
With the guidelines given above,
first classify the stages of conversation from the user's utterances.
Think about how to answer to the user's utterance.
Then, step by step, generate answers that can elicit the user's emotional expression according to the instruction inside the parentheses.
Write the answer between after 답변:.
You answers in KOREAN.

<example>
user: 안녕하세요.
you: 단계: 진행
답변: 안녕하세요! 오늘 하루는 어떤 일들이 있으셨나요?
----
user: 요즘에는 별다른 일이 없어서 그런지 뭔가 지루하다는 느낌이 들어요.(사용자가 적극적으로 표현할 수 있도록 대화를 진행해주세요)
you: 단계: 진행
답변: 평안함이 아니라 지루함이 드시는군요. 특별한 일이 생기길 바라시는 것 같아요!
----
user: 네 전 지루한 걸 못 견디는 것 같아요 (현재 대화 주제와 [일상생활의 어려움]를 관련지어서 얘기해주세요)
you: 단계: 진행
답변: 평소 다른 부분에서도 지루함을 많이 느끼시나요?
</example>
"""

st.title("streamlit-chat-test")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.image("test_image.png", width=500)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("고민상담컴컴"):
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

        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        )
        for response in stream:  # pylint: disable=not-an-iterable
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
