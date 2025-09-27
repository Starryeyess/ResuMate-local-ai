import streamlit as st
import hashlib
import json
import plotly.express as px
import pandas as pd
import database as db
import utils




def display_simplified_report(json_report_str):
    """
    Parses the JSON report and displays it in a simplified, visual format.
    """
    try:
        
        start_index = json_report_str.find('{')
        end_index = json_report_str.rfind('}') + 1
        
        if start_index == -1 or end_index == 0:
            raise json.JSONDecodeError("Could not find a JSON object in the response.", json_report_str, 0)
            
        clean_json_str = json_report_str[start_index:end_index]
        report_data = json.loads(clean_json_str)

        # --- 1. Overall Score and AI Summary ---
        st.subheader("📊 Your Summary")
        
        summary_prompt = prompts.SIMPLIFY_REPORT_PROMPT.format(json_report=clean_json_str)
        friendly_summary = ai_core.get_gemini_response(summary_prompt)
        st.markdown(friendly_summary)

        score = report_data.get("Overall Match Score", 0)
        st.progress(score, text=f"Overall Match Score: {score}%")
        
        st.markdown("---")

        # --- 2. Keywords Analysis ---
        st.subheader("🔑 Keywords Analysis")
        missing_keywords = report_data.get("Keywords Analysis", [])
        if missing_keywords:
            st.warning("Keywords from the job description that are missing in your resume:")
            cols = st.columns(3)
            for i, keyword in enumerate(missing_keywords):
                with cols[i % 3]:
                    st.info(f"• {keyword}")
        else:
            st.success("Great job! Your resume contains all the crucial keywords from the job descriptions.")

        st.markdown("---")

        # --- 3. Actionable Advice ---
        st.subheader("🚀 Your Next Steps")
        suggestions = report_data.get("Improvement Suggestions", [])
        if suggestions:
            for suggestion in suggestions:
                st.success(f"💡 {suggestion}")
        
        with st.expander("View Full JSON Report"):
            st.json(report_data)

    except (json.JSONDecodeError, KeyError):
        st.error("There was an issue parsing the analysis report. Displaying the raw text below.")
        st.markdown(json_report_str)

        
        # Allow user to see the full raw report if they want
        with st.expander("View Full JSON Report"):
            st.json(report_data)

    except (json.JSONDecodeError, KeyError) as e:
        st.error("There was an issue parsing the analysis report. Displaying the raw text below.")
        st.markdown(json_report_str)

# --- Page Configuration ---
st.set_page_config(page_title="ResuMate", page_icon="📄", layout="wide")

# --- USER AUTHENTICATION & SESSION STATE ---
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
    st.session_state.username = None
    st.session_state.name = None

def login_user(username, password):
    """Checks credentials against the database."""
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
    st.session_state.auth_status = False
    st.session_state.username = None
    st.session_state.name = None

# --- UI RENDERING ---
if not st.session_state.auth_status:
    # --- LOGIN / REGISTRATION UI ---
    st.title("Welcome to  ResuMate 🚀")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user(login_username, login_password):
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with col2:
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

    # Initialize session states for app features
    if 'job_descriptions' not in st.session_state:
        st.session_state.job_descriptions = []
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["**🎯 Matcher**", "**✅ ATS Checker**", "**✍️ Generator**", "**📈 Dashboard**", "**📂 Batch Processing**", "**📝 Interactive Editor**"])

    # In app.py

# ... (keep all the code before this)

    with tab1:
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
                    # Clear the text area after adding
                    st.rerun()

            st.markdown("---")
            
# Find the "Analyze Match" button in tab1 and REPLACE its if/else block with this:
            if st.button("Analyze Match", type="primary"):
                if uploaded_files and st.session_state.job_descriptions:
                    with st.spinner("Analyzing locally..."):
                        resume_text = utils.get_text_from_files(uploaded_files)
                        jd_text = "\n\n---\n\n".join(st.session_state.job_descriptions)

                        # --- NEW LOCAL CALCULATION ---
                        # Import the function at the top of app.py: from ai_core import calculate_match_score
                        score = calculate_match_score(resume_text, jd_text)

                        # Log the result to the database (we'll just log the score)
                        db.log_analysis(st.session_state.username, "Resume Matcher", f"{{'match_score': {score}}}")

                        # --- NEW DISPLAY LOGIC ---
                        st.subheader("📊 Analysis Result")
                        st.progress(int(score), text=f"Your resume matches the job description by {score:.2f}%")
                        st.info("This score is calculated locally based on keyword similarity using TF-IDF.")
                else:
                    st.error("Please upload at least one resume and add at least one job description.")
        # --- NEW FEATURE: Display JDs with a Remove Button ---
        if st.session_state.job_descriptions:
            st.markdown("---")
            st.subheader("Added Job Descriptions")
            
            # We iterate backwards to safely remove items from the list while looping
            for i in range(len(st.session_state.job_descriptions) - 1, -1, -1):
                jd = st.session_state.job_descriptions[i]
                col_jd, col_btn = st.columns([5, 1]) # Create columns for text and button
                with col_jd:
                    st.info(f"{jd[:100]}...")
                with col_btn:
                    # Each button needs a unique key
                    if st.button(f"Remove", key=f"remove_jd_{i}"):
                        st.session_state.job_descriptions.pop(i)
                        st.rerun() # Refresh the page to show the item is gone

# ... (keep the rest of your app.py code)
    with tab2:
        st.header("Check if Your Resume is ATS-Friendly")
        ats_resume = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="ats_resume")
        if st.button("Check ATS Compatibility", type="primary"):
            if ats_resume:
                with st.spinner("Scanning your resume..."):
                    resume_text = utils.get_text_from_files([ats_resume])
                    prompt = prompts.ATS_CHECKER_PROMPT.format(resume_text=resume_text)
                    response = ai_core.get_gemini_response(prompt)
                    try:
                        if '```json' in response:
                            response = response.split('```json')[1].split('```')[0]
                        report = json.loads(response)
                        db.log_analysis(st.session_state.username, "ATS Checker", json.dumps(report))
                        st.subheader(f"ATS Compatibility Report (Score: {report.get('ats_score', 'N/A')}/100)")
                        st.info(f"**Parsing & Compatibility:**\n{report.get('parsing_feedback')}")
                        st.warning(f"**Keyword Optimization:**\n{report.get('keyword_feedback')}")
                        st.info(f"**Formatting & Structure:**\n{report.get('formatting_feedback')}")
                        st.subheader("Actionable Advice")
                        for advice in report.get('actionable_advice', []):
                            st.success(f"- {advice}")
                    except (json.JSONDecodeError, KeyError):
                        st.error("Error processing AI report. Raw output:")
                        st.markdown(response)
            else:
                st.error("Please upload a resume to check.")

    with tab3:
        st.header("Generate ATS-Friendly Resume Content")
        user_input = st.text_area("Describe what you want to write...", height=200)
        if st.button("Generate Content", type="primary"):
            if user_input:
                with st.spinner("AI is crafting your content..."):
                    prompt = prompts.CONTENT_GENERATOR_PROMPT.format(user_info=user_input)
                    generated_content = ai_core.get_gemini_response(prompt)
                    db.log_analysis(st.session_state.username, "Content Generator", generated_content)
                    st.subheader("Generated Content")
                    st.markdown(generated_content)
                    st.markdown(utils.create_download_link(generated_content, "Generated_Resume_Content"), unsafe_allow_html=True)
            else:
                st.error("Please provide some input.")

    with tab4:
        st.header("📈 Your Analytics Dashboard")
        history_df = db.get_history_for_dashboard(st.session_state.username)
        if history_df.empty:
            st.info("No analysis history yet. Use other tabs to get started!")
        else:
            st.subheader("ATS Score Over Time")
            ats_data = history_df.dropna(subset=['ats_score'])
            if not ats_data.empty:
                fig = px.line(ats_data, x='timestamp', y='ats_score', title='Your ATS Score Progression', markers=True, labels={'timestamp': 'Date', 'ats_score': 'ATS Score (out of 100)'})
                fig.update_layout(yaxis_range=[0,100])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ATS checks performed yet to display a score progression.")
            st.subheader("Full Analysis History")
            st.dataframe(history_df[['timestamp', 'analysis_type', 'result']].rename(columns={'timestamp': 'Date', 'analysis_type': 'Analysis Type', 'result': 'AI Output'}))

    with tab5:
        st.header("📂 Process a Batch of Resumes")
        uploaded_zip = st.file_uploader("Upload a .zip file containing multiple resumes", type="zip", key="batch_zip")
        if st.button("Process Batch", type="primary"):
            if uploaded_zip:
                with st.spinner("Extracting and analyzing resumes..."):
                    resumes = utils.process_zip_file(uploaded_zip)
                    if not resumes:
                        st.error("Could not find supported files in the ZIP archive.")
                    else:
                        st.success(f"Found and processed {len(resumes)} resumes!")
                        for filename, resume_text in resumes.items():
                            with st.expander(f"**{filename}**"):
                                if "Error reading" in resume_text:
                                    st.error(resume_text)
                                else:
                                    prompt = prompts.BATCH_SUMMARY_PROMPT.format(resume_text=resume_text)
                                    summary = ai_core.get_gemini_response(prompt)
                                    st.markdown(summary)
            else:
                st.error("Please upload a ZIP file.")

    with tab6:
        st.header("📝 Live Resume Editor")
        editor_resume = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="editor_resume")
        if editor_resume:
            if 'file_id' not in st.session_state or st.session_state.file_id != editor_resume.id:
                st.session_state.file_id = editor_resume.id
                st.session_state.resume_text = utils.get_text_from_files([editor_resume])
                st.session_state.suggestions = []
        if st.button("Analyze for Suggestions"):
            if st.session_state.resume_text:
                with st.spinner("AI is analyzing your resume..."):
                    prompt = prompts.INTERACTIVE_EDITOR_PROMPT.format(resume_text=st.session_state.resume_text)
                    response = ai_core.get_gemini_response(prompt)
                    try:
                        if '```json' in response:
                            response = response.split('```json')[1].split('```')[0]
                        improvements = json.loads(response).get("improvements", [])
                        st.session_state.suggestions = improvements
                    except (json.JSONDecodeError, KeyError):
                        st.error("Could not parse AI suggestions.")
                        st.session_state.suggestions = []
            else:
                st.warning("Please upload a resume first.")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Resume")
            st.session_state.resume_text = st.text_area("Edit your resume text here:", value=st.session_state.resume_text, height=600, key="editable_resume")
        with col2:
            st.subheader("AI Suggestions")
            if not st.session_state.suggestions:
                st.info("Click 'Analyze for Suggestions' to get feedback.")
            else:
                for i, suggestion in enumerate(st.session_state.suggestions):
                    with st.container(border=True):
                        st.write("**Original:**")
                        st.warning(suggestion['original'])
                        st.write("**Suggestion:**")
                        st.success(suggestion['suggestion'])
                        if st.button(f"Apply Suggestion {i+1}", key=f"apply_{i}"):
                            st.session_state.resume_text = st.session_state.resume_text.replace(suggestion['original'], suggestion['suggestion'], 1)
                            st.session_state.suggestions.pop(i)
                            st.rerun()