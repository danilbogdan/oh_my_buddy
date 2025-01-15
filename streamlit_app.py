import os
import streamlit as st
import requests
from datetime import datetime

# Set the URL of the Django app view
app_host = os.getenv('PROMPT_API_HOST', 'http://127.0.0.1:8000/')
auth_api = app_host + "/auth/token/login/"
chat_api = app_host + "/chatbot/prompt/"
create_user_api = app_host + "/auth/users/"
delete_user_api = app_host + "/auth/users/me/"

st.set_page_config("Buddy - AI Assistant", "🤖", layout="wide")

st.title("Buddy - AI Assistant")

# Authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
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
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        with st.form(key="create_user_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            create_button = st.form_submit_button(label="Create User")

        if create_button:
            create_response = requests.post(
                create_user_api,
                data={"username": new_username, "password": new_password}
            )
            
            if create_response.status_code == 201:
                st.success("User created successfully! You can now login.")
            else:
                error_message = create_response.json()
                st.error(f"Failed to create user: {error_message}")

else:
    st.subheader(f"Welcome, {st.session_state['username']}")

    # User control buttons in better layout
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Logout", use_container_width=True):

            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.session_state["authenticated"] = False
            st.success("Logged out successfully")
            st.rerun()
    
    with col2:
        if st.button("Delete Account", type="primary", use_container_width=True):
            st.session_state['show_delete_confirm'] = True

    # Show delete confirmation form
    if st.session_state.get('show_delete_confirm', False):
        st.warning("⚠️ This action cannot be undone!")
        
        with st.form("delete_account_form"):
            current_password = st.text_input("Confirm your password", type="password")
            confirm_delete = st.form_submit_button("Confirm Delete", use_container_width=True)
        
        # Cancel button outside the form
        if st.button("Cancel", use_container_width=True):
            st.session_state['show_delete_confirm'] = False
            st.rerun()
            
        if confirm_delete:
            headers = {"Authorization": f'Token {st.session_state["token"]}'}
            delete_response = requests.delete(
                delete_user_api,
                headers=headers,
                json={"current_password": current_password}
            )

            if delete_response.status_code == 204:
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                st.session_state["authenticated"] = False
                st.success("Account deleted successfully")
                st.rerun()
            else:
                st.error(f"Failed to delete user: {delete_response.json()}")

if st.session_state["authenticated"]:
    # Fetch conversation history
    headers = {"Authorization": f'Token {st.session_state["token"]}'}
    history_response = requests.get(chat_api, headers=headers)

    if history_response.status_code == 200:
        st.session_state["conversation"] = history_response.json()

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
                    text = chunk.decode("utf-8", errors='replace')
                    chatbot_response += text
                    yield text
                st.session_state["conversation"].append({"role": "chatbot", "content": chatbot_response})
            with st.chat_message("assistant"):
                st.write(iter_content())

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
