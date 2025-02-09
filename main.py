import streamlit as st
import groq
import os

# Load API key from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("❌ API Key is missing! Set it in the secrets.toml file.")
    st.stop()

# Initialize Groq client
client = groq.Client(api_key=api_key)

# Streamlit UI configurations
st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("Custom Crave Assistance")

# Initialize session state for chat history and user input
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are an AI expert in Pakistani cuisine and meal planning. You specialize in keto, Mediterranean, vegan, vegetarian, and non-vegetarian meal plans. You help users with meal suggestions, ingredients, nutritional values, and weight management (gain, loss, maintain). Do not answer questions outside this niche."}
    ]

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Function to handle user input submission
def process_input():
    user_input = st.session_state["user_input"]
    if user_input.strip():  # Ensure input is not empty
        # Append user message to chat history
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Call Groq API
        try:
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=st.session_state["messages"]
            )

            # Extract AI response
            ai_response = response.choices[0].message.content if response.choices else "⚠️ No response from AI."

            # Append AI response to chat history
            st.session_state["messages"].append({"role": "assistant", "content": ai_response})

        except Exception as e:
            st.session_state["messages"].append({"role": "assistant", "content": f"⚠️ Error: {e}"})

        # Clear the input field AFTER processing
        st.session_state["user_input"] = ""

# Display chat history
for msg in st.session_state["messages"]:
    role = "**You:**" if msg["role"] == "user" else "**AI:**"
    st.markdown(f"{role} {msg['content']}")

# User input field with `on_change` callback
st.text_input(
    "Type your message:",
    key="user_input",
    placeholder="Ask me anything about meal planning...",
    on_change=process_input
)
