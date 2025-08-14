# Biomedical Text Agent - Frontend

A modern React-based web interface for the biomedical literature extraction and analysis system.

## Features

### 🎛️ **Dashboard**
- Real-time system overview and statistics
- Interactive charts and visualizations
- System health monitoring
- Performance metrics tracking

### 📚 **Knowledge Base Management**
- HPO/UMLS ontology browser and editor
- Custom vocabulary creation
- Concept relationship visualization
- Term normalization tools

### 🗄️ **Database Management**
- Patient data browser and editor
- Visual query builder
- Data export/import tools
- Backup and restore functionality

### 🤖 **Agent Management**
- Real-time extraction monitoring
- Performance tracking and analytics
- Error analysis and debugging
- A/B testing for different models

### 📄 **Document Management**
- Paper/patent upload interface
- Metadata editing and enrichment
- Document status tracking
- Batch processing monitoring

### ✅ **Validation Interface**
- Manual validation workflow
- Ground truth comparison tools
- Annotation interface for corrections
- Quality assurance metrics

### 📊 **Monitoring**
- API usage analytics
- Rate limiting configuration
- Performance alerts
- System diagnostics

## Technology Stack

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Query + Context API
- **Routing**: React Router v6
- **Charts**: Recharts
- **WebSocket**: react-use-websocket
- **Forms**: React Hook Form with Yup validation
- **Styling**: Emotion (CSS-in-JS)

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on port 8000

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Environment setup**:
   ```bash
   # Copy environment template
   cp .env.example .env.local
   
   # Edit environment variables
   REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   REACT_APP_WS_URL=ws://localhost:8000/api/v1/ws
   ```

3. **Start development server**:
   ```bash
   npm start
   # or
   yarn start
   ```

4. **Open browser**: Navigate to `http://localhost:3000`

### Building for Production

```bash
# Build optimized production bundle
npm run build
# or
yarn build

# Serve built files (optional)
npm install -g serve
serve -s build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Main layout and navigation
│   ├── Dashboard/      # Dashboard-specific components
│   ├── Forms/          # Form components
│   ├── Charts/         # Chart components
│   └── Common/         # Common UI components
├── pages/              # Page components
│   ├── Dashboard/      # Dashboard page
│   ├── KnowledgeBase/  # Knowledge base pages
│   ├── Database/       # Database management pages
│   ├── Agents/         # Agent management pages
│   ├── Documents/      # Document management pages
│   ├── Validation/     # Validation pages
│   ├── Monitoring/     # Monitoring pages
│   └── Auth/           # Authentication pages
├── contexts/           # React contexts
│   ├── AuthContext.tsx # Authentication state
│   └── WebSocketContext.tsx # WebSocket connections
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication hook
│   ├── useWebSocket.ts # WebSocket hook
│   └── useApi.ts       # API hooks
├── services/           # API services
│   ├── api.ts          # Main API client
│   ├── auth.ts         # Authentication API
│   └── websocket.ts    # WebSocket utilities
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── App.tsx             # Main application component
```

## Key Components

### Layout System
- **Layout.tsx**: Main application layout with navigation
- **Sidebar**: Collapsible navigation sidebar
- **Header**: Top navigation bar with user menu
- **Responsive**: Mobile-friendly design

### Dashboard
- **Overview Cards**: Key metrics and statistics
- **Charts**: Interactive data visualizations
- **Real-time Updates**: Live data via WebSocket
- **System Status**: Health monitoring

### Knowledge Base
- **Ontology Browser**: Navigate HPO/UMLS hierarchies
- **Term Editor**: Create and edit custom terms
- **Relationship Viewer**: Visualize concept relationships
- **Search Interface**: Advanced term search

### Database Management
- **Data Browser**: Paginated data tables
- **Query Builder**: Visual query construction
- **Export Tools**: CSV/JSON data export
- **Import Wizard**: Bulk data import

### Agent Management
- **Performance Dashboard**: Real-time metrics
- **Configuration Panel**: Agent settings
- **Testing Interface**: A/B testing tools
- **Error Analysis**: Debugging tools

### Document Management
- **Upload Interface**: Drag-and-drop file upload
- **Metadata Editor**: Rich metadata editing
- **Status Tracking**: Processing status
- **Batch Operations**: Bulk processing

### Validation
- **Annotation Interface**: Manual validation tools
- **Comparison View**: Side-by-side comparison
- **Quality Metrics**: Accuracy tracking
- **Workflow Management**: Validation pipelines

## State Management

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Role-based access control
- Secure logout

### WebSocket Integration
- Real-time notifications
- Live data updates
- Connection management
- Automatic reconnection

### API Integration
- React Query for data fetching
- Automatic caching and invalidation
- Error handling and retry logic
- Loading states

## Styling and Theming

### Material-UI Theme
- Custom color palette
- Typography scale
- Component overrides
- Dark/light mode support

### Responsive Design
- Mobile-first approach
- Breakpoint-based layouts
- Touch-friendly interfaces
- Adaptive navigation

## Development Guidelines

### Code Style
- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Consistent naming conventions

### Component Structure
- Functional components with hooks
- Props interface definitions
- Default props and prop types
- Error boundaries

### Performance
- Code splitting with React.lazy
- Memoization with React.memo
- Virtual scrolling for large lists
- Image optimization

## Testing

```bash
# Run tests
npm test
# or
yarn test

# Run tests with coverage
npm test -- --coverage
# or
yarn test --coverage
```

## Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t biomedical-ui .

# Run container
docker run -p 3000:3000 biomedical-ui
```

### Static Hosting
- Build files can be served from any static hosting
- Configure API base URL for production
- Set up proper routing for SPA

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

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation
4. Submit pull requests

## License

This project is part of the Biomedical Text Agent system.

