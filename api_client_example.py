import requests
import json

# API Base URL
BASE_URL = "http://localhost:8000"

def analyze_proposal_text(proposal_text, extra_components=None):
    """Example of analyzing proposal components"""
    url = f"{BASE_URL}/analyze/components"
    payload = {
        "proposal_text": proposal_text,
        "extra_components": extra_components
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def upload_and_analyze_file(file_path):
    """Example of uploading and analyzing a file"""
    url = f"{BASE_URL}/upload/proposal"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        extracted_text = result['text']
        
        # Now analyze the extracted text
        analysis_result = analyze_proposal_text(extracted_text)
        return analysis_result
    else:
        return {"error": response.text}

def run_complete_analysis(proposal_text, extra_components=None):
    """Run all analysis types"""
    analyses = {}
    
    # Component Analysis
    component_result = requests.post(f"{BASE_URL}/analyze/components", 
                                   json={"proposal_text": proposal_text, 
                                        "extra_components": extra_components})
    analyses['components'] = component_result.json()
    
    # Pricing Analysis
    pricing_result = requests.post(f"{BASE_URL}/analyze/pricing", 
                                 json={"proposal_text": proposal_text})
    analyses['pricing'] = pricing_result.json()
    
    # Cost Realism
    cost_result = requests.post(f"{BASE_URL}/analyze/cost-realism", 
                              json={"proposal_text": proposal_text})
    analyses['cost_realism'] = cost_result.json()
    
    # Technical Analysis
    tech_result = requests.post(f"{BASE_URL}/analyze/technical", 
                              json={"proposal_text": proposal_text})
    analyses['technical'] = tech_result.json()
    
    # Compliance
    compliance_result = requests.post(f"{BASE_URL}/analyze/compliance", 
                                    json={"proposal_text": proposal_text})
    analyses['compliance'] = compliance_result.json()
    
    return analyses

# Example usage
if __name__ == "__main__":
    # Example 1: Direct text analysis
    sample_text = "Your proposal text here..."
    result = analyze_proposal_text(sample_text)
    print("Component Analysis:", result)
    
    # Example 2: File upload and analysis
    # result = upload_and_analyze_file("path/to/your/proposal.pdf")
    # print("File Analysis:", result)
    
    # Example 3: Complete analysis
    # all_analyses = run_complete_analysis(sample_text)
    # print("All Analyses:", json.dumps(all_analyses, indent=2))