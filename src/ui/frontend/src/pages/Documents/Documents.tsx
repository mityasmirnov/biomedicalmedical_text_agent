import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  PlayArrow as ProcessIcon,
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  Description as DocumentIcon,
  PictureAsPdf as PdfIcon,
  Article as TextIcon,
  Folder as FolderIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

const Documents: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isProcessDialogOpen, setIsProcessDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);

  const documents = [
    {
      id: 1,
      name: 'PMID32679198.pdf',
      type: 'pdf',
      size: '2.3 MB',
      status: 'completed',
      uploaded: '2024-01-15 10:30',
      processed: '2024-01-15 10:35',
      patient_count: 1,
      extraction_score: 94.2,
      category: 'Case Report',
      source: 'PubMed',
    },
    {
      id: 2,
      name: 'leigh_syndrome_study.pdf',
      type: 'pdf',
      size: '4.1 MB',
      status: 'processing',
      uploaded: '2024-01-15 09:15',
      processed: null,
      patient_count: 3,
      extraction_score: null,
      category: 'Research Study',
      source: 'Upload',
    },
    {
      id: 3,
      name: 'mitochondrial_disorders.txt',
      type: 'text',
      size: '156 KB',
      status: 'pending',
      uploaded: '2024-01-15 08:45',
      processed: null,
      patient_count: 0,
      extraction_score: null,
      category: 'Literature Review',
      source: 'Upload',
    },
    {
      id: 4,
      name: 'clinical_trial_001.pdf',
      type: 'pdf',
      size: '8.7 MB',
      status: 'error',
      uploaded: '2024-01-15 07:30',
      processed: null,
      patient_count: 0,
      extraction_score: null,
      category: 'Clinical Trial',
      source: 'Upload',
      error: 'OCR processing failed',
    },
    {
      id: 5,
      name: 'patient_case_series.pdf',
      type: 'pdf',
      size: '3.2 MB',
      status: 'completed',
      uploaded: '2024-01-14 16:20',
      processed: '2024-01-14 16:28',
      patient_count: 5,
      extraction_score: 91.7,
      category: 'Case Series',
      source: 'Upload',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'pending': return 'info';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CompletedIcon />;
      case 'processing': return <ProcessIcon />;
      case 'pending': return <PendingIcon />;
      case 'error': return <ErrorIcon />;
      default: return <PendingIcon />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'pdf': return <PdfIcon />;
      case 'text': return <TextIcon />;
      default: return <DocumentIcon />;
    }
  };

  const filteredDocuments = documents.filter(doc =>
    (selectedStatus === 'all' || doc.status === selectedStatus) &&
    (searchQuery === '' || 
     doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     doc.category.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const statusCounts = {
    completed: documents.filter(d => d.status === 'completed').length,
    processing: documents.filter(d => d.status === 'processing').length,
    pending: documents.filter(d => d.status === 'pending').length,
    error: documents.filter(d => d.status === 'error').length,
  };

  const totalSize = documents.reduce((sum, doc) => {
    const size = parseFloat(doc.size.replace(' MB', '').replace(' KB', ''));
    return sum + (doc.size.includes('MB') ? size : size / 1024);
  }, 0);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Document Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload, process, and manage biomedical documents for AI-powered extraction
        </Typography>
      </Box>

      {/* Document Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <DocumentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Documents</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {documents.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {totalSize.toFixed(1)} MB total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CompletedIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Completed</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {statusCounts.completed}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Successfully processed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ProcessIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Processing</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {statusCounts.processing + statusCounts.pending}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                In queue or processing
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ErrorIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Errors</Typography>
              </Box>
              <Typography variant="h4" color="error.main">
                {statusCounts.error}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed processing
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status Filter</InputLabel>
                <Select
                  value={selectedStatus}
                  label="Status Filter"
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={5}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<UploadIcon />}
                  onClick={() => setIsUploadDialogOpen(true)}
                >
                  Upload Documents
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ProcessIcon />}
                  onClick={() => setIsProcessDialogOpen(true)}
                >
                  Process Queue
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                >
                  Export Results
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                >
                  Refresh
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Document Library ({filteredDocuments.length})
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Patients</TableCell>
                  <TableCell>Score</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getTypeIcon(doc.type)}
                        <Box sx={{ ml: 1 }}>
                          <Typography variant="body2" fontWeight="medium">
                            {doc.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {doc.source} • {doc.uploaded}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={doc.type.toUpperCase()} 
                        size="small" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>{doc.size}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(doc.status)}
                        label={doc.status}
                        color={getStatusColor(doc.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={doc.category} 
                        size="small" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      {doc.patient_count > 0 ? (
                        <Chip 
                          label={doc.patient_count} 
                          size="small" 
                          color="primary" 
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.extraction_score ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {doc.extraction_score}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={doc.extraction_score} 
                            sx={{ width: 60, height: 6 }}
                            color={doc.extraction_score > 90 ? 'success' : doc.extraction_score > 80 ? 'warning' : 'error'}
                          />
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Document">
                          <IconButton size="small" color="primary">
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View Results">
                          <IconButton size="small" color="secondary">
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        {doc.status === 'error' && (
                          <Tooltip title="Retry Processing">
                            <IconButton size="small" color="warning">
                              <ProcessIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
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
      <Dialog open={isUploadDialogOpen} onClose={() => setIsUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                Supported formats: PDF, TXT, DOCX. Maximum file size: 50MB per file.
              </Alert>
            </Grid>
            <Grid item xs={12}>
              <Box
                sx={{
                  border: '2px dashed',
                  borderColor: 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <UploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Drop files here or click to browse
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You can upload multiple files at once
                </Typography>
                <Button variant="contained" sx={{ mt: 2 }}>
                  Choose Files
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Processing Priority</InputLabel>
                <Select label="Processing Priority" defaultValue="normal">
                  <MenuItem value="high">High Priority</MenuItem>
                  <MenuItem value="normal">Normal Priority</MenuItem>
                  <MenuItem value="low">Low Priority</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Extraction Mode</InputLabel>
                <Select label="Extraction Mode" defaultValue="standard">
                  <MenuItem value="standard">Standard Extraction</MenuItem>
                  <MenuItem value="comprehensive">Comprehensive</MenuItem>
                  <MenuItem value="fast">Fast Processing</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsUploadDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsUploadDialogOpen(false)}>
            Upload Documents
          </Button>
        </DialogActions>
      </Dialog>

      {/* Process Queue Dialog */}
      <Dialog open={isProcessDialogOpen} onClose={() => setIsProcessDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Document Queue</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will start processing all pending documents in the queue.
          </Alert>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Currently {statusCounts.pending + statusCounts.processing} documents are waiting to be processed.
          </Typography>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Processing Strategy</InputLabel>
            <Select label="Processing Strategy" defaultValue="parallel">
              <MenuItem value="parallel">Parallel Processing (Faster)</MenuItem>
              <MenuItem value="sequential">Sequential Processing (More Reliable)</MenuItem>
              <MenuItem value="batch">Batch Processing (Balanced)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsProcessDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsProcessDialogOpen(false)}>
            Start Processing
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents;
