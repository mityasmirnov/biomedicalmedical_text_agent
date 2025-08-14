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
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Description as DocumentIcon,
  SmartToy as AgentIcon,
  CheckCircle as ValidatedIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
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
import { useWebSocket } from '../../hooks/useWebSocket';

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

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography color="error">Error loading dashboard: {error.message}</Typography>
      </Box>
    );
  }

  return (
    <Box>
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

      {/* Loading indicator */}
      {isLoading && (
        <Box mb={2}>
          <LinearProgress />
        </Box>
      )}

      {/* Main Stats Grid */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Documents"
            value={statistics?.total_documents || 0}
            change={statistics?.documents_this_period || 0}
            changeLabel="this month"
            icon={<DocumentIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Successful Extractions"
            value={statistics?.successful_extractions || 0}
            change={statistics?.success_rate || 0}
            changeLabel="success rate"
            icon={<AgentIcon />}
            color="success"
            isPercentage
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Validated Results"
            value={statistics?.validated_extractions || 0}
            change={85}
            changeLabel="accuracy"
            icon={<ValidatedIcon />}
            color="info"
            isPercentage
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Processing Time"
            value={`${(statistics?.average_extraction_time || 0).toFixed(1)}s`}
            change={-12}
            changeLabel="improvement"
            icon={<SpeedIcon />}
            color="warning"
            isPercentage
          />
        </Grid>
      </Grid>

      {/* System Status and Alerts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <SystemStatusCard status={systemStatus} />
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
                      fillOpacity={0.6}
                      name="Total Extractions"
                    />
                    <Area
                      type="monotone"
                      dataKey="success"
                      stackId="2"
                      stroke={theme.palette.success.main}
                      fill={theme.palette.success.light}
                      fillOpacity={0.8}
                      name="Successful"
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

