import os
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
from docx2pdf import convert
from pathlib import Path
import streamlit as st

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiClient:
    def __init__(self, model_name="gemini-2.0-flash"):
        """Initialize the Gemini client with the specified model"""
        self.model = genai.GenerativeModel(model_name)
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract_text_from_docx(self, docx_file):
        """
        Convert DOCX to PDF and then extract text using Gemini
        """
        try:
            # Create temporary directory for file processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded DOCX file temporarily
                docx_path = os.path.join(temp_dir, "document.docx")
                with open(docx_path, "wb") as f:
                    f.write(docx_file.getvalue())
                
                # Convert DOCX to PDF
                pdf_path = os.path.join(temp_dir, "document.pdf")
                convert(docx_path, pdf_path)
                
                # Extract text from PDF using Gemini
                return self.extract_text_from_pdf_file(pdf_path)
                
        except Exception as e:
            st.error(f"Error processing DOCX file: {str(e)}")
            return None
    
    def extract_text_from_pdf_file(self, pdf_path):
        """
        Extract text from PDF file using Gemini's multimodal capabilities
        """
        try:
            # Upload file to Gemini
            with open(pdf_path, 'rb') as f:
               pdf_bytes = f.read()
            
            # Extract text using Gemini
            prompt = """
            Please extract all text content from this PDF document. 
            Return only the extracted text without any additional formatting or commentary.
            Preserve the structure and organization of the content as much as possible.
            """
            
            # Create the image part from PDF bytes (first page)
            # Note: For multi-page PDFs, you may need to split it first
            response = self.model.generate_content([
               prompt,
               {'mime_type': 'application/pdf', 'data': pdf_bytes}
            ])
            
            # Process and return the extraction result
            return response.text
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def extract_text_from_uploaded_pdf(self, pdf_file):
        """
        Extract text from uploaded PDF file using Gemini
        """
        try:
            # Create temporary file for PDF processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                # Extract text using Gemini
                text = self.extract_text_from_pdf_file(temp_file_path)
                return text
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            st.error(f"Error processing uploaded PDF: {str(e)}")
            return None
    
    def analyze_eligibility(self, rfp_text, company_profile):
        """
        Analyze if the company meets the eligibility requirements in the RFP
        """
        prompt = f"""
        You are an experienced bid manager specializing in evaluating RFP eligibility. 
        Based on the following RFP document and company profile, analyze whether the company meets the basic eligibility requirements to respond to this RFP.
        
        RFP Text:
        {rfp_text}
        
        Company Profile:
        {company_profile}
        
        Provide a comprehensive eligibility analysis with the following sections:
        
        1. **Summary of Eligibility**:
           - Overall assessment of eligibility (Fully Eligible, Partially Eligible, Not Eligible)
           - Executive summary of key findings
        
        2. **Mandatory Requirements Analysis**:
           - Table listing all mandatory requirements from the RFP
           - For each requirement, indicate whether the company meets it (Met, Partially Met, Not Met)
           - Provide justification for each assessment based on the company profile
        
        3. **Gap Analysis**:
           - Identify any significant gaps between RFP requirements and company capabilities
           - Suggest possible ways to address these gaps (partnerships, new hires, etc.)
        
        4. **Competitive Position**:
           - Assess how well the company is positioned compared to likely competitors
           - Identify any unique advantages or disadvantages
        
        5. **Recommendation**:
           - Clear recommendation on whether to proceed with a proposal
           - If proceeding, note any special considerations that should be addressed in the proposal
        
        Format your response in markdown, with clear headings, tables, and bullet points.
        Use factual, objective language based strictly on the information provided.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
        
    def generate_project_proposal(self, rfp_text, company_profile):
        """
        Generate a comprehensive project proposal addressing semantic gaps in typical proposals
        """
        prompt = f"""
        You are an expert proposal writer specializing in strategic business transformation proposals. 
        Create a comprehensive, executive-ready project proposal that goes beyond basic technical delivery 
        to demonstrate strategic business value and competitive differentiation.

        RFP Text:
        {rfp_text}

        Company Profile:
        {company_profile}

        Create a proposal with the following enhanced sections:

        1. **EXECUTIVE SUMMARY & STRATEGIC ALIGNMENT**:
        - Quantifiable business impact and ROI projections with timelines
        - Strategic alignment with client's long-term business objectives
        - Competitive advantage creation and market positioning benefits
        - Executive-level value propositions that resonate with C-suite decision makers

        2. **COMPANY PROFILE & COMPETITIVE DIFFERENTIATION**:
        - Unique market position and proprietary methodologies
        - Industry-specific expertise and relevant case studies with measurable outcomes
        - Innovation track record and emerging technology adoption
        - Partnership ecosystem and vendor relationships

        3. **BUSINESS TRANSFORMATION VISION**:
        - Comprehensive understanding of client's industry challenges and market forces
        - Digital transformation roadmap beyond immediate project scope
        - Change management strategy addressing cultural and organizational transformation
        - Future-state business capabilities and competitive positioning

        4. **SOLUTION ARCHITECTURE & INNOVATION**:
        - Modern, scalable architecture with cloud-native approaches
        - AI/ML integration opportunities and data-driven insights
        - API-first design and microservices architecture where applicable
        - Security-by-design and compliance framework
        - Emerging technology integration roadmap (IoT, blockchain, etc.)

        5. **IMPLEMENTATION METHODOLOGY & RISK MITIGATION**:
        - Agile/DevOps delivery methodology with continuous value delivery
        - Comprehensive risk assessment with quantified impact analysis
        - Scenario planning and contingency strategies
        - Quality assurance framework and success metrics
        - Stakeholder engagement and communication strategy

        6. **TEAM STRUCTURE & CAPABILITY BUILDING**:
        - Senior leadership involvement and escalation procedures
        - Knowledge transfer and capability building programs
        - Center of Excellence establishment
        - Long-term skill development and certification roadmaps

        7. **FINANCIAL MODEL & VALUE REALIZATION**:
        - Detailed cost-benefit analysis with NPV calculations
        - Phased investment approach with quick wins identification
        - Total Economic Impact (TEI) analysis
        - Cost optimization strategies and efficiency gains
        - Flexible pricing models and payment structures

        8. **RISK MANAGEMENT & BUSINESS CONTINUITY**:
        - Enterprise risk assessment matrix with probability and impact scores
        - Business continuity planning and disaster recovery strategies
        - Vendor risk management and third-party dependencies
        - Compliance and regulatory risk mitigation
        - Change management risk assessment

        9. **INNOVATION & FUTURE ROADMAP**:
        - Technology evolution strategy and platform extensibility
        - Industry 4.0 readiness and digital maturity advancement
        - Sustainability and ESG considerations
        - Competitive intelligence and market trend analysis
        - Long-term partnership and growth opportunities

        10. **SUCCESS METRICS & GOVERNANCE**:
            - KPI framework with baseline establishment methodology
            - Business value measurement and tracking systems
            - Governance structure with executive oversight
            - Continuous improvement processes and feedback loops
            - Performance dashboards and reporting mechanisms

        11. **CLIENT SUCCESS ENABLEMENT**:
            - User adoption acceleration programs
            - Training and certification pathways
            - Support model and service level agreements
            - Community building and best practice sharing
            - Continuous optimization and enhancement services

        12. **NEXT STEPS & PARTNERSHIP VISION**:
            - Decision timeline and onboarding acceleration
            - Strategic partnership framework
            - Proof of concept or pilot program proposals
            - Long-term relationship and growth planning

        FORMATTING REQUIREMENTS:
        - Use professional markdown formatting with clear headings and subheadings
        - Include tables for complex information (timelines, costs, risks)
        - Add executive summary boxes for key value propositions
        - Use bullet points for clarity and scanability
        - Include quantified benefits wherever possible
        - Ensure content is tailored to the specific industry and client context
        - Write at an executive level that would impress C-suite decision makers
        - Focus on business outcomes rather than just technical deliverables

        TONE AND APPROACH:
        - Strategic and consultative rather than purely technical
        - Forward-thinking and innovation-focused
        - Risk-aware but opportunity-driven
        - Partnership-oriented rather than vendor-focused
        - Quantified and metrics-driven where possible
        """
        max_generation_config = genai.types.GenerationConfig(
        temperature=0.3,           # Slightly creative but focused
        top_p=0.8,                # Nucleus sampling
        top_k=40,                 # Top-k sampling
        max_output_tokens=8192,   # Maximum tokens for Gemini Pro
        candidate_count=1,        # Number of response candidates
        stop_sequences=None,      # No stop sequences for max output
    )
        response = self.model.generate_content(prompt, generation_config=max_generation_config)
        return response.text
    
    def analyze_competitive_landscape(self, rfp_text, company_profile):
        """
        Analyze competitive landscape and positioning
        """
        prompt = f"""
        Analyze the competitive landscape for this RFP and provide strategic positioning recommendations:
        
        RFP Text: {rfp_text}
        Company Profile: {company_profile}
        
        Provide:
        1. **Likely Competitors**: Who else will bid on this RFP?
        2. **Competitive Advantages**: What are our unique differentiators?
        3. **Competitive Threats**: Where might we be at a disadvantage?
        4. **Positioning Strategy**: How should we position our proposal?
        5. **Win Themes**: Key messages that will differentiate us
        6. **Price Strategy**: Competitive pricing considerations
        
        Format in markdown with actionable recommendations.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def generate_executive_briefing(self, rfp_text, company_profile):
        """
        Generate C-suite level executive briefing
        """
        prompt = f"""
        Create an executive briefing document for C-level decision makers:
        
        RFP Text: {rfp_text}
        Company Profile: {company_profile}
        
        Include:
        1. **Strategic Opportunity Assessment** (2-3 sentences)
        2. **Business Impact Summary** (quantified benefits)
        3. **Investment Summary** (high-level costs and ROI)
        4. **Risk Assessment** (top 3 risks and mitigations)
        5. **Decision Recommendation** (Go/No-Go with rationale)
        6. **Key Success Factors** (what needs to happen to win)
        
        Keep it concise - maximum 1 page when printed.
        Use executive language focused on business value, not technical details.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def assess_innovation_opportunities(self, rfp_text):
        """
        Identify opportunities for innovation and emerging technology integration
        """
        prompt = f"""
        Analyze this RFP for innovation and emerging technology opportunities:
        
        RFP Text: {rfp_text}
        
        Identify:
        1. **AI/ML Integration Opportunities**: Where can AI add value?
        2. **Automation Potential**: What processes can be automated?
        3. **Data Analytics Opportunities**: What insights can be generated?
        4. **Cloud-Native Advantages**: How can cloud architecture benefit the client?
        5. **Industry 4.0 Applications**: IoT, edge computing, digital twin opportunities
        6. **Future Technology Roadmap**: 2-3 year technology evolution plan
        
        Focus on business value and competitive advantage, not just technical possibilities.
        """
        response = self.model.generate_content(prompt)
        return response.text
    def analyze_rfp(self, rfp_text):
        """
        Analyze the RFP document and provide a comprehensive breakdown
        """
        prompt = f"""
        You are an expert RFP analyst. Analyze the following RFP document and provide a detailed breakdown:
        
        RFP Text:
        {rfp_text}
        
        Provide a comprehensive breakdown that includes:
        1. Executive Summary - Brief overview of the RFP
        2. Key Requirements - Critical requirements listed in the RFP
        3. Evaluation Criteria - How proposals will be evaluated
        4. Timeline - Important dates and deadlines
        5. Budget Considerations - Any budget information provided
        
        Format your response in markdown.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def extract_requirements(self, rfp_text):
        """
        Extract specific requirements from the RFP text
        """
        prompt = f"""
        You are an expert in requirement analysis. Extract and categorize all requirements from the following RFP text:
        
        RFP Text:
        {rfp_text}
        
        For each requirement:
        1. Assign a unique ID (REQ-001, REQ-002, etc.)
        2. Classify as Functional, Non-Functional, Technical, or Business
        3. Assign a priority (Critical, High, Medium, Low)
        4. Provide a clear, concise description
        
        Format your response as a markdown table with these columns:
        | ID | Type | Priority | Requirement Description |
        
        Ensure all requirements are specific, measurable, and actionable.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_tasks(self, requirements):
        """
        Generate actionable Jira-style tasks based on the requirements
        """
        prompt = f"""
        You are a project manager experienced in breaking down requirements into actionable tasks. 
        Based on the following requirements, create Jira-style tasks:
        
        Requirements:
        {requirements}
        
        For each task:
        1. Assign a unique ID (TASK-001, TASK-002, etc.)
        2. Provide a short, descriptive title
        3. Write a detailed description
        4. Estimate effort (Story Points: 1, 2, 3, 5, 8, 13)
        5. Assign a task type (Development, Testing, Documentation, Design)
        6. Map to the requirement ID it fulfills
        
        Format your response as a markdown table with these columns:
        | Task ID | Title | Description | Story Points | Type | Requirement ID |
        
        Ensure tasks are specific, actionable, and can be completed in 1-3 days of work.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def analysis_proposal(self, proposal_text, extra_components=None):
        """
        Check the key components that are present in the RFP proposal
        
        Args:
            proposal_text (str): The RFP proposal text to analyze
            extra_components (str or list, optional): Additional components to check for
        
        Returns:
            str: Analysis results in markdown table format
        """
        standard_components = [
            "1. Executive Summary / Project Overview",
            "2. Scope of Work (In Scope)",
            "3. Out of Scope",
            "4. Prerequisites / Requirements",
            "5. Deliverables",
            "6. Timeline / Schedule",
            "7. Technology Stack / Technical Requirements",
            "8. Budget / Cost Estimation",
            "9. Team Structure / Resources",
            "10. Risk Assessment / Mitigation",
            "11. Success Criteria / Acceptance Criteria",
            "12. Testing Strategy",
            "13. Maintenance & Support",
            "14. Additional Comments / Notes"
        ]
        
        # Create copy of standard components
        components_to_check = standard_components.copy()
        
        # Handle extra components
        if extra_components:
            next_number = len(standard_components) + 1
            
            if isinstance(extra_components, str):
                components_to_check.append(f"{next_number}. {extra_components}")
            elif isinstance(extra_components, list):
                for component in extra_components:
                    components_to_check.append(f"{next_number}. {component}")
                    next_number += 1
        
        components_list = "\n  ".join(components_to_check)
        
        prompt = f"""
        You are a project manager experienced in analyzing RFP (Request for Proposal) documents. 
        Based on the following proposal text, analyze which key RFP components are present:
        
        Proposal Text:
        {proposal_text}
        
        The RFP components to check for are:
        {components_list}
        
        Format your response as a markdown table with these columns:
        | Component | Present (True/False) if true ✅ else ❌  | Details/Notes | PageNumber
        
        For each component, indicate whether it's present in the proposal and provide brief details if found.
        """       
        response = self.model.generate_content(prompt)
        return response.text

    def analysis_proposal_summary(self, proposal_text, analysis_proposal_text):
        """
        Generate a comprehensive summary of the RFP proposal analysis
        
        Args:
            proposal_text: The main proposal content to be used for overall assessment
            analysis_proposal_text: Detailed component analysis to be used for the Component Analysis Summary
        
        Returns:
            str: A comprehensive executive summary in markdown format
        """
        prompt = f"""
        You are a senior project manager with extensive experience in RFP evaluation and proposal analysis. 
        Based on the following RFP analysis results, create a comprehensive executive summary:
        
        **Proposal Content for Overall Assessment:**
        {proposal_text}
        
        **Detailed Component Analysis:**
        {analysis_proposal_text}
        
        Please provide a detailed 2-3 page executive summary that includes:
        
        1. **Executive Overview**
        - High-level assessment of the proposal completeness based on the overall content
        - Overall recommendation (Approved/Needs Revision/Rejected)
        - Summary of key findings from the proposal content
        
        2. **Component Analysis Summary**
        - Critical components present in the proposal (from the detailed component analysis)
        - Components that are missing or incomplete
        - Quality assessment of present components
        - Specific findings from the component analysis
        
        3. **Strengths and Opportunities**
        - Key strengths identified in both the overall proposal and component analysis
        - Areas that need improvement or clarification
        - Missing elements that should be addressed
        
        4. **Risk Assessment**
        - Potential risks based on missing components or proposal weaknesses
        - Impact of incomplete sections on project success
        
        5. **Recommendations**
        - Specific actions required before approval
        - Suggested improvements or additions
        - Next steps in the evaluation process
        
        6. **Conclusion**
        - Final assessment and decision rationale combining insights from both analyses
        - Timeline for resubmission if needed
        
        Format the response in well-structured markdown with clear headings, bullet points where appropriate, 
        and professional language suitable for stakeholder presentation.
        
        Aim for approximately 2-3 pages of detailed analysis (1500-2000 words).
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def extract_text_from_docx_proposal(self, docx_file):
        """
        Convert DOCX to PDF and then extract text using Gemini
        """
        try:
            # Create temporary directory for file processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded DOCX file temporarily
                docx_path = os.path.join(temp_dir, "document.docx")
                with open(docx_path, "wb") as f:
                    f.write(docx_file.getvalue())
                
                # Convert DOCX to PDF
                pdf_path = os.path.join(temp_dir, "document.pdf")
                convert(docx_path, pdf_path)
                
                # Extract text from PDF using Gemini
                return self.extract_text_from_pdf_file_proposal(pdf_path)
                
        except Exception as e:
            st.error(f"Error processing DOCX file: {str(e)}")
            return None

    def extract_text_from_pdf_file_proposal(self, pdf_path):
        """
        Extract text from PDF file using Gemini's multimodal capabilities
        """
        try:
            # Upload file to Gemini
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Extract text using Gemini
            prompt = """
            Please extract all text content from this PDF document. 
            Return only the extracted text without any additional formatting or commentary.
            Preserve the structure and organization of the content as much as possible.
            Also include the PDF page number for each section of text.
            """
        
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'application/pdf', 'data': pdf_bytes}
            ])
            
            # Check if response was successful and has text
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                st.error("No text content returned from Gemini")
                return None
                
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def extract_text_from_uploaded_pdf_proposal(self, pdf_file):
        """
        Extract text from uploaded PDF file using Gemini
        """
        try:
            # Create temporary file for PDF processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                # Extract text using Gemini
                text = self.extract_text_from_pdf_file(temp_file_path)
                return text
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            st.error(f"Error processing uploaded PDF: {str(e)}")
            return None
    