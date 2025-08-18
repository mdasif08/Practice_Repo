# CraftNudge Frontend

A React + Vite frontend application for the CraftNudge Git Commit Logger microservice.

## Features

- **Track Now Button**: Fetches and displays recent Git commits from your backend
- **GitHub Button**: Fetches your GitHub repositories using your personal access token
- **Repository Selection**: Dropdown menu to select and view repository details
- **Modern UI**: Built with Material-UI for a clean, responsive design

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on `http://localhost:5000`

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

### Track Now Button
- Click "Track Now" to fetch recent commits from your backend
- Displays commit messages, authors, hashes, and timestamps
- Shows branch information if available

### GitHub Button
- Click "GitHub" to fetch your repositories using your personal access token
- Select a repository from the dropdown to view details
- View repository information including:
  - Name and description
  - Language and statistics
  - Creation date
  - Direct link to GitHub

## Configuration

### Backend API
The frontend is configured to connect to the backend at `http://localhost:5000`. You can modify this in `src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:5000';
```

### GitHub Token
The GitHub personal access token is configured in the `handleGitHubFetch` function. For security, consider moving this to an environment variable.

## Build for Production

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Technologies Used

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Material-UI**: Component library
- **Axios**: HTTP client for API calls
- **GitHub API**: For repository data

## Security Notes

- The GitHub token is currently hardcoded in the component
- For production, use environment variables
- Consider implementing proper authentication
- The backend should validate all requests

## Troubleshooting

### Backend Connection Issues
- Ensure your backend server is running on port 5000
- Check that CORS is properly configured
- Verify the API endpoints are working

### GitHub API Issues
- Verify your GitHub token is valid
- Check token permissions (repo access required)
- Ensure you're not hitting API rate limits

### Build Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify all dependencies are installed
