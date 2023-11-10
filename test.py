import streamlit as st
from deta import Deta


def app():
    # Usernm = []
    deta = Deta("c0s6CpFN39n_3kGRmJCADFYJLkCndrWpsz6z2woBaJaY")

    db = deta.Base("users_db")

    def create_user(email, password, username):
        return db.put({"key": email, "name": username, "password": password, "state": "begin", "cnt_qus": 1})

    st.title("Welcome to :violet[ThinkingBridge] :sunglasses:")

    if "username" not in st.session_state:
        st.session_state.username = ""
    if "useremail" not in st.session_state:
        st.session_state.useremail = ""

    def f():
        user = db.get(email)

        if user is None:
            st.warning("로그인 실패")
        elif (user["password"] == st.session_state.password):
            st.session_state.username = user["name"]
            st.session_state.useremail = user["key"]

            global Usernm
            Usernm = user["key"]

            st.session_state.signedout = True
            st.session_state.signout = True
        else:
            st.warning("잘못된 비밀번호입니다.")

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ""

    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if "signout" not in st.session_state:
        st.session_state["signout"] = False

    if not st.session_state[
        "signedout"
    ]:  # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox("로그인/회원가입", ["로그인", "회원가입"])
        email = st.text_input("이메일")
        st.session_state.password = st.text_input("비밀번호", type="password")

        if choice == "로그인":
            username = st.text_input("이름")

            if st.button("계정생성"):
                create_user(email, st.session_state.password, username)

                st.success("계정이 성공적으로 생성되었습니다.")
                st.markdown("이메일과 비밀번호를 이용하여 로그인을 시도해주세요.")
                st.balloons()
        else:
            # st.button('Login', on_click=f)
            st.button("로그인", on_click=f)

    if st.session_state.signout:
        st.text("이름 " + st.session_state.username)
        st.text("이메일: " + st.session_state.useremail)
        st.button("로그아웃", on_click=t)
