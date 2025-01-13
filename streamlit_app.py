import os
import streamlit as st
import requests
from streamlit_cookies_controller import CookieController

# Set the URL of the Django app view
app_host = os.getenv('PROMPT_API_HOST', 'http://localhost:8000')
auth_api = app_host + "/auth/token/login/"
auth_api_logout = app_host + "/auth/token/logout/"
chat_api = app_host + "/chatbot/prompt/"

st.set_page_config("Chatbot Interface", "🤖", layout="wide")
controller = CookieController()

st.title("Chatbot Interface")

# Authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Check for token in cookies
if controller.get("token"):
    st.session_state["authenticated"] = True
    st.session_state["token"] = controller.get("token")
    st.session_state["username"] = controller.get("username")
    st.session_state["conversation"] = []

if not st.session_state["authenticated"]:
    st.subheader("Login")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

    if submit_button:
        auth_response = requests.post(
            auth_api, data={"username": username, "password": password}
        )

        if auth_response.status_code == 200:
            st.session_state["authenticated"] = True
            st.session_state["token"] = auth_response.json().get("auth_token")
            st.session_state["username"] = username
            st.session_state["conversation"] = []
            controller.set("token", st.session_state["token"], max_age=1 * 60 * 60)
            controller.set("username", st.session_state["username"], max_age=1 * 60 * 60)
            st.success("Logged in successfully")
        else:
            st.error("Invalid username or password")
        st.rerun()

    if st.button("Try without login"):
        st.session_state["authenticated"] = True
        st.session_state["token"] = None
        st.session_state["username"] = "Guest"
        st.session_state["conversation"] = []
        st.rerun()

else:
    st.subheader(f"Welcome, {st.session_state['username']}")

    if st.session_state["token"]:
        if st.button("Logout"):
            # Call the logout API
            headers = {"Authorization": f'Token {st.session_state["token"]}'}
            logout_response = requests.post(auth_api_logout, headers=headers)
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["username"] = None
            st.session_state["conversation"] = []
            controller.remove("token")
            controller.remove("username")
            st.success("Logged out successfully")
            st.rerun()

if st.session_state["authenticated"]:
    headers = {"Authorization": f'Token {st.session_state["token"]}'} if st.session_state["token"] else {}
    if "conversation" not in st.session_state or not st.session_state["conversation"]:
        history_response = requests.get(chat_api, headers=headers)

        if history_response.status_code == 200:
            st.session_state["conversation"] = history_response.json()
        elif history_response.status_code == 401:
            st.error("Call limit for anonymous users exceeded")

    # Display conversation history
    for message in st.session_state["conversation"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for user query
    if prompt := st.chat_input("Enter your query:"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state["conversation"].append({"role": "user", "content": prompt})
        response = requests.post(chat_api, json={"prompt": prompt}, headers=headers, stream=True)

        if response.status_code == 200:
            def iter_content():
                chatbot_response = ""
                for chunk in response.iter_content(chunk_size=20):
                    text = chunk.decode("utf-8", errors='ignore')
                    chatbot_response += text
                    yield text
                st.session_state["conversation"].append({"role": "assistant", "content": chatbot_response})
            with st.chat_message("assistant"):
                st.write(iter_content())
        elif response.status_code == 401:
            st.error("Call limit for anonymous users exceeded")
        else:
            st.write("Error: Unable to get response from chatbot.")

    # Clear chat button
    if st.button("Clear Chat"):
        clear_response = requests.delete(chat_api, headers=headers)
        if clear_response.status_code == 200:
            st.session_state["conversation"] = []
            st.rerun()
        else:
            st.error("Failed to clear chat")
