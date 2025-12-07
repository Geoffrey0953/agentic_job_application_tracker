"""
Agentic Orchestrator - Makes the application truly agentic
Uses Claude to plan, execute, and adapt workflows dynamically
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.bedrock_service import bedrock_service
from app.services.s3_service import s3_service
from app.models import Application, UserProfile
from sqlalchemy.orm import Session


class AgenticOrchestrator:
    """
    Agentic orchestrator that plans and executes workflows dynamically
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.execution_history = []
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize available tools for the agent"""
        return {
            "analyze_job": {
                "description": "Analyze a job description and extract key information",
                "function": bedrock_service.analyze_job
            },
            "generate_resume": {
                "description": "Generate a tailored resume based on job requirements and profile",
                "function": bedrock_service.generate_resume
            },
            "generate_cover_letter": {
                "description": "Generate a personalized cover letter",
                "function": bedrock_service.generate_cover_letter
            },
            "calculate_ats_score": {
                "description": "Calculate ATS match score between resume and job",
                "function": bedrock_service.calculate_ats_score
            },
            "get_user_profile": {
                "description": "Retrieve user profile information",
                "function": self._get_user_profile
            },
            "get_past_applications": {
                "description": "Get past successful applications for learning",
                "function": self._get_past_applications
            },
            "save_application": {
                "description": "Save application to database",
                "function": self._save_application
            },
            "upload_to_s3": {
                "description": "Upload documents to S3 storage",
                "function": self._upload_to_s3
            }
        }
    
    def _get_user_profile(self) -> Dict[str, Any]:
        """Tool: Get user profile"""
        profile = self.db.query(UserProfile).first()
        if not profile:
            return None
        
        return {
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "portfolio_url": profile.portfolio_url,
            "summary": profile.summary,
            "resume_text": profile.resume_text,
            "experiences": profile.experiences or [],
            "education": profile.education or [],
            "skills": profile.skills or [],
            "projects": profile.projects or [],
            "certifications": profile.certifications or []
        }
    
    def _get_past_applications(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Tool: Get past successful applications for learning"""
        apps = self.db.query(Application).filter(
            Application.match_score >= 70
        ).order_by(
            Application.match_score.desc()
        ).limit(limit).all()
        
        return [{
            "job_title": app.job_title,
            "company": app.company,
            "match_score": app.match_score,
            "status": app.status,
            "key_insights": app.parsed_data.get("key_requirements", []) if app.parsed_data else []
        } for app in apps]
    
    def _save_application(self, application_data: Dict[str, Any]) -> int:
        """Tool: Save application to database"""
        application = Application(**application_data)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application.id
    
    def _upload_to_s3(self, content: str, application_id: int, doc_type: str) -> Optional[str]:
        """Tool: Upload document to S3"""
        try:
            if doc_type == "resume":
                return s3_service.upload_resume(content, application_id)
            elif doc_type == "cover_letter":
                return s3_service.upload_cover_letter(content, application_id)
        except Exception as e:
            print(f"S3 upload failed: {e}")
            return None
    
    def plan_workflow(self, job_description: str, goal: str = "create_complete_application") -> List[Dict[str, Any]]:
        """
        Use Claude to plan the workflow dynamically based on the job description
        """
        # Get context from past applications
        past_apps = self._get_past_applications(3)
        past_context = ""
        if past_apps:
            past_context = f"\n\nPast successful applications (learn from these):\n{json.dumps(past_apps, indent=2)}"
        
        # Get available tools
        tools_description = "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])
        
        planning_prompt = f"""You are an intelligent agent orchestrator. Your goal is to: {goal}

Job Description:
{job_description[:2000]}  # Limit to avoid token issues
{past_context}

Available Tools:
{tools_description}

Based on the job description and your goal, create a step-by-step plan. Consider:
1. What information do I need to extract?
2. What documents need to be generated?
3. What analysis is needed?
4. What can I learn from past successful applications?

Return a JSON plan with this structure:
{{
    "plan": [
        {{
            "step": 1,
            "action": "tool_name",
            "reasoning": "why this step is needed",
            "parameters": {{"param1": "value1"}},
            "expected_output": "what we expect from this step"
        }},
        ...
    ],
    "adaptation_strategy": "how to adapt if steps fail",
    "quality_checks": ["check1", "check2"]
}}

Return ONLY the JSON, no other text."""

        try:
            response = bedrock_service.call_claude(
                planning_prompt,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for planning
            )
            
            # Parse JSON from response
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            plan_data = json.loads(response)
            return plan_data.get("plan", [])
        
        except Exception as e:
            print(f"Planning failed: {e}, using default plan")
            return self._get_default_plan()
    
    def _get_default_plan(self) -> List[Dict[str, Any]]:
        """Fallback default plan if AI planning fails"""
        return [
            {"step": 1, "action": "analyze_job", "parameters": {}, "reasoning": "Extract job requirements"},
            {"step": 2, "action": "get_user_profile", "parameters": {}, "reasoning": "Get user information"},
            {"step": 3, "action": "generate_resume", "parameters": {}, "reasoning": "Create tailored resume"},
            {"step": 4, "action": "generate_cover_letter", "parameters": {}, "reasoning": "Create cover letter"},
            {"step": 5, "action": "calculate_ats_score", "parameters": {}, "reasoning": "Evaluate match"}
        ]
    
    def execute_plan(self, plan: List[Dict[str, Any]], job_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the planned workflow with error recovery and adaptation
        """
        if context is None:
            context = {}
        
        results = {}
        errors = []
        
        for step in plan:
            step_num = step.get("step", 0)
            action = step.get("action")
            parameters = step.get("parameters", {})
            reasoning = step.get("reasoning", "")
            
            print(f"\n🤖 Step {step_num}: {action}")
            print(f"   Reasoning: {reasoning}")
            
            try:
                # Execute the tool
                result = self._execute_tool(action, parameters, context, job_description)
                
                # Store result in context for next steps
                context[action] = result
                results[action] = result
                
                # Log execution
                self.execution_history.append({
                    "step": step_num,
                    "action": action,
                    "status": "success",
                    "result": str(result)[:200] if result else None,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                print(f"   ✅ Success")
                
            except Exception as e:
                error_msg = str(e)
                errors.append({
                    "step": step_num,
                    "action": action,
                    "error": error_msg
                })
                
                print(f"   ❌ Error: {error_msg}")
                
                # Try to recover
                recovery_result = self._attempt_recovery(action, parameters, context, error_msg)
                if recovery_result:
                    context[action] = recovery_result
                    results[action] = recovery_result
                    print(f"   🔄 Recovered")
                else:
                    # If critical step fails, replan
                    if action in ["analyze_job", "get_user_profile"]:
                        print(f"   ⚠️  Critical step failed, cannot continue")
                        break
        
        return {
            "results": results,
            "errors": errors,
            "execution_history": self.execution_history,
            "success": len(errors) == 0 or len(results) > 0
        }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any], job_description: str) -> Any:
        """Execute a specific tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_info = self.tools[tool_name]
        tool_func = tool_info["function"]
        
        # Prepare parameters based on tool
        if tool_name == "analyze_job":
            return tool_func(job_description)
        
        elif tool_name == "get_user_profile":
            return tool_func()
        
        elif tool_name == "generate_resume":
            job_analysis = context.get("analyze_job", {})
            user_profile = context.get("get_user_profile")
            if not user_profile:
                user_profile = self._get_user_profile()
            return tool_func(job_analysis, user_profile)
        
        elif tool_name == "generate_cover_letter":
            job_analysis = context.get("analyze_job", {})
            user_profile = context.get("get_user_profile")
            if not user_profile:
                user_profile = self._get_user_profile()
            return tool_func(job_analysis, user_profile)
        
        elif tool_name == "calculate_ats_score":
            resume_content = context.get("generate_resume")
            job_analysis = context.get("analyze_job", {})
            if not resume_content or not job_analysis:
                raise ValueError("Need resume and job analysis for ATS score")
            return tool_func(resume_content, job_analysis)
        
        elif tool_name == "get_past_applications":
            limit = parameters.get("limit", 5)
            return tool_func(limit)
        
        elif tool_name == "save_application":
            return tool_func(parameters)
        
        elif tool_name == "upload_to_s3":
            content = parameters.get("content")
            app_id = parameters.get("application_id")
            doc_type = parameters.get("doc_type", "resume")
            return tool_func(content, app_id, doc_type)
        
        else:
            raise ValueError(f"Tool {tool_name} not implemented")
    
    def _attempt_recovery(self, failed_action: str, parameters: Dict[str, Any], context: Dict[str, Any], error: str) -> Optional[Any]:
        """
        Attempt to recover from a failed step using AI reasoning
        """
        recovery_prompt = f"""A step in the workflow failed. Help me recover.

Failed Action: {failed_action}
Parameters: {json.dumps(parameters, indent=2)}
Error: {error}
Current Context: {json.dumps({k: str(v)[:200] for k, v in context.items()}, indent=2)}

Suggest a recovery strategy. Options:
1. Retry with modified parameters
2. Use alternative approach
3. Skip if not critical
4. Use fallback data

Return JSON:
{{
    "strategy": "retry|alternative|skip|fallback",
    "modified_parameters": {{}},
    "reasoning": "why this recovery should work"
}}

Return ONLY the JSON."""

        try:
            response = bedrock_service.call_claude(recovery_prompt, max_tokens=1000, temperature=0.5)
            
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            recovery_plan = json.loads(response)
            strategy = recovery_plan.get("strategy")
            
            if strategy == "retry":
                modified_params = recovery_plan.get("modified_parameters", parameters)
                return self._execute_tool(failed_action, modified_params, context, "")
            elif strategy == "alternative":
                # Try alternative approach
                return None  # Would need alternative implementations
            elif strategy == "skip":
                return None
            elif strategy == "fallback":
                return recovery_plan.get("fallback_data")
        
        except Exception as e:
            print(f"Recovery planning failed: {e}")
        
        return None
    
    def create_application_agentic(self, job_description: str, auto_generate: bool = True) -> Dict[str, Any]:
        """
        Main agentic method - plans and executes workflow dynamically
        """
        print("\n" + "="*60)
        print("🤖 AGENTIC WORKFLOW STARTING")
        print("="*60)
        
        # Step 1: Plan the workflow
        print("\n📋 Planning workflow...")
        plan = self.plan_workflow(job_description)
        print(f"✅ Planned {len(plan)} steps")
        
        # Step 2: Execute the plan
        print("\n⚙️  Executing plan...")
        context = {"job_description": job_description}
        execution_result = self.execute_plan(plan, job_description, context)
        
        # Step 3: Create application record
        if execution_result["success"] and auto_generate:
            job_analysis = context.get("analyze_job", {})
            resume_content = context.get("generate_resume")
            cover_letter_content = context.get("generate_cover_letter")
            ats_analysis = context.get("calculate_ats_score", {})
            
            # Create application
            application = Application(
                job_title=job_analysis.get('job_title', 'Unknown Position'),
                company=job_analysis.get('company', 'Unknown Company'),
                location=job_analysis.get('location', 'Unknown'),
                job_description=job_description,
                salary_range=job_analysis.get('salary_range'),
                parsed_data=job_analysis,
                status='pending',
                resume_content=resume_content,
                cover_letter_content=cover_letter_content,
                match_score=ats_analysis.get('overall_score', 0) if isinstance(ats_analysis, dict) else None
            )
            
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            
            # Upload to S3 if available
            try:
                if resume_content:
                    application.resume_url = s3_service.upload_resume(resume_content, application.id)
                if cover_letter_content:
                    application.cover_letter_url = s3_service.upload_cover_letter(cover_letter_content, application.id)
                self.db.commit()
            except:
                pass
            
            print(f"\n✅ Application created: ID {application.id}")
            
            return {
                "success": True,
                "application_id": application.id,
                "execution_result": execution_result,
                "plan": plan,
                "ats_score": ats_analysis.get('overall_score') if isinstance(ats_analysis, dict) else None
            }
        
        return {
            "success": False,
            "execution_result": execution_result,
            "plan": plan
        }

