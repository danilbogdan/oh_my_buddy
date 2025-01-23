import os
import streamlit as st
import requests
from datetime import datetime

# Set the URL of the Django app view
app_host = os.getenv("PROMPT_API_HOST", "http://127.0.0.1:8000/")
auth_api = app_host + "/auth/token/login/"
create_user_api = app_host + "/auth/users/"
delete_user_api = app_host + "/auth/users/me/"
conversation_api = app_host + "/chatbot/conversation/"
agents_api = app_host + "/chatbot/agents/"

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
            auth_response = requests.post(auth_api, data={"username": username, "password": password})

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
            create_response = requests.post(create_user_api, data={"username": new_username, "password": new_password})

            if create_response.status_code == 201:
                st.success("User created successfully! You can now login.")
            else:
                error_message = create_response.json()
                st.error(f"Failed to create user: {error_message}")

if st.session_state["authenticated"]:
    # User controls in sidebar
    with st.sidebar:
        st.info(f"Logged in as: {st.session_state['username']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state["authenticated"] = False
                st.success("Logged out successfully")
                st.rerun()

        with col2:
            if st.button("Delete Account", type="primary", use_container_width=True):
                st.session_state["show_delete_confirm"] = True

        # Show delete confirmation form
        if st.session_state.get("show_delete_confirm", False):
            st.warning("⚠️ This action cannot be undone!")

            with st.form("delete_account_form"):
                current_password = st.text_input("Confirm your password", type="password")
                confirm_delete = st.form_submit_button("Confirm Delete", use_container_width=True)

            # Cancel button outside the form
            if st.button("Cancel", use_container_width=True):
                st.session_state["show_delete_confirm"] = False
                st.rerun()

            if confirm_delete:
                headers = {"Authorization": f'Token {st.session_state["token"]}'}
                delete_response = requests.delete(
                    delete_user_api, headers=headers, json={"current_password": current_password}
                )

                if delete_response.status_code in [204, 200]:
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state["authenticated"] = False
                    st.success("Account deleted successfully")
                    st.rerun()
                else:
                    st.error(f"Failed to delete user: {delete_response.json()}")

        st.markdown("---")
        st.header("💬 Conversations")
        st.markdown("---")

        # Create new conversation button with better visibility
        if st.button("➕ New Conversation", type="primary", use_container_width=True):
            headers = {"Authorization": f'Token {st.session_state["token"]}'}
            response = requests.post(conversation_api, headers=headers)
            if response.status_code == 201:
                if "current_conversation" not in st.session_state:
                    st.session_state["current_conversation"] = response.json()
                st.rerun()

        # Add a small spacing
        st.markdown("<br>", unsafe_allow_html=True)

        # Rest of the sidebar code remains the same
        headers = {"Authorization": f'Token {st.session_state["token"]}'}
        conv_response = requests.get(conversation_api, headers=headers)

        if conv_response.status_code == 200:
            conversations = conv_response.json()

            for conv in conversations:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    # Show conversation title with click handling
                    if st.button(conv["title"] or "New Chat", key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state["current_conversation"] = conv
                        st.session_state["conversation"] = []  # Clear current messages
                        st.rerun()

                with col2:
                    # Rename conversation
                    if st.button("✏️", key=f"rename_{conv['id']}", use_container_width=True):
                        st.session_state[f"rename_conv_{conv['id']}"] = True

                with col3:
                    # Delete conversation
                    if st.button("🗑️", key=f"delete_{conv['id']}", use_container_width=True):
                        delete_url = f"{conversation_api}{conv['id']}/"
                        delete_response = requests.delete(delete_url, headers=headers)
                        if delete_response.status_code in [204, 200]:
                            if st.session_state.get("current_conversation", {}).get("id") == conv["id"]:
                                st.session_state.pop("current_conversation", None)
                            st.rerun()

                # Show rename form if requested
                if st.session_state.get(f"rename_conv_{conv['id']}", False):
                    with st.form(key=f"rename_form_{conv['id']}"):
                        new_title = st.text_input("New title", value=conv["title"] or "")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Save", use_container_width=True):
                                update_url = f"{conversation_api}{conv['id']}/"
                                update_response = requests.patch(update_url, headers=headers, json={"title": new_title})
                                if update_response.status_code == 200:
                                    st.session_state[f"rename_conv_{conv['id']}"] = False
                                    st.rerun()
                        with col2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state[f"rename_conv_{conv['id']}"] = False
                                st.rerun()

    # Remove the welcome header since username is now in sidebar
    if "current_conversation" not in st.session_state:
        st.info("Select a conversation from the sidebar or create a new one")
    else:
        current_conv = st.session_state["current_conversation"]

        # Add agent selector
        headers = {"Authorization": f'Token {st.session_state["token"]}'}
        agents_response = requests.get(agents_api, headers=headers)

        if agents_response.status_code == 200:
            agents = agents_response.json()
            agent_options = {a["name"]: a["id"] for a in agents}
            selected_agent = st.selectbox(
                "Select Agent",
                options=list(agent_options.keys()),
                index=0 if agent_options else None,
            )

            if selected_agent and "current_agent_id" not in st.session_state:
                st.session_state["current_agent_id"] = agent_options[selected_agent]

        st.subheader(current_conv["title"] or "New Chat")

        # Fetch conversation history
        conv_url = f"{conversation_api}{current_conv['id']}/"
        history_response = requests.get(conv_url, headers=headers)

        if history_response.status_code == 200:
            st.session_state["conversation"] = history_response.json()

        # Display conversation history
        for message in st.session_state["conversation"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input field for user query
        if prompt := st.chat_input("Enter your query:"):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state["conversation"].append({"role": "user", "content": prompt})

            response = requests.post(
                conv_url,
                json={"prompt": prompt, "agent_id": st.session_state.get("current_agent_id")},
                headers=headers,
                stream=True,
            )

            if response.status_code == 200:

                def iter_content():
                    chatbot_response = ""
                    temp_response = b""
                    for chunk in response.iter_content():
                        try:
                            temp_response += chunk
                            yield temp_response.decode("utf-8")
                            chatbot_response += temp_response.decode("utf-8")
                            temp_response = b""
                        except UnicodeDecodeError:
                            pass
                    st.session_state["conversation"].append({"role": "chatbot", "content": chatbot_response})

                with st.chat_message("assistant"):
                    st.write_stream(iter_content())
            else:
                st.error("Error: Unable to get response from chatbot.")
