import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  useTheme,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  Switch,
  FormControlLabel,
  Slider,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Timeline as TimelineIcon,
  ShowChart as ShowChartIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Settings as SettingsIcon,
  Visibility as ViewIcon,
  VisibilityOff as HideIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
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
  ScatterChart,
  Scatter,
  ComposedChart,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Treemap,
  Tooltip as TreemapTooltip,
} from 'recharts';

interface DataMetric {
  name: string;
  value: number;
  unit: string;
  change: number;
  trend: 'up' | 'down' | 'stable';
  status: 'normal' | 'warning' | 'critical';
}

interface ChartData {
  time: string;
  value: number;
  category?: string;
  subcategory?: string;
}

interface PerformanceMetric {
  category: string;
  value: number;
  target: number;
  status: 'excellent' | 'good' | 'fair' | 'poor';
}

const DataVisualization: React.FC = () => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['extractions', 'accuracy', 'processing_time']);
  const [chartType, setChartType] = useState('line');
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedMetrics, setShowAdvancedMetrics] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30);

  // Sample data
  const [extractionData] = useState<ChartData[]>([
    { time: '00:00', value: 45, category: 'phenotypes' },
    { time: '04:00', value: 52, category: 'phenotypes' },
    { time: '08:00', value: 78, category: 'phenotypes' },
    { time: '12:00', value: 85, category: 'phenotypes' },
    { time: '16:00', value: 72, category: 'phenotypes' },
    { time: '20:00', value: 58, category: 'phenotypes' },
    { time: '24:00', value: 45, category: 'phenotypes' },
  ]);

  const [accuracyData] = useState<ChartData[]>([
    { time: '00:00', value: 94.2, category: 'overall' },
    { time: '04:00', value: 93.8, category: 'overall' },
    { time: '08:00', value: 95.1, category: 'overall' },
    { time: '12:00', value: 96.3, category: 'overall' },
    { time: '16:00', value: 95.7, category: 'overall' },
    { time: '20:00', value: 94.9, category: 'overall' },
    { time: '24:00', value: 94.2, category: 'overall' },
  ]);

  const [processingTimeData] = useState<ChartData[]>([
    { time: '00:00', value: 2.3, category: 'average' },
    { time: '04:00', value: 2.1, category: 'average' },
    { time: '08:00', value: 3.2, category: 'average' },
    { time: '12:00', value: 3.8, category: 'average' },
    { time: '16:00', value: 3.1, category: 'average' },
    { time: '20:00', value: 2.7, category: 'average' },
    { time: '24:00', value: 2.3, category: 'average' },
  ]);

  const [categoryDistribution] = useState([
    { name: 'Phenotypes', value: 1250, fill: theme.palette.primary.main },
    { name: 'Genes', value: 890, fill: theme.palette.secondary.main },
    { name: 'Treatments', value: 720, fill: theme.palette.success.main },
    { name: 'Demographics', value: 450, fill: theme.palette.warning.main },
    { name: 'Other', value: 290, fill: theme.palette.error.main },
  ]);

  const [performanceMetrics] = useState<PerformanceMetric[]>([
    { category: 'Extraction Accuracy', value: 94.2, target: 95, status: 'good' },
    { category: 'Processing Speed', value: 2.8, target: 2.5, status: 'fair' },
    { category: 'Data Completeness', value: 87.5, target: 90, status: 'fair' },
    { category: 'System Uptime', value: 99.8, target: 99.9, status: 'excellent' },
    { category: 'Error Rate', value: 2.1, target: 1.5, status: 'poor' },
  ]);

  const [systemMetrics] = useState<DataMetric[]>([
    {
      name: 'CPU Usage',
      value: 45.2,
      unit: '%',
      change: 2.1,
      trend: 'up',
      status: 'normal',
    },
    {
      name: 'Memory Usage',
      value: 78.5,
      unit: '%',
      change: 5.3,
      trend: 'up',
      status: 'warning',
    },
    {
      name: 'Disk Usage',
      value: 62.1,
      unit: '%',
      change: 1.2,
      trend: 'stable',
      status: 'normal',
    },
    {
      name: 'Network I/O',
      value: 125.7,
      unit: 'MB/s',
      change: -8.4,
      trend: 'down',
      status: 'normal',
    },
  ]);

  const handleRefresh = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handleMetricToggle = (metric: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metric) 
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
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

  const getPerformanceColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'success';
      case 'good': return 'primary';
      case 'fair': return 'warning';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const renderChart = () => {
    const data = selectedMetrics.includes('extractions') ? extractionData : 
                 selectedMetrics.includes('accuracy') ? accuracyData : 
                 selectedMetrics.includes('processing_time') ? processingTimeData : extractionData;

    switch (chartType) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            {selectedMetrics.includes('extractions') && (
              <Line type="monotone" dataKey="value" stroke="#8884d8" name="Extractions" />
            )}
            {selectedMetrics.includes('accuracy') && (
              <Line type="monotone" dataKey="value" stroke="#82ca9d" name="Accuracy %" />
            )}
            {selectedMetrics.includes('processing_time') && (
              <Line type="monotone" dataKey="value" stroke="#ffc658" name="Processing Time (s)" />
            )}
          </LineChart>
        );
      case 'area':
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            {selectedMetrics.includes('extractions') && (
              <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" name="Extractions" />
            )}
            {selectedMetrics.includes('accuracy') && (
              <Area type="monotone" dataKey="value" stroke="#82ca9d" fill="#82ca9d" name="Accuracy %" />
            )}
            {selectedMetrics.includes('processing_time') && (
              <Area type="monotone" dataKey="value" stroke="#ffc658" fill="#ffc658" name="Processing Time (s)" />
            )}
          </AreaChart>
        );
      case 'bar':
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            {selectedMetrics.includes('extractions') && (
              <Bar dataKey="value" fill="#8884d8" name="Extractions" />
            )}
            {selectedMetrics.includes('accuracy') && (
              <Bar dataKey="value" fill="#82ca9d" name="Accuracy %" />
            )}
            {selectedMetrics.includes('processing_time') && (
              <Bar dataKey="value" fill="#ffc658" name="Processing Time (s)" />
            )}
          </BarChart>
        );
      default:
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#8884d8" name="Value" />
          </LineChart>
        );
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Advanced Analytics Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive data visualization and performance analytics
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="1h">Last Hour</MenuItem>
              <MenuItem value="6h">Last 6 Hours</MenuItem>
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={20} /> : 'Refresh'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {systemMetrics.map((metric) => (
          <Grid item xs={12} sm={6} md={3} key={metric.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" color="text.secondary">
                    {metric.name}
                  </Typography>
                  {getTrendIcon(metric.trend)}
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
                  <Typography 
                    variant="body2" 
                    color={metric.change >= 0 ? 'error' : 'success'}
                    sx={{ mr: 1 }}
                  >
                    {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    from last period
                  </Typography>
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={metric.unit === '%' ? metric.value : Math.min(metric.value / 2, 100)}
                  color={getStatusColor(metric.status) as any}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Chart Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" gutterBottom>
                Chart Type
              </Typography>
              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(e, newValue) => newValue && setChartType(newValue)}
                size="small"
              >
                <ToggleButton value="line">
                  <ShowChartIcon />
                </ToggleButton>
                <ToggleButton value="area">
                  <TimelineIcon />
                </ToggleButton>
                <ToggleButton value="bar">
                  <BarChartIcon />
                </ToggleButton>
              </ToggleButtonGroup>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Metrics to Display
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {['extractions', 'accuracy', 'processing_time'].map((metric) => (
                  <Chip
                    key={metric}
                    label={metric.replace('_', ' ')}
                    onClick={() => handleMetricToggle(metric)}
                    color={selectedMetrics.includes(metric) ? 'primary' : 'default'}
                    variant={selectedMetrics.includes(metric) ? 'filled' : 'outlined'}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showAdvancedMetrics}
                    onChange={(e) => setShowAdvancedMetrics(e.target.checked)}
                  />
                }
                label="Advanced Metrics"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Performance Trends
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            {renderChart()}
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics vs Targets
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {performanceMetrics.map((metric) => (
                  <Box key={metric.category}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">{metric.category}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="medium">
                          {metric.value}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          / {metric.target}
                        </Typography>
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((metric.value / metric.target) * 100, 100)}
                      sx={{ height: 8, borderRadius: 4 }}
                      color={getPerformanceColor(metric.status) as any}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {metric.value >= metric.target ? 'Target met' : `${((metric.target - metric.value) / metric.target * 100).toFixed(1)}% below target`}
                      </Typography>
                      <Chip
                        label={metric.status}
                        size="small"
                        color={getPerformanceColor(metric.status) as any}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Advanced Metrics */}
      {showAdvancedMetrics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Health Overview
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={[
                    { metric: 'CPU', value: 45, fullMark: 100 },
                    { metric: 'Memory', value: 78, fullMark: 100 },
                    { metric: 'Disk', value: 62, fullMark: 100 },
                    { metric: 'Network', value: 85, fullMark: 100 },
                    { metric: 'Response Time', value: 92, fullMark: 100 },
                  ]}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="System Health" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    <RechartsTooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Queue Status
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={[
                    { time: '00:00', queue: 45, processing: 12, completed: 33 },
                    { time: '04:00', queue: 52, processing: 15, completed: 37 },
                    { time: '08:00', queue: 78, processing: 25, completed: 53 },
                    { time: '12:00', queue: 85, processing: 30, completed: 55 },
                    { time: '16:00', queue: 72, processing: 22, completed: 50 },
                    { time: '20:00', queue: 58, processing: 18, completed: 40 },
                    { time: '24:00', queue: 45, processing: 12, completed: 33 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Area type="monotone" dataKey="queue" fill="#8884d8" stroke="#8884d8" name="Queue" />
                    <Bar dataKey="processing" fill="#82ca9d" name="Processing" />
                    <Line type="monotone" dataKey="completed" stroke="#ffc658" name="Completed" />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Data Quality Metrics */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Quality Metrics
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main" gutterBottom>
                  94.2%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overall Accuracy
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary.main" gutterBottom>
                  87.5%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Data Completeness
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main" gutterBottom>
                  2.1%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Error Rate
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main" gutterBottom>
                  99.8%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  System Uptime
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Settings Panel */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Dashboard Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Auto-refresh Interval
              </Typography>
              <Slider
                value={refreshInterval}
                onChange={(e, newValue) => setRefreshInterval(newValue as number)}
                min={5}
                max={300}
                step={5}
                marks={[
                  { value: 5, label: '5s' },
                  { value: 30, label: '30s' },
                  { value: 60, label: '1m' },
                  { value: 300, label: '5m' },
                ]}
                valueLabelDisplay="auto"
              />
              <Typography variant="caption" color="text.secondary">
                Refresh every {refreshInterval} seconds
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Chart Preferences
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Show Grid Lines"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Show Legends"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Animate Charts"
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Export Options
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button variant="outlined" size="small" startIcon={<DownloadIcon />}>
                  Export as PNG
                </Button>
                <Button variant="outlined" size="small" startIcon={<DownloadIcon />}>
                  Export as PDF
                </Button>
                <Button variant="outlined" size="small" startIcon={<DownloadIcon />}>
                  Export Data (CSV)
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataVisualization;