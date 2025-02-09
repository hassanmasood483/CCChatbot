import streamlit as st
import groq
import os

# Load API key
api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error("❌ API Key is missing! Set it in the secrets.toml file.")
    st.stop()

# Initialize Groq client
client = groq.Client(api_key=api_key)

# Streamlit UI configurations
st.set_page_config(page_title="AI Chatbot", layout="wide")

# Custom CSS to style the title and input field
st.markdown("""
    <style>
        /* Align the title to the top left */
        .title-container {
            position: absolute;
            top: 10px;
            left: 20px;
            font-size: 32px;
            font-weight: bold;
        }
        
        /* Keep the chat area scrollable */
        .chat-container {
            max-height: 70vh;
            overflow-y: auto;
            padding-bottom: 80px;
        }

        /* Fix the input box at the bottom */
        .stTextInput {
            position: fixed;
            bottom: 10px;
            width: 80%;
            left: 10%;
            z-index: 100;
            padding: 10px;
        }
    </style>
    <div class="title-container">Custom Crave Assistance</div>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# System prompt for AI
system_prompt = {
    "role": "system",
    "content": (
        "You are a knowledgeable AI assistant specializing in Pakistani cuisine, meal planning, nutrition, and healthy eating. "
        "You can answer questions about recipes, meal plans, ingredients, health benefits of foods, and dietary needs. "
        "You are also an expert in weight management, including weight gain, weight loss, and maintaining a balanced diet. "
        "You do NOT answer questions unrelated to food, nutrition, or health. "
        "If a question is not food-related, politely redirect the user to meal planning or healthy eating topics."
    )
}

# Function to check if query is relevant
def is_relevant_query(query):
    general_greetings = ["hi", "hello", "hey", "salam", "how are you", "good morning", "good evening"]
    
    relevant_keywords = [
        "meal", "recipe", "food", "nutrition", "diet", "calories", "Pakistani", 
        "keto", "vegan", "vegetarian", "non-veg", "healthy eating", "snacks",
        "weight gain", "gain weight", "weight loss", "lose weight", "muscle gain", "bulk up",
        "weight management", "fat loss", "protein foods", "carbs", "fats", "fitness diet", "low carb"
    ]
    
    query_lower = query.lower()

    if any(greet in query_lower for greet in general_greetings):
        return True

    if any(keyword in query_lower for keyword in relevant_keywords):
        return True

    return False

# Function to process user input
def process_input():
    user_input = st.session_state["user_input"].strip()
    
    if user_input:
        # Add user message to session state
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Generate AI response
        if not is_relevant_query(user_input):
            ai_response = "I specialize in Pakistani cuisine, nutrition, and meal planning. Please ask something related to food, diet, or healthy eating."
        else:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[system_prompt] + st.session_state["messages"]
                )
                ai_response = response.choices[0].message.content if response.choices else "⚠️ No response from AI."
            except Exception as e:
                ai_response = f"⚠️ Error: {e}"

        # Add AI response to session state
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})

        # Clear input box
        st.session_state["user_input"] = ""

# **Display chat history**
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(f"**{'You' if role == 'user' else 'AI'}:** {msg['content']}")
st.markdown('</div>', unsafe_allow_html=True)

# **Sticky input field**
st.text_input(
    "",
    key="user_input",
    placeholder="Ask me about meal planning, nutrition, and Pakistani cuisine...",
    on_change=process_input
)
