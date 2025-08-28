"""
Enhanced UI Components

Complete functional UI components for the biomedical text agent
with real backend integration and interactive features.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# React TypeScript Component Templates
ENHANCED_DASHBOARD_TSX = '''
import React, { useState, useEffect, useCallback } from 'react';
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
  Paper,
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
  Download,
  Visibility,
  Edit,
  Delete,
  PlayArrow,
  Stop,
  Settings,
  Assessment,
  Search,
  FilterList
} from '@mui/icons-material';
import { useWebSocket } from '../contexts/WebSocketContext';
import { useAuth } from '../contexts/AuthContext';
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
  
  // Dialogs
  const [metadataSearchOpen, setMetadataSearchOpen] = useState(false);
  const [documentUploadOpen, setDocumentUploadOpen] = useState(false);
  const [configOpen, setConfigOpen] = useState(false);
  
  // Search and filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('google/gemma-2-27b-it:free');
  const [maxResults, setMaxResults] = useState(100);
  
  const { socket, isConnected } = useWebSocket();
  const { user } = useAuth();

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // WebSocket updates
  useEffect(() => {
    if (socket) {
      socket.on('system_status_update', handleSystemStatusUpdate);
      socket.on('processing_update', handleProcessingUpdate);
      socket.on('extraction_complete', handleExtractionComplete);
      
      return () => {
        socket.off('system_status_update');
        socket.off('processing_update');
        socket.off('extraction_complete');
      };
    }
  }, [socket]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statusRes, queueRes, resultsRes] = await Promise.all([
        api.dashboard.getSystemStatus(),
        api.dashboard.getProcessingQueue(),
        api.dashboard.getRecentResults()
      ]);
      
      setSystemStatus(statusRes.data);
      setProcessingQueue(queueRes.data);
      setRecentResults(resultsRes.data);
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
      const response = await api.metadata.search({
        query: searchQuery,
        max_results: maxResults,
        include_fulltext: true
      });
      
      // Close dialog and show success
      setMetadataSearchOpen(false);
      // Add to processing queue
      handleProcessingUpdate({
        id: response.data.job_id,
        type: 'metadata_search',
        status: 'running',
        progress: 0,
        created_at: new Date().toISOString(),
        details: { query: searchQuery, max_results: maxResults }
      });
    } catch (err) {
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
      // Add upload jobs to queue
      response.data.jobs.forEach((job: ProcessingJob) => {
        handleProcessingUpdate(job);
      });
    } catch (err) {
      setError('Failed to upload documents');
    }
  };

  const handleValidateExtraction = async (extractionId: string) => {
    try {
      // Open validation interface
      window.open(`/validation/${extractionId}`, '_blank');
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

      {/* Header */}
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
          <Button
            variant="contained"
            startIcon={<Settings />}
            onClick={() => setConfigOpen(true)}
          >
            Configure
          </Button>
        </Box>
      </Box>

      {/* System Status Cards */}
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

      {/* Quick Actions */}
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
              href="/analytics"
            >
              View Analytics
            </Button>
            <Button
              variant="outlined"
              startIcon={<Visibility />}
              href="/validation"
            >
              Validation Queue
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Card>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Processing Queue" />
          <Tab label="Recent Results" />
          <Tab label="System Monitoring" />
        </Tabs>

        {/* Processing Queue Tab */}
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

        {/* Recent Results Tab */}
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
                        <IconButton size="small" href={`/results/${result.id}`}>
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

        {/* System Monitoring Tab */}
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

      {/* Metadata Search Dialog */}
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

      {/* Document Upload Dialog */}
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
'''

VALIDATION_INTERFACE_TSX = '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Cancel,
  Edit,
  Save,
  Visibility,
  HighlightAlt,
  Assessment
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';

interface ExtractionSpan {
  start: number;
  end: number;
  text: string;
  extraction_type: string;
  field_name: string;
  confidence: number;
  normalized_value?: string;
}

interface ValidationData {
  extraction_id: string;
  original_text: string;
  highlighted_text: string;
  extractions: any[];
  spans: ExtractionSpan[];
  confidence_scores: Record<string, number>;
  validation_status: string;
  validator_notes?: string;
}

interface FieldCorrection {
  field_name: string;
  original_value: any;
  corrected_value: any;
  correction_type: 'value_change' | 'addition' | 'deletion';
}

const ValidationInterface: React.FC = () => {
  const { extractionId } = useParams<{ extractionId: string }>();
  const [validationData, setValidationData] = useState<ValidationData | null>(null);
  const [corrections, setCorrections] = useState<FieldCorrection[]>([]);
  const [validatorNotes, setValidatorNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<ExtractionSpan | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    if (extractionId) {
      loadValidationData();
    }
  }, [extractionId]);

  const loadValidationData = async () => {
    try {
      setLoading(true);
      const response = await api.validation.getExtractionData(extractionId);
      setValidationData(response.data);
      setValidatorNotes(response.data.validator_notes || '');
      setError(null);
    } catch (err) {
      setError('Failed to load validation data');
      console.error('Validation load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSpanClick = (span: ExtractionSpan) => {
    setSelectedSpan(span);
    setEditValue(span.normalized_value || span.text);
    setEditDialogOpen(true);
  };

  const handleFieldCorrection = () => {
    if (!selectedSpan) return;

    const correction: FieldCorrection = {
      field_name: selectedSpan.field_name,
      original_value: selectedSpan.normalized_value || selectedSpan.text,
      corrected_value: editValue,
      correction_type: editValue !== (selectedSpan.normalized_value || selectedSpan.text) 
        ? 'value_change' 
        : 'addition'
    };

    setCorrections(prev => {
      const existing = prev.findIndex(c => c.field_name === correction.field_name);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = correction;
        return updated;
      } else {
        return [...prev, correction];
      }
    });

    setEditDialogOpen(false);
    setSelectedSpan(null);
  };

  const handleValidationSubmit = async (status: 'validated' | 'rejected') => {
    try {
      setSaving(true);
      
      await api.validation.submitValidation(extractionId!, {
        validation_status: status,
        corrections: corrections.length > 0 ? corrections : undefined,
        validator_notes: validatorNotes || undefined
      });

      // Redirect or show success message
      alert(`Validation ${status} successfully!`);
      
    } catch (err) {
      setError(`Failed to submit validation: ${err}`);
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getExtractionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'demographics': '#FFE6E6',
      'genetics': '#E6F3FF',
      'phenotypes': '#E6FFE6',
      'treatments': '#FFF0E6',
      'outcomes': '#F0E6FF'
    };
    return colors[type] || '#F5F5F5';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Typography>Loading validation data...</Typography>
      </Box>
    );
  }

  if (!validationData) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load validation data for extraction {extractionId}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Validation Interface
        </Typography>
        <Box>
          <Chip
            label={validationData.validation_status}
            color={validationData.validation_status === 'validated' ? 'success' : 'default'}
            sx={{ mr: 2 }}
          />
          <Typography variant="body2" color="textSecondary">
            Extraction ID: {validationData.extraction_id}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Left Panel - Text with Highlighting */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Original Text with Extractions
              </Typography>
              
              {/* Text Display */}
              <Box
                sx={{
                  border: '1px solid #ddd',
                  borderRadius: 1,
                  p: 2,
                  maxHeight: '600px',
                  overflow: 'auto',
                  backgroundColor: '#fafafa',
                  fontFamily: 'monospace',
                  lineHeight: 1.6
                }}
                dangerouslySetInnerHTML={{
                  __html: validationData.highlighted_text.replace(
                    /<span class="extraction-highlight"([^>]*)>([^<]*)<\/span>/g,
                    (match, attrs, text) => {
                      const fieldMatch = attrs.match(/data-field="([^"]*)"/) || [];
                      const typeMatch = attrs.match(/data-type="([^"]*)"/) || [];
                      const confidenceMatch = attrs.match(/data-confidence="([^"]*)"/) || [];
                      
                      const field = fieldMatch[1] || '';
                      const type = typeMatch[1] || '';
                      const confidence = parseFloat(confidenceMatch[1] || '0');
                      
                      return `<span 
                        style="
                          background-color: ${getExtractionTypeColor(type)};
                          padding: 2px 4px;
                          border-radius: 3px;
                          cursor: pointer;
                          border: 1px solid #ccc;
                        "
                        onclick="handleSpanClick('${field}', '${text}', ${confidence})"
                        title="Field: ${field}, Confidence: ${confidence.toFixed(2)}"
                      >${text}</span>`;
                    }
                  )
                }}
              />

              {/* Legend */}
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Extraction Types:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {Object.entries({
                    'demographics': 'Demographics',
                    'genetics': 'Genetics',
                    'phenotypes': 'Phenotypes',
                    'treatments': 'Treatments',
                    'outcomes': 'Outcomes'
                  }).map(([type, label]) => (
                    <Chip
                      key={type}
                      label={label}
                      size="small"
                      sx={{ backgroundColor: getExtractionTypeColor(type) }}
                    />
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Panel - Extraction Details */}
        <Grid item xs={12} md={4}>
          {/* Confidence Summary */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Confidence Summary
              </Typography>
              {Object.entries(validationData.confidence_scores).map(([field, confidence]) => (
                <Box key={field} mb={1}>
                  <Box display="flex" justifyContent="between" alignItems="center">
                    <Typography variant="body2">{field}</Typography>
                    <Chip
                      label={`${(confidence * 100).toFixed(0)}%`}
                      size="small"
                      color={getConfidenceColor(confidence)}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={confidence * 100}
                    color={getConfidenceColor(confidence)}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>

          {/* Extracted Fields */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Extracted Fields
              </Typography>
              {validationData.spans.map((span, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" justifyContent="between" alignItems="center" width="100%">
                      <Typography variant="body2">{span.field_name}</Typography>
                      <Chip
                        label={`${(span.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color={getConfidenceColor(span.confidence)}
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        <strong>Extracted Text:</strong> {span.text}
                      </Typography>
                      {span.normalized_value && (
                        <Typography variant="body2" gutterBottom>
                          <strong>Normalized Value:</strong> {span.normalized_value}
                        </Typography>
                      )}
                      <Typography variant="body2" gutterBottom>
                        <strong>Type:</strong> {span.extraction_type}
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<Edit />}
                        onClick={() => handleSpanClick(span)}
                      >
                        Edit
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>

          {/* Corrections */}
          {corrections.length > 0 && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Corrections Made
                </Typography>
                {corrections.map((correction, index) => (
                  <Box key={index} mb={1} p={1} border="1px solid #ddd" borderRadius={1}>
                    <Typography variant="body2">
                      <strong>{correction.field_name}:</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {correction.original_value} → {correction.corrected_value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Validator Notes */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validator Notes
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={validatorNotes}
                onChange={(e) => setValidatorNotes(e.target.value)}
                placeholder="Add notes about the validation..."
                variant="outlined"
              />
            </CardContent>
          </Card>

          {/* Validation Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validation Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircle />}
                  onClick={() => handleValidationSubmit('validated')}
                  disabled={saving}
                  fullWidth
                >
                  Approve Extraction
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Cancel />}
                  onClick={() => handleValidationSubmit('rejected')}
                  disabled={saving}
                  fullWidth
                >
                  Reject Extraction
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  disabled={saving}
                  fullWidth
                >
                  Save Draft
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Edit Field: {selectedSpan?.field_name}
        </DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Typography variant="body2" color="textSecondary">
              Original Text: "{selectedSpan?.text}"
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Confidence: {((selectedSpan?.confidence || 0) * 100).toFixed(0)}%
            </Typography>
          </Box>
          <TextField
            autoFocus
            fullWidth
            label="Corrected Value"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            variant="outlined"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleFieldCorrection} variant="contained">
            Apply Correction
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ValidationInterface;
'''


def create_enhanced_ui_files():
    """Create all enhanced UI component files."""
    
    # Create directory structure
    ui_dir = Path("enhanced_ui_components")
    ui_dir.mkdir(exist_ok=True)
    
    components_dir = ui_dir / "components"
    components_dir.mkdir(exist_ok=True)
    
    pages_dir = ui_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    # Write component files
    files_created = []
    
    # Enhanced Dashboard
    dashboard_file = pages_dir / "EnhancedDashboard.tsx"
    with open(dashboard_file, 'w') as f:
        f.write(ENHANCED_DASHBOARD_TSX)
    files_created.append(str(dashboard_file))
    
    # Validation Interface
    validation_file = pages_dir / "ValidationInterface.tsx"
    with open(validation_file, 'w') as f:
        f.write(VALIDATION_INTERFACE_TSX)
    files_created.append(str(validation_file))
    
    # Additional component templates
    additional_components = {
        "MetadataManager.tsx": create_metadata_manager_component(),
        "DatabaseManager.tsx": create_database_manager_component(),
        "APIManager.tsx": create_api_manager_component(),
        "KnowledgeBaseManager.tsx": create_knowledge_base_manager_component(),
        "DocumentManager.tsx": create_document_manager_component(),
        "OntologyBrowser.tsx": create_ontology_browser_component(),
        "PromptManager.tsx": create_prompt_manager_component(),
        "DataVisualization.tsx": create_data_visualization_component()
    }
    
    for filename, content in additional_components.items():
        file_path = pages_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        files_created.append(str(file_path))
    
    # Create API service file
    api_service = create_api_service()
    api_file = ui_dir / "api_service.ts"
    with open(api_file, 'w') as f:
        f.write(api_service)
    files_created.append(str(api_file))
    
    # Create package.json with all dependencies
    package_json = create_package_json()
    package_file = ui_dir / "package.json"
    with open(package_file, 'w') as f:
        f.write(package_json)
    files_created.append(str(package_file))
    
    logger.info(f"Created {len(files_created)} enhanced UI component files")
    return files_created


def create_metadata_manager_component():
    """Create metadata manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  LinearProgress
} from '@mui/material';
import { Search, Download, Refresh, FilterList, Visibility } from '@mui/icons-material';
import { api } from '../services/api';

const MetadataManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    source: 'all',
    dateRange: 'all',
    relevanceThreshold: 0.5,
    includeFulltext: true
  });

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await api.metadata.search({
        query: searchQuery,
        filters: filters,
        max_results: 1000
      });
      setSearchResults(response.data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.metadata.export({
        results: searchResults,
        format: 'csv'
      });
      // Download file
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'metadata_results.csv';
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Metadata Management
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search Query"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., Leigh syndrome case report"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Source</InputLabel>
                <Select
                  value={filters.source}
                  onChange={(e) => setFilters({...filters, source: e.target.value})}
                >
                  <MenuItem value="all">All Sources</MenuItem>
                  <MenuItem value="pubmed">PubMed</MenuItem>
                  <MenuItem value="europepmc">Europe PMC</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={handleSearch}
                disabled={loading || !searchQuery}
                fullWidth
              >
                Search
              </Button>
            </Grid>
          </Grid>
          
          {/* Advanced Filters */}
          <Box mt={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.includeFulltext}
                  onChange={(e) => setFilters({...filters, includeFulltext: e.target.checked})}
                />
              }
              label="Include Full-text Download"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Results */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {searchResults.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Search Results ({searchResults.length})
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExport}
              >
                Export CSV
              </Button>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>PMID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Journal</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Relevance</TableCell>
                    <TableCell>Full-text</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {searchResults.map((result: any) => (
                    <TableRow key={result.pmid}>
                      <TableCell>{result.pmid}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {result.title}
                        </Typography>
                      </TableCell>
                      <TableCell>{result.journal}</TableCell>
                      <TableCell>{result.publication_date}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${(result.relevance_score * 100).toFixed(0)}%`}
                          color={result.relevance_score > 0.7 ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.fulltext_available ? 'Available' : 'Not Available'}
                          color={result.fulltext_available ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          href={`/documents/${result.pmid}`}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default MetadataManager;
'''


def create_database_manager_component():
    """Create database manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  LinearProgress
} from '@mui/material';
import { Storage, Visibility, Download, Refresh, Search } from '@mui/icons-material';
import { api } from '../services/api';

const DatabaseManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [schema, setSchema] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDatabaseInfo();
  }, []);

  const loadDatabaseInfo = async () => {
    setLoading(true);
    try {
      const [tablesRes, statsRes] = await Promise.all([
        api.database.getTables(),
        api.database.getStatistics()
      ]);
      setTables(tablesRes.data);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Failed to load database info:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async (tableName: string) => {
    setLoading(true);
    try {
      const [dataRes, schemaRes] = await Promise.all([
        api.database.getTableData(tableName, { limit: 100 }),
        api.database.getTableSchema(tableName)
      ]);
      setTableData(dataRes.data);
      setSchema(schemaRes.data);
      setSelectedTable(tableName);
    } catch (error) {
      console.error('Failed to load table data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Tables" />
        <Tab label="Schema" />
        <Tab label="Statistics" />
        <Tab label="Query" />
      </Tabs>

      {/* Tables Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Tables
                </Typography>
                {tables.map((table: any) => (
                  <Box key={table.name} mb={1}>
                    <Button
                      fullWidth
                      variant={selectedTable === table.name ? 'contained' : 'outlined'}
                      onClick={() => loadTableData(table.name)}
                      startIcon={<Storage />}
                    >
                      {table.name} ({table.row_count})
                    </Button>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {selectedTable && (
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {selectedTable} Data
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={() => api.database.exportTable(selectedTable)}
                    >
                      Export
                    </Button>
                  </Box>
                  
                  {loading && <LinearProgress sx={{ mb: 2 }} />}
                  
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          {schema?.columns.map((column: any) => (
                            <TableCell key={column.name}>
                              {column.name}
                              <Typography variant="caption" display="block">
                                {column.type}
                              </Typography>
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tableData.map((row: any, index: number) => (
                          <TableRow key={index}>
                            {schema?.columns.map((column: any) => (
                              <TableCell key={column.name}>
                                {row[column.name]}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}

      {/* Statistics Tab */}
      {selectedTab === 2 && statistics && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Statistics
                </Typography>
                <Box>
                  <Typography variant="body2">
                    Total Records: {statistics.total_records}
                  </Typography>
                  <Typography variant="body2">
                    Database Size: {statistics.database_size}
                  </Typography>
                  <Typography variant="body2">
                    Last Updated: {statistics.last_updated}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Table Statistics
                </Typography>
                {statistics.table_stats?.map((table: any) => (
                  <Box key={table.name} mb={1}>
                    <Typography variant="body2">
                      {table.name}: {table.row_count} rows
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default DatabaseManager;
'''


def create_api_manager_component():
    """Create API manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Settings, Key, Assessment, Refresh, Add } from '@mui/icons-material';
import { api } from '../services/api';

const APIManager: React.FC = () => {
  const [providers, setProviders] = useState([]);
  const [usage, setUsage] = useState({});
  const [models, setModels] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [apiKeys, setApiKeys] = useState({});
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAPIData();
  }, []);

  const loadAPIData = async () => {
    setLoading(true);
    try {
      const [providersRes, usageRes, modelsRes] = await Promise.all([
        api.config.getProviders(),
        api.config.getUsage(),
        api.config.getModels()
      ]);
      setProviders(providersRes.data);
      setUsage(usageRes.data);
      setModels(modelsRes.data);
    } catch (error) {
      console.error('Failed to load API data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    try {
      await api.config.updateApiKey(selectedProvider, newApiKey);
      setConfigDialogOpen(false);
      setNewApiKey('');
      loadAPIData();
    } catch (error) {
      console.error('Failed to save API key:', error);
    }
  };

  const handleToggleProvider = async (provider: string, enabled: boolean) => {
    try {
      await api.config.updateProvider(provider, { enabled });
      loadAPIData();
    } catch (error) {
      console.error('Failed to update provider:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        API Management
      </Typography>

      {/* Provider Configuration */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Providers
              </Typography>
              {providers.map((provider: any) => (
                <Box key={provider.name} mb={2} p={2} border="1px solid #ddd" borderRadius={1}>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="subtitle1">{provider.display_name}</Typography>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={provider.enabled}
                          onChange={(e) => handleToggleProvider(provider.name, e.target.checked)}
                        />
                      }
                      label="Enabled"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" mb={1}>
                    {provider.description}
                  </Typography>
                  
                  <Box display="flex" justifyContent="between" alignItems="center">
                    <Chip
                      label={provider.api_key_configured ? 'API Key Set' : 'No API Key'}
                      color={provider.api_key_configured ? 'success' : 'error'}
                      size="small"
                    />
                    <Button
                      size="small"
                      startIcon={<Key />}
                      onClick={() => {
                        setSelectedProvider(provider.name);
                        setConfigDialogOpen(true);
                      }}
                    >
                      Configure
                    </Button>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Usage Statistics
              </Typography>
              {Object.entries(usage).map(([provider, stats]: [string, any]) => (
                <Box key={provider} mb={2}>
                  <Typography variant="subtitle2">{provider}</Typography>
                  <Box display="flex" justifyContent="between">
                    <Typography variant="body2">
                      Requests: {stats.total_requests}
                    </Typography>
                    <Typography variant="body2">
                      Cost: ${stats.total_cost?.toFixed(2) || '0.00'}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(stats.total_requests / stats.limit) * 100}
                    sx={{ mt: 1 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Available Models */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Models
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell>Provider</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Cost</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model: any) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.name}</TableCell>
                    <TableCell>{model.provider}</TableCell>
                    <TableCell>
                      <Chip
                        label={model.type}
                        size="small"
                        color={model.type === 'free' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {model.cost_per_token ? `$${model.cost_per_token}/token` : 'Free'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.available ? 'Available' : 'Unavailable'}
                        color={model.available ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* API Key Configuration Dialog */}
      <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Configure API Key - {selectedProvider}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="API Key"
            type="password"
            fullWidth
            variant="outlined"
            value={newApiKey}
            onChange={(e) => setNewApiKey(e.target.value)}
            placeholder="Enter your API key"
          />
          <Alert severity="info" sx={{ mt: 2 }}>
            API keys are stored securely and encrypted. They are only used for making requests to the respective services.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveApiKey} variant="contained" disabled={!newApiKey}>
            Save API Key
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default APIManager;
'''


def create_knowledge_base_manager_component():
    """Create knowledge base manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Tree,
  TreeItem,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { AccountTree, Add, Edit, Delete, Search, Refresh } from '@mui/icons-material';
import { api } from '../services/api';

const KnowledgeBaseManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [ontologies, setOntologies] = useState([]);
  const [selectedOntology, setSelectedOntology] = useState(null);
  const [ontologyTerms, setOntologyTerms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOntologies();
  }, []);

  const loadOntologies = async () => {
    setLoading(true);
    try {
      const response = await api.ontologies.getAll();
      setOntologies(response.data);
    } catch (error) {
      console.error('Failed to load ontologies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOntologyTerms = async (ontologyId: string) => {
    setLoading(true);
    try {
      const response = await api.ontologies.getTerms(ontologyId);
      setOntologyTerms(response.data);
      setSelectedOntology(ontologyId);
    } catch (error) {
      console.error('Failed to load ontology terms:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchTerms = async () => {
    if (!searchQuery) return;
    
    setLoading(true);
    try {
      const response = await api.ontologies.search({
        query: searchQuery,
        ontology: selectedOntology
      });
      setOntologyTerms(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Management
      </Typography>

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Ontologies" />
        <Tab label="Gene Database" />
        <Tab label="Custom Vocabularies" />
      </Tabs>

      {/* Ontologies Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Available Ontologies
                </Typography>
                {ontologies.map((ontology: any) => (
                  <Box key={ontology.id} mb={1}>
                    <Button
                      fullWidth
                      variant={selectedOntology === ontology.id ? 'contained' : 'outlined'}
                      onClick={() => loadOntologyTerms(ontology.id)}
                      startIcon={<AccountTree />}
                    >
                      {ontology.name}
                    </Button>
                    <Typography variant="caption" display="block" color="textSecondary">
                      {ontology.term_count} terms
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {selectedOntology && (
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      Ontology Terms
                    </Typography>
                    <Box display="flex" gap={1}>
                      <TextField
                        size="small"
                        placeholder="Search terms..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && searchTerms()}
                      />
                      <Button
                        variant="outlined"
                        startIcon={<Search />}
                        onClick={searchTerms}
                      >
                        Search
                      </Button>
                    </Box>
                  </Box>
                  
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Term ID</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Definition</TableCell>
                          <TableCell>Synonyms</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {ontologyTerms.map((term: any) => (
                          <TableRow key={term.id}>
                            <TableCell>
                              <Chip label={term.id} size="small" />
                            </TableCell>
                            <TableCell>{term.name}</TableCell>
                            <TableCell>
                              <Typography variant="body2" noWrap>
                                {term.definition}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              {term.synonyms?.map((synonym: string, index: number) => (
                                <Chip
                                  key={index}
                                  label={synonym}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mr: 0.5, mb: 0.5 }}
                                />
                              ))}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default KnowledgeBaseManager;
'''


def create_document_manager_component():
    """Create document manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Upload, Visibility, Download, Delete, PlayArrow, Stop } from '@mui/icons-material';
import { api } from '../services/api';

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState([]);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [extractionModel, setExtractionModel] = useState('google/gemma-2-27b-it:free');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.documents.getAll();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles) return;

    const formData = new FormData();
    Array.from(selectedFiles).forEach(file => {
      formData.append('files', file);
    });
    formData.append('extraction_model', extractionModel);

    try {
      await api.documents.upload(formData);
      setUploadDialogOpen(false);
      setSelectedFiles(null);
      loadDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleExtraction = async (documentId: string) => {
    try {
      await api.documents.startExtraction(documentId, {
        model: extractionModel
      });
      loadDocuments();
    } catch (error) {
      console.error('Extraction failed:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Management
      </Typography>

      {/* Upload Button */}
      <Box mb={3}>
        <Button
          variant="contained"
          startIcon={<Upload />}
          onClick={() => setUploadDialogOpen(true)}
        >
          Upload Documents
        </Button>
      </Box>

      {/* Documents Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Documents ({documents.length})
          </Typography>
          
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Patients</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documents.map((doc: any) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {doc.filename}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {doc.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={doc.file_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={doc.status}
                        color={getStatusColor(doc.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {doc.status === 'processing' ? (
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={doc.progress || 0}
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">
                            {doc.progress || 0}%
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2">
                          {doc.status === 'completed' ? '100%' : '-'}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.patient_count || 0}
                    </TableCell>
                    <TableCell>
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          href={`/documents/${doc.id}`}
                        >
                          View
                        </Button>
                        {doc.status === 'uploaded' && (
                          <Button
                            size="small"
                            startIcon={<PlayArrow />}
                            onClick={() => handleExtraction(doc.id)}
                          >
                            Extract
                          </Button>
                        )}
                        {doc.status === 'processing' && (
                          <Button
                            size="small"
                            startIcon={<Stop />}
                            color="error"
                          >
                            Stop
                          </Button>
                        )}
                        {doc.status === 'completed' && (
                          <Button
                            size="small"
                            startIcon={<Download />}
                            href={`/api/documents/${doc.id}/export`}
                          >
                            Export
                          </Button>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Box mb={3}>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              onChange={(e) => setSelectedFiles(e.target.files)}
              style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
            />
          </Box>
          
          <FormControl fullWidth>
            <InputLabel>Extraction Model</InputLabel>
            <Select
              value={extractionModel}
              onChange={(e) => setExtractionModel(e.target.value)}
              label="Extraction Model"
            >
              <MenuItem value="google/gemma-2-27b-it:free">Gemma 2 27B (Free)</MenuItem>
              <MenuItem value="microsoft/phi-3-mini-128k-instruct:free">Phi-3 Mini (Free)</MenuItem>
              <MenuItem value="meta-llama/llama-3.1-8b-instruct:free">Llama 3.1 8B (Free)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpload} variant="contained" disabled={!selectedFiles}>
            Upload & Process
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentManager;
'''


def create_ontology_browser_component():
    """Create ontology browser component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Tree,
  TreeItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { Search, AccountTree, Visibility, Edit } from '@mui/icons-material';
import { api } from '../services/api';

const OntologyBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [termDetails, setTermDetails] = useState(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    setLoading(true);
    try {
      const response = await api.ontologies.search({
        query: searchQuery,
        include_synonyms: true,
        include_definitions: true
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTermClick = async (termId: string) => {
    try {
      const response = await api.ontologies.getTermDetails(termId);
      setTermDetails(response.data);
      setSelectedTerm(termId);
      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Failed to load term details:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Ontology Browser
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              label="Search Terms"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., developmental delay, lactic acidosis"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={handleSearch}
              disabled={loading || !searchQuery}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Search Results ({searchResults.length})
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Term ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Ontology</TableCell>
                    <TableCell>Definition</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {searchResults.map((term: any) => (
                    <TableRow key={term.id}>
                      <TableCell>
                        <Chip label={term.id} size="small" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {term.name}
                        </Typography>
                        {term.synonyms && (
                          <Box mt={0.5}>
                            {term.synonyms.slice(0, 3).map((synonym: string, index: number) => (
                              <Chip
                                key={index}
                                label={synonym}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 0.5, fontSize: '0.7rem' }}
                              />
                            ))}
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={term.ontology}
                          size="small"
                          color={term.ontology === 'HPO' ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {term.definition}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          onClick={() => handleTermClick(term.id)}
                        >
                          Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Term Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Term Details: {termDetails?.name}
        </DialogTitle>
        <DialogContent>
          {termDetails && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {termDetails.name}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                ID: {termDetails.id} | Ontology: {termDetails.ontology}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Definition
              </Typography>
              <Typography variant="body2" paragraph>
                {termDetails.definition}
              </Typography>
              
              {termDetails.synonyms && termDetails.synonyms.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Synonyms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.synonyms.map((synonym: string, index: number) => (
                      <Chip
                        key={index}
                        label={synonym}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </>
              )}
              
              {termDetails.parents && termDetails.parents.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Parent Terms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.parents.map((parent: any, index: number) => (
                      <Chip
                        key={index}
                        label={`${parent.id}: ${parent.name}`}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </>
              )}
              
              {termDetails.children && termDetails.children.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Child Terms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.children.slice(0, 10).map((child: any, index: number) => (
                      <Chip
                        key={index}
                        label={`${child.id}: ${child.name}`}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                    {termDetails.children.length > 10 && (
                      <Typography variant="caption" color="textSecondary">
                        ... and {termDetails.children.length - 10} more
                      </Typography>
                    )}
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OntologyBrowser;
'''


def create_prompt_manager_component():
    """Create prompt manager component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Edit, Add, Delete, Save, Visibility } from '@mui/icons-material';
import { api } from '../services/api';

const PromptManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [promptName, setPromptName] = useState('');
  const [promptType, setPromptType] = useState('system');
  const [agentType, setAgentType] = useState('demographics');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    setLoading(true);
    try {
      const response = await api.prompts.getAll();
      setPrompts(response.data);
    } catch (error) {
      console.error('Failed to load prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditPrompt = (prompt: any) => {
    setSelectedPrompt(prompt);
    setPromptName(prompt.name);
    setPromptText(prompt.content);
    setPromptType(prompt.type);
    setAgentType(prompt.agent_type);
    setEditDialogOpen(true);
  };

  const handleSavePrompt = async () => {
    try {
      const promptData = {
        name: promptName,
        content: promptText,
        type: promptType,
        agent_type: agentType
      };

      if (selectedPrompt) {
        await api.prompts.update(selectedPrompt.id, promptData);
      } else {
        await api.prompts.create(promptData);
      }

      setEditDialogOpen(false);
      resetForm();
      loadPrompts();
    } catch (error) {
      console.error('Failed to save prompt:', error);
    }
  };

  const resetForm = () => {
    setSelectedPrompt(null);
    setPromptName('');
    setPromptText('');
    setPromptType('system');
    setAgentType('demographics');
  };

  const handleDeletePrompt = async (promptId: string) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await api.prompts.delete(promptId);
        loadPrompts();
      } catch (error) {
        console.error('Failed to delete prompt:', error);
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Prompt Management
      </Typography>

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="System Prompts" />
        <Tab label="Agent Prompts" />
        <Tab label="LangExtract Schemas" />
      </Tabs>

      {/* Add New Prompt Button */}
      <Box mb={3}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            resetForm();
            setEditDialogOpen(true);
          }}
        >
          Add New Prompt
        </Button>
      </Box>

      {/* Prompts Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Prompts ({prompts.length})
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Agent</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Modified</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {prompts.map((prompt: any) => (
                  <TableRow key={prompt.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {prompt.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {prompt.content.substring(0, 100)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={prompt.type}
                        size="small"
                        color={prompt.type === 'system' ? 'primary' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={prompt.agent_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={prompt.active ? 'Active' : 'Inactive'}
                        color={prompt.active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(prompt.updated_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          startIcon={<Edit />}
                          onClick={() => handleEditPrompt(prompt)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Delete />}
                          color="error"
                          onClick={() => handleDeletePrompt(prompt.id)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Edit Prompt Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {selectedPrompt ? 'Edit Prompt' : 'Add New Prompt'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Prompt Name"
                value={promptName}
                onChange={(e) => setPromptName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={promptType}
                  onChange={(e) => setPromptType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="system">System</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="schema">Schema</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Agent Type</InputLabel>
                <Select
                  value={agentType}
                  onChange={(e) => setAgentType(e.target.value)}
                  label="Agent Type"
                >
                  <MenuItem value="demographics">Demographics</MenuItem>
                  <MenuItem value="genetics">Genetics</MenuItem>
                  <MenuItem value="phenotypes">Phenotypes</MenuItem>
                  <MenuItem value="treatments">Treatments</MenuItem>
                  <MenuItem value="outcomes">Outcomes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={15}
                label="Prompt Content"
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder="Enter your prompt content here..."
                variant="outlined"
                sx={{ fontFamily: 'monospace' }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePrompt} variant="contained" disabled={!promptName || !promptText}>
            Save Prompt
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PromptManager;
'''


def create_data_visualization_component():
    """Create data visualization component."""
    return '''
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip
} from '@mui/material';
import { Assessment, Download, Refresh } from '@mui/icons-material';
import { api } from '../services/api';

// Placeholder for chart components - would use recharts, plotly, or similar
const PlotlyChart = ({ data, layout, config }: any) => (
  <div style={{ width: '100%', height: '400px', border: '1px solid #ddd', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <Typography color="textSecondary">
      Chart: {layout?.title?.text || 'Visualization'}
    </Typography>
  </div>
);

const DataVisualization: React.FC = () => {
  const [visualizations, setVisualizations] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('all');
  const [selectedChart, setSelectedChart] = useState('overview');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVisualizations();
  }, [selectedDataset, selectedChart]);

  const loadVisualizations = async () => {
    setLoading(true);
    try {
      const response = await api.analytics.getVisualizations({
        dataset: selectedDataset,
        chart_type: selectedChart
      });
      setVisualizations(response.data);
    } catch (error) {
      console.error('Failed to load visualizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const response = await api.analytics.exportVisualizations({
        dataset: selectedDataset,
        format: format
      });
      // Download file
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'text/html' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `visualizations.${format}`;
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Visualization
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Dataset</InputLabel>
                <Select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  label="Dataset"
                >
                  <MenuItem value="all">All Data</MenuItem>
                  <MenuItem value="leigh_syndrome">Leigh Syndrome</MenuItem>
                  <MenuItem value="mitochondrial">Mitochondrial Diseases</MenuItem>
                  <MenuItem value="recent">Recent Extractions</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Chart Type</InputLabel>
                <Select
                  value={selectedChart}
                  onChange={(e) => setSelectedChart(e.target.value)}
                  label="Chart Type"
                >
                  <MenuItem value="overview">Overview Dashboard</MenuItem>
                  <MenuItem value="demographics">Demographics</MenuItem>
                  <MenuItem value="genetics">Genetic Analysis</MenuItem>
                  <MenuItem value="phenotypes">Phenotype Distribution</MenuItem>
                  <MenuItem value="treatments">Treatment Patterns</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadVisualizations}
                disabled={loading}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => handleExport('html')}
                fullWidth
              >
                Export
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Visualizations */}
      <Grid container spacing={3}>
        {visualizations.map((viz: any, index: number) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    {viz.title}
                  </Typography>
                  <Chip
                    label={viz.type}
                    size="small"
                    color="primary"
                  />
                </Box>
                
                <PlotlyChart
                  data={viz.data}
                  layout={viz.layout}
                  config={viz.config}
                />
                
                {viz.description && (
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                    {viz.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {visualizations.length === 0 && !loading && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No visualizations available
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Select a dataset and chart type to view visualizations
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DataVisualization;
'''


def create_api_service():
    """Create API service for frontend."""
    return '''
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Dashboard APIs
  dashboard: {
    getSystemStatus: () => apiClient.get('/dashboard/status'),
    getProcessingQueue: () => apiClient.get('/dashboard/queue'),
    getRecentResults: () => apiClient.get('/dashboard/results'),
  },

  // Metadata APIs
  metadata: {
    search: (params: any) => apiClient.post('/metadata/search', params),
    export: (params: any) => apiClient.post('/metadata/export', params),
    getAll: () => apiClient.get('/metadata'),
    getById: (id: string) => apiClient.get(`/metadata/${id}`),
  },

  // Document APIs
  documents: {
    getAll: () => apiClient.get('/documents'),
    getById: (id: string) => apiClient.get(`/documents/${id}`),
    upload: (formData: FormData) => apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    startExtraction: (id: string, params: any) => apiClient.post(`/documents/${id}/extract`, params),
    getExtractionResults: (id: string) => apiClient.get(`/documents/${id}/results`),
  },

  // Validation APIs
  validation: {
    getExtractionData: (id: string) => apiClient.get(`/validation/${id}`),
    submitValidation: (id: string, data: any) => apiClient.post(`/validation/${id}/submit`, data),
    getQueue: (status?: string) => apiClient.get('/validation/queue', { params: { status } }),
  },

  // Database APIs
  database: {
    getTables: () => apiClient.get('/database/tables'),
    getTableData: (table: string, params?: any) => apiClient.get(`/database/tables/${table}/data`, { params }),
    getTableSchema: (table: string) => apiClient.get(`/database/tables/${table}/schema`),
    getStatistics: () => apiClient.get('/database/statistics'),
    exportTable: (table: string) => apiClient.get(`/database/tables/${table}/export`),
    query: (sql: string) => apiClient.post('/database/query', { sql }),
  },

  // Configuration APIs
  config: {
    getProviders: () => apiClient.get('/config/providers'),
    updateProvider: (provider: string, data: any) => apiClient.put(`/config/providers/${provider}`, data),
    getModels: () => apiClient.get('/config/models'),
    updateApiKey: (provider: string, apiKey: string) => apiClient.put(`/config/providers/${provider}/key`, { api_key: apiKey }),
    getUsage: () => apiClient.get('/config/usage'),
  },

  // Ontology APIs
  ontologies: {
    getAll: () => apiClient.get('/ontologies'),
    getTerms: (ontologyId: string) => apiClient.get(`/ontologies/${ontologyId}/terms`),
    getTermDetails: (termId: string) => apiClient.get(`/ontologies/terms/${termId}`),
    search: (params: any) => apiClient.post('/ontologies/search', params),
  },

  // Prompt APIs
  prompts: {
    getAll: () => apiClient.get('/prompts'),
    getById: (id: string) => apiClient.get(`/prompts/${id}`),
    create: (data: any) => apiClient.post('/prompts', data),
    update: (id: string, data: any) => apiClient.put(`/prompts/${id}`, data),
    delete: (id: string) => apiClient.delete(`/prompts/${id}`),
  },

  // Analytics APIs
  analytics: {
    getVisualizations: (params: any) => apiClient.get('/analytics/visualizations', { params }),
    exportVisualizations: (params: any) => apiClient.post('/analytics/export', params),
    getMetrics: () => apiClient.get('/analytics/metrics'),
  },

  // Authentication APIs
  auth: {
    login: (credentials: any) => apiClient.post('/auth/login', credentials),
    logout: () => apiClient.post('/auth/logout'),
    refresh: () => apiClient.post('/auth/refresh'),
    getProfile: () => apiClient.get('/auth/profile'),
  },
};

export default apiClient;
'''


def create_package_json():
    """Create package.json with all dependencies."""
    return '''
{
  "name": "biomedical-text-agent-ui",
  "version": "1.0.0",
  "description": "Enhanced UI for Biomedical Text Agent",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.14.19",
    "@mui/material": "^5.14.20",
    "@mui/x-data-grid": "^6.18.2",
    "@mui/x-tree-view": "^6.17.0",
    "@types/node": "^16.18.68",
    "@types/react": "^18.2.42",
    "@types/react-dom": "^18.2.17",
    "axios": "^1.6.2",
    "plotly.js": "^2.27.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-plotly.js": "^2.6.0",
    "react-router-dom": "^6.20.1",
    "react-scripts": "5.0.1",
    "recharts": "^2.8.0",
    "socket.io-client": "^4.7.4",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@types/plotly.js": "^2.12.29",
    "@types/react-plotly.js": "^2.6.3"
  }
}
'''


if __name__ == "__main__":
    # Create enhanced UI components
    files_created = create_enhanced_ui_files()
    
    logger.info(f"Enhanced UI components created successfully!")
    logger.info(f"Files created: {len(files_created)}")
    
    for file_path in files_created:
        logger.info(f"  - {file_path}")

