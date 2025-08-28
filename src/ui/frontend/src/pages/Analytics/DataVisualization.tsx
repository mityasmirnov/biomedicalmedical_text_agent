import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  CircularProgress
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  Download,
  Refresh,
  FilterList,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { api } from '../../services/api';

interface AnalyticsData {
  extraction_stats: {
    total_extractions: number;
    successful_extractions: number;
    failed_extractions: number;
    average_confidence: number;
    total_documents: number;
  };
  agent_performance: {
    agent_id: string;
    agent_name: string;
    total_requests: number;
    success_rate: number;
    average_response_time: number;
    error_rate: number;
  }[];
  extraction_timeline: {
    date: string;
    extractions: number;
    documents: number;
    confidence: number;
  }[];
  concept_distribution: {
    concept: string;
    count: number;
    percentage: number;
  }[];
  document_types: {
    type: string;
    count: number;
    percentage: number;
  }[];
  validation_stats: {
    total_validated: number;
    approved: number;
    rejected: number;
    pending: number;
    average_validation_time: number;
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const DataVisualization: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const response = await api.analytics.getVisualizations({ time_range: timeRange });
      setAnalyticsData(response.data);
      setError(null);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      setError('Failed to load analytics data - using mock data');
      // Set mock data for development
      setAnalyticsData({
        extraction_stats: {
          total_extractions: 1250,
          successful_extractions: 1180,
          failed_extractions: 70,
          average_confidence: 0.87,
          total_documents: 450
        },
        agent_performance: [
          {
            agent_id: 'extraction-agent',
            agent_name: 'Extraction Agent',
            total_requests: 850,
            success_rate: 0.94,
            average_response_time: 2.3,
            error_rate: 0.06
          },
          {
            agent_id: 'validation-agent',
            agent_name: 'Validation Agent',
            total_requests: 400,
            success_rate: 0.98,
            average_response_time: 1.8,
            error_rate: 0.02
          }
        ],
        extraction_timeline: [
          { date: '2024-01-01', extractions: 45, documents: 12, confidence: 0.85 },
          { date: '2024-01-02', extractions: 52, documents: 15, confidence: 0.87 },
          { date: '2024-01-03', extractions: 38, documents: 10, confidence: 0.89 },
          { date: '2024-01-04', extractions: 61, documents: 18, confidence: 0.86 },
          { date: '2024-01-05', extractions: 48, documents: 14, confidence: 0.88 },
          { date: '2024-01-06', extractions: 55, documents: 16, confidence: 0.90 },
          { date: '2024-01-07', extractions: 42, documents: 11, confidence: 0.87 }
        ],
        concept_distribution: [
          { concept: 'Patient Demographics', count: 450, percentage: 36 },
          { concept: 'Clinical Symptoms', count: 380, percentage: 30.4 },
          { concept: 'Laboratory Findings', count: 220, percentage: 17.6 },
          { concept: 'Genetic Variants', count: 150, percentage: 12 },
          { concept: 'Treatment Information', count: 50, percentage: 4 }
        ],
        document_types: [
          { type: 'Case Reports', count: 280, percentage: 62.2 },
          { type: 'Research Papers', count: 120, percentage: 26.7 },
          { type: 'Clinical Trials', count: 35, percentage: 7.8 },
          { type: 'Review Articles', count: 15, percentage: 3.3 }
        ],
        validation_stats: {
          total_validated: 850,
          approved: 780,
          rejected: 45,
          pending: 25,
          average_validation_time: 3.2
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.9) return 'success';
    if (rate >= 0.7) return 'warning';
    return 'error';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;
  const formatNumber = (value: number) => value.toLocaleString();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!analyticsData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">No analytics data available</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Data Analytics & Visualization
        </Typography>
        
        <Box display="flex" gap={2}>
          <FormControl size="small">
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="1d">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
              <MenuItem value="1y">Last Year</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            startIcon={<Refresh />}
            onClick={loadAnalyticsData}
            variant="outlined"
          >
            Refresh
          </Button>
          
          <Button
            startIcon={<Download />}
            variant="contained"
          >
            Export Report
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Extractions
              </Typography>
              <Typography variant="h4">
                {formatNumber(analyticsData.extraction_stats.total_extractions)}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  +12% from last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h4">
                {formatPercentage(analyticsData.extraction_stats.successful_extractions / analyticsData.extraction_stats.total_extractions)}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  +2.1% from last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Confidence
              </Typography>
              <Typography variant="h4">
                {formatPercentage(analyticsData.extraction_stats.average_confidence)}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  +1.5% from last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Documents Processed
              </Typography>
              <Typography variant="h4">
                {formatNumber(analyticsData.extraction_stats.total_documents)}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  +8% from last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Validation Rate
              </Typography>
              <Typography variant="h4">
                {formatPercentage(analyticsData.validation_stats.approved / analyticsData.validation_stats.total_validated)}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  +3.2% from last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Extraction Timeline" />
          <Tab label="Agent Performance" />
          <Tab label="Concept Distribution" />
          <Tab label="Document Types" />
          <Tab label="Validation Stats" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Extraction Timeline
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={analyticsData.extraction_timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="extractions"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                      name="Extractions"
                    />
                    <Area
                      type="monotone"
                      dataKey="documents"
                      stackId="2"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      name="Documents"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Confidence Trend
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={analyticsData.extraction_timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="confidence"
                      stroke="#ff7300"
                      strokeWidth={2}
                      dot={{ fill: '#ff7300', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {selectedTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Agent Performance Metrics
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Agent</TableCell>
                    <TableCell align="right">Total Requests</TableCell>
                    <TableCell align="right">Success Rate</TableCell>
                    <TableCell align="right">Avg Response Time (s)</TableCell>
                    <TableCell align="right">Error Rate</TableCell>
                    <TableCell align="right">Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analyticsData.agent_performance.map((agent) => (
                    <TableRow key={agent.agent_id}>
                      <TableCell>
                        <Typography variant="subtitle2">{agent.agent_name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {agent.agent_id}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {formatNumber(agent.total_requests)}
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={formatPercentage(agent.success_rate)}
                          color={getSuccessRateColor(agent.success_rate)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        {agent.average_response_time.toFixed(1)}s
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={formatPercentage(agent.error_rate)}
                          color={getSuccessRateColor(1 - agent.error_rate)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" gap={1}>
                          <LinearProgress
                            variant="determinate"
                            value={agent.success_rate * 100}
                            sx={{ width: 60, height: 8 }}
                            color={getSuccessRateColor(agent.success_rate)}
                          />
                          <Typography variant="caption">
                            {formatPercentage(agent.success_rate)}
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {selectedTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Concept Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={analyticsData.concept_distribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ concept, percentage }) => `${concept}: ${percentage}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {analyticsData.concept_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Concept Counts
                </Typography>
                <Box>
                  {analyticsData.concept_distribution.map((concept, index) => (
                    <Box key={concept.concept} display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Box
                          width={16}
                          height={16}
                          borderRadius="50%"
                          bgcolor={COLORS[index % COLORS.length]}
                        />
                        <Typography variant="body2">{concept.concept}</Typography>
                      </Box>
                      <Box textAlign="right">
                        <Typography variant="subtitle2">{formatNumber(concept.count)}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {concept.percentage}%
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {selectedTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Types
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analyticsData.document_types}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Type Breakdown
                </Typography>
                <Box>
                  {analyticsData.document_types.map((docType, index) => (
                    <Box key={docType.type} mb={2}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">{docType.type}</Typography>
                        <Typography variant="body2">
                          {docType.count} ({docType.percentage}%)
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={docType.percentage}
                        sx={{ height: 8, borderRadius: 4 }}
                        color="primary"
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {selectedTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Validation Status
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Approved', value: analyticsData.validation_stats.approved, color: '#4caf50' },
                        { name: 'Rejected', value: analyticsData.validation_stats.rejected, color: '#f44336' },
                        { name: 'Pending', value: analyticsData.validation_stats.pending, color: '#ff9800' }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percentage }) => `${name}: ${value}`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: 'Approved', value: analyticsData.validation_stats.approved, color: '#4caf50' },
                        { name: 'Rejected', value: analyticsData.validation_stats.rejected, color: '#f44336' },
                        { name: 'Pending', value: analyticsData.validation_stats.pending, color: '#ff9800' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Validation Metrics
                </Typography>
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="body2">Total Validated</Typography>
                    <Typography variant="h6">{formatNumber(analyticsData.validation_stats.total_validated)}</Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="body2">Approval Rate</Typography>
                    <Typography variant="h6" color="success.main">
                      {formatPercentage(analyticsData.validation_stats.approved / analyticsData.validation_stats.total_validated)}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="body2">Rejection Rate</Typography>
                    <Typography variant="h6" color="error.main">
                      {formatPercentage(analyticsData.validation_stats.rejected / analyticsData.validation_stats.total_validated)}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="body2">Pending</Typography>
                    <Typography variant="h6" color="warning.main">
                      {formatNumber(analyticsData.validation_stats.pending)}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">Avg Validation Time</Typography>
                    <Typography variant="h6">
                      {analyticsData.validation_stats.average_validation_time.toFixed(1)}s
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default DataVisualization;
