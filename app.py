import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="IntakeAgent", page_icon="🏥", layout="centered")

# --- GROQ CLIENT ---
@st.cache_resource
def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found.")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# --- SYSTEM PROMPT ---
system_prompt = """You are an AI Medical Receptionist. 
Your ONLY job is to conduct a pre-visit patient intake. 

Rules:
1. Be polite, empathetic, and professional.
2. Ask ONE question at a time.
3. You need to collect: Chief Complaint, Duration of symptoms, Current Medications, and Allergies.
4. Once you have all 4 pieces of information, output a final summary in bullet points and tell the patient they are ready to see the doctor.
5. STRICT RULE: Do NOT answer medical questions. Do NOT suggest tests. Do NOT give medical advice. If the patient asks a medical question (e.g., "What are the side effects of this drug?" or "What tests do I need?"), you must reply: "I am just the intake assistant, so I cannot give medical advice. Please save that question to ask the doctor when they see you."
6. Keep your answers short. You are not a chatbot; you are a form-filler.

Start by asking for their name and chief complaint."""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am the AI Medical Assistant. I'll ask a few quick questions before you see the doctor. Could you please tell me your name and what brings you in today?"}
    ]

# --- UI ---
st.title("🏥 IntakeAgent")
st.write("Automated patient intake for clinics.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your reply here..."):
    # 1. Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages
                    ],
                    temperature=0.2
                )
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                
                # 3. Add AI message to state
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Reset button
with st.sidebar:
    st.header("Clinic Admin")
    if st.button("Start New Patient Intake"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am the AI Medical Assistant. I'll ask a few quick questions before you see the doctor. Could you please tell me your name and what brings you in today?"}
        ]
        st.rerun()
