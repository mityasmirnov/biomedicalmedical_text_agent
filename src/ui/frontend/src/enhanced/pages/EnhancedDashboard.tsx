import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import {
  Refresh,
  Upload,
  Visibility,
  Edit,
  Stop,
  Assessment,
  Search
} from '@mui/icons-material';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

interface SystemStatus {
  status: 'healthy' | 'warning' | 'error';
  uptime: number;
  processing_queue: number;
  active_extractions: number;
  database_size: number;
  api_usage: {
    openrouter: number;
    huggingface: number;
    total_requests: number;
  };
  last_updated: string;
}

interface ProcessingJob {
  id: string;
  type: 'metadata_search' | 'document_extraction' | 'validation';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  estimated_completion?: string;
  details: any;
}

interface ExtractionResult {
  id: string;
  document_id: string;
  title: string;
  extraction_type: string;
  confidence_score: number;
  validation_status: 'pending' | 'validated' | 'rejected';
  created_at: string;
  patient_count: number;
}

const EnhancedDashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [processingQueue, setProcessingQueue] = useState<ProcessingJob[]>([]);
  const [recentResults, setRecentResults] = useState<ExtractionResult[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [metadataSearchOpen, setMetadataSearchOpen] = useState(false);
  const [documentUploadOpen, setDocumentUploadOpen] = useState(false);
  

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('google/gemma-2-27b-it:free');
  const [maxResults, setMaxResults] = useState(100);

  const { isConnected, lastMessage } = useWebSocket();
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (!lastMessage) return;
    try {
      const message: any = lastMessage;
      switch (message.type) {
        case 'system_status_update':
          handleSystemStatusUpdate(message.data);
          break;
        case 'processing_update':
          if (message.data) {
            handleProcessingUpdate(message.data);
          }
          break;
        case 'extraction_complete':
          if (message.data) {
            handleExtractionComplete(message.data);
          }
          break;
        default:
          break;
      }
    } catch (e) {
      // ignore
    }
  }, [lastMessage]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statusRes, queueRes, resultsRes] = await Promise.all([
        api.dashboard.getSystemStatus(),
        api.dashboard.getProcessingQueue(),
        api.dashboard.getRecentResults()
      ]);

      // Normalize potentially wrapped payloads to arrays
      const statusPayload = (statusRes as any)?.data ?? statusRes;
      const queuePayload = (queueRes as any)?.data ?? queueRes;
      const resultsPayload = (resultsRes as any)?.data ?? resultsRes;

      setSystemStatus(statusPayload);
      setProcessingQueue(
        Array.isArray(queuePayload)
          ? queuePayload
          : (queuePayload?.queue || queuePayload?.activities || [])
      );
      setRecentResults(
        Array.isArray(resultsPayload)
          ? resultsPayload
          : (resultsPayload?.results || resultsPayload?.data || [])
      );
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSystemStatusUpdate = (status: SystemStatus) => {
    setSystemStatus(status);
  };

  const handleProcessingUpdate = (job: ProcessingJob) => {
    setProcessingQueue(prev => {
      const index = prev.findIndex(j => j.id === job.id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = job;
        return updated;
      } else {
        return [job, ...prev];
      }
    });
  };

  const handleExtractionComplete = (result: ExtractionResult) => {
    setRecentResults(prev => [result, ...prev.slice(0, 9)]);
  };

  const handleMetadataSearch = async () => {
    try {
      if (!searchQuery.trim()) return;
      const res = await api.metadataTriage.search(searchQuery.trim());
      const raw = (res as any)?.data?.results || [];
      const normalized = raw.map((doc: any) => {
        const authorsField = Array.isArray(doc?.authors)
          ? doc.authors
              .map((a: any) => (typeof a === 'string' ? a : (a?.name || [a?.ForeName, a?.LastName].filter(Boolean).join(' '))))
              .filter(Boolean)
              .join(', ')
          : (doc?.authors || '');
        const year = doc?.year || doc?.publication_year;
        const pubDate = doc?.publication_date || doc?.pub_date || (year ? `${year}-01-01` : '');
        return {
          pmid: doc?.pmid || doc?.id || '',
          title: doc?.title || doc?.article_title || doc?.document_title || 'Untitled',
          abstract: doc?.abstract || doc?.summary || '',
          journal: doc?.journal || doc?.journal_title || '',
          publication_date: pubDate,
          authors: authorsField,
          relevance_score: typeof doc?.relevance_score === 'number' ? doc.relevance_score : 0,
          fulltext_available: Boolean(doc?.pmc_link || doc?.full_text_available),
          source: doc?.source || 'pubmed',
        };
      });
      setMetadataSearchOpen(false);
      navigate('/knowledge-base/metadata', { state: { searchResults: normalized, searchQuery } });
    } catch (err) {
      console.error('Metadata search failed:', err);
      setError('Failed to start metadata search');
    }
  };

  const handleDocumentUpload = async (files: FileList) => {
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await api.documents.upload(formData);
      setDocumentUploadOpen(false);
      response.data.jobs.forEach((job: ProcessingJob) => {
        handleProcessingUpdate(job);
      });
    } catch (err) {
      setError('Failed to upload documents');
    }
  };

  const handleValidateExtraction = async (extractionId: string) => {
    try {
      window.open(`#/validation/${extractionId}`, '_blank');
    } catch (err) {
      setError('Failed to open validation interface');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Biomedical Text Agent Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDashboardData}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                System Status
              </Typography>
              <Box display="flex" alignItems="center">
                <Chip
                  label={systemStatus?.status || 'Unknown'}
                  color={getStatusColor(systemStatus?.status || 'default')}
                  size="small"
                />
                <Typography variant="body2" sx={{ ml: 1 }}>
                  {isConnected ? 'Connected' : 'Disconnected'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Processing Queue
              </Typography>
              <Typography variant="h5">
                {systemStatus?.processing_queue || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {systemStatus?.active_extractions || 0} active extractions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Database Size
              </Typography>
              <Typography variant="h5">
                {systemStatus?.database_size || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                records stored
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                API Usage
              </Typography>
              <Typography variant="h5">
                {systemStatus?.api_usage?.total_requests || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                total requests
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={() => setMetadataSearchOpen(true)}
            >
              Search Literature
            </Button>
            <Button
              variant="contained"
              startIcon={<Upload />}
              onClick={() => setDocumentUploadOpen(true)}
            >
              Upload Documents
            </Button>
            <Button
              variant="outlined"
              startIcon={<Assessment />}
              href="#/analytics"
            >
              View Analytics
            </Button>
            <Button
              variant="outlined"
              startIcon={<Visibility />}
              href="#/validation"
            >
              Validation Queue
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Processing Queue" />
          <Tab label="Recent Results" />
          <Tab label="System Monitoring" />
        </Tabs>

        {selectedTab === 0 && (
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Job ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {processingQueue.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.id}</TableCell>
                      <TableCell>{job.type}</TableCell>
                      <TableCell>
                        <Chip
                          label={job.status}
                          color={getJobStatusColor(job.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={job.progress}
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">
                            {job.progress}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {new Date(job.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                        {job.status === 'running' && (
                          <IconButton size="small" color="error">
                            <Stop />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        )}

        {selectedTab === 1 && (
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Document</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Patients</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Validation</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentResults.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {result.title}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {result.document_id}
                        </Typography>
                      </TableCell>
                      <TableCell>{result.extraction_type}</TableCell>
                      <TableCell>{result.patient_count}</TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={result.confidence_score * 100}
                          sx={{ width: 80 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.validation_status}
                          color={result.validation_status === 'validated' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(result.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleValidateExtraction(result.id)}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton size="small" href={`#/results/${result.id}`}>
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        )}

        {selectedTab === 2 && (
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  API Usage
                </Typography>
                <Box>
                  <Typography variant="body2">
                    OpenRouter: {systemStatus?.api_usage?.openrouter || 0} requests
                  </Typography>
                  <Typography variant="body2">
                    HuggingFace: {systemStatus?.api_usage?.huggingface || 0} requests
                  </Typography>
                  <Typography variant="body2">
                    Total: {systemStatus?.api_usage?.total_requests || 0} requests
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  System Health
                </Typography>
                <Box>
                  <Typography variant="body2">
                    Uptime: {systemStatus?.uptime || 0} seconds
                  </Typography>
                  <Typography variant="body2">
                    Last Updated: {systemStatus?.last_updated || 'Never'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        )}
      </Card>

      <Dialog open={metadataSearchOpen} onClose={() => setMetadataSearchOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Search Literature</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Search Query"
            fullWidth
            variant="outlined"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g., Leigh syndrome case report"
            sx={{ mb: 2 }}
          />
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Model</InputLabel>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  label="Model"
                >
                  <MenuItem value="google/gemma-2-27b-it:free">Gemma 2 27B (Free)</MenuItem>
                  <MenuItem value="microsoft/phi-3-mini-128k-instruct:free">Phi-3 Mini (Free)</MenuItem>
                  <MenuItem value="meta-llama/llama-3.1-8b-instruct:free">Llama 3.1 8B (Free)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="Max Results"
                type="number"
                fullWidth
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                inputProps={{ min: 1, max: 1000 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMetadataSearchOpen(false)}>Cancel</Button>
          <Button onClick={handleMetadataSearch} variant="contained" disabled={!searchQuery}>
            Start Search
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={documentUploadOpen} onClose={() => setDocumentUploadOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Box
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': { borderColor: 'primary.main' }
            }}
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            <Upload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Drop files here or click to upload
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: PDF, DOCX, TXT
            </Typography>
            <input
              id="file-upload"
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && handleDocumentUpload(e.target.files)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDocumentUploadOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedDashboard;



