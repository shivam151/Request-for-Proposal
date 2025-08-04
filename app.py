import streamlit as st
import pandas as pd
import time
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from gemini_client import GeminiClient

# Enhanced UI components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_lottie import st_lottie

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Google API key not found. Please set it in your .env file.")
    st.stop()

# Initialize Gemini client
gemini = GeminiClient()

# Function to load CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Function to process uploaded files
def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text content"""
    if uploaded_file is not None:
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        
        with st.status(f"Processing {file_name}...", expanded=True) as status:
            if file_type == "text/plain":
                # Handle text files
                st.write("📄 Reading text file...")
                content = uploaded_file.getvalue().decode("utf-8")
                status.update(label=f"✅ {file_name} processed successfully!", state="complete")
                return content
                
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # Handle DOCX files
                st.write("📄 Converting DOCX to PDF...")
                st.write("🔍 Extracting text using Gemini...")
                content = gemini.extract_text_from_docx(uploaded_file)
                if content:
                    status.update(label=f"✅ {file_name} processed successfully!", state="complete")
                    return content
                else:
                    status.update(label=f"❌ Failed to process {file_name}", state="error")
                    return None
                    
            elif file_type == "application/pdf":
                # Handle PDF files
                st.write("📄 Processing PDF file...")
                st.write("🔍 Extracting text using Gemini...")
                content = gemini.extract_text_from_uploaded_pdf(uploaded_file)
                if content:
                    status.update(label=f"✅ {file_name} processed successfully!", state="complete")
                    return content
                else:
                    status.update(label=f"❌ Failed to process {file_name}", state="error")
                    return None
            else:
                st.error(f"Unsupported file type: {file_type}")
                return None
    return None

# Set page configuration
st.set_page_config(
    page_title="Project Management tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS (with error handling)
try:
    load_css("assets/style.css")
except:
    pass  # Continue without custom CSS if file doesn't exist

# Initialize session state for tracking progress and storing data
if 'step' not in st.session_state:
    st.session_state.step = 1  # Start at step 1
if 'rfp_text' not in st.session_state:
    st.session_state.rfp_text = ""
if 'company_profile' not in st.session_state:
    # Read company profile from file
    try:
        with open('D:/rfp_analysis_tool/company_profile.txt', 'r') as file:
            st.session_state.company_profile = file.read()
    except:
        st.session_state.company_profile = ""
if 'rfp_breakdown' not in st.session_state:
    st.session_state.rfp_breakdown = None
if 'eligibility_analysis' not in st.session_state:
    st.session_state.eligibility_analysis = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = None
if 'proposal' not in st.session_state:
    st.session_state.proposal = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_filename' not in st.session_state:
    st.session_state.current_filename = None

# Function to advance to next step
def next_step():
    st.session_state.step += 1
    st.session_state.processing = False

# Function to reset steps but keep company profile
def reset_process():
    company_profile_backup = st.session_state.company_profile
    for key in list(st.session_state.keys()):
        if key != 'company_profile':
            del st.session_state[key]
    st.session_state.step = 1
    st.session_state.company_profile = company_profile_backup
    st.session_state.processing = False

# Sidebar
with st.sidebar:
    # Logo and title
    st.title("Project Management Tool")
    
    # Progress tracker
    colored_header(
        label="Progress Tracker",
        description="Follow your proposal generation progress",
        color_name="green-70"
    )
    
    total_steps = 9
    
    # Calculate completion percentage
    completion = int((st.session_state.step - 1) / total_steps * 100)
    st.progress(completion / 100)
    st.write(f"**{completion}%** completed")
    add_vertical_space(1)
    
    # Display steps with visual indicators
    for i, step_name in enumerate([
        "Input RFP",
        "RFP Breakdown", 
        "Eligibility Analysis",
        "Requirements Extraction",
        "Task Generation",
        "Competitive Analysis",    # New step
        "Innovation Assessment",   # New step
        "Executive Briefing",      # New step
        "Proposal Generation"
    ], 1):
        if i < st.session_state.step:
            step_status = "✅ "  # Completed
        elif i == st.session_state.step:
            step_status = "🔄 "  # In progress
        else:
            step_status = "⏳ "  # Pending
        
        with stylable_container(
            key=f"step_{i}",
            css_styles="""
                {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
                """
        ):
            st.write(f"**{step_status} Step {i}: {step_name}**")
    
    add_vertical_space(2)
    
    # Action buttons
    if st.button("🔄 Start Over", use_container_width=True):
        reset_process()
        st.rerun()
    
    # Help info
    with st.expander("ℹ️ Help"):
        st.write("""
        **How to use this tool:**
        1. Upload or paste your RFP text
        2. Review the automatic analysis results
        3. Follow the process through eligibility check
        4. Examine requirements and tasks
        5. Generate and download your full proposal
        
        **Supported file formats:**
        - Text files (.txt)
        - PDF files (.pdf)
        - Word documents (.docx)
        
        All steps are processed automatically once you provide the RFP text.
        """)
    
    # Footer
    add_vertical_space(2)
    st.caption("© 2025 DataNova Solutions | Powered by Gemini API")

# Main content area
# Step 1: Input RFP

if st.session_state.step == 1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        colored_header(
            label="Input RFP Document",
            description="Provide the Request for Proposal text to analyze",
            color_name="blue-green-70"
        )
        
        input_method = st.radio(
            "Choose input method:",
            ["Upload RFP File", "Paste RFP Text"],
            horizontal=True
        )

        if input_method == "Upload RFP File":
            uploaded_file = st.file_uploader(
                "Upload RFP document",
                type=["txt", "pdf", "docx"],
                help="Supports text files (.txt), PDF files (.pdf), and Word documents (.docx)"
            )
            
            if uploaded_file is not None:
                st.session_state.current_filename = uploaded_file.name
                
                # Process the uploaded file
                extracted_text = process_uploaded_file(uploaded_file)
                
                if extracted_text:
                    st.session_state.rfp_text = extracted_text
                    st.success(f"✅ File '{uploaded_file.name}' processed successfully!")
                    
                    # Show preview of extracted text
                    with st.expander("📄 Preview extracted text", expanded=False):
                        st.text_area(
                            "Extracted content:",
                            value=extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                            height=200,
                            disabled=True
                        )
                else:
                    st.error("❌ Failed to extract text from the uploaded file. Please try a different file or paste the content manually.")
                    
        else:
            sample_placeholder = """Paste your RFP text here, or use our sample by clicking 'Load Sample RFP'"""
            
            rfp_text_input = st.text_area(
                "RFP Content:",
                height=400,
                placeholder=sample_placeholder,
                value=st.session_state.rfp_text
            )
            
            if rfp_text_input:
                st.session_state.rfp_text = rfp_text_input
            
            col1a, col1b = st.columns([1, 1])
            with col1a:
                if st.button("📄 Load Sample RFP", use_container_width=True):
                    try:
                        with open('D:/rfp_analysis_tool/sample_rfp.txt', 'r') as file:
                            st.session_state.rfp_text = file.read()
                            st.session_state.current_filename = "sample_rfp.txt"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Could not load sample RFP: {e}")
    
    with col2:
        # Lottie animation
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_bhebjzpu.json"  # Document analysis animation
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=200, key="document")
        
        # Company profile for eligibility analysis
        st.subheader("Company Profile")
        st.info("This profile will be used to analyze if your company meets the RFP requirements.")
        
        company_profile = st.text_area(
            "Company profile:",
            height=340,
            value=st.session_state.company_profile
        )
        
        if company_profile:
            st.session_state.company_profile = company_profile
    
    # Proceed button - only show if both RFP and company profile are provided
    if st.session_state.rfp_text and st.session_state.company_profile:
        st.success("✅ All information provided! Click below to start the analysis process.")
        
        # Show document info
        if st.session_state.current_filename:
            st.info(f"📄 Document: **{st.session_state.current_filename}** | Length: **{len(st.session_state.rfp_text):,} characters**")
        
        if st.button("▶️ Start Analysis Process", type="primary", use_container_width=True):
            st.session_state.processing = True
            st.session_state.step = 2
            st.rerun()
    else:
        st.warning("Please provide both RFP text and company profile to proceed.")

# Auto-process subsequent steps
elif st.session_state.step == 2:  # RFP Breakdown
    colored_header(
        label="RFP Breakdown Analysis",
        description="Comprehensive analysis of the RFP document",
        color_name="blue-green-70"
    )
    
    # Display file info
    if st.session_state.current_filename:
        st.info(f"Analyzing RFP document: **{st.session_state.current_filename}**", icon="📄")
    
    # Process breakdown if not done yet
    if not st.session_state.rfp_breakdown:
        with st.status("Analyzing RFP...", expanded=True) as status:
            st.write("Extracting key information from the RFP...")
            st.session_state.rfp_breakdown = gemini.analyze_rfp(st.session_state.rfp_text)
            time.sleep(1)
            st.write("Analysis complete! ✅")
            status.update(label="Analysis completed!", state="complete", expanded=False)
    
    # Display breakdown in an expander
    with st.expander("RFP Breakdown Analysis", expanded=True):
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.rfp_breakdown)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download RFP Breakdown",
                data=st.session_state.rfp_breakdown,
                file_name="rfp_breakdown.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Auto-proceed to next step
    st.success("RFP breakdown completed successfully!")
    if st.button("Proceed to eligibility analysis"):
        next_step()
        st.rerun()

elif st.session_state.step == 3:  # Eligibility Analysis
    colored_header(
        label="Eligibility Analysis",
        description="Determining if your company meets the RFP requirements",
        color_name="blue-green-70"
    )
    
    # Process eligibility if not done yet
    if not st.session_state.eligibility_analysis:
        with st.status("Analyzing eligibility...", expanded=True) as status:
            st.write("Extracting requirements from the RFP...")
            time.sleep(1)
            st.write("Comparing against company capabilities...")
            st.session_state.eligibility_analysis = gemini.analyze_eligibility(
                st.session_state.rfp_text, st.session_state.company_profile
            )
            time.sleep(1)
            st.write("Analysis complete! ✅")
            status.update(label="Eligibility analysis completed!", state="complete", expanded=False)
    
    # Display eligibility analysis in an expander
    with st.expander("Eligibility Analysis Results", expanded=True):
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.eligibility_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download Eligibility Analysis",
                data=st.session_state.eligibility_analysis,
                file_name="eligibility_analysis.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Ask user if they want to proceed based on eligibility
    st.write("### Decision Point")
    st.write("Based on the eligibility analysis, would you like to proceed with the proposal?")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Yes, proceed with analysis", type="primary", use_container_width=True):
            next_step()
            st.rerun()
    with col2:
        if st.button("❌ No, start over with a different RFP", use_container_width=True):
            reset_process()
            st.rerun()

elif st.session_state.step == 4:  # Requirements Extraction
    colored_header(
        label="Requirements Extraction",
        description="Identifying and categorizing all requirements in the RFP",
        color_name="blue-green-70"
    )
    
    # Process requirements if not done yet
    if not st.session_state.requirements:
        with st.status("Extracting requirements...", expanded=True) as status:
            st.write("Analyzing RFP for specific requirements...")
            time.sleep(1)
            st.write("Categorizing and prioritizing requirements...")
            st.session_state.requirements = gemini.extract_requirements(st.session_state.rfp_text)
            time.sleep(1)
            st.write("Extraction complete! ✅")
            status.update(label="Requirements extraction completed!", state="complete", expanded=False)
    
    # Display requirements in an expander
    with st.expander("Extracted Requirements", expanded=True):
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.requirements)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download Requirements",
                data=st.session_state.requirements,
                file_name="rfp_requirements.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Auto-proceed to next step
    st.success("Requirements extraction completed successfully!")
    if st.button("Proceed to task generation"):
        next_step()
        st.rerun()

elif st.session_state.step == 5:  # Task Generation
    colored_header(
        label="Task Generation",
        description="Creating actionable Jira-style tasks based on the requirements",
        color_name="blue-green-70"
    )
    
    # Process tasks if not done yet
    if not st.session_state.tasks:
        with st.status("Generating tasks...", expanded=True) as status:
            st.write("Converting requirements to actionable tasks...")
            time.sleep(1)
            st.write("Estimating effort and assigning task types...")
            st.session_state.tasks = gemini.generate_tasks(st.session_state.requirements)
            time.sleep(1)
            st.write("Task generation complete! ✅")
            status.update(label="Task generation completed!", state="complete", expanded=False)
    
    # Display tasks in an expander
    with st.expander("Generated Tasks", expanded=True):
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.tasks)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download Tasks",
                data=st.session_state.tasks,
                file_name="rfp_tasks.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Auto-proceed to next step
    st.success("Task generation completed successfully!")
    if st.button("Proceed to proposal generation"):
        next_step()
        st.rerun()

elif st.session_state.step == 6:  # Competitive Analysis
    colored_header(
        label="Competitive Analysis",
        description="Analyzing competitive landscape and positioning strategy",
        color_name="blue-green-70"
    )
    
    if 'competitive_analysis' not in st.session_state:
        st.session_state.competitive_analysis = None
    
    if not st.session_state.competitive_analysis:
        with st.status("Analyzing competitive landscape...", expanded=True) as status:
            st.write("Identifying likely competitors...")
            st.write("Analyzing competitive advantages...")
            st.session_state.competitive_analysis = gemini.analyze_competitive_landscape(
                st.session_state.rfp_text, st.session_state.company_profile
            )
            status.update(label="Competitive analysis completed!", state="complete", expanded=False)
    
    with st.expander("Competitive Analysis Results", expanded=True):
        st.markdown(st.session_state.competitive_analysis)
        st.download_button(
            label="📥 Download Competitive Analysis",
            data=st.session_state.competitive_analysis,
            file_name="competitive_analysis.md",
            mime="text/markdown"
        )
    
    if st.button("Proceed to innovation assessment"):
        next_step()
        st.rerun()

elif st.session_state.step == 7:  # Innovation Assessment
    colored_header(
        label="Innovation Assessment",
        description="Identifying opportunities for emerging technology integration",
        color_name="blue-green-70"
    )
    
    if 'innovation_assessment' not in st.session_state:
        st.session_state.innovation_assessment = None
    
    if not st.session_state.innovation_assessment:
        with st.status("Assessing innovation opportunities...", expanded=True) as status:
            st.write("Analyzing AI/ML integration potential...")
            st.write("Identifying automation opportunities...")
            st.session_state.innovation_assessment = gemini.assess_innovation_opportunities(
                st.session_state.rfp_text
            )
            status.update(label="Innovation assessment completed!", state="complete", expanded=False)
    
    with st.expander("Innovation Assessment Results", expanded=True):
        st.markdown(st.session_state.innovation_assessment)
        st.download_button(
            label="📥 Download Innovation Assessment",
            data=st.session_state.innovation_assessment,
            file_name="innovation_assessment.md",
            mime="text/markdown"
        )
    
    if st.button("Proceed to executive briefing"):
        next_step()
        st.rerun()

elif st.session_state.step == 8:  # Executive Briefing
    colored_header(
        label="Executive Briefing",
        description="C-suite level summary and decision recommendation",
        color_name="blue-green-70"
    )
    
    if 'executive_briefing' not in st.session_state:
        st.session_state.executive_briefing = None
    
    if not st.session_state.executive_briefing:
        with st.status("Generating executive briefing...", expanded=True) as status:
            st.write("Creating C-level summary...")
            st.write("Developing decision recommendations...")
            st.session_state.executive_briefing = gemini.generate_executive_briefing(
                st.session_state.rfp_text, st.session_state.company_profile
            )
            status.update(label="Executive briefing completed!", state="complete", expanded=False)
    
    with st.expander("Executive Briefing", expanded=True):
        st.markdown(st.session_state.executive_briefing)
        st.download_button(
            label="📥 Download Executive Briefing",
            data=st.session_state.executive_briefing,
            file_name="executive_briefing.md",
            mime="text/markdown"
        )
    
    if st.button("Proceed to final proposal generation"):
        next_step()
        st.rerun()

# Update the final step number to 9
elif st.session_state.step == 9:
    colored_header(
        label="Project Proposal Generation",
        description="Creating a comprehensive project proposal based on the RFP",
        color_name="blue-green-70"
    )
    
    # Process proposal if not done yet
    if not st.session_state.proposal:
        with st.status("Generating proposal...", expanded=True) as status:
            st.write("Analyzing all previous insights...")
            time.sleep(1)
            st.write("Crafting a comprehensive project proposal...")
            st.session_state.proposal = gemini.generate_project_proposal(st.session_state.rfp_text,st.session_state.company_profile)
            time.sleep(1)
            st.write("Proposal generation complete! ✅")
            status.update(label="Proposal generation completed!", state="complete", expanded=False)
    
    # Display proposal in an expander
    with st.expander("Complete Project Proposal", expanded=True):
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.proposal)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download Complete Proposal",
                data=st.session_state.proposal,
                file_name="rfp_proposal.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # Offer options to generate new proposal or start over
    st.success("🎉 Proposal generation process completed successfully!")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("💾 Download All Files as ZIP", use_container_width=True):
            st.info("This feature would create a ZIP file with all generated files.")
            
    with col2:
        if st.button("🔄 Generate New Proposal", use_container_width=True):
            # Reset only the proposal
            st.session_state.proposal = None
            st.rerun()
            
    with col3:
        if st.button("📄 Start New RFP Analysis", use_container_width=True):
            reset_process()
            st.rerun()

# Apply metric card styling
style_metric_cards()