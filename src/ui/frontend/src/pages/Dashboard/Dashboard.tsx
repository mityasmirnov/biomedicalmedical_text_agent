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

// Hooks
import { useDashboardData } from '../../hooks/useDashboardData';
import { useWebSocket } from '../../contexts/WebSocketContext';

// Components
import StatCard from '../../components/Dashboard/StatCard';
import SystemStatusCard from '../../components/Dashboard/SystemStatusCard';
import RecentActivitiesCard from '../../components/Dashboard/RecentActivitiesCard';
import AlertsCard from '../../components/Dashboard/AlertsCard';

const Dashboard: React.FC = () => {
  const theme = useTheme();
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

  // Sample data for charts (in production, this would come from the API)
  const extractionTrendData = [
    { date: '2024-01-01', extractions: 45, success: 42 },
    { date: '2024-01-02', extractions: 52, success: 48 },
    { date: '2024-01-03', extractions: 38, success: 36 },
    { date: '2024-01-04', extractions: 61, success: 58 },
    { date: '2024-01-05', extractions: 55, success: 52 },
    { date: '2024-01-06', extractions: 67, success: 63 },
    { date: '2024-01-07', extractions: 72, success: 69 },
  ];

  const agentPerformanceData = [
    { agent: 'Demographics', accuracy: 95, count: 234 },
    { agent: 'Genetics', accuracy: 88, count: 189 },
    { agent: 'Phenotypes', accuracy: 92, count: 156 },
    { agent: 'Treatments', accuracy: 85, count: 143 },
    { agent: 'Outcomes', accuracy: 90, count: 167 },
  ];

  const documentTypeData = [
    { name: 'Case Reports', value: 45, color: '#8884d8' },
    { name: 'Clinical Trials', value: 25, color: '#82ca9d' },
    { name: 'Reviews', value: 20, color: '#ffc658' },
    { name: 'Other', value: 10, color: '#ff7300' },
  ];

  // Handle button actions
  const handleUploadDocuments = () => {
    // Navigate to documents page or open upload dialog
    window.location.href = '/documents';
  };

  const handleViewAgents = () => {
    window.location.href = '/agents';
  };

  const handleViewValidation = () => {
    window.location.href = '/validation';
  };

  const handleViewDatabase = () => {
    window.location.href = '/database';
  };

  const handleViewKnowledgeBase = () => {
    window.location.href = '/knowledge-base';
  };

  // Show loading state
  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <LinearProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading dashboard data...
        </Typography>
      </Box>
    );
  }

  // Show error state
  if (error) {
    const errText = (error as any)?.message || String(error);
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom color="error">
          Error Loading Dashboard
        </Typography>
        <Typography color="error" sx={{ mb: 2 }}>
          {errText}
        </Typography>
        <Button variant="contained" onClick={refetch}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            size="small"
          />
          <IconButton onClick={refetch} disabled={isLoading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Quick Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<UploadIcon />}
                onClick={handleUploadDocuments}
              >
                Upload Documents
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AgentIcon />}
                onClick={handleViewAgents}
              >
                View Agents
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AssessmentIcon />}
                onClick={handleViewValidation}
              >
                Validation
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<ValidatedIcon />}
                onClick={handleViewDatabase}
              >
                Database
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Stats Grid */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Documents"
            value={statistics?.total_documents || 0}
            change={statistics?.processed_today || 0}
            changeLabel="today"
            icon={<DocumentIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${statistics?.success_rate || 0}%`}
            change={statistics?.success_rate || 0}
            changeLabel="success rate"
            icon={<AgentIcon />}
            color="success"
            isPercentage
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Extractions"
            value={statistics?.total_extractions || 0}
            change={statistics?.validation_pending || 0}
            changeLabel="pending validation"
            icon={<ValidatedIcon />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Processing Time"
            value={`${(statistics?.average_processing_time || 0).toFixed(1)}s`}
            change={statistics?.active_agents || 0}
            changeLabel="active agents"
            icon={<SpeedIcon />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* System Status and Alerts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <SystemStatusCard 
            status={systemStatus?.status || 'Unknown'} 
            details={overview ? 'System operational' : 'Loading system status'} 
            health={(overview ? 'healthy' : 'warning') as 'healthy' | 'warning' | 'critical'} 
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <AlertsCard alerts={alerts || []} />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} mb={3}>
        {/* Extraction Trends */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Extraction Trends (Last 7 Days)
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={extractionTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <Area
                      type="monotone"
                      dataKey="extractions"
                      stackId="1"
                      stroke={theme.palette.primary.main}
                      fill={theme.palette.primary.light}
                      name="Total Extractions"
                    />
                    <Area
                      type="monotone"
                      dataKey="success"
                      stackId="2"
                      stroke={theme.palette.success.main}
                      fill={theme.palette.success.light}
                      name="Successful Extractions"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Document Types */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Types
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={documentTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {documentTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              <Box mt={2}>
                {documentTypeData.map((item, index) => (
                  <Box key={index} display="flex" alignItems="center" mb={1}>
                    <Box
                      width={12}
                      height={12}
                      bgcolor={item.color}
                      borderRadius="50%"
                      mr={1}
                    />
                    <Typography variant="body2" flexGrow={1}>
                      {item.name}
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {item.value}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Performance */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Performance
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={agentPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="agent" />
                    <YAxis yAxisId="left" orientation="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Bar
                      yAxisId="left"
                      dataKey="accuracy"
                      fill={theme.palette.primary.main}
                      name="Accuracy (%)"
                    />
                    <Bar
                      yAxisId="right"
                      dataKey="count"
                      fill={theme.palette.secondary.main}
                      name="Extractions Count"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <RecentActivitiesCard activities={recentActivities || []} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

