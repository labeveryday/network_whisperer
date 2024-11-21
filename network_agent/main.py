import streamlit as st
from chat_engine import chat
from bedrock_utils import initialize_bedrock_client
from tools import get_all_tools


def main():
    st.title("AWS Network Assistant")
    st.write("Ask about VPCs, Internet Gateways, NAT Gateways, Route Tables, and other network components.")

    # Initialize the bedrock client and tools
    if 'bedrock_client' not in st.session_state:
        st.session_state.bedrock_client = initialize_bedrock_client()
    if 'tools' not in st.session_state:
        st.session_state.tools = get_all_tools()
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Create a chat input
    user_input = st.chat_input("Type your question here...")

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"][0]["text"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"][0]["text"])

    # Handle new user input
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": [{"text": user_input}]
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)

        # Get and display assistant response
        with st.chat_message("assistant"):
            response = chat(
                user_input, 
                st.session_state.messages, 
                st.session_state.bedrock_client, 
                st.session_state.tools
            )
            st.write(response[-1]["content"][0]["text"])

        # Add assistant response to chat history
        st.session_state.messages.extend(response)

if __name__ == "__main__":
    main()
