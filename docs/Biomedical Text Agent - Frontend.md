## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend API (FastAPI) running or available on port 8000

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Environment setup (development):
```bash
# Copy environment template (if present)
cp .env.example .env.local

# Edit development environment variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/api/v1/ws
```

3. Start development server (optional):
```bash
npm start
# or
yarn start
```
Open browser at `http://localhost:3000`.

### Building for Production

```bash
# Build optimized production bundle
npm run build
# or
yarn build
```

### Serve Production UI via FastAPI (Recommended)
The backend serves the built React app directly.

1) Build the frontend as above (produces `src/ui/frontend/build`).
2) Start the FastAPI backend with static serving enabled:
```bash
# from project root
source venv/bin/activate
export PYTHONPATH=src
python -m uvicorn src.ui.backend.app:create_app --factory --host 127.0.0.1 --port 8000
```
3) Access the UI at `http://127.0.0.1:8000/`.

Notes:
- The UI is a Single Page Application (SPA). Any frontend route like `/login`, `/dashboard`, etc. is served by the same `index.html` with client-side routing.
- API endpoints under `/api/v1/...` intentionally return JSON (e.g., `/api/v1/dashboard/overview`). The frontend fetches these to render UI.
- If you see JSON at `/api/v1/...`, that is correct. To view the UI, use `/` or a UI route.

### Alternative Static Serving (Optional)
You can serve the build folder with any static server:
```bash
npm install -g serve
serve -s build
```
Ensure `REACT_APP_API_BASE_URL` points to your backend (e.g., `http://localhost:8000/api/v1`).

## Environment Variables

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/api/v1/ws

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DEBUG=false

# Authentication
REACT_APP_AUTH_PROVIDER=local
REACT_APP_SESSION_TIMEOUT=3600
```
