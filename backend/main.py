"""FastAPI backend for NetSage AI - Cisco Network Troubleshooting Assistant."""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from src.data_loader import load_cases, validate_dataset, get_case, get_cases_by_concept
from src.evidence_parser import load_evidence, parse_evidence_file, create_all_placeholders
from src.diagnosis import diagnose, format_diagnosis, filter_candidate_cases
from src.rule_checker import run_rule_checker
from src.human_review import HumanReview, interactive_review, ReviewStatus, REVIEW_LOG_FILE
from src.dashboard import Dashboard, DASHBOARD_FILE
from src.evaluator import evaluate_all_cases
from src.models import Case, Evidence, DiagnosisResult, CandidateCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Request/Response models
class DiagnoseRequest(BaseModel):
    case_id: Optional[int] = None
    evidence_text: str
    auto_review: bool = False

class ReviewRequest(BaseModel):
    case_id: int
    decision: str  # Accepted, Edited, Rejected
    notes: str = ""
    corrected_fault: str = ""
    corrected_confidence: float = 0.0
    corrected_reasoning: str = ""
    corrected_fix: str = ""
    corrected_commands: List[str] = []

class DashboardData(BaseModel):
    stats: Dict[str, int]
    concept_counts: Dict[str, int]
    severity_counts: Dict[str, int]
    corrected_cases: List[Dict[str, Any]]
    all_cases: List[Dict[str, Any]]
    agreement_rate: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NetSage AI Backend...")
    create_all_placeholders()
    logger.info("Placeholders created")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="NetSage AI",
    description="Cisco Network Troubleshooting Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

# ===================== WebSocket =====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for keepalive
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ===================== Pages =====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})

@app.get("/diagnose", response_class=HTMLResponse)
async def diagnose_page(request: Request):
    cases = load_cases()
    return templates.TemplateResponse(request, "diagnose.html", {"request": request, "cases": cases})

@app.get("/cases", response_class=HTMLResponse)
async def cases_page(request: Request):
    cases = load_cases()
    return templates.TemplateResponse(request, "cases.html", {"request": request, "cases": cases})

@app.get("/review", response_class=HTMLResponse)
async def review_page(request: Request):
    review = HumanReview()
    stats = review.get_review_stats()
    corrected = review.list_corrected_cases()
    return templates.TemplateResponse(request, "review.html", {
        "request": request, 
        "stats": stats, 
        "corrected": corrected
    })

# ===================== API Endpoints =====================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "NetSage AI"}

@app.get("/api/cases")
async def api_list_cases():
    cases = load_cases()
    return [
        {
            "case_id": c.case_id,
            "title": c.title,
            "concept": c.concept,
            "severity": c.severity,
            "osi_layer": c.osi_layer
        }
        for c in cases
    ]

@app.get("/api/cases/{case_id}")
async def api_get_case(case_id: int):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    evidence = load_evidence(case_id)
    return {
        "case": {
            "case_id": case.case_id,
            "title": case.title,
            "topology": case.topology,
            "symptom": case.symptom,
            "topology_note": case.topology_note,
            "show_outputs": case.show_outputs,
            "expected_fault": case.expected_fault,
            "osi_layer": case.osi_layer,
            "concept": case.concept,
            "severity": case.severity
        },
        "evidence": evidence.to_dict() if evidence else {},
        "evidence_raw": evidence.other_cli_output if evidence else ""
    }

@app.post("/api/diagnose")
async def api_diagnose(request: DiagnoseRequest):
    try:
        # Parse evidence
        if request.case_id:
            evidence = Evidence(case_id=request.case_id)
        else:
            evidence = Evidence()
        
        if request.evidence_text:
            evidence.other_cli_output = request.evidence_text
        
        # Run rule checker
        case_obj = get_case(request.case_id) if request.case_id else None
        rule_results = run_rule_checker(evidence, case_obj)
        
        # Run AI diagnosis
        result = diagnose(evidence, request.case_id)
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "diagnosis_complete",
            "data": {
                "case_id": request.case_id,
                "predicted_fault": result.predicted_fault,
                "confidence": result.confidence,
                "reasoning_summary": result.reasoning_summary,
                "evidence_used": result.evidence_used,
                "recommended_fix": result.recommended_fix,
                "commands": result.commands,
                "needs_more_evidence": result.needs_more_evidence,
                "rule_results": rule_results
            }
        }))
        
        return {
            "success": True,
            "diagnosis": {
                "predicted_fault": result.predicted_fault,
                "confidence": result.confidence,
                "reasoning_summary": result.reasoning_summary,
                "evidence_used": result.evidence_used,
                "recommended_fix": result.recommended_fix,
                "commands": result.commands,
                "needs_more_evidence": result.needs_more_evidence
            },
            "rule_results": rule_results,
            "formatted": format_diagnosis(result)
        }
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review")
async def api_review(request: ReviewRequest):
    try:
        review = HumanReview()
        case = get_case(request.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Load the original diagnosis (we'd need to store this)
        # For now, create a minimal diagnosis object
        from src.models import DiagnosisResult
        ai_diagnosis = DiagnosisResult(
            case_id=request.case_id,
            predicted_fault=request.corrected_fault or "Unknown",
            confidence=request.corrected_confidence,
            reasoning_summary=request.corrected_reasoning,
            evidence_used=[],
            recommended_fix=request.corrected_fix,
            commands=request.corrected_commands,
            needs_more_evidence=False
        )
        
        review.log_review(
            case_id=request.case_id,
            case_title=case.title,
            ai_diagnosis=ai_diagnosis,
            human_decision=request.decision,
            human_notes=request.notes,
            corrected_fault=request.corrected_fault,
            corrected_confidence=request.corrected_confidence,
            corrected_reasoning=request.corrected_reasoning,
            corrected_fix=request.corrected_fix,
            corrected_commands=request.corrected_commands
        )
        
        # Broadcast update
        await manager.broadcast(json.dumps({
            "type": "review_added",
            "data": {
                "case_id": request.case_id,
                "decision": request.decision
            }
        }))
        
        return {"success": True, "message": "Review logged"}
    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/review/stats")
async def api_review_stats():
    review = HumanReview()
    stats = review.get_review_stats()
    corrected = review.list_corrected_cases()
    return {
        "stats": stats,
        "corrected_cases": corrected
    }

@app.get("/api/dashboard/data")
async def api_dashboard_data():
    cases = load_cases()
    review = HumanReview()
    stats = review.get_review_stats()
    corrected = review.list_corrected_cases()
    
    concept_counts = {}
    severity_counts = {}
    for case in cases:
        concept_counts[case.concept] = concept_counts.get(case.concept, 0) + 1
        severity_counts[case.severity] = severity_counts.get(case.severity, 0) + 1
    
    agreement_rate = 0
    if stats['total'] > 0:
        agreement_rate = (stats['accepted'] / stats['total']) * 100
    
    return {
        "stats": stats,
        "concept_counts": concept_counts,
        "severity_counts": severity_counts,
        "corrected_cases": corrected,
        "all_cases": [
            {
                "case_id": c.case_id,
                "title": c.title,
                "concept": c.concept,
                "severity": c.severity,
                "osi_layer": c.osi_layer
            }
            for c in cases
        ],
        "agreement_rate": agreement_rate
    }

@app.post("/api/evaluate")
async def api_evaluate():
    try:
        report = evaluate_all_cases()
        return report
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/validate")
async def api_validate():
    report = validate_dataset()
    return report

@app.post("/api/rule-check")
async def api_rule_check(case_id: int = Form(...)):
    evidence = load_evidence(case_id)
    if not evidence or evidence.is_empty():
        raise HTTPException(status_code=404, detail="No evidence found")
    
    case = get_case(case_id)
    results = run_rule_checker(evidence, case)
    return {"case_id": case_id, "results": results}

@app.post("/api/generate-dashboard")
async def api_generate_dashboard():
    dashboard = Dashboard()
    filepath = dashboard.generate()
    return {"success": True, "filepath": filepath}

# ===================== Main =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)