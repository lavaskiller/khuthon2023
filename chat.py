import streamlit as st
import openai, test, json, time
from datetime import datetime
from deta import Deta

openai.api_key = st.secrets["api_key"]


def app():
    st.subheader("")

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    def key():
        return datetime.now().strftime("%Y%m%d%H%M%S") + st.session_state.useremail

    if not st.session_state.signout:
        st.title("로그인 해주세요")
    else:
        st.title("Welcome! " + st.session_state.username + ",")

        deta = Deta(st.secrets["db_key"])
        # db = deta.Base(st.session_state.useremail)
        sys = deta.Base("sys_log")
        sys2 = deta.Base("sys2_log")
        chat = deta.Base("chat_log")
        user = deta.Base("users_db")

        # Initialize chat history
        if not [
            {"content": item["content"], "role": item["role"]}
            for item in chat.fetch({"user": st.session_state.useremail}).items
        ]:
            chat.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "assistant",
                    "content": "안녕하세요, khuras입니다. 질문을 입력해주세요.",
                }
            )

        # Display chat messages from history on app rerun
        for message in [
            {"content": item["content"], "role": item["role"]}
            for item in chat.fetch({"user": st.session_state.useremail}).items
        ]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Hello! Who are you?"):
            user_input = prompt
            chat.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "user",
                    "content": prompt,
                }
            )
            sys.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "user",
                    "content": prompt,
                }
            )
            sys2.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "user",
                    "content": prompt,
                }
            )
            # output = generate_response(user_input)

            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container

            if user.get(st.session_state.useremail)["state"] == "begin":
                gpt_prompt = [
                    {
                        "role": "system",
                        "content": "Analyze the user's question to identify the core topic, which we will define as main_key. Think of the correct answer to the question and define it as anw. [You should not directly reveal anw.] Remember, you are an educator, not just a provider of answers. Your role is to guide the student to discover anw on their own. To achieve this, you can explain the concepts must be need for understanding anw but not realated to it and pose guiding questions that lead to anw. Your response to the student will be defined as resp in Korean. Output main_key, anw, resp in JSON format. Before finalizing the output, ensure it meets the following conditions: (1) Yun MUST NOT reveal anw in resp!!!!, (2) the output must be in JSON format like {} so that I can straightly use json.loads, and (3) it must consist of main_key, anw, and resp. (4) resp must be written in Korean.",
                    }
                ]
                user.update({"state": "lead"}, st.session_state.useremail)
                gpt_prompt.append({"role": "user", "content": user_input})

            elif user.get(st.session_state.useremail)["state"] == "lead":
                gpt_prompt = [
                    {"content": item["content"], "role": item["role"]}
                    for item in sys.fetch({"user": st.session_state.useremail}).items
                ]
                gpt_prompt.append(
                    {
                        "role": "user",
                        "content": "If the user's response is correct and close enough to anw that no further guiding questions are necessary, store 'finish_session' in the flag and save a simplified explanation of anw and the user's response in resp in Korean. In all other cases, if you determine that additional guiding questions are needed, store 'keep_session' in the flag and save either an explanation of the key concepts needed to understand anw or the necessary guiding questions to approach anw in resp in Koren. Define the level of understanding as understand and rate it as 10 points. 0 to 3 points for negative or incorrect answers, 1 to 5 points for answers with questions, 4 to 9 points for partially correct answers, and 10 points for really perfectly correct answers. Output understand, flag, resp in JSON format. Before finalizing the output, ensure it meets these conditions: (1) In cases where the flag is 'keep_session', resp must not contain anw, (2) In cases where the flag is 'finish_session', resp must have the right answer and anw in it, (3) the output must be in JSON format like {} so that I can straightly use json.loads, and (4) it must consist of understand, flag, and resp. (5) resp must be written in Korean. User's response follows : "
                        + user_input,
                    }
                )

            print(gpt_prompt)

            # for response in openai.ChatCompletion.create(
            #     model="gpt-4",
            #     messages=gpt_prompt,
            #     stream=True,
            # ):
            #     full_response += response.choices[0].delta.get("content", "")
            #     message_placeholder.markdown(full_response + "▌ ")

            with st.spinner("답변이 생성되는 중입니다..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-1106", messages=gpt_prompt, stream=False
                    )
                    full_response = response["choices"][0]["message"]["content"]
                    user.update(
                        {"uses": user.get(st.session_state.useremail)["uses"] + 1},
                        st.session_state.useremail,
                    )
                except Exception as e:
                    st.error("응답 처리 중 오류 발생: {}".format(e))
                    raise

            try:
                json.loads(full_response)
            except:
                full_response = full_response.split("json", 1)[1].rsplit("```", 1)[0]

            try:
                with st.chat_message("assistant"):
                    st.markdown(json.loads(full_response)["resp"])

                if json.loads(full_response)["flag"] == "finish_session":
                    user.update({"state": "begin"}, st.session_state.useremail)
                    user.update(
                        {
                            "cnt_qus": user.get(st.session_state.useremail)["cnt_qus"]
                            + 1
                        },
                        st.session_state.useremail,
                    )
                    for item in sys.fetch({"user": st.session_state.useremail}).items:
                        sys.delete(item["key"])

            except:
                print("Failed to")

            sys.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "assistant",
                    "content": full_response,
                }
            )
            sys2.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "assistant",
                    "content": full_response,
                }
            )
            chat.put(
                {
                    "key": key(),
                    "user": st.session_state.useremail,
                    "role": "assistant",
                    "content": json.loads(full_response)["resp"],
                }
            )
            # print(chat.fetch({"user": st.session_state.useremail}).items)
