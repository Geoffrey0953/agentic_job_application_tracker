#!/usr/bin/env python3
"""
Simple script to view database tables and their contents
Usage: python view_db.py
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.models import UserProfile, Application
from sqlalchemy import inspect

def format_json(data):
    """Format JSON data for display"""
    if data is None:
        return "None"
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)

def format_text(text, max_length=100):
    """Truncate long text for display"""
    if text is None:
        return "None"
    text = str(text)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def view_tables():
    """List all tables in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\n" + "="*60)
    print("DATABASE TABLES")
    print("="*60)
    for table in tables:
        print(f"  ✓ {table}")
    print("="*60 + "\n")
    return tables

def view_user_profiles():
    """View all user profiles"""
    db = SessionLocal()
    try:
        profiles = db.query(UserProfile).all()
        
        print("\n" + "="*60)
        print(f"USER PROFILES ({len(profiles)} found)")
        print("="*60)
        
        if not profiles:
            print("  No profiles found.")
            return
        
        for profile in profiles:
            print(f"\n📋 Profile ID: {profile.id}")
            print(f"   Name: {profile.full_name or 'Not set'}")
            print(f"   Email: {profile.email or 'Not set'}")
            print(f"   Phone: {profile.phone or 'Not set'}")
            print(f"   LinkedIn: {profile.linkedin_url or 'Not set'}")
            print(f"   GitHub: {profile.github_url or 'Not set'}")
            print(f"   Summary: {format_text(profile.summary, 80)}")
            print(f"   Resume Text: {format_text(profile.resume_text, 80)}")
            print(f"   Experiences: {len(profile.experiences or [])} entries")
            print(f"   Education: {len(profile.education or [])} entries")
            print(f"   Skills: {len(profile.skills or [])} skills")
            print(f"   Projects: {len(profile.projects or [])} projects")
            print(f"   Certifications: {len(profile.certifications or [])} certifications")
            print(f"   Created: {profile.created_at}")
            print(f"   Updated: {profile.updated_at}")
            
            if profile.experiences:
                print("\n   Work Experience:")
                for i, exp in enumerate(profile.experiences, 1):
                    print(f"     {i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
            
            if profile.skills:
                print(f"\n   Skills: {', '.join(profile.skills[:10])}")
                if len(profile.skills) > 10:
                    print(f"            ... and {len(profile.skills) - 10} more")
        
    finally:
        db.close()

def view_applications():
    """View all job applications"""
    db = SessionLocal()
    try:
        applications = db.query(Application).order_by(Application.created_at.desc()).all()
        
        print("\n" + "="*60)
        print(f"JOB APPLICATIONS ({len(applications)} found)")
        print("="*60)
        
        if not applications:
            print("  No applications found.")
            return
        
        for app in applications:
            print(f"\n💼 Application ID: {app.id}")
            print(f"   Job Title: {app.job_title}")
            print(f"   Company: {app.company}")
            print(f"   Location: {app.location or 'Not specified'}")
            print(f"   Status: {app.status}")
            print(f"   Applied Date: {app.applied_date}")
            print(f"   Match Score: {app.match_score or 'Not calculated'}")
            print(f"   Job Description: {format_text(app.job_description, 100)}")
            print(f"   Has Resume: {'Yes' if app.resume_content else 'No'}")
            print(f"   Has Cover Letter: {'Yes' if app.cover_letter_content else 'No'}")
            print(f"   Resume URL: {app.resume_url or 'Not uploaded'}")
            print(f"   Cover Letter URL: {app.cover_letter_url or 'Not uploaded'}")
            print(f"   Created: {app.created_at}")
            print(f"   Updated: {app.updated_at}")
            
            if app.parsed_data:
                print(f"\n   Parsed Data (Job Analysis):")
                parsed = app.parsed_data
                if isinstance(parsed, dict):
                    for key, value in list(parsed.items())[:5]:  # Show first 5 items
                        print(f"     - {key}: {format_text(str(value), 50)}")
        
    finally:
        db.close()

def view_table_schema():
    """View table schemas"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n" + "="*60)
    print("TABLE SCHEMAS")
    print("="*60)
    
    for table_name in tables:
        print(f"\n📊 Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col.get('default') else ""
            print(f"   - {col['name']}: {col_type} {nullable}{default}")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("DATABASE VIEWER")
    print("="*60)
    
    # Check if database exists
    db_path = os.getenv("DATABASE_URL", "sqlite:///./jobtracker.db")
    if db_path.startswith("sqlite"):
        db_file = db_path.replace("sqlite:///", "")
        if not os.path.exists(db_file):
            print(f"\n❌ Database file not found: {db_file}")
            print("   Start the app first to create the database.")
            return
    
    try:
        # View table schemas
        view_table_schema()
        
        # View tables
        view_tables()
        
        # View data
        view_user_profiles()
        view_applications()
        
        print("\n" + "="*60)
        print("✅ Done!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

