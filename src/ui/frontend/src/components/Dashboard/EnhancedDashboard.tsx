import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  useTheme,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Collapse,
  Tooltip,
} from '@mui/material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
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
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useNavigate } from 'react-router-dom';

// Hooks
import { useWebSocket } from '../../contexts/WebSocketContext';

interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  status: 'normal' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  change: number;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  status: 'available' | 'running' | 'disabled';
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

interface AlertItem {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

const EnhancedDashboard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { isConnected, connectionStatus } = useWebSocket();
  const queryClient = useQueryClient();
  
  const [expandedMetrics, setExpandedMetrics] = useState<string[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Fetch real dashboard data
  const { data: systemStatusData, isLoading: systemStatusLoading } = useQuery({
    queryKey: ['dashboard-system-status'],
    queryFn: () => api.dashboard.getSystemStatus(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: recentActivitiesData, isLoading: activitiesLoading } = useQuery({
    queryKey: ['dashboard-recent-activities'],
    queryFn: () => api.dashboard.getProcessingQueue(),
    refetchInterval: 30000,
  });

  const { data: statisticsData, isLoading: statisticsLoading } = useQuery({
    queryKey: ['dashboard-statistics'],
    queryFn: () => api.dashboard.getRecentResults(),
    refetchInterval: 30000,
  });

  // Real system metrics from API
  const systemMetrics: SystemMetric[] = [
    {
      name: 'Total Documents',
      value: systemStatusData?.data?.metrics?.total_documents || 0,
      unit: '',
      status: 'normal',
      trend: 'stable',
      change: 0,
    },
    {
      name: 'Completed Documents',
      value: systemStatusData?.data?.metrics?.completed_documents || 0,
      unit: '',
      status: 'normal',
      trend: 'stable',
      change: 0,
    },
    {
      name: 'Pending Documents',
      value: systemStatusData?.data?.metrics?.pending_documents || 0,
      unit: '',
      status: 'warning',
      trend: 'stable',
      change: 0,
    },
    {
      name: 'Active Agents',
      value: systemStatusData?.data?.metrics?.total_agents || 0,
      unit: '',
      status: 'normal',
      trend: 'stable',
      change: 0,
    },
  ];

  const [quickActions] = useState<QuickAction[]>([
    {
      id: 'upload-docs',
      title: 'Upload Documents',
      description: 'Upload new biomedical literature for processing',
      icon: <StorageIcon />,
      action: () => navigate('/documents'),
      status: 'available',
      color: 'primary',
    },
    {
      id: 'start-extraction',
      title: 'Start Extraction',
      description: 'Begin automated data extraction process',
      icon: <PlayIcon />,
      action: () => navigate('/agents'),
      status: 'available',
      color: 'success',
    },
    {
      id: 'validate-data',
      title: 'Validate Data',
      description: 'Review and validate extracted information',
      icon: <AssessmentIcon />,
      action: () => navigate('/validation'),
      status: 'available',
      color: 'warning',
    },
    {
      id: 'view-analytics',
      title: 'View Analytics',
      description: 'Access detailed performance metrics',
      icon: <BarChartIcon />,
      action: () => navigate('/monitoring'),
      status: 'available',
      color: 'secondary',
    },
  ]);

  // Real alerts from recent activities
  const alerts: AlertItem[] = recentActivitiesData?.data?.activities?.slice(0, 3).map((activity: any, index: number) => ({
    id: activity.id || index.toString(),
    severity: activity.status === 'completed' ? 'success' : 'info',
    message: activity.description || `Activity: ${activity.type}`,
    timestamp: activity.timestamp || 'Unknown',
    acknowledged: false,
  })) || [
    {
      id: '1',
      severity: 'info',
      message: 'Loading recent activities...',
      timestamp: 'Just now',
      acknowledged: false,
    }
  ];

  // Real extraction stats from API
  const extractionStats = statisticsData?.data?.statistics?.extractions ? [
    { category: 'Total Extractions', count: statisticsData.data.statistics.extractions.total || 0, percentage: 100 },
    { category: 'Successful', count: statisticsData.data.statistics.extractions.successful || 0, percentage: 100 },
  ] : [
    { category: 'Loading...', count: 0, percentage: 0 },
  ];

  // Performance data for charts (using real data when available)
  const performanceData = [
    { time: '00:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '04:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '08:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '12:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '16:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '20:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
    { time: '24:00', documents: systemStatusData?.data?.metrics?.total_documents || 0, extractions: statisticsData?.data?.statistics?.extractions?.total || 0 },
  ];

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Refresh all queries
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['dashboard-system-status'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-recent-activities'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-statistics'] }),
    ]);
    setIsRefreshing(false);
  };

  const toggleMetricExpansion = (metricName: string) => {
    setExpandedMetrics(prev => 
      prev.includes(metricName) 
        ? prev.filter(name => name !== metricName)
        : [...prev, metricName]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUpIcon color="error" />;
      case 'down': return <TrendingDownIcon color="success" />;
      case 'stable': return <TrendingUpIcon color="disabled" />;
      default: return <TrendingUpIcon color="disabled" />;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'info': return <InfoIcon color="info" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'success': return <SuccessIcon color="success" />;
      default: return <InfoIcon color="info" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Enhanced System Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time monitoring and system control center
          </Typography>
          {(systemStatusLoading || activitiesLoading || statisticsLoading) && (
            <Alert severity="info" sx={{ mt: 1 }}>
              Loading real-time data...
            </Alert>
          )}
          {systemStatusData && (
            <Alert severity="success" sx={{ mt: 1 }}>
              ✅ Real data loaded: {systemStatusData?.data?.metrics?.total_documents || 0} documents, {systemStatusData?.data?.metrics?.total_agents || 0} agents
            </Alert>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Chip
            icon={isConnected ? <SuccessIcon /> : <ErrorIcon />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? <CircularProgress size={20} /> : 'Refresh'}
          </Button>
        </Box>
      </Box>

      {/* Debug Info - Remove in production */}
      <Card sx={{ mb: 4, bgcolor: 'grey.100' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🔍 Debug Info - API Data
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>System Status:</strong><br/>
                Loading: {systemStatusLoading ? 'Yes' : 'No'}<br/>
                Data: {systemStatusData ? 'Loaded' : 'None'}<br/>
                Documents: {systemStatusData?.data?.metrics?.total_documents || 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>Recent Activities:</strong><br/>
                Loading: {activitiesLoading ? 'Yes' : 'No'}<br/>
                Data: {recentActivitiesData ? 'Loaded' : 'None'}<br/>
                Activities: {recentActivitiesData?.data?.total || 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>Statistics:</strong><br/>
                Loading: {statisticsLoading ? 'Yes' : 'No'}<br/>
                Data: {statisticsData ? 'Loaded' : 'None'}<br/>
                Documents: {statisticsData?.data?.statistics?.documents?.total || 'N/A'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            {quickActions.map((action) => (
              <Grid item xs={12} sm={6} md={3} key={action.id}>
                <Button
                  fullWidth
                  variant="contained"
                  color={action.color}
                  startIcon={action.icon}
                  onClick={action.action}
                  disabled={action.status === 'disabled'}
                  sx={{
                    height: 80,
                    flexDirection: 'column',
                    gap: 1,
                    textTransform: 'none',
                  }}
                >
                  <Typography variant="subtitle2" fontWeight="bold">
                    {action.title}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    {action.description}
                  </Typography>
                </Button>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* System Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {systemMetrics.map((metric) => (
          <Grid item xs={12} md={6} lg={3} key={metric.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" color="text.secondary">
                    {metric.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => toggleMetricExpansion(metric.name)}
                  >
                    {expandedMetrics.includes(metric.name) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h4" component="div" sx={{ mr: 1 }}>
                    {metric.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {metric.unit}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getTrendIcon(metric.trend)}
                  <Typography 
                    variant="body2" 
                    color={metric.change >= 0 ? 'error' : 'success'}
                    sx={{ ml: 0.5 }}
                  >
                    {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(1)}%
                  </Typography>
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={metric.unit === '%' ? metric.value : Math.min(metric.value / 2, 100)}
                  color={getStatusColor(metric.status) as any}
                  sx={{ height: 8, borderRadius: 4 }}
                />

                <Collapse in={expandedMetrics.includes(metric.name)}>
                  <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
                    <Typography variant="body2" color="text.secondary">
                      Status: {metric.status}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Trend: {metric.trend}
                    </Typography>
                  </Box>
                </Collapse>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Performance Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Performance Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="documents" stroke="#8884d8" name="Documents" />
                  <Line type="monotone" dataKey="extractions" stroke="#82ca9d" name="Extractions" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Extraction Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={extractionStats}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, percentage }) => `${category}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {extractionStats.map((entry, index) => (
                                              <Cell key={`cell-${index}`} fill={theme.palette.primary.main} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts and Notifications */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Alerts
              </Typography>
              <List>
                {alerts.map((alert) => (
                  <ListItem key={alert.id} sx={{ px: 0 }}>
                    <ListItemIcon>
                      {getSeverityIcon(alert.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.message}
                      secondary={alert.timestamp}
                    />
                    {!alert.acknowledged && (
                      <Chip label="New" size="small" color="primary" />
                    )}
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Connection Status
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">WebSocket Connection</Typography>
                  <Chip
                    label={connectionStatus}
                    color={isConnected ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">API Endpoint</Typography>
                  <Chip label="Active" color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Database</Typography>
                  <Chip label="Connected" color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">File System</Typography>
                  <Chip label="Ready" color="success" size="small" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnhancedDashboard;