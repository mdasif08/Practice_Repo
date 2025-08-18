import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [loading, setLoading] = useState(false);
  const [commits, setCommits] = useState([]);
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [repoDetails, setRepoDetails] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTrackNow = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('Fetching commits from backend...');
      const response = await axios.get(`${API_BASE_URL}/recent-commits?author=mdasif08&limit=20`);
      console.log('Backend response:', response.data);
      setCommits(response.data.commits || []);
      setSuccess(`✅ Successfully fetched ${response.data.commits?.length || 0} commits from mdasif08 (PostgreSQL database)`);
    } catch (err) {
      console.error('Error fetching commits:', err);
      if (err.code === 'ECONNREFUSED') {
        setError('❌ Cannot connect to backend server. Please ensure the backend is running on port 5000.');
      } else if (err.response) {
        setError(`❌ Backend error: ${err.response.data.message || err.response.statusText}`);
      } else {
        setError('❌ Failed to fetch commits. Please check your network connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGitHub = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('Fetching repositories from GitHub...');
      const response = await axios.get('https://api.github.com/user/repos', {
        headers: {
          'Authorization': `Bearer ${process.env.REACT_APP_GITHUB_TOKEN || 'your_github_token_here'}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });
      
      setRepositories(response.data);
      setSuccess(`✅ Successfully fetched ${response.data.length} repositories from GitHub`);
    } catch (err) {
      console.error('Error fetching repositories:', err);
      setError('❌ Failed to fetch repositories. Please check your GitHub token.');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setSuccess(`✅ Backend connection successful! Status: ${response.data.status}`);
    } catch (err) {
      console.error('Connection test failed:', err);
      setError('❌ Backend connection failed. Please ensure the server is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchRealCommits = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      console.log('Fetching real GitHub commits...');
      const response = await axios.post(`${API_BASE_URL}/fetch-github-commits`, {
        repo_owner: 'mdasif08',
        repo_name: 'Practice_Repo',
        max_commits: 5
      });
      
      setSuccess(`✅ ${response.data.message}`);
      console.log('Real commits fetched:', response.data);
    } catch (err) {
      console.error('Error fetching real commits:', err);
      setError('❌ Failed to fetch real commits. Please check your GitHub token and repository.');
    } finally {
      setLoading(false);
    }
  };

  const handleRepoSelect = (event) => {
    const repoName = event.target.value;
    setSelectedRepo(repoName);
    
    const repo = repositories.find(r => r.name === repoName);
    if (repo) {
      setRepoDetails(repo);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        <h1 className="title">🎉 CraftNudge Git Tracker</h1>
        <p className="subtitle">Track your Git commits and manage GitHub repositories</p>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Action Buttons */}
        <div className="button-container">
          <button 
            className={`action-button primary ${loading ? 'loading' : ''}`}
            onClick={handleTrackNow}
            disabled={loading}
          >
            {loading ? '⏳ Loading...' : '📊 Track Now'}
          </button>
          <button 
            className={`action-button secondary ${loading ? 'loading' : ''}`}
            onClick={handleGitHub}
            disabled={loading}
          >
            {loading ? '⏳ Loading...' : '🐙 GitHub'}
          </button>
          <button 
            className={`action-button secondary ${loading ? 'loading' : ''}`}
            onClick={handleTestConnection}
            disabled={loading}
          >
            {loading ? '⏳ Loading...' : '🔗 Test Connection'}
          </button>
          <button 
            className={`action-button secondary ${loading ? 'loading' : ''}`}
            onClick={handleFetchRealCommits}
            disabled={loading}
          >
            {loading ? '⏳ Loading...' : '🔄 Fetch Real Commits'}
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="alert error">
            {error}
          </div>
        )}
        {success && (
          <div className="alert success">
            {success}
          </div>
        )}

        {/* Content Sections */}
        <div className="content-section">
          {/* Repository Selection */}
          {repositories.length > 0 && (
            <div className="card">
              <h3>📁 Select Repository</h3>
              <select 
                value={selectedRepo} 
                onChange={handleRepoSelect}
                className="repo-select"
              >
                <option value="">Choose a repository...</option>
                {repositories.map((repo) => (
                  <option key={repo.id} value={repo.name}>
                    {repo.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Repository Details */}
          {repoDetails && (
            <div className="card">
              <h3>📋 Repository Details</h3>
              <div className="repo-details">
                <div className="repo-info">
                  <h4>{repoDetails.name}</h4>
                  <p>{repoDetails.description || 'No description available'}</p>
                  <span className={`status-chip ${repoDetails.private ? 'private' : 'public'}`}>
                    {repoDetails.private ? '🔒 Private' : '🌐 Public'}
                  </span>
                </div>
                <div className="repo-stats">
                  <p><strong>Language:</strong> {repoDetails.language || 'Not specified'}</p>
                  <p><strong>Stars:</strong> ⭐ {repoDetails.stargazers_count}</p>
                  <p><strong>Forks:</strong> 🍴 {repoDetails.forks_count}</p>
                  <p><strong>Created:</strong> 📅 {formatDate(repoDetails.created_at)}</p>
                  <a 
                    href={repoDetails.html_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="github-link"
                  >
                    🔗 View on GitHub
                  </a>
                </div>
              </div>
            </div>
          )}

          {/* Commits Display */}
          {commits.length > 0 && (
            <div className="card">
              <h3>📝 Recent Commits from PostgreSQL Database</h3>
              <div className="commits-list">
                {commits.map((commit, index) => (
                  <div key={index} className="commit-item">
                    <div className="commit-content">
                      <h4>{commit.message}</h4>
                      <p><strong>👤 Author:</strong> {commit.author}</p>
                      <p><strong>🔗 Hash:</strong> {commit.commit_hash?.substring(0, 8)}...</p>
                    </div>
                    <div className="commit-meta">
                      <p className="commit-date">📅 {formatDate(commit.timestamp_commit)}</p>
                      {commit.branch && (
                        <span className="branch-chip">🌿 {commit.branch}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Welcome Card (shown when no data) */}
          {commits.length === 0 && repositories.length === 0 && !loading && (
            <div className="welcome-section">
              <h3>🎯 Welcome to CraftNudge!</h3>
              <p>This is a React + Vite frontend for your Git commit tracking microservice.</p>
              <p>Click the buttons above to fetch your Git commits and GitHub repositories.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
