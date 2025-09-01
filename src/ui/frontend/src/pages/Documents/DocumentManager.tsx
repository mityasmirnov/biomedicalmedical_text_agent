import React, { useState, useEffect, useRef } from 'react';
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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tooltip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Upload,
  Download,
  Delete,
  Visibility,
  Search,
  Refresh,
  Description,
  Science,
  CloudUpload,
  CloudDownload
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Document {
  id: string;
  title: string;
  type: 'paper' | 'patent' | 'case_report' | 'clinical_trial' | 'review' | 'other';
  source: string;
  pmid?: string;
  doi?: string;
  authors?: string[];
  abstract?: string;
  content?: string;
  file_path?: string;
  file_size?: number;
  upload_date: string;
  status: 'uploaded' | 'processing' | 'extracted' | 'validated' | 'error';
  metadata?: Record<string, any>;
  extraction_results?: any;
}

interface UploadProgress {
  [fileId: string]: {
    progress: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
    message?: string;
  };
}

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.documents.getAll();
      setDocuments(response.data.documents || []);
      setError(null);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError('Failed to load documents - using mock data');
      // Set mock data for development
      setDocuments([
        {
          id: 'doc-1',
          title: 'Leigh Syndrome: A Case Report and Literature Review',
          type: 'case_report',
          source: 'PubMed',
          pmid: '32679198',
          doi: '10.1000/example.doi',
          authors: ['Smith J', 'Johnson A', 'Brown K'],
          abstract: 'This case report describes a patient with Leigh syndrome...',
          content: 'Full text content would be here...',
          file_path: '/data/input/PMID32679198.pdf',
          file_size: 2048576,
          upload_date: '2024-01-15T10:30:00Z',
          status: 'extracted',
          extraction_results: {
            patient_demographics: { age: 25, gender: 'male' },
            diagnosis: 'Leigh syndrome',
            symptoms: ['muscle weakness', 'fatigue']
          }
        },
        {
          id: 'doc-2',
          title: 'Genetic Analysis of Mitochondrial Disorders',
          type: 'paper',
          source: 'Europe PMC',
          doi: '10.1000/example2.doi',
          authors: ['Davis M', 'Wilson R'],
          abstract: 'A comprehensive analysis of mitochondrial disorders...',
          upload_date: '2024-01-14T15:45:00Z',
          status: 'processing'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList) => {
    const fileArray = Array.from(files);
    
    // Initialize progress for each file
    const newProgress: UploadProgress = {};
    fileArray.forEach(file => {
      const fileId = `file-${Date.now()}-${Math.random()}`;
      newProgress[fileId] = {
        progress: 0,
        status: 'uploading'
      };
    });
    setUploadProgress(newProgress);

    // Upload each file
    for (const file of fileArray) {
      const fileId = Object.keys(newProgress).find(key => 
        newProgress[key].status === 'uploading'
      );
      
      if (!fileId) continue;

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', 'auto'); // Auto-detect type
        formData.append('source', 'manual');

        // Simulate upload progress
        const interval = setInterval(() => {
          setUploadProgress(prev => ({
            ...prev,
            [fileId]: {
              ...prev[fileId],
              progress: Math.min(prev[fileId].progress + 10, 90)
            }
          }));
        }, 200);

        const response = await api.documents.upload(formData);
        
        clearInterval(interval);
        
        // Update progress to completed
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: {
            ...prev[fileId],
            progress: 100,
            status: 'completed'
          }
        }));

        // Add new document to list
        setDocuments(prev => [...prev, response.data.document]);

      } catch (error) {
        console.error('Failed to upload file:', error);
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: {
            ...prev[fileId],
            status: 'error',
            message: 'Upload failed'
          }
        }));
      }
    }

    // Close dialog after a delay to show completion
    setTimeout(() => {
      setUploadDialogOpen(false);
      setUploadProgress({});
    }, 2000);
  };

  const handleExtractDocument = async (documentId: string) => {
    try {
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId 
          ? { ...doc, status: 'processing' }
          : doc
      ));

      const response = await api.documents.extract(documentId);
      
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId 
          ? { ...doc, status: 'extracted', extraction_results: response.data.results }
          : doc
      ));

    } catch (error) {
      console.error('Failed to extract document:', error);
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId 
          ? { ...doc, status: 'error' }
          : doc
      ));
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await api.documents.delete(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document. Please try again.');
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'paper': return <Description />;
      case 'patent': return <Description />;
      case 'case_report': return <Description />;
      case 'clinical_trial': return <Science />;
      case 'review': return <Description />;
      default: return <Description />;
    }
  };

  const getDocumentTypeColor = (type: string) => {
    switch (type) {
      case 'paper': return 'primary';
      case 'patent': return 'secondary';
      case 'case_report': return 'success';
      case 'clinical_trial': return 'warning';
      case 'review': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploaded': return 'info';
      case 'processing': return 'warning';
      case 'extracted': return 'success';
      case 'validated': return 'success';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.abstract?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.authors?.some(author => author.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesType = filterType === 'all' || doc.type === filterType;
    const matchesStatus = filterStatus === 'all' || doc.status === filterStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Document Management
        </Typography>
        
        <Box display="flex" gap={2}>
          <Button
            startIcon={<Refresh />}
            onClick={loadDocuments}
            variant="outlined"
          >
            Refresh
          </Button>
          
          <Button
            startIcon={<Upload />}
            variant="contained"
            onClick={() => setUploadDialogOpen(true)}
          >
            Upload Documents
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search and Filters */}
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
                  startAdornment: <Search />
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Document Type</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  label="Document Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="paper">Papers</MenuItem>
                  <MenuItem value="patent">Patents</MenuItem>
                  <MenuItem value="case_report">Case Reports</MenuItem>
                  <MenuItem value="clinical_trial">Clinical Trials</MenuItem>
                  <MenuItem value="review">Reviews</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="uploaded">Uploaded</MenuItem>
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="extracted">Extracted</MenuItem>
                  <MenuItem value="validated">Validated</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Typography variant="body2" color="textSecondary">
                {filteredDocuments.length} of {documents.length} documents
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Document List */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Upload Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {doc.title}
                        </Typography>
                        {doc.authors && (
                          <Typography variant="caption" color="textSecondary">
                            {doc.authors.join(', ')}
                          </Typography>
                        )}
                        {doc.abstract && (
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {doc.abstract.length > 100 
                              ? `${doc.abstract.substring(0, 100)}...`
                              : doc.abstract
                            }
                          </Typography>
                        )}
                        {doc.file_size && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            {formatFileSize(doc.file_size)}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Chip
                        icon={getDocumentTypeIcon(doc.type)}
                        label={doc.type.replace('_', ' ')}
                        color={getDocumentTypeColor(doc.type)}
                        size="small"
                      />
                    </TableCell>
                    
                    <TableCell>
                      <Box>
                        <Typography variant="body2">{doc.source}</Typography>
                        {doc.pmid && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            PMID: {doc.pmid}
                          </Typography>
                        )}
                        {doc.doi && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            DOI: {doc.doi}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Chip
                        label={doc.status}
                        color={getStatusColor(doc.status)}
                        size="small"
                      />
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(doc.upload_date).toLocaleDateString()}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(doc.upload_date).toLocaleTimeString()}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Document">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        
                        {doc.status === 'uploaded' && (
                          <Tooltip title="Extract Data">
                            <IconButton
                              size="small"
                              onClick={() => handleExtractDocument(doc.id)}
                            >
                              <Science />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        {doc.status === 'extracted' && (
                          <Tooltip title="View Extraction Results">
                            <IconButton size="small">
                              <Description />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="Download">
                          <IconButton size="small">
                            <Download />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteDocument(doc.id)}
                          >
                            <Delete />
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
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Upload Documents
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body2" color="textSecondary" mb={2}>
              Upload papers, patents, case reports, and other biomedical documents. 
              Supported formats: PDF, DOCX, TXT. Maximum file size: 50MB per file.
            </Typography>
            
            <Box
              border="2px dashed #ccc"
              borderRadius={2}
              p={4}
              textAlign="center"
              sx={{
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover'
                }
              }}
              onClick={() => fileInputRef.current?.click()}
            >
              <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Click to select files or drag and drop
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Select multiple files to upload at once
              </Typography>
            </Box>
            
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
            />
            
            {/* Upload Progress */}
            {Object.keys(uploadProgress).length > 0 && (
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Upload Progress
                </Typography>
                {Object.entries(uploadProgress).map(([fileId, progress]) => (
                  <Box key={fileId} mb={2}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">
                        File {fileId.slice(-8)}
                      </Typography>
                      <Typography variant="body2">
                        {progress.progress}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={progress.progress}
                      color={progress.status === 'error' ? 'error' : 'primary'}
                    />
                    {progress.message && (
                      <Typography variant="caption" color="error.main">
                        {progress.message}
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentManager;
