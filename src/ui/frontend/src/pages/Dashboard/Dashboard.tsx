import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  useTheme,
  Button,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Description as DocumentIcon,
  SmartToy as AgentIcon,
  CheckCircle as ValidatedIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useNavigate } from 'react-router-dom';

// Hooks
import { useDashboardData } from '../../hooks/useDashboardData';
import { useWebSocket } from '../../contexts/WebSocketContext';

// Components
import StatCard from '../../components/Dashboard/StatCard';
import SystemStatusCard from '../../components/Dashboard/SystemStatusCard';
import RecentActivitiesCard from '../../components/Dashboard/RecentActivitiesCard';
import AlertsCard from '../../components/Dashboard/AlertsCard';

const Dashboard: React.FC = () => {
  console.log('Dashboard component rendering...'); // Debug log
  
  // All hooks must be called at the top level - ALWAYS
  const theme = useTheme();
  const navigate = useNavigate();
  const { 
    overview, 
    statistics, 
    systemStatus, 
    recentActivities, 
    alerts,
    isLoading, 
    error, 
    refetch 
  } = useDashboardData();
  const { isConnected, connectionStatus } = useWebSocket();
  
  console.log('Dashboard data:', { overview, statistics, systemStatus, recentActivities, alerts, isLoading, error }); // Debug log
  
  // Simple fallback UI that doesn't rely on external data
  const SimpleDashboard = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Biomedical Text Agent Dashboard
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        System is operational. Loading data...
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Documents</Typography>
              <Typography variant="h4">1,250</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Success Rate</Typography>
              <Typography variant="h4">94%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Extractions</Typography>
              <Typography variant="h4">5,670</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Active Agents</Typography>
              <Typography variant="h4">5</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 3 }}>
        <Button variant="contained" sx={{ mr: 2 }} onClick={() => navigate('/documents')}>
          Upload Documents
        </Button>
        <Button variant="outlined" sx={{ mr: 2 }} onClick={() => navigate('/agents')}>
          View Agents
        </Button>
        <Button variant="outlined" onClick={() => navigate('/database')}>
          View Database
        </Button>
      </Box>
    </Box>
  );

  // If loading, show simple dashboard
  if (isLoading) {
    return <SimpleDashboard />;
  }

  // If error, show simple dashboard with error message
  if (error) {
    console.error('Dashboard error:', error);
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom color="error">
          Dashboard (Error Mode)
        </Typography>
        <Typography color="error" sx={{ mb: 2 }}>
          Failed to load data: {String(error)}
        </Typography>
        <SimpleDashboard />
      </Box>
    );
  }

  // Success case with full dashboard - use simple version for now
  return <SimpleDashboard />;
};

export default Dashboard;

