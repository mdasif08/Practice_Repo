import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

// Use environment variable or default to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';

function App() {
  const [loading, setLoading] = useState(false);
  const [commits, setCommits] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statistics, setStatistics] = useState(null);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState({});
  const [formData, setFormData] = useState({
    owner: '',
    repo: '',
    max_commits: 10
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    const newSocket = io(SOCKET_URL);
    
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
      newSocket.emit('subscribe_commits');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
    });

    newSocket.on('new_commit', (data) => {
      console.log('New commit received:', data);
      setSuccess(`🆕 New commit detected: ${data.data.commit_hash}`);
      // Refresh commits list
      handleRefresh();
    });

    newSocket.on('ai_analysis', (data) => {
      console.log('AI analysis received:', data);
      setAiAnalysis(prev => ({
        ...prev,
        [data.data.commit_hash]: data.data.analysis
      }));
      setSuccess(`🤖 AI analysis completed for commit: ${data.data.commit_hash}`);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const handleTrackNow = async () => {
    if (!formData.owner || !formData.repo) {
      setError('Please enter both repository owner and name');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/track-commits`, {
        owner: formData.owner,
        repo: formData.repo,
        max_commits: formData.max_commits
      });
      
      setSuccess(`Successfully tracked ${response.data.commits_stored} commits from ${formData.owner}/${formData.repo}`);
      
      // Fetch fresh commits after tracking
      const timestamp = new Date().getTime();
      const commitsResponse = await axios.get(`${API_BASE_URL}/commits?limit=20&_t=${timestamp}`);
      setCommits(commitsResponse.data.commits || []);
      
    } catch (err) {
      console.error('Error tracking commits:', err);
      if (err.code === 'ECONNREFUSED') {
        setError('Cannot connect to microservice. Please ensure all services are running.');
      } else if (err.response) {
        const errorMessage = err.response.data.error || err.response.data.message || err.response.statusText;
        if (errorMessage.includes('GitHub token') || errorMessage.includes('GITHUB_TOKEN')) {
          setError('GitHub token not configured. Please run "python setup-github-token.py" to configure your GitHub token for real commits.');
        } else {
          setError(`Service error: ${errorMessage}`);
        }
      } else {
        setError('Failed to track commits. Please check your network connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Add cache-busting parameter to force fresh data
      const timestamp = new Date().getTime();
      const response = await axios.get(`${API_BASE_URL}/commits?limit=20&_t=${timestamp}`);
      setCommits(response.data.commits || []);
      setSuccess(`Refreshed! Found ${response.data.commits?.length || 0} commits in database`);
    } catch (err) {
      console.error('Error refreshing commits:', err);
      setError('Failed to refresh commits. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleGitHub = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/github/test`);
      if (response.data.demo_mode) {
        setSuccess('GitHub service is running in demo mode');
      } else if (response.data.authenticated) {
        setSuccess(`GitHub API connected! Username: ${response.data.username}`);
      } else {
        const errorMessage = response.data.error || response.data.message || 'Unknown error';
        if (errorMessage.includes('GitHub token') || errorMessage.includes('GITHUB_TOKEN')) {
          setError('GitHub token not configured. Please run "python setup-github-token.py" to configure your GitHub token for real commits.');
        } else {
          setError(`GitHub API error: ${errorMessage}`);
        }
      }
    } catch (err) {
      console.error('GitHub test failed:', err);
      if (err.response && err.response.data.error && err.response.data.error.includes('GitHub token')) {
        setError('GitHub token not configured. Please run "python setup-github-token.py" to configure your GitHub token for real commits.');
      } else {
        setError('GitHub API test failed. Please check your token configuration.');
      }
    } finally {
      setLoading(false);
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
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1>🚀 CraftNudge Microservice</h1>
          <p>Git Commit Tracking & AI Analysis</p>
          
          {/* WebSocket Status */}
          <div className={`websocket-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🔗 Real-time Connected' : '❌ Real-time Disconnected'}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Repository Form */}
          <div className="form-section">
            <div className="form-card">
              <h2>📋 Repository Information</h2>
              <div className="form-row">
                <div className="form-group">
                  <label>Repository Owner:</label>
                  <input
                    type="text"
                    placeholder="e.g., mdasif08"
                    value={formData.owner}
                    onChange={(e) => setFormData({...formData, owner: e.target.value})}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label>Repository Name:</label>
                  <input
                    type="text"
                    placeholder="e.g., my-app"
                    value={formData.repo}
                    onChange={(e) => setFormData({...formData, repo: e.target.value})}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label>Max Commits:</label>
                  <input
                    type="number"
                    value={formData.max_commits}
                    onChange={(e) => setFormData({...formData, max_commits: parseInt(e.target.value) || 10})}
                    className="form-input"
                    min="1"
                    max="100"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="button-section">
            <button 
              className={`btn btn-primary ${loading ? 'loading' : ''}`}
              onClick={handleTrackNow}
              disabled={loading}
            >
              {loading ? '⏳ Tracking...' : '📊 Track Now'}
            </button>
            <button 
              className={`btn btn-secondary ${loading ? 'loading' : ''}`}
              onClick={handleRefresh}
              disabled={loading}
            >
              {loading ? '⏳ Loading...' : '🔄 Refresh'}
            </button>
            <button 
              className={`btn btn-secondary ${loading ? 'loading' : ''}`}
              onClick={handleGitHub}
              disabled={loading}
            >
              {loading ? '⏳ Testing...' : '🐙 GitHub'}
            </button>
          </div>

          {/* Messages */}
          {error && (
            <div className="message error">
              ❌ {error}
            </div>
          )}
          {success && (
            <div className="message success">
              ✅ {success}
            </div>
          )}

          {/* AI Analysis Display */}
          {Object.keys(aiAnalysis).length > 0 && (
            <div className="ai-analysis-section">
              <div className="ai-analysis-card">
                <h2>🤖 AI Analysis Results</h2>
                {Object.entries(aiAnalysis).map(([commitHash, analysis]) => (
                  <div key={commitHash} className="analysis-item">
                    <h3>Commit: {commitHash.substring(0, 8)}...</h3>
                    <div className="analysis-content">
                      <pre>{analysis}</pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Commits Display */}
          {commits.length > 0 && (
            <div className="commits-section">
              <div className="commits-card">
                <h2>📝 Commits ({commits.length})</h2>
                <div className="commits-list">
                  {commits.map((commit, index) => (
                    <div key={index} className="commit-item">
                      <div className="commit-header">
                        <h3>{commit.message}</h3>
                        <span className="commit-date">{formatDate(commit.timestamp)}</span>
                      </div>
                      <div className="commit-details">
                        <p><strong>Author:</strong> {commit.author}</p>
                        <p><strong>Commit ID:</strong> {commit.commit_id?.substring(0, 8)}...</p>
                        {commit.changed_files && commit.changed_files.length > 0 && (
                          <div className="files-section">
                            <p><strong>Files Changed:</strong></p>
                            <div className="files-list">
                              {commit.changed_files.map((file, fileIndex) => (
                                <span key={fileIndex} className={`file-tag ${file.change_type}`}>
                                  {file.file_name} ({file.change_type})
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {/* AI Analysis for this commit */}
                        {aiAnalysis[commit.commit_id] && (
                          <div className="commit-ai-analysis">
                            <p><strong>🤖 AI Analysis:</strong></p>
                            <div className="ai-content">
                              <pre>{aiAnalysis[commit.commit_id]}</pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Welcome Message */}
          {commits.length === 0 && !loading && (
            <div className="welcome-section">
              <div className="welcome-card">
                <h2>🎯 Welcome to CraftNudge!</h2>
                <p>Enter a repository owner and name above, then click "Track Now" to fetch commits from GitHub.</p>
                <div className="features">
                  <h3>✨ Features:</h3>
                  <ul>
                    <li>🔗 Direct GitHub API integration</li>
                    <li>💾 PostgreSQL database storage</li>
                    <li>📊 Real-time commit tracking</li>
                    <li>🐳 Docker containerized microservices</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2025 CraftNudge - Microservice Architecture Demo</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
