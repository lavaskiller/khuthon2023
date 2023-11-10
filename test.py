import streamlit as st
from deta import Deta


def app():
    # Usernm = []
    deta = Deta("c0s6CpFN39n_3kGRmJCADFYJLkCndrWpsz6z2woBaJaY")

    db = deta.Base("users_db")

    def create_user(email, password, username):
        return db.put({"key": email, "name": username, "password": password})

    st.title("Welcome to :violet[ThinkingBridge] :sunglasses:")

    if "username" not in st.session_state:
        st.session_state.username = ""
    if "useremail" not in st.session_state:
        st.session_state.useremail = ""

    def f():
        user = db.get(email)

        if user is None:
            st.warning("Login Failed")
        elif user["password"] == st.session_state.password:
            st.session_state.username = user["name"]
            st.session_state.useremail = user["key"]

            global Usernm
            Usernm = user["key"]

            st.session_state.signedout = True
            st.session_state.signout = True
        else:
            st.warning("Wrong password")

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
        choice = st.selectbox("Login/Signup", ["Login", "Sign up"])
        email = st.text_input("Email Address")
        st.session_state.password = st.text_input("Password", type="password")

        if choice == "Sign up":
            username = st.text_input("Enter  your unique username")

            if st.button("Create my account"):
                create_user(email, st.session_state.password, username)

                st.success("Account created successfully!")
                st.markdown("Please Login using your email and password")
                st.balloons()
        else:
            # st.button('Login', on_click=f)
            st.button("Login", on_click=f)

    if st.session_state.signout:
        st.text("Name " + st.session_state.username)
        st.text("Email id: " + st.session_state.useremail)
        st.button("Sign out", on_click=t)

    def ap():
        st.write("Posts")
