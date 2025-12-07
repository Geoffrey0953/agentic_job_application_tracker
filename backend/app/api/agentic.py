"""
New Agentic API endpoints - Fully agentic workflow
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import AgentJobAnalysisRequest, AgentCreateApplicationRequest, AgentResponse
from app.services.agentic_orchestrator import AgenticOrchestrator

router = APIRouter()

@router.post("/agentic/create-application")
async def create_application_fully_agentic(
    request: AgentCreateApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Fully agentic application creation
    
    The AI agent will:
    1. Analyze the job description
    2. Plan a custom workflow based on the job
    3. Learn from past successful applications
    4. Execute the plan with error recovery
    5. Adapt if steps fail
    6. Create the complete application package
    """
    try:
        orchestrator = AgenticOrchestrator(db)
        result = orchestrator.create_application_agentic(
            request.job_description,
            request.auto_generate
        )
        
        if result["success"]:
            return AgentResponse(
                success=True,
                message="Application created using fully agentic AI workflow!",
                data={
                    "application_id": result["application_id"],
                    "ats_score": result.get("ats_score"),
                    "execution_plan": result.get("plan"),
                    "execution_history": result.get("execution_result", {}).get("execution_history", []),
                    "errors": result.get("execution_result", {}).get("errors", []),
                    "agentic": True
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Agentic workflow failed: {result.get('execution_result', {}).get('errors', [])}"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agentic/plan-workflow")
async def plan_workflow_agentic(
    request: AgentJobAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Just plan the workflow without executing
    Useful for previewing what the agent will do
    """
    try:
        orchestrator = AgenticOrchestrator(db)
        plan = orchestrator.plan_workflow(request.job_description)
        
        return AgentResponse(
            success=True,
            message="Workflow planned successfully",
            data={
                "plan": plan,
                "steps_count": len(plan)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

