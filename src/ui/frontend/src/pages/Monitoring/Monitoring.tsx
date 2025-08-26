import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  BugReport as BugIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';

const Monitoring: React.FC = () => {
  const [isSettingsDialogOpen, setIsSettingsDialogOpen] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 25.5,
    memory: 68.2,
    disk: 45.7,
    network: 12.3,
    temperature: 42.1,
  });

  // Simulate real-time updates
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.max(0, Math.min(100, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(0, Math.min(100, prev.memory + (Math.random() - 0.5) * 5)),
        disk: Math.max(0, Math.min(100, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.max(0, Math.min(100, prev.network + (Math.random() - 0.5) * 8)),
        temperature: Math.max(30, Math.min(80, prev.temperature + (Math.random() - 0.5) * 3)),
      }));
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const systemAlerts = [
    {
      id: 1,
      type: 'warning',
      title: 'High Memory Usage',
      message: 'System memory usage is at 68.2% - consider optimization',
      timestamp: '2 minutes ago',
      severity: 'medium',
    },
    {
      id: 2,
      type: 'info',
      title: 'Backup Completed',
      message: 'Daily database backup completed successfully',
      timestamp: '1 hour ago',
      severity: 'low',
    },
    {
      id: 3,
      type: 'success',
      title: 'System Optimization',
      message: 'AI model cache optimization completed',
      timestamp: '3 hours ago',
      severity: 'low',
    },
  ];

  const performanceMetrics = [
    {
      name: 'Document Processing',
      current: 45,
      target: 50,
      unit: 'docs/hour',
      trend: 'up',
      status: 'good',
    },
    {
      name: 'API Response Time',
      current: 245,
      target: 200,
      unit: 'ms',
      trend: 'down',
      status: 'warning',
    },
    {
      name: 'Extraction Accuracy',
      current: 94.2,
      target: 95.0,
      unit: '%',
      trend: 'up',
      status: 'good',
    },
    {
      name: 'System Uptime',
      current: 99.87,
      target: 99.9,
      unit: '%',
      trend: 'stable',
      status: 'good',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'info';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'success': return <SuccessIcon />;
      case 'warning': return <WarningIcon />;
      case 'error': return <ErrorIcon />;
      case 'info': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'info': return 'info';
      default: return 'info';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUpIcon color="success" />;
      case 'down': return <TrendingUpIcon color="error" sx={{ transform: 'rotate(180deg)' }} />;
      case 'stable': return <TimelineIcon color="info" />;
      default: return <TimelineIcon color="info" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          System Monitoring
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time system performance monitoring and health status
        </Typography>
      </Box>

      {/* System Health Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">CPU Usage</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemMetrics.cpu.toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.cpu} 
                sx={{ mt: 1 }}
                color={systemMetrics.cpu > 80 ? 'error' : systemMetrics.cpu > 60 ? 'warning' : 'success'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {systemMetrics.cpu > 80 ? 'High load' : systemMetrics.cpu > 60 ? 'Moderate load' : 'Normal load'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MemoryIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Memory Usage</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemMetrics.memory.toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.memory} 
                sx={{ mt: 1 }}
                color={systemMetrics.memory > 85 ? 'error' : systemMetrics.memory > 70 ? 'warning' : 'success'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {systemMetrics.memory > 85 ? 'Critical' : systemMetrics.memory > 70 ? 'High' : 'Normal'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Disk Usage</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemMetrics.disk.toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.disk} 
                sx={{ mt: 1 }}
                color={systemMetrics.disk > 90 ? 'error' : systemMetrics.disk > 80 ? 'warning' : 'success'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {systemMetrics.disk > 90 ? 'Critical' : systemMetrics.disk > 80 ? 'High' : 'Normal'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NetworkIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Network</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemMetrics.network.toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.network} 
                sx={{ mt: 1 }}
                color={systemMetrics.network > 80 ? 'error' : systemMetrics.network > 60 ? 'warning' : 'success'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {systemMetrics.network > 80 ? 'High traffic' : systemMetrics.network > 60 ? 'Moderate' : 'Normal'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Performance Metrics</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    size="small"
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<SettingsIcon />}
                    size="small"
                    onClick={() => setIsSettingsDialogOpen(true)}
                  >
                    Settings
                  </Button>
                </Box>
              </Box>
              
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Metric</TableCell>
                      <TableCell>Current</TableCell>
                      <TableCell>Target</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Trend</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceMetrics.map((metric) => (
                      <TableRow key={metric.name} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {metric.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {metric.current} {metric.unit}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {metric.target} {metric.unit}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={metric.status}
                            color={getStatusColor(metric.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {getTrendIcon(metric.trend)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Controls
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                    />
                  }
                  label="Auto-refresh metrics"
                />
                <Typography variant="caption" color="text.secondary" display="block">
                  Updates every {refreshInterval} seconds
                </Typography>
              </Box>

              <Button
                fullWidth
                variant="contained"
                startIcon={<StartIcon />}
                sx={{ mb: 2 }}
              >
                Start All Services
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<PauseIcon />}
                sx={{ mb: 2 }}
              >
                Pause Monitoring
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<StopIcon />}
                sx={{ mb: 2 }}
              >
                Stop All Services
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AssessmentIcon />}
              >
                Generate Report
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Alerts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">System Alerts</Typography>
                <Chip label={`${systemAlerts.length} active`} color="primary" size="small" />
              </Box>
              
              {systemAlerts.map((alert) => (
                <Alert
                  key={alert.id}
                  severity={getAlertColor(alert.type) as any}
                  icon={getAlertIcon(alert.type)}
                  sx={{ mb: 2 }}
                  action={
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton size="small" color="inherit">
                        <NotificationsIcon />
                      </IconButton>
                      <IconButton size="small" color="inherit">
                        <BugIcon />
                      </IconButton>
                    </Box>
                  }
                >
                  <Box>
                    <Typography variant="subtitle2" fontWeight="medium">
                      {alert.title}
                    </Typography>
                    <Typography variant="body2">
                      {alert.message}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {alert.timestamp}
                    </Typography>
                  </Box>
                </Alert>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Status
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="AI Agents" 
                    secondary="All running normally" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Database" 
                    secondary="Connected and healthy" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="API Services" 
                    secondary="Responding normally" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Memory Cache" 
                    secondary="75% utilization" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SuccessIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Network" 
                    secondary="Stable connection" 
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Settings Dialog */}
      <Dialog open={isSettingsDialogOpen} onClose={() => setIsSettingsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Monitoring Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                  />
                }
                label="Enable auto-refresh"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Refresh Interval (seconds)</InputLabel>
                <Select
                  value={refreshInterval}
                  label="Refresh Interval (seconds)"
                  onChange={(e) => setRefreshInterval(e.target.value as number)}
                >
                  <MenuItem value={10}>10 seconds</MenuItem>
                  <MenuItem value={30}>30 seconds</MenuItem>
                  <MenuItem value={60}>1 minute</MenuItem>
                  <MenuItem value={300}>5 minutes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsSettingsDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsSettingsDialogOpen(false)}>
            Save Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Monitoring;
