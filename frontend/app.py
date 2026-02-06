import streamlit as st
import json
import requests
from .utils import upload_and_extract_resume, match_with_job, complete_analysis
import os

# Check backend connection
BACKEND_URL = "https://resume-matcher-api-mail.onrender.com"

def check_backend_health():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Page config
st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="📄",
    layout="wide"
)

# Show backend connection status
if check_backend_health():
    st.sidebar.success("✅ Connected to backend")
else:
    st.sidebar.error(f"❌ Cannot connect to backend at {BACKEND_URL}")
    st.sidebar.info("The backend service might be starting up. Please wait a moment and refresh.")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 AI Resume Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your resume and compare it with job descriptions using AI</div>', unsafe_allow_html=True)

# Initialize session state
if 'resume_details' not in st.session_state:
    st.session_state.resume_details = None
if 'match_result' not in st.session_state:
    st.session_state.match_result = None

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "🎯 Match with Job", "📊 Results"])

# Tab 1: Upload Resume
with tab1:
    st.header("Step 1: Upload Your Resume")
    
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🔍 Extract Resume Details", type="primary", use_container_width=True):
                with st.spinner("Analyzing your resume..."):
                    result = upload_and_extract_resume(uploaded_file)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.session_state.resume_details = result.get('resume_details')
                        st.success("✅ Resume extracted successfully!")
                        st.balloons()
        
        # Display extracted details
        if st.session_state.resume_details:
            st.divider()
            st.subheader("📋 Extracted Resume Details")
            
            details = st.session_state.resume_details
            
            # Contact Info
            if details.get('contact_info'):
                with st.expander("👤 Contact Information", expanded=True):
                    contact = details['contact_info']
                    col1, col2 = st.columns(2)
                    with col1:
                        if contact.get('name'):
                            st.write(f"**Name:** {contact['name']}")
                        if contact.get('email'):
                            st.write(f"**Email:** {contact['email']}")
                        if contact.get('phone'):
                            st.write(f"**Phone:** {contact['phone']}")
                    with col2:
                        if contact.get('location'):
                            st.write(f"**Location:** {contact['location']}")
                        if contact.get('linkedin'):
                            st.write(f"**LinkedIn:** {contact['linkedin']}")
                        if contact.get('github'):
                            st.write(f"**GitHub:** {contact['github']}")
            
            # Professional Summary
            if details.get('professional_summary'):
                with st.expander("📝 Professional Summary"):
                    st.write(details['professional_summary'])
            
            # Work Experience
            if details.get('work_experience'):
                with st.expander("💼 Work Experience"):
                    for exp in details['work_experience']:
                        st.write(f"**{exp.get('title', 'N/A')}** at **{exp.get('company', 'N/A')}**")
                        st.write(f"*{exp.get('start_date', '')} - {exp.get('end_date', '')}*")
                        if exp.get('responsibilities'):
                            st.write("Responsibilities:")
                            for resp in exp['responsibilities']:
                                st.write(f"  • {resp}")
                        st.divider()
            
            # Education
            if details.get('education'):
                with st.expander("🎓 Education"):
                    for edu in details['education']:
                        st.write(f"**{edu.get('degree', 'N/A')}** - {edu.get('institution', 'N/A')}")
                        if edu.get('graduation_date'):
                            st.write(f"Graduated: {edu['graduation_date']}")
                        if edu.get('gpa'):
                            st.write(f"GPA: {edu['gpa']}")
                        st.divider()
            
            # Skills
            col1, col2 = st.columns(2)
            with col1:
                if details.get('technical_skills'):
                    with st.expander("💻 Technical Skills"):
                        for skill in details['technical_skills']:
                            st.write(f"• {skill}")
            
            with col2:
                if details.get('certifications'):
                    with st.expander("🏆 Certifications"):
                        for cert in details['certifications']:
                            st.write(f"• {cert}")

# Tab 2: Match with Job
with tab2:
    st.header("Step 2: Compare with Job Description")
    
    if not st.session_state.resume_details:
        st.warning("⚠️ Please upload and extract your resume first in the 'Upload Resume' tab.")
    else:
        job_description = st.text_area(
            "Paste the job description here:",
            height=300,
            placeholder="Paste the full job description including requirements, responsibilities, and qualifications..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🎯 Analyze Match", type="primary", use_container_width=True, disabled=not job_description):
                with st.spinner("Analyzing match..."):
                    result = match_with_job(
                        st.session_state.resume_details,
                        job_description
                    )
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.session_state.match_result = result.get('match_analysis')
                        st.success("✅ Analysis complete!")
                        st.balloons()

# Tab 3: Results
with tab3:
    st.header("📊 Match Analysis Results")
    
    if not st.session_state.match_result:
        st.info("👆 Complete the previous steps to see the analysis results.")
    else:
        match = st.session_state.match_result
        
        # Match Score
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Match Percentage",
                value=f"{match.get('match_percentage', 0)}%"
            )
        
        with col2:
            verdict = match.get('verdict', 'N/A')
            verdict_color = {
                'STRONG_MATCH': '🟢',
                'MODERATE_MATCH': '🟡',
                'WEAK_MATCH': '🟠',
                'POOR_MATCH': '🔴'
            }
            st.metric(
                label="Verdict",
                value=f"{verdict_color.get(verdict, '⚪')} {verdict.replace('_', ' ')}"
            )
        
        with col3:
            likelihood = match.get('interview_likelihood', 'N/A')
            st.metric(
                label="Interview Likelihood",
                value=likelihood
            )
        
        st.divider()
        
        # Summary
        if match.get('summary'):
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📝 Summary")
            st.write(match['summary'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Strengths and Gaps
        col1, col2 = st.columns(2)
        
        with col1:
            if match.get('key_strengths'):
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.subheader("💪 Key Strengths")
                for strength in match['key_strengths']:
                    st.write(f"✅ {strength}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if match.get('matching_skills'):
                with st.expander("✅ Matching Skills"):
                    for skill in match['matching_skills']:
                        st.write(f"• {skill}")
        
        with col2:
            if match.get('gaps_to_address'):
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.subheader("🔧 Gaps to Address")
                for gap in match['gaps_to_address']:
                    st.write(f"⚠️ {gap}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if match.get('missing_critical_requirements'):
                with st.expander("❌ Missing Critical Requirements"):
                    for req in match['missing_critical_requirements']:
                        st.write(f"• {req}")
        
        st.divider()
        
        # Recommendations
        if match.get('recommendations'):
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(match['recommendations'], 1):
                st.write(f"{i}. {rec}")
        
        # Assessment Details
        with st.expander("📊 Detailed Assessment"):
            if match.get('experience_assessment'):
                st.write("**Experience Assessment:**")
                st.write(match['experience_assessment'])
            
            if match.get('education_fit'):
                st.write("\n**Education Fit:**")
                st.write(match['education_fit'])
        
        # Download Results
        st.divider()
        result_json = json.dumps({
            "resume_details": st.session_state.resume_details,
            "match_analysis": match
        }, indent=2)
        
        st.download_button(
            label="📥 Download Full Analysis (JSON)",
            data=result_json,
            file_name="resume_analysis.json",
            mime="application/json"
        )
