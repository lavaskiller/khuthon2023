import streamlit as st
import smtplib as s
import time
import email_validation as sc
from deta import Deta
from suggest_email import suggest_email_domain
from popular_domains import emailDomains
from email.mime.text import MIMEText
from random import randint


def app():
    st.subheader("")
    image = "logo.png"

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Usernm = []
    deta = Deta(st.secrets["db_key"])

    db = deta.Base("users_db")

    def create_user(email, password, username):
        user = db.get(email.lower())

        if user is None:
            db.put(
                {
                    "key": email.lower(),
                    "name": username,
                    "password": password,
                    "state": "begin",
                    "cnt_qus": 1,
                    "uses": 0,
                    "limit": 5,
                }
            )
            return True
        else:
            db.put(
                {
                    "key": email.lower(),
                    "name": username,
                    "password": password,
                    "state": user["state"],
                    "cnt_qus": user["cnt_qus"],
                    "uses": user["uses"],
                    "limit": 5,
                }
            )
            return False

    st.title("Welcome to :violet[ThinkingBridge] :sunglasses:")

    if "username" not in st.session_state:
        st.session_state.username = ""
    if "useremail" not in st.session_state:
        st.session_state.useremail = ""

    def f():
        try:
            user = db.get(email.lower())
        except:
            st.error("로그인 실패")

        if user is None:
            st.warning("로그인 실패")
        elif user["password"] == st.session_state.password:
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

    def ck(email):
        result = {}
        result["syntaxValidation"] = sc.is_valid_email(email)

        if result["syntaxValidation"]:
            domain_part = email.split("@")[1] if "@" in email else ""

            if not domain_part:
                st.warning("유효한 이메일이 아닙니다.")
            else:
                # Additional validation for the domain part
                if not sc.has_valid_mx_record(domain_part):
                    # st.warning("Not valid: MX record not found.")
                    # suggested_domains = suggest_email_domain(domain_part, emailDomains)
                    # if suggested_domains:
                    #     st.info("Suggested Domains:")
                    #     for suggested_domain in suggested_domains:
                    #         st.write(suggested_domain)
                    # else:
                    #    st.warning("No suggested domains found.")

                    return False
                else:
                    # MX record validation
                    result["MXRecord"] = sc.has_valid_mx_record(domain_part)

                    # SMTP validation
                    if result["MXRecord"]:
                        result["smtpConnection"] = sc.verify_email(email)
                    else:
                        result["smtpConnection"] = False

                    # Temporary domain check
                    result["is Temporary"] = sc.is_disposable(domain_part)

                    # Determine validity status and message
                    is_valid = (
                        result["syntaxValidation"]
                        and result["MXRecord"]
                        and result["smtpConnection"]
                        and not result["is Temporary"]
                    )
                    return is_valid

        return False

    def send_verification(user, email):
        otp = str(randint(100000, 999999))
        body = (
            f"안녕하세요. {user}님,\n"
            "ThinkingBridge에서 회원가입을 위한 인증키가 발송되었습니다.\n\n"
            f"인증번호는 {otp}입니다."
        )
        msg = MIMEText(body)
        msg["To"] = email
        msg["Subject"] = "[ThinkingBridge] 회원가입 인증키가 발송되었습니다."

        try:
            server = s.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("woohyuk@khu.ac.kr", st.secrets["password"])
            server.sendmail("woohyuk@khu.ac.kr", email, msg.as_string())
            server.quit()
        except Exception as e:
            st.error(f"에러가 발생하였습니다. woohyuk@khu.ac.kr로 문의주세요. : {e}")
        return otp

    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if "signout" not in st.session_state:
        st.session_state["signout"] = False

    if not st.session_state[
        "signedout"
    ]:  # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox("로그인/회원가입", ["로그인", "회원가입"])

        if choice == "회원가입":
            email = st.text_input("이메일")
            st.session_state.password = st.text_input("비밀번호", type="password")
            username = st.text_input("이름")

            if "otp" not in st.session_state:
                st.session_state.otp = None
                st.session_state.otp_time = 5

            if st.button("계정생성"):
                with st.spinner("이메일 확인중..."):
                    if st.session_state.otp == None and ck(email.lower()):
                        # 이메일 인증 코드 전송
                        st.session_state.otp = send_verification(
                            username, email.lower()
                        )
                    elif st.session_state.otp == None:
                        st.error("유효한 이메일이 아닙니다.")

            if st.session_state.otp:
                if st.session_state.otp_time > 0:
                    # 인증번호 입력
                    rec_otp = st.text_input("인증번호", key="otp_input")
                    verify_button = st.button("인증번호 확인", key="verify_otp")

                    # 인증번호 확인
                    if verify_button and st.session_state.otp == rec_otp:
                        with st.spinner("계정 생성중..."):
                            if create_user(
                                email.lower(), st.session_state.password, username
                            ):
                                st.success("계정이 성공적으로 생성되었습니다.")
                                st.markdown("이메일과 비밀번호를 이용하여 로그인을 시도해주세요.")
                                st.balloons()
                            else:
                                st.warning(
                                    "회원가입 이력이 존재하는 이메일입니다. 입력하신 비밀번호와 이름으로 변경되었습니다."
                                )
                                st.markdown("변경된 비밀번호를 이용하여 로그인을 시도해주세요.")

                            # 타이머 및 OTP 초기화
                            st.session_state.otp = None
                            st.session_state.otp_time = 5
                    elif verify_button:
                        st.warning("인증번호를 정확히 기입해주세요.")
                        st.session_state.otp_time -= 1
                        # 남은 횟수 표시
                        st.write(f"남은 시도 횟수: {st.session_state.otp_time}")

                else:
                    st.error("인증 횟수가 종료되었습니다.")
                    # 타이머 및 OTP 초기화
                    st.session_state.otp = None
                    st.session_state.otp_time = 3
        else:
            # st.button('Login', on_click=f)
            email = st.text_input("이메일")
            st.session_state.password = st.text_input("비밀번호", type="password")
            st.button("로그인", on_click=f)

    if st.session_state.signout:
        st.text("이름: " + st.session_state.username)
        st.text("이메일: " + st.session_state.useremail)
        st.button("로그아웃", on_click=t)
