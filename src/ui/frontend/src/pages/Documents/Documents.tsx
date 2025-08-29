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
  Schedule as ScheduleIcon,
  Description as DocumentIcon,
  PictureAsPdf as PdfIcon,
  Article as TextIcon,
  Folder as FolderIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

const Documents: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isProcessDialogOpen, setIsProcessDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch real documents data
  const { data: documentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['documents'],
            queryFn: () => api.documents.getAll(),
  });

  // Extract documents from API response
  const documents = Array.isArray(documentsData) ? documentsData : [];

  // Filter and sort documents - newest first
  const filteredDocuments = documents
    .filter((doc: any) => {
      const matchesSearch = (doc.title || doc.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                           (doc.abstract || '').toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = selectedStatus === 'all' || doc.status === selectedStatus;
      
      return matchesSearch && matchesStatus;
    })
    .sort((a: any, b: any) => {
      // Sort by upload date, newest first
      const dateA = new Date(a.upload_date || a.uploaded || 0);
      const dateB = new Date(b.upload_date || b.uploaded || 0);
      return dateB.getTime() - dateA.getTime();
    });

  const handleProcessDocument = (documentId: string) => {
    // This would integrate with your orchestrator
    console.log('Processing document:', documentId);
    setIsProcessDialogOpen(false);
  };

  // File upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.documents.upload(formData);
    },
    onSuccess: (data) => {
      console.log('Upload successful:', data);
      // Show success message - handle both Axios response and direct data
      const responseData = data.data || data;
      setUploadSuccess(`Document "${responseData.filename}" uploaded successfully!`);
      // Force refresh the documents list
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      // Also refetch immediately to ensure we get the latest data
      refetch();
      setIsUploadDialogOpen(false);
      // Clear success message after 5 seconds
      setTimeout(() => setUploadSuccess(null), 5000);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
      // You could add error handling here
    },
  });

  const handleFileUpload = (file: File) => {
    uploadMutation.mutate(file);
  };

  const handleViewDocument = (document: any) => {
    setSelectedDocument(document);
  };

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
      case 'processing': return <ScheduleIcon />;
      case 'pending': return <ScheduleIcon />;
      case 'error': return <ErrorIcon />;
      default: return <ScheduleIcon />;
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Loading Documents...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load documents: {String(error)}
        </Alert>
        <Button variant="contained" onClick={() => refetch()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Document Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and process your biomedical documents
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setIsUploadDialogOpen(true)}
        >
          Upload Document
        </Button>
      </Box>

      {/* Success Message */}
      {uploadSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setUploadSuccess(null)}>
          {uploadSuccess}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <DocumentIcon color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h4">{documents.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Documents</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CompletedIcon color="success" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h4" color="success.main">
                    {documents.filter((d: any) => d.status === 'completed').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">Completed</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ScheduleIcon color="warning" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {documents.filter((d: any) => d.status === 'pending').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">Pending</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ProcessIcon color="info" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h4" color="info.main">
                    {documents.filter((d: any) => d.status === 'processing').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">Processing</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search documents by name, title, or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={selectedStatus}
                  label="Status"
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
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Documents ({filteredDocuments.length})
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell>Processed</TableCell>
                  <TableCell>Patient Count</TableCell>
                  <TableCell>Extraction Score</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDocuments.map((doc: any) => (
                  <TableRow key={doc.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {doc.type === 'pdf' ? <PdfIcon sx={{ mr: 1, color: 'error.main' }} /> : 
                         doc.type === 'text' ? <TextIcon sx={{ mr: 1, color: 'primary.main' }} /> :
                         <DocumentIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {doc.title || doc.name}
                          </Typography>
                          {doc.pmid && (
                            <Typography variant="caption" color="text.secondary">
                              PMID: {doc.pmid}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={doc.type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{doc.file_size ? `${Math.round(doc.file_size / 1024)} KB` : '-'}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(doc.status)}
                        label={doc.status}
                        color={getStatusColor(doc.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{doc.upload_date || doc.uploaded || '-'}</TableCell>
                    <TableCell>{doc.processed || '-'}</TableCell>
                    <TableCell>
                      {doc.extraction_results?.patient_count > 0 ? (
                        <Chip label={doc.extraction_results.patient_count} size="small" color="primary" />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.extraction_results?.confidence_score ? (
                        <Chip 
                          label={`${Math.round(doc.extraction_results.confidence_score * 100)}%`} 
                          size="small" 
                          color={doc.extraction_results.confidence_score > 0.9 ? 'success' : doc.extraction_results.confidence_score > 0.8 ? 'warning' : 'error'}
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewDocument(doc)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        {doc.status === 'pending' && (
                          <Tooltip title="Process Document">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={() => {
                                setSelectedDocument(doc);
                                setIsProcessDialogOpen(true);
                              }}
                            >
                              <ProcessIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        {doc.pmid && (
                          <Tooltip title="View on PubMed">
                            <IconButton 
                              size="small" 
                              onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${doc.pmid}/`, '_blank')}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
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
      <Dialog 
        open={isUploadDialogOpen} 
        onClose={() => !uploadMutation.isPending && setIsUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {uploadMutation.isPending ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <LinearProgress sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Uploading document... Please wait.
                </Typography>
              </Box>
            ) : (
              <>
                <input
                  accept=".pdf,.csv,.txt"
                  style={{ display: 'none' }}
                  id="document-upload-input"
                  type="file"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      handleFileUpload(file);
                    }
                  }}
                />
                <label htmlFor="document-upload-input">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    fullWidth
                    sx={{ mb: 2 }}
                  >
                    Choose File
                  </Button>
                </label>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Supported formats: PDF, CSV, TXT
                </Typography>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setIsUploadDialogOpen(false)} 
            disabled={uploadMutation.isPending}
          >
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Process Dialog */}
      <Dialog 
        open={isProcessDialogOpen} 
        onClose={() => setIsProcessDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Process Document</DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Process "{selectedDocument.title || selectedDocument.name}" using your extraction pipeline?
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsProcessDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={() => selectedDocument && handleProcessDocument(selectedDocument.id)}
          >
            Process Document
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Details Dialog */}
      <Dialog 
        open={!!selectedDocument} 
        onClose={() => setSelectedDocument(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Document Details</DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {selectedDocument.title || selectedDocument.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedDocument.pmid && `PMID: ${selectedDocument.pmid}`}
                </Typography>
              </Grid>
              
              {selectedDocument.abstract && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>Abstract</Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {selectedDocument.abstract}
                  </Typography>
                </Grid>
              )}
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Document Type</Typography>
                <Typography variant="body2">{selectedDocument.type}</Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Size</Typography>
                <Typography variant="body2">{selectedDocument.file_size ? `${Math.round(selectedDocument.file_size / 1024)} KB` : '-'}</Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Status</Typography>
                <Chip 
                  label={selectedDocument.status} 
                  color={getStatusColor(selectedDocument.status) as any}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Category</Typography>
                <Typography variant="body2">{selectedDocument.category || 'Unknown'}</Typography>
              </Grid>
              
              {selectedDocument.source_path && (
                <Grid item xs={12}>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => window.open(selectedDocument.source_path, '_blank')}
                    fullWidth
                  >
                    View Source Document
                  </Button>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedDocument(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents;
