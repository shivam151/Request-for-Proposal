from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from gemini_client import GeminiClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RFP Proposal Analyzer API", version="1.0.0")

# Initialize Gemini client
gemini = GeminiClient()

# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    proposal_text: str
    extra_components: Optional[str] = None

class RFPAnalysisRequest(BaseModel):
    rfp_text: str
    company_profile: Optional[str] = None

class AnalysisResponse(BaseModel):
    status: str
    result: str
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "RFP Proposal Analyzer API is running"}

@app.post("/analyze/components", response_model=AnalysisResponse)
async def analyze_proposal_components(request: AnalysisRequest):
    """Analyze proposal components"""
    try:
        result = gemini.analysis_proposal(request.proposal_text, request.extra_components)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/analyze/pricing", response_model=AnalysisResponse)
async def analyze_pricing(request: AnalysisRequest):
    """Analyze pricing structure"""
    try:
        # First get component analysis
        component_analysis = gemini.analysis_proposal(request.proposal_text, request.extra_components)
        result = gemini.analyze_pricing(request.proposal_text, component_analysis)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/analyze/cost-realism", response_model=AnalysisResponse)
async def analyze_cost_realism(request: AnalysisRequest):
    """Perform cost realism analysis"""
    try:
        component_analysis = gemini.analysis_proposal(request.proposal_text, request.extra_components)
        result = gemini.analyze_cost_realism(request.proposal_text, component_analysis)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/analyze/technical", response_model=AnalysisResponse)
async def technical_analysis(request: AnalysisRequest):
    """Perform technical analysis"""
    try:
        result = gemini.technical_analysis_review(request.proposal_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/analyze/compliance", response_model=AnalysisResponse)
async def compliance_analysis(request: AnalysisRequest):
    """Perform compliance assessment"""
    try:
        result = gemini.compliance_assessment(request.proposal_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/upload/proposal")
async def upload_proposal_file(file: UploadFile = File(...)):
    """Upload and extract text from proposal file"""
    try:
        if file.content_type == "application/pdf":
            text = await gemini.extract_text_from_uploaded_pdf_proposal(file)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = await gemini.extract_text_from_docx_proposal(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file")
            
        return {"status": "success", "text": text, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rfp/analyze", response_model=AnalysisResponse)
async def analyze_rfp(request: RFPAnalysisRequest):
    """Analyze RFP document"""
    try:
        result = gemini.analyze_rfp(request.rfp_text)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/rfp/eligibility", response_model=AnalysisResponse)
async def check_eligibility(request: RFPAnalysisRequest):
    """Check eligibility for RFP"""
    try:
        if not request.company_profile:
            raise HTTPException(status_code=400, detail="Company profile required")
        result = gemini.analyze_eligibility(request.rfp_text, request.company_profile)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/rfp/generate-proposal", response_model=AnalysisResponse)
async def generate_proposal(request: RFPAnalysisRequest):
    """Generate project proposal"""
    try:
        if not request.company_profile:
            raise HTTPException(status_code=400, detail="Company profile required")
        result = gemini.generate_project_proposal(request.rfp_text, request.company_profile)
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

@app.post("/generate/summary", response_model=AnalysisResponse)
async def generate_summary(
    proposal_text: str = Form(...),
    component_analysis: Optional[str] = Form(None),
    price_analysis: Optional[str] = Form(None),
    cost_realism: Optional[str] = Form(None),
    technical_analysis: Optional[str] = Form(None),
    compliance_assessment: Optional[str] = Form(None)
):
    """Generate comprehensive summary"""
    try:
        result = gemini.analysis_proposal_summary(
            proposal_text, component_analysis, price_analysis, 
            cost_realism, technical_analysis, compliance_assessment
        )
        return AnalysisResponse(status="success", result=result)
    except Exception as e:
        return AnalysisResponse(status="error", result="", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)