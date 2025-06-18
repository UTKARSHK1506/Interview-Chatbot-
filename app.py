import streamlit as st
from openai import OpenAI


client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key= st.secrets["OPENAI_API_KEY"])


if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
    st.session_state.question_count = 0
    st.session_state.feedback_given = False

st.set_page_config(page_title="Interview Chatbot", page_icon=":robot_face:", layout="wide")

def show_setup_form():
    st.title("🎙️ Interview Chatbot")
    st.subheader("Personal Information", divider="rainbow")

    # Use session state for each parameter
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experience" not in st.session_state:
        st.session_state.experience = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""
    if "level" not in st.session_state:
        st.session_state.level = "Junior"
    if "position" not in st.session_state:
        st.session_state.position = "Software Engineer"
    if "company" not in st.session_state:
        st.session_state.company = "Google"

    st.session_state.name = st.text_input("Name", value=st.session_state.name, placeholder="Enter your name", max_chars=50)
    st.session_state.experience = st.text_area("Experience", value=st.session_state.experience, placeholder="Describe your experience", max_chars=500)
    st.session_state.skills = st.text_area("Skills", value=st.session_state.skills, placeholder="List your skills", max_chars=500)

    st.subheader("Company and Position", divider="rainbow")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.level = st.radio(
            "Level",
            key="level_radio",
            options=["Junior", "Mid", "Senior"],
            index=["Junior", "Mid", "Senior"].index(st.session_state.level)
        )

    with col2:
        st.session_state.position = st.selectbox(
            "Position",
            options=["Software Engineer", "Data Scientist", "Product Manager", "Designer"],
            index=["Software Engineer", "Data Scientist", "Product Manager", "Designer"].index(st.session_state.position)
        )

    st.session_state.company = st.selectbox(
        "Company",
        options=["Google", "Microsoft", "Amazon", "Facebook", "Apple"],
        index=["Google", "Microsoft", "Amazon", "Facebook", "Apple"].index(st.session_state.company)
    )

    if st.button("Start Chat"):
        st.session_state.setup_done = True
        st.session_state.question_count = 0
        st.session_state.feedback_given = False
        if 'openai' not in st.session_state:
            st.session_state['openai'] = "openai/gpt-4o"
        if 'messages' not in st.session_state:
            st.session_state.messages = [{
                "role": "system",
                "content": (
                    f"You are a HR Executive that takes questions from {st.session_state.name} "
                    f"who is applying for a {st.session_state.position} position at {st.session_state.company}. "
                    "You will ask questions based on the information provided by the user."
                )
            }]
        # No rerun needed

if not st.session_state.setup_done:
    show_setup_form()
else:
    st.info('''This is a chat interface where you can ask questions related to your interview preparation. Begin by entering your personal information and the position you are applying for.''')
    # Display existing chat history
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue  # Don't show system messages in the UI
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Limit to 5 interview questions
    if st.session_state.question_count < 15:
        if prompt := st.chat_input("How can I help you?"):
            # Store user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.question_count += 1

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant message (streaming)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Stream response from GPT-4o
                        response = client.chat.completions.create(
                            model=st.session_state['openai'],
                            messages=st.session_state.messages,
                            stream=True,
                        )

                        # Write response stream and collect final content
                        full_response = st.write_stream(response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                    except Exception as e:
                        st.error(f"❌ API Error: {e}")
    else:
        st.warning("You have reached the limit of 5 interview questions.")
        if not st.session_state.feedback_given:
            st.subheader("🔔 Interview Feedback")
            st.markdown("Please rate yourself on the following parameters (1 = Poor, 5 = Excellent):")
            tech = st.slider("Technical Skills", 1, 5, 3)
            comm = st.slider("Communication", 1, 5, 3)
            prob = st.slider("Problem Solving", 1, 5, 3)
            culture = st.slider("Culture Fit", 1, 5, 3)
            confidence = st.slider("Confidence", 1, 5, 3)
            if st.button("Submit Feedback"):
                st.success(
                    f"Thank you for your feedback! \n\n"
                    f"**Technical Skills:** {tech}/5\n"
                    f"**Communication:** {comm}/5\n"
                    f"**Problem Solving:** {prob}/5\n"
                    f"**Culture Fit:** {culture}/5\n"
                    f"**Confidence:** {confidence}/5"
                )
                st.session_state.feedback_given = True
