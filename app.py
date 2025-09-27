import streamlit as st
import hashlib
import json
import plotly.express as px
import pandas as pd
import database as db
import utils
import ai_core
import nltk

# --- Page Configuration ---
st.set_page_config(page_title="ResuMate", page_icon="📄", layout="wide")

# --- NLTK Data Check ---
# This ensures the app doesn't crash if the user hasn't downloaded the data.
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
except LookupError:
    st.error("One or more NLTK data packages are not found!")
    st.info("Please run the following command in your terminal to download them, then refresh this page:")
    st.code("python -c \"import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('stopwords')\"")
    st.stop()

# --- USER AUTHENTICATION & SESSION STATE ---
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
    st.session_state.username = None
    st.session_state.name = None

def login_user(username, password):
    """Checks credentials against the database."""
    # This function remains the same
    conn = db.db_connect()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    db_password_hash = c.fetchone()
    conn.close()
    if db_password_hash:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash == db_password_hash[0]:
            st.session_state.auth_status = True
            st.session_state.username = username
            st.session_state.name = username.capitalize()
            return True
    return False

def logout_user():
    """Logs the user out."""
    st.session_state.auth_status = False
    st.session_state.username = None
    st.session_state.name = None

# --- UI RENDERING ---
if not st.session_state.auth_status:
    # --- LOGIN / REGISTRATION UI ---
    st.title("Welcome to ResuMate 🚀")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user(login_username, login_password):
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
        with st.expander("New here? Register now!"):
            st.subheader("Create a New Account")
            new_username = st.text_input("Username", key="new_user")
            new_password = st.text_input("Password", type="password", key="new_pass")
            if st.button("Register"):
                if new_username and new_password:
                    if db.add_user(new_username, new_password):
                        st.success("Account created successfully! You can now log in.")
                    else:
                        st.error("Username already exists.")
                else:
                    st.warning("Please enter both a username and a password.")
else:
    # --- MAIN APPLICATION LOGIC ---
    st.sidebar.title(f"Welcome, {st.session_state.name}!")
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

    # Initialize session states
    if 'job_descriptions' not in st.session_state:
        st.session_state.job_descriptions = []
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["**🎯 Matcher**", "**✅ ATS Checker**", "**✍️ Generator**", "**📈 Dashboard**", "**📂 Batch Processing**", "**📝 Interactive Editor**"])

    with tab1:
        # This tab remains largely the same
        st.header("Analyze Your Resume Against Job Descriptions")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Your Resume(s)")
            uploaded_files = st.file_uploader("Upload your resume(s) (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True, key="matcher_uploader")
        
        with col2:
            st.subheader("Job Description(s)")
            new_jd = st.text_area("Paste a new job description here", height=150, key="new_jd")
            if st.button("Add Job Description"):
                if new_jd:
                    st.session_state.job_descriptions.append(new_jd)
                    st.success("Job description added!")
                    st.rerun()

            st.markdown("---")
            
            if st.button("Analyze Match", type="primary"):
                if uploaded_files and st.session_state.job_descriptions:
                    with st.spinner("Analyzing locally..."):
                        resume_text = utils.get_text_from_files(uploaded_files)
                        jd_text = "\n\n---\n\n".join(st.session_state.job_descriptions)
                        
                        score = ai_core.calculate_match_score(resume_text, jd_text)
                        db.log_analysis(st.session_state.username, "Resume Matcher", json.dumps({'match_score': score}))

                        st.subheader("📊 Analysis Result")
                        st.progress(int(score), text=f"Your resume matches the job description by {score:.2f}%")
                        st.info("This score is calculated locally based on keyword similarity using TF-IDF.")
                else:
                    st.error("Please upload at least one resume and add at least one job description.")

        if st.session_state.job_descriptions:
            st.markdown("---")
            st.subheader("Added Job Descriptions")
            for i in range(len(st.session_state.job_descriptions) - 1, -1, -1):
                jd = st.session_state.job_descriptions[i]
                col_jd, col_btn = st.columns([5, 1])
                with col_jd:
                    st.info(f"{jd[:100]}...")
                with col_btn:
                    if st.button(f"Remove", key=f"remove_jd_{i}"):
                        st.session_state.job_descriptions.pop(i)
                        st.rerun()

    with tab2:
        st.header("✅ Check if Your Resume is ATS-Friendly")
        ats_resume = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="ats_resume")
        if st.button("Check ATS Compatibility", type="primary"):
            if ats_resume:
                with st.spinner("Scanning your resume..."):
                    resume_text = utils.get_text_from_files([ats_resume])
                    report = ai_core.analyze_ats_friendliness(resume_text)
                    db.log_analysis(st.session_state.username, "ATS Checker", json.dumps(report))
                    
                    st.subheader(f"ATS Compatibility Report (Score: {report.get('ats_score', 0)}/100)")
                    
                    st.info(f"**Contact Info:** Found {', '.join(report['contact_info_feedback']['found'])}. Missing: {', '.join(report['contact_info_feedback']['missing'])}")
                    st.info(f"**Standard Sections:** Found {len(report['sections_feedback']['found'])} sections like '{report['sections_feedback']['found'][0]}' and '{report['sections_feedback']['found'][1]}'.")
                    st.info(f"**Action Verbs:** Found {report['action_verbs_feedback']['good_lines']} of {report['action_verbs_feedback']['total_lines']} bullet points starting with an action verb. {report['action_verbs_feedback']['feedback']}")
                    st.info(f"**Top Keywords:** Your resume's top keywords are: {', '.join(report['keyword_feedback']['top_keywords'])}.")
            else:
                st.error("Please upload a resume to check.")

    with tab3:
        st.header("✍️ Template-Based Content Generator")
        st.warning("This is a simple template generator, not a creative AI. It provides a starting point for your resume sections.")
        user_input = st.text_area("Describe what you want to write (e.g., 'a professional summary for a data analyst' or 'bullet points').", height=150)
        if st.button("Generate Content", type="primary"):
            if user_input:
                with st.spinner("Generating from template..."):
                    generated_content = ai_core.generate_content_local(user_input)
                    db.log_analysis(st.session_state.username, "Content Generator", generated_content)
                    st.subheader("Generated Content")
                    st.markdown(generated_content)
            else:
                st.error("Please provide some input.")

    with tab4:
        st.header("📈 Your Analytics Dashboard")
        history_df = db.get_history_for_dashboard(st.session_state.username)
        if history_df.empty:
            st.info("No analysis history yet. Use other tabs to get started!")
        else:
            st.subheader("Match Score Over Time")
            match_data = history_df.dropna(subset=['match_score'])
            if not match_data.empty:
                fig = px.line(match_data, x='timestamp', y='match_score', title='Your Resume Match Score Progression', markers=True)
                fig.update_layout(yaxis_range=[0,100])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Resume Matcher analyses performed yet.")

            st.subheader("ATS Score Over Time")
            ats_data = history_df.dropna(subset=['ats_score'])
            if not ats_data.empty:
                fig_ats = px.line(ats_data, x='timestamp', y='ats_score', title='Your ATS Score Progression', markers=True)
                fig_ats.update_layout(yaxis_range=[0,100])
                st.plotly_chart(fig_ats, use_container_width=True)
            else:
                st.info("No ATS checks performed yet.")

    with tab5:
        st.header("📂 Process a Batch of Resumes")
        analysis_type = st.radio("Select Analysis Type:", ("Resume Matcher", "ATS Checker"), horizontal=True)
        uploaded_zip = st.file_uploader("Upload a .zip file containing multiple resumes", type="zip", key="batch_zip")
        
        jd_for_batch = ""
        if analysis_type == "Resume Matcher":
            jd_for_batch = st.text_area("Paste the single job description to match all resumes against:", height=150)

        if st.button("Process Batch", type="primary"):
            if uploaded_zip:
                if analysis_type == "Resume Matcher" and not jd_for_batch:
                    st.error("Please provide a job description for the Resume Matcher.")
                else:
                    with st.spinner("Extracting and analyzing resumes..."):
                        resumes = utils.process_zip_file(uploaded_zip)
                        st.success(f"Found and processed {len(resumes)} resumes!")
                        for filename, resume_text in resumes.items():
                            with st.expander(f"**{filename}**"):
                                if "Error reading" in resume_text:
                                    st.error(resume_text)
                                else:
                                    if analysis_type == "ATS Checker":
                                        report = ai_core.analyze_ats_friendliness(resume_text)
                                        st.write(f"**ATS Score: {report.get('ats_score', 0)}/100**")
                                    elif analysis_type == "Resume Matcher":
                                        score = ai_core.calculate_match_score(resume_text, jd_for_batch)
                                        st.write(f"**Match Score: {score:.2f}%**")
            else:
                st.error("Please upload a ZIP file.")

    with tab6:
        st.header("📝 Interactive Editor")
        st.info("This editor identifies common weak phrases and suggests stronger alternatives.")
        editor_resume = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="editor_resume")
        
        if editor_resume:
            if 'file_id' not in st.session_state or st.session_state.file_id != editor_resume.id:
                st.session_state.file_id = editor_resume.id
                st.session_state.resume_text = utils.get_text_from_files([editor_resume])
                st.session_state.suggestions = []
        
        if st.button("Analyze for Suggestions"):
            if st.session_state.resume_text:
                with st.spinner("Analyzing your resume for weak phrases..."):
                    suggestion_data = ai_core.get_interactive_suggestions(st.session_state.resume_text)
                    st.session_state.suggestions = suggestion_data.get("improvements", [])
            else:
                st.warning("Please upload a resume first.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Resume")
            st.session_state.resume_text = st.text_area("Edit your resume text here:", value=st.session_state.resume_text, height=600, key="editable_resume")
        with col2:
            st.subheader("Improvement Suggestions")
            if not st.session_state.suggestions:
                st.info("Click 'Analyze for Suggestions' to get feedback.")
            else:
                for i, suggestion in enumerate(st.session_state.suggestions):
                    with st.container(border=True):
                        st.warning(f"**Original:** {suggestion['original']}")
                        st.success(f"**Suggestion:** {suggestion['suggestion']}")

