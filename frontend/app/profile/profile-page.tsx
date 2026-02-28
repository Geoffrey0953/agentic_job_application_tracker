'use client';

import { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  Linkedin, 
  Github, 
  Globe,
  Briefcase,
  GraduationCap,
  Code,
  Award,
  Plus,
  X,
  Save,
  AlertCircle,
  FileText
} from 'lucide-react';

export default function ProfilePage() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    phone: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    summary: '',
    resume_text: '',
    experiences: [],
    education: [],
    skills: [],
    projects: [],
    certifications: []
  });

  const [newSkill, setNewSkill] = useState('');

  // Fetch existing profile on mount
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/profile');
      
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else if (response.status === 404) {
        // No profile exists yet, that's okay
        console.log('No profile found, create a new one');
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const response = await fetch('http://localhost:8000/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error('Failed to save profile');
      }

      const data = await response.json();
      setProfile(data);
      setSuccess('Profile saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to save profile. Please try again.');
      console.error('Error saving profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const addExperience = () => {
    setProfile({
      ...profile,
      experiences: [
        ...profile.experiences,
        {
          title: '',
          company: '',
          description: '',
          start_date: '',
          end_date: ''
        }
      ]
    });
  };

  const updateExperience = (index, field, value) => {
    const updated = [...profile.experiences];
    updated[index][field] = value;
    setProfile({ ...profile, experiences: updated });
  };

  const removeExperience = (index) => {
    setProfile({
      ...profile,
      experiences: profile.experiences.filter((_, i) => i !== index)
    });
  };

  const addEducation = () => {
    setProfile({
      ...profile,
      education: [
        ...profile.education,
        {
          degree: '',
          school: '',
          graduation_date: '',
          gpa: ''
        }
      ]
    });
  };

  const updateEducation = (index, field, value) => {
    const updated = [...profile.education];
    updated[index][field] = value;
    setProfile({ ...profile, education: updated });
  };

  const removeEducation = (index) => {
    setProfile({
      ...profile,
      education: profile.education.filter((_, i) => i !== index)
    });
  };

  const addSkill = () => {
    if (newSkill.trim() && !profile.skills.includes(newSkill.trim())) {
      setProfile({
        ...profile,
        skills: [...profile.skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setProfile({
      ...profile,
      skills: profile.skills.filter(s => s !== skill)
    });
  };

  const addProject = () => {
    setProfile({
      ...profile,
      projects: [
        ...profile.projects,
        {
          name: '',
          description: '',
          technologies: [],
          url: ''
        }
      ]
    });
  };

  const updateProject = (index, field, value) => {
    const updated = [...profile.projects];
    updated[index][field] = value;
    setProfile({ ...profile, projects: updated });
  };

  const removeProject = (index) => {
    setProfile({
      ...profile,
      projects: profile.projects.filter((_, i) => i !== index)
    });
  };

  const addCertification = () => {
    setProfile({
      ...profile,
      certifications: [
        ...profile.certifications,
        {
          name: '',
          issuer: '',
          date: ''
        }
      ]
    });
  };

  const updateCertification = (index, field, value) => {
    const updated = [...profile.certifications];
    updated[index][field] = value;
    setProfile({ ...profile, certifications: updated });
  };

  const removeCertification = (index) => {
    setProfile({
      ...profile,
      certifications: profile.certifications.filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Your Profile</h1>
              <p className="text-sm text-slate-600 mt-1">This information will be used to generate tailored resumes</p>
            </div>
            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-4xl">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-800">
            <AlertCircle className="w-5 h-5" />
            {success}
          </div>
        )}
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Basic Information */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            Basic Information
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name *</label>
              <input
                type="text"
                value={profile.full_name}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="(555) 123-4567"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">LinkedIn URL</label>
              <input
                type="url"
                value={profile.linkedin_url}
                onChange={(e) => setProfile({ ...profile, linkedin_url: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://linkedin.com/in/johndoe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">GitHub URL</label>
              <input
                type="url"
                value={profile.github_url}
                onChange={(e) => setProfile({ ...profile, github_url: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://github.com/johndoe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Portfolio URL</label>
              <input
                type="url"
                value={profile.portfolio_url}
                onChange={(e) => setProfile({ ...profile, portfolio_url: e.target.value })}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://johndoe.com"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">Professional Summary</label>
            <textarea
              value={profile.summary}
              onChange={(e) => setProfile({ ...profile, summary: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Brief summary of your background and career goals..."
            />
          </div>
        </div>

        {/* Resume Text */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Resume
          </h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Paste Your Resume Here
            </label>
            <p className="text-sm text-slate-600 mb-3">
              Paste your complete resume text here. This will be used as a base for generating tailored resumes for each job application.
            </p>
            <textarea
              value={profile.resume_text || ''}
              onChange={(e) => setProfile({ ...profile, resume_text: e.target.value })}
              rows={15}
              className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="Paste your complete resume here...&#10;&#10;John Doe&#10;Email: john@example.com&#10;Phone: (555) 123-4567&#10;&#10;EXPERIENCE&#10;...&#10;&#10;EDUCATION&#10;..."
            />
          </div>
        </div>

        {/* Work Experience */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Work Experience
            </h2>
            <button
              onClick={addExperience}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Experience
            </button>
          </div>
          
          {profile.experiences.map((exp, index) => (
            <div key={index} className="mb-4 p-4 border border-slate-200 rounded-lg relative">
              <button
                onClick={() => removeExperience(index)}
                className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded"
              >
                <X className="w-4 h-4" />
              </button>
              
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Job Title *</label>
                  <input
                    type="text"
                    value={exp.title}
                    onChange={(e) => updateExperience(index, 'title', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Software Engineer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Company *</label>
                  <input
                    type="text"
                    value={exp.company}
                    onChange={(e) => updateExperience(index, 'company', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Company Name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Start Date</label>
                  <input
                    type="text"
                    value={exp.start_date}
                    onChange={(e) => updateExperience(index, 'start_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="2023-01 or Jan 2023"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">End Date</label>
                  <input
                    type="text"
                    value={exp.end_date}
                    onChange={(e) => updateExperience(index, 'end_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Present or 2024-12"
                  />
                </div>
              </div>
              <div className="mt-3">
                <label className="block text-sm font-medium text-slate-700 mb-1">Description *</label>
                <textarea
                  value={exp.description}
                  onChange={(e) => updateExperience(index, 'description', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe your responsibilities and achievements..."
                />
              </div>
            </div>
          ))}
          
          {profile.experiences.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-4">No experience added yet. Click "Add Experience" to get started.</p>
          )}
        </div>

        {/* Education */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <GraduationCap className="w-5 h-5" />
              Education
            </h2>
            <button
              onClick={addEducation}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Education
            </button>
          </div>
          
          {profile.education.map((edu, index) => (
            <div key={index} className="mb-4 p-4 border border-slate-200 rounded-lg relative">
              <button
                onClick={() => removeEducation(index)}
                className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded"
              >
                <X className="w-4 h-4" />
              </button>
              
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Degree *</label>
                  <input
                    type="text"
                    value={edu.degree}
                    onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="BS Computer Science"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">School *</label>
                  <input
                    type="text"
                    value={edu.school}
                    onChange={(e) => updateEducation(index, 'school', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="UC Irvine"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Graduation Date *</label>
                  <input
                    type="text"
                    value={edu.graduation_date}
                    onChange={(e) => updateEducation(index, 'graduation_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="2026 or May 2026"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">GPA (Optional)</label>
                  <input
                    type="text"
                    value={edu.gpa || ''}
                    onChange={(e) => updateEducation(index, 'gpa', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="3.8"
                  />
                </div>
              </div>
            </div>
          ))}
          
          {profile.education.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-4">No education added yet.</p>
          )}
        </div>

        {/* Skills */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Code className="w-5 h-5" />
            Skills
          </h2>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSkill()}
              className="flex-1 px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add a skill (e.g., Python, React, AWS)"
            />
            <button
              onClick={addSkill}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add
            </button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((skill, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
              >
                {skill}
                <button
                  onClick={() => removeSkill(skill)}
                  className="hover:text-blue-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          
          {profile.skills.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-4">No skills added yet.</p>
          )}
        </div>

        {/* Projects */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Projects
            </h2>
            <button
              onClick={addProject}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Project
            </button>
          </div>
          
          {profile.projects.map((project, index) => (
            <div key={index} className="mb-4 p-4 border border-slate-200 rounded-lg relative">
              <button
                onClick={() => removeProject(index)}
                className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded"
              >
                <X className="w-4 h-4" />
              </button>
              
              <div className="grid gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Project Name *</label>
                  <input
                    type="text"
                    value={project.name}
                    onChange={(e) => updateProject(index, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="My Awesome Project"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Description *</label>
                  <textarea
                    value={project.description}
                    onChange={(e) => updateProject(index, 'description', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Brief description of the project..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Technologies (comma-separated)</label>
                  <input
                    type="text"
                    value={Array.isArray(project.technologies) ? project.technologies.join(', ') : ''}
                    onChange={(e) => updateProject(index, 'technologies', e.target.value.split(',').map(t => t.trim()))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="React, Node.js, AWS"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Project URL</label>
                  <input
                    type="url"
                    value={project.url || ''}
                    onChange={(e) => updateProject(index, 'url', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://github.com/username/project"
                  />
                </div>
              </div>
            </div>
          ))}
          
          {profile.projects.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-4">No projects added yet.</p>
          )}
        </div>

        {/* Certifications */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5" />
              Certifications
            </h2>
            <button
              onClick={addCertification}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Certification
            </button>
          </div>
          
          {profile.certifications.map((cert, index) => (
            <div key={index} className="mb-4 p-4 border border-slate-200 rounded-lg relative">
              <button
                onClick={() => removeCertification(index)}
                className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded"
              >
                <X className="w-4 h-4" />
              </button>
              
              <div className="grid md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Certification Name *</label>
                  <input
                    type="text"
                    value={cert.name}
                    onChange={(e) => updateCertification(index, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="AWS Solutions Architect"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Issuer *</label>
                  <input
                    type="text"
                    value={cert.issuer}
                    onChange={(e) => updateCertification(index, 'issuer', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Amazon Web Services"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date *</label>
                  <input
                    type="text"
                    value={cert.date}
                    onChange={(e) => updateCertification(index, 'date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="2024"
                  />
                </div>
              </div>
            </div>
          ))}
          
          {profile.certifications.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-4">No certifications added yet.</p>
          )}
        </div>

        {/* Save Button (Bottom) */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  );
}