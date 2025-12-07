import boto3
import json
import os
from typing import Optional, Dict, Any

class BedrockService:
    """
    Service for interacting with AWS Bedrock (Claude)
    """
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        self.model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    def call_claude(
        self, 
        prompt: str, 
        max_tokens: int = 2000,
        temperature: float = 1.0,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Call Claude via Bedrock
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            system_prompt: Optional system instruction
            
        Returns:
            Claude's text response
        """
        try:
            body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            }
            
            if system_prompt:
                body['system'] = system_prompt
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        
        except Exception as e:
            raise Exception(f"Error calling Claude: {str(e)}")
    
    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description and extract key information
        
        Returns:
            Dictionary with job analysis
        """
        prompt = f"""Analyze this job description and extract the following information.
Return ONLY valid JSON with these exact fields:

{{
    "job_title": "the job title",
    "company": "company name (or 'Unknown' if not mentioned)",
    "location": "job location (or 'Remote' or 'Unknown')",
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...],
    "experience_years": number or 0 if not specified,
    "keywords": ["keyword1", "keyword2", ...],
    "salary_range": "salary range if mentioned, otherwise null",
    "job_type": "Full-time/Part-time/Contract/Internship",
    "responsibilities": ["resp1", "resp2", ...]
}}

Job Description:
{job_description}

Return ONLY the JSON, no other text."""

        response = self.call_claude(prompt, max_tokens=3000)
        
        # Clean JSON from markdown code blocks
        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            # If parsing fails, return error info
            return {
                "error": "Failed to parse JSON",
                "raw_response": response,
                "job_title": "Unknown",
                "company": "Unknown"
            }
    
    def generate_resume(
        self, 
        job_analysis: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """
        Generate a tailored resume based on job requirements and user profile
        
        Returns:
            Resume content in markdown format
        """
        # Build resume base if resume_text exists
        resume_base = ""
        if user_profile.get('resume_text'):
            resume_base = f"\n\nOriginal Resume:\n{user_profile['resume_text']}\n"
        
        prompt = f"""You are a senior technical recruiter at a top tech company (Google, Meta, Amazon) with 15+ years of experience reviewing resumes and understanding what hiring managers look for.

    Your task: Create an ATS-optimized, compelling resume tailored specifically for this role.

    Job Requirements:
    {json.dumps(job_analysis, indent=2)}

    User Profile:
    {json.dumps({k: v for k, v in user_profile.items() if k != 'resume_text'}, indent=2)}
    {resume_base}

    CRITICAL GUIDELINES:

    **Honesty & Authenticity:**
    - NEVER fabricate experiences, skills, or achievements
    - NEVER exaggerate metrics beyond what's actually stated in the user profile
    - NEVER add technologies or tools the user hasn't mentioned
    - If the user lacks a required skill, DO NOT claim they have it
    - Present real experiences in the best possible light WITHOUT lying
    - It's better to be honest than to risk credibility

    **Content Strategy:**
    1. **Impact-Driven Bullets:**
    - Start with strong action verbs (Built, Engineered, Designed, Implemented, Architected, Optimized, Led)
    - Use quantifiable metrics ONLY from the user's actual experiences
    - Focus on outcomes and business impact, not just responsibilities
    - Apply STAR method: Situation, Task, Action, Result

    2. **ATS Optimization:**
    - Use exact keywords from the job description naturally throughout
    - Include required skills prominently (but ONLY skills the user actually has)
    - Use standard section headers (Education, Experience, Skills, Projects, Certifications)
    - Avoid tables, graphics, or complex formatting
    - Ensure clean, scannable layout

    3. **Relevance & Prioritization:**
    - Highlight experiences most relevant to this specific role first
    - Emphasize transferable skills that match job requirements
    - Include projects that demonstrate relevant technical abilities
    - De-emphasize (but don't remove) less relevant experiences

    4. **Professional Polish:**
    - Keep descriptions concise (1-2 lines per bullet point)
    - Use industry-standard terminology from the job posting
    - Maintain consistent formatting throughout
    - Tailor the summary to this specific position

    5. **Technical Accuracy:**
    - List technologies, tools, and frameworks the user has ACTUALLY used
    - Demonstrate depth with specific examples from real projects
    - Show progression and growth in responsibilities
    - Match technical terminology to the job description where truthful

    6. **Smart Positioning (Without Lying):**
    - Reframe experiences to highlight relevant aspects
    - Use job description language to describe actual work done
    - Group similar skills to emphasize strengths
    - Lead with most impressive and relevant achievements

    **If the user's profile doesn't fully match the job:**
    - Focus on transferable skills and adaptability
    - Highlight learning ability and past skill acquisition
    - Emphasize relevant projects or coursework
    - DO NOT claim skills or experiences they don't have

    **Resume Structure:**

    **[Full Name]**
    [Contact info from profile]


    **EDUCATION**
    [Format: Degree | School | Graduation Date | GPA if 3.5+]
    [Relevant coursework if recent grad and matches job requirements]

    **TECHNICAL SKILLS**
    [Categorize: Languages, Frameworks, Tools, Cloud/DevOps]
    [List ONLY skills mentioned in user profile - prioritize job-relevant ones first]

    **PROFESSIONAL EXPERIENCE**
    [Most relevant position first]
    **[Job Title]** | [Company] | [Dates]
    - [Achievement bullet using real metrics and action verbs]
    - [Project detail showing relevant technical skills]
    - [Impact statement with quantifiable results if available]
    - [Collaboration or leadership example if applicable]

    [Continue with other positions, prioritizing relevance]

    **PROJECTS**
    [Include if relevant to the role]
    **[Project Name]** | [Technologies used]
    [1-2 lines describing project with impact and relevance]

    **CERTIFICATIONS**
    [Include if mentioned in profile and relevant to role]

    Return ONLY the formatted resume in clean markdown. No additional commentary.

    Remember: A honest, well-positioned resume is far more valuable than an exaggerated one. Focus on making their REAL experiences shine."""

        return self.call_claude(prompt, max_tokens=4000, temperature=0.7)
    
    def generate_cover_letter(
        self,
        job_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
        company_research: Optional[str] = None
    ) -> str:
        """
        Generate a personalized cover letter
        
        Returns:
            Cover letter content
        """
        prompt = f"""Write a compelling, personalized cover letter for this job application.

Job Details:
{json.dumps(job_analysis, indent=2)}

Applicant Profile:
{json.dumps(user_profile, indent=2)}

{'Company Research: ' + company_research if company_research else ''}

Write a cover letter that:
1. Opens with genuine enthusiasm and a strong hook
2. Highlights 2-3 most relevant experiences with specific examples
3. Shows you understand the company and role
4. Explains why you're a great fit
5. Closes with a strong call to action
6. Is 300-400 words
7. Has a professional but personable tone

Format as a proper business letter.
Return ONLY the letter content, no other text."""

        return self.call_claude(prompt, max_tokens=3000, temperature=0.8)
    
    def calculate_ats_score(
        self,
        resume_content: str,
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate ATS match score between resume and job requirements
        
        Returns:
            Dictionary with score and analysis
        """
        prompt = f"""Analyze how well this resume matches the job requirements for ATS systems.

Job Requirements:
{json.dumps(job_analysis, indent=2)}

Resume:
{resume_content}

Provide a detailed ATS analysis in JSON format:
{{
    "overall_score": number from 0-100,
    "matched_keywords": ["keyword1", "keyword2", ...],
    "missing_keywords": ["keyword1", "keyword2", ...],
    "strengths": ["strength1", "strength2", ...],
    "improvements": ["improvement1", "improvement2", ...],
    "keyword_density": "Low/Medium/High"
}}

Return ONLY the JSON."""

        response = self.call_claude(prompt, max_tokens=2000)
        
        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overall_score": 0,
                "error": "Failed to parse ATS analysis"
            }

# Singleton instance
bedrock_service = BedrockService()