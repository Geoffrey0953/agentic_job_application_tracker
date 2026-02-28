'use client';

import { useState, useEffect } from 'react';
import {
  Briefcase,
  FileText,
  Mail,
  Plus,
  Search,
  CheckCircle2,
  Clock,
  XCircle,
  Send,
  Calendar,
  Building2,
  MapPin,
  Sparkles,
  TrendingUp,
  Eye,
  AlertCircle,
  Trash2
} from 'lucide-react';

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700 border-yellow-200', icon: Clock },
  applied: { label: 'Applied', color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Send },
  interview: { label: 'Interview', color: 'bg-purple-100 text-purple-700 border-purple-200', icon: Calendar },
  offer: { label: 'Offer', color: 'bg-green-100 text-green-700 border-green-200', icon: CheckCircle2 },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700 border-red-200', icon: XCircle }
};

const API_BASE_URL = 'http://localhost:8000';

export default function Dashboard() {
  const [showNewJobModal, setShowNewJobModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [applications, setApplications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Fetch applications on mount
  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/applications`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }
      
      const data = await response.json();
      setApplications(data);
    } catch (err) {
      console.error('Error fetching applications:', err);
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const handleAddJob = async () => {
    if (!jobDescription.trim()) return;
    
    setIsGenerating(true);
    setError('');
    
    try {
      // Use agentic endpoint for intelligent workflow
      const response = await fetch(`${API_BASE_URL}/api/agentic/create-application`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_description: jobDescription,
          auto_generate: true
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create application');
      }

      const data = await response.json();
      
      if (data.success) {
        // Refresh applications list
        await fetchApplications();
        setJobDescription('');
        setShowNewJobModal(false);
        
        // Show success message
        alert(`Application created! ATS Score: ${data.data.ats_score}%`);
      } else if (data.data?.needs_profile) {
        alert('Please create your profile first before generating applications!');
        // Optionally redirect to profile page
        // window.location.href = '/profile';
      }
    } catch (err) {
      console.error('Error creating application:', err);
      setError(err.message || 'Failed to create application. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const viewApplicationDetails = async (app) => {
    setSelectedApplication(app);
    setShowDetailsModal(true);
  };

  const handleDeleteApplication = async (appId: number) => {
    if (!confirm('Delete this application? This cannot be undone.')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/${appId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete application');
      }

      setApplications(prev => prev.filter(a => a.id !== appId));
    } catch (err) {
      setError(err.message || 'Failed to delete application');
    }
  };

  const stats = [
    { label: 'Total Applications', value: applications.length, icon: Briefcase, color: 'from-blue-500 to-blue-600' },
    { label: 'In Progress', value: applications.filter(a => a.status === 'interview').length, icon: Clock, color: 'from-purple-500 to-purple-600' },
    { label: 'Avg Match Score', value: applications.length > 0 ? Math.round(applications.reduce((acc, a) => acc + (a.match_score || 0), 0) / applications.length) + '%' : '0%', icon: TrendingUp, color: 'from-green-500 to-green-600' },
    { label: 'Offers', value: applications.filter(a => a.status === 'offer').length, icon: CheckCircle2, color: 'from-pink-500 to-pink-600' }
  ];

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.job_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         app.company.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || app.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading applications...</p>
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
              <h1 className="text-2xl font-bold text-slate-900">Job Application Tracker</h1>
              <p className="text-sm text-slate-600 mt-1">Powered by AI • AWS Bedrock</p>
            </div>
            <div className="flex gap-3">
              <a
                href="/profile"
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-100 text-slate-700 rounded-lg font-semibold hover:bg-slate-200 transition-all"
              >
                Profile
              </a>
              <button
                onClick={() => setShowNewJobModal(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl hover:scale-105"
              >
                <Plus className="w-5 h-5" />
                New Application
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            {error}
            <button onClick={() => setError('')} className="ml-auto">
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-3xl font-bold text-slate-900">{stat.value}</span>
              </div>
              <p className="text-sm font-medium text-slate-600">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search jobs or companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="applied">Applied</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {filteredApplications.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center shadow-sm border border-slate-100">
              <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No applications yet</h3>
              <p className="text-slate-600 mb-6">Start tracking your job applications by adding your first one</p>
              <button
                onClick={() => setShowNewJobModal(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all"
              >
                <Plus className="w-5 h-5" />
                Add Your First Job
              </button>
            </div>
          ) : (
            filteredApplications.map((app) => {
              const StatusIcon = statusConfig[app.status as keyof typeof statusConfig]?.icon || Clock;
              
              return (
                <div key={app.id} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-all">
                  <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                    {/* Job Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Building2 className="w-6 h-6 text-slate-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-bold text-slate-900 truncate">{app.job_title}</h3>
                          <p className="text-slate-600 font-medium">{app.company}</p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                            <span className="inline-flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {app.location || 'Not specified'}
                            </span>
                            <span className="inline-flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(app.applied_date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Tags */}
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${statusConfig[app.status]?.color || statusConfig.pending.color}`}>
                          <StatusIcon className="w-4 h-4" />
                          {statusConfig[app.status]?.label || 'Pending'}
                        </span>
                        {app.match_score && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-green-50 text-green-700 border border-green-200">
                            <TrendingUp className="w-4 h-4" />
                            {app.match_score}% Match
                          </span>
                        )}
                        {app.salary_range && (
                          <span className="text-sm text-slate-600 font-medium">{app.salary_range}</span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 lg:flex-col lg:items-end">
                      <div className="flex gap-2">
                        {app.resume_content && (
                          <button
                            onClick={() => viewApplicationDetails(app)}
                            className="p-2 text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                            title="View Resume"
                          >
                            <FileText className="w-5 h-5" />
                          </button>
                        )}
                        {app.cover_letter_content && (
                          <button
                            onClick={() => viewApplicationDetails(app)}
                            className="p-2 text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
                            title="View Cover Letter"
                          >
                            <Mail className="w-5 h-5" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteApplication(app.id)}
                          className="p-2 text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                          title="Delete application"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => viewApplicationDetails(app)}
                          className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
                        >
                          <Eye className="w-4 h-4 inline mr-1" />
                          View
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* New Job Modal */}
      {showNewJobModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900">Add New Job Application</h2>
                  <p className="text-sm text-slate-600 mt-1">Paste the job description and AI will generate everything</p>
                </div>
                <button
                  onClick={() => setShowNewJobModal(false)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Job Description *
                  </label>
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the full job description here... Include the job title, company, requirements, responsibilities, etc."
                    rows={12}
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex gap-3">
                    <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900 mb-1">AI Will Generate:</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>✓ Job analysis and requirement extraction</li>
                        <li>✓ Tailored resume optimized for this role</li>
                        <li>✓ Personalized cover letter</li>
                        <li>✓ ATS match score and analysis</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-800">
                    <AlertCircle className="w-5 h-5" />
                    <p className="text-sm">{error}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 border-t border-slate-200 bg-slate-50">
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowNewJobModal(false)}
                  className="px-6 py-3 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddJob}
                  disabled={!jobDescription.trim() || isGenerating}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Application
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Application Details Modal */}
      {showDetailsModal && selectedApplication && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900">{selectedApplication.job_title}</h2>
                  <p className="text-sm text-slate-600 mt-1">{selectedApplication.company}</p>
                </div>
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {/* ATS Score */}
              {selectedApplication.match_score && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <h3 className="text-lg font-bold text-green-900">ATS Match Score</h3>
                  </div>
                  <p className="text-3xl font-bold text-green-600">{selectedApplication.match_score}%</p>
                </div>
              )}

              {/* Resume */}
              {selectedApplication.resume_content && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Generated Resume
                  </h3>
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm text-slate-700 font-mono">
                      {selectedApplication.resume_content}
                    </pre>
                  </div>
                </div>
              )}

              {/* Cover Letter */}
              {selectedApplication.cover_letter_content && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                    <Mail className="w-5 h-5" />
                    Generated Cover Letter
                  </h3>
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm text-slate-700">
                      {selectedApplication.cover_letter_content}
                    </pre>
                  </div>
                </div>
              )}

              {/* Job Description */}
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">Job Description</h3>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <p className="whitespace-pre-wrap text-sm text-slate-700">
                    {selectedApplication.job_description}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-200 bg-slate-50">
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="px-6 py-3 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}