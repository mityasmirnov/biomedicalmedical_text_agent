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
import { documentsAPI } from '../../services/api';

const Documents: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isProcessDialogOpen, setIsProcessDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const queryClient = useQueryClient();

  // Fetch real documents data
  const { data: documentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.getDocuments(),
  });

  // Extract documents from API response
  const documents = Array.isArray(documentsData) ? documentsData : [];

  // Filter documents based on search and status
  const filteredDocuments = documents.filter((doc: any) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.abstract?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = selectedStatus === 'all' || doc.status === selectedStatus;
    
    return matchesSearch && matchesStatus;
  });

  const handleProcessDocument = (documentId: string) => {
    // This would integrate with your orchestrator
    console.log('Processing document:', documentId);
    setIsProcessDialogOpen(false);
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
                    <TableCell>{doc.size}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(doc.status)}
                        label={doc.status}
                        color={getStatusColor(doc.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{doc.uploaded}</TableCell>
                    <TableCell>{doc.processed || '-'}</TableCell>
                    <TableCell>
                      {doc.patient_count > 0 ? (
                        <Chip label={doc.patient_count} size="small" color="primary" />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.extraction_score ? (
                        <Chip 
                          label={`${Math.round(doc.extraction_score)}%`} 
                          size="small" 
                          color={doc.extraction_score > 90 ? 'success' : doc.extraction_score > 80 ? 'warning' : 'error'}
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
        onClose={() => setIsUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Document upload functionality will be implemented here.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsUploadDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Upload</Button>
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
                <Typography variant="body2">{selectedDocument.size}</Typography>
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
