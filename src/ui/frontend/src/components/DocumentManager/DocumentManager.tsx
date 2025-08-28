import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
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
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Divider,
  Tabs,
  Tab,
  InputAdornment,
  CircularProgress,
  Snackbar,
  Autocomplete,
  Checkbox,
  FormGroup,
  Badge,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Upload as UploadIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  PlayArrow as ProcessIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  AutoFixHigh as AutoFixIcon,
  Save as SaveIcon,
  History as HistoryIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Link as LinkIcon,
  LinkOff as UnlinkIcon,
  Schema as SchemaIcon,
  DataObject as DataObjectIcon,
  CloudUpload as CloudUploadIcon,
  Folder as FolderIcon,
  FileCopy as FileCopyIcon,
  Archive as ArchiveIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useDropzone } from 'react-dropzone';

interface Document {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  type: string;
  status: 'uploaded' | 'processing' | 'processed' | 'error' | 'archived';
  uploadDate: string;
  processedDate?: string;
  extractedData?: any;
  confidence: number;
  tags: string[];
  collection: string;
  metadata: {
    title?: string;
    authors?: string[];
    journal?: string;
    year?: number;
    doi?: string;
    pmid?: string;
    abstract?: string;
  };
  processingHistory: ProcessingStep[];
  filePath: string;
  checksum: string;
}

interface ProcessingStep {
  id: string;
  step: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
  duration?: number;
  error?: string;
  output?: any;
}

interface ExtractionResult {
  id: string;
  documentId: string;
  phenotypes: string[];
  genes: string[];
  treatments: string[];
  demographics: any;
  confidence: number;
  status: 'validated' | 'pending' | 'rejected';
  validatedBy?: string;
  validationDate?: string;
}

const validationSchema = yup.object({
  title: yup.string().required('Title is required'),
  authors: yup.string().required('Authors are required'),
  journal: yup.string(),
  year: yup.number().min(1900).max(new Date().getFullYear()),
  doi: yup.string().url('Must be a valid URL'),
  abstract: yup.string(),
});

const DocumentManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isEditDocumentDialogOpen, setIsEditDocumentDialogOpen] = useState(false);
  const [isViewDocumentDialogOpen, setIsViewDocumentDialogOpen] = useState(false);
  const [isProcessingDialogOpen, setIsProcessingDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedCollection, setSelectedCollection] = useState('all');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      title: '',
      authors: '',
      journal: '',
      year: new Date().getFullYear(),
      doi: '',
      abstract: '',
    }
  });

  // Sample data
  const [documents] = useState<Document[]>([
    {
      id: '1',
      filename: 'mitochondrial_disorder_study.pdf',
      originalName: 'Mitochondrial Disorder Study.pdf',
      size: 2048576,
      type: 'application/pdf',
      status: 'processed',
      uploadDate: '2024-01-15 10:30',
      processedDate: '2024-01-15 10:35',
      confidence: 94.2,
      tags: ['mitochondrial', 'neurology', 'genetics'],
      collection: 'Research Papers',
      metadata: {
        title: 'Novel genetic variants associated with mitochondrial disorders',
        authors: ['Smith J', 'Johnson A', 'Brown K'],
        journal: 'Nature Genetics',
        year: 2023,
        doi: 'https://doi.org/10.1038/ng.1234',
        pmid: '12345678',
        abstract: 'This study identifies novel genetic variants associated with mitochondrial disorders...',
      },
      processingHistory: [
        {
          id: '1',
          step: 'Text Extraction',
          status: 'completed',
          startTime: '2024-01-15 10:30',
          endTime: '2024-01-15 10:31',
          duration: 1,
        },
        {
          id: '2',
          step: 'Entity Recognition',
          status: 'completed',
          startTime: '2024-01-15 10:31',
          endTime: '2024-01-15 10:33',
          duration: 2,
        },
        {
          id: '3',
          step: 'Data Extraction',
          status: 'completed',
          startTime: '2024-01-15 10:33',
          endTime: '2024-01-15 10:35',
          duration: 2,
        },
      ],
      filePath: '/uploads/mitochondrial_disorder_study.pdf',
      checksum: 'abc123def456',
    },
    {
      id: '2',
      filename: 'clinical_trial_results.pdf',
      originalName: 'Clinical Trial Results.pdf',
      size: 1536000,
      type: 'application/pdf',
      status: 'processing',
      uploadDate: '2024-01-15 11:00',
      confidence: 0,
      tags: ['clinical trial', 'treatment', 'outcomes'],
      collection: 'Clinical Studies',
      metadata: {
        title: 'Clinical trial results for novel treatment approach',
        authors: ['Davis M', 'Wilson R'],
        journal: 'Journal of Clinical Medicine',
        year: 2023,
      },
      processingHistory: [
        {
          id: '1',
          step: 'Text Extraction',
          status: 'completed',
          startTime: '2024-01-15 11:00',
          endTime: '2024-01-15 11:01',
          duration: 1,
        },
        {
          id: '2',
          step: 'Entity Recognition',
          status: 'running',
          startTime: '2024-01-15 11:01',
        },
      ],
      filePath: '/uploads/clinical_trial_results.pdf',
      checksum: 'def456ghi789',
    },
    {
      id: '3',
      filename: 'case_study_report.pdf',
      originalName: 'Case Study Report.pdf',
      size: 1024000,
      type: 'application/pdf',
      status: 'uploaded',
      uploadDate: '2024-01-15 11:30',
      confidence: 0,
      tags: ['case study', 'patient', 'diagnosis'],
      collection: 'Case Reports',
      metadata: {
        title: 'Case study: Rare genetic disorder presentation',
        authors: ['Anderson L', 'Martinez P'],
        journal: 'Case Reports in Medicine',
        year: 2023,
      },
      processingHistory: [],
      filePath: '/uploads/case_study_report.pdf',
      checksum: 'ghi789jkl012',
    },
  ]);

  const [extractions] = useState<ExtractionResult[]>([
    {
      id: '1',
      documentId: '1',
      phenotypes: ['HP:0001250', 'HP:0001344', 'HP:0002134'],
      genes: ['MT-ATP6', 'MT-ND1', 'MT-ND4'],
      treatments: ['Coenzyme Q10', 'L-carnitine', 'Supportive care'],
      demographics: { age: 32, gender: 'female', ethnicity: 'caucasian' },
      confidence: 94.2,
      status: 'validated',
      validatedBy: 'Dr. Smith',
      validationDate: '2024-01-15 14:00',
    },
  ]);

  const [collections] = useState([
    { name: 'Research Papers', count: 1250 },
    { name: 'Clinical Studies', count: 890 },
    { name: 'Case Reports', count: 720 },
    { name: 'Review Articles', count: 450 },
  ]);

  const filteredDocuments = documents.filter(doc =>
    (selectedStatus === 'all' || doc.status === selectedStatus) &&
    (selectedCollection === 'all' || doc.collection === selectedCollection) &&
    (searchQuery === '' || 
     doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
     doc.metadata.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
     doc.metadata.authors?.some(author => author.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      console.log('Files dropped:', acceptedFiles);
      setSnackbar({ open: true, message: `${acceptedFiles.length} files uploaded successfully`, severity: 'success' });
    },
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleUploadDocument = (data: any) => {
    console.log('Uploading document:', data);
    setIsUploadDialogOpen(false);
    reset();
    setSnackbar({ open: true, message: 'Document uploaded successfully', severity: 'success' });
  };

  const handleEditDocument = (data: any) => {
    console.log('Editing document:', data);
    setIsEditDocumentDialogOpen(false);
    setSnackbar({ open: true, message: 'Document updated successfully', severity: 'success' });
  };

  const handleDeleteDocument = (id: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      console.log('Deleting document:', id);
      setSnackbar({ open: true, message: 'Document deleted successfully', severity: 'success' });
    }
  };

  const handleProcessDocument = (document: Document) => {
    setSelectedDocument(document);
    setIsProcessingDialogOpen(true);
  };

  const handleStopProcessing = (document: Document) => {
    console.log('Stopping processing for:', document.id);
    setSnackbar({ open: true, message: 'Processing stopped', severity: 'info' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploaded': return 'info';
      case 'processing': return 'warning';
      case 'processed': return 'success';
      case 'error': return 'error';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploaded': return <InfoIcon />;
      case 'processing': return <WarningIcon />;
      case 'processed': return <ValidIcon />;
      case 'error': return <InvalidIcon />;
      case 'archived': return <ArchiveIcon />;
      default: return <InfoIcon />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getProcessingProgress = (document: Document) => {
    if (document.status === 'processed') return 100;
    if (document.status === 'uploaded') return 0;
    
    const completedSteps = document.processingHistory.filter(step => step.status === 'completed').length;
    const totalSteps = document.processingHistory.length;
    return totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Document Management System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload, manage, and extract data from biomedical documents
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Documents" icon={<DocumentIcon />} />
          <Tab label="Extractions" icon={<DataObjectIcon />} />
          <Tab label="Collections" icon={<FolderIcon />} />
          <Tab label="Processing Queue" icon={<ProcessIcon />} />
          <Tab label="Upload" icon={<CloudUploadIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <>
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
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={selectedStatus}
                      label="Status"
                      onChange={(e) => setSelectedStatus(e.target.value)}
                    >
                      <MenuItem value="all">All Statuses</MenuItem>
                      <MenuItem value="uploaded">Uploaded</MenuItem>
                      <MenuItem value="processing">Processing</MenuItem>
                      <MenuItem value="processed">Processed</MenuItem>
                      <MenuItem value="error">Error</MenuItem>
                      <MenuItem value="archived">Archived</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Collection</InputLabel>
                    <Select
                      value={selectedCollection}
                      label="Collection"
                      onChange={(e) => setSelectedCollection(e.target.value)}
                    >
                      <MenuItem value="all">All Collections</MenuItem>
                      {collections.map((collection) => (
                        <MenuItem key={collection.name} value={collection.name}>
                          {collection.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    variant="contained"
                    startIcon={<UploadIcon />}
                    onClick={() => setIsUploadDialogOpen(true)}
                    fullWidth
                  >
                    Upload
                  </Button>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={() => {
                      setSearchQuery('');
                      setSelectedStatus('all');
                      setSelectedCollection('all');
                    }}
                    fullWidth
                  >
                    Clear Filters
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Documents Grid */}
          <Grid container spacing={3}>
            {filteredDocuments.map((document) => (
              <Grid item xs={12} md={6} lg={4} key={document.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <DocumentIcon />
                        <Typography variant="h6" component="h2" noWrap sx={{ maxWidth: 200 }}>
                          {document.metadata.title || document.originalName}
                        </Typography>
                      </Box>
                      <Chip
                        icon={getStatusIcon(document.status)}
                        label={document.status}
                        color={getStatusColor(document.status) as any}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                      {document.metadata.abstract || 'No abstract available'}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        File Information
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Size: {formatFileSize(document.size)} • Type: {document.type}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Uploaded: {document.uploadDate}
                      </Typography>
                      {document.processedDate && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Processed: {document.processedDate}
                        </Typography>
                      )}
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Collection & Tags
                      </Typography>
                      <Chip label={document.collection} size="small" color="primary" sx={{ mb: 1 }} />
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {document.tags.slice(0, 3).map((tag, index) => (
                          <Chip key={index} label={tag} size="small" variant="outlined" />
                        ))}
                        {document.tags.length > 3 && (
                          <Chip label={`+${document.tags.length - 3}`} size="small" />
                        )}
                      </Box>
                    </Box>

                    {document.status === 'processing' && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Processing Progress
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={getProcessingProgress(document)}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {document.processingHistory.filter(step => step.status === 'completed').length} of {document.processingHistory.length} steps completed
                        </Typography>
                      </Box>
                    )}

                    {document.status === 'processed' && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Extraction Confidence
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {document.confidence}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={document.confidence} 
                            sx={{ flexGrow: 1, height: 6 }}
                            color={document.confidence > 90 ? 'success' : document.confidence > 70 ? 'warning' : 'error'}
                          />
                        </Box>
                      </Box>
                    )}

                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedDocument(document);
                          setIsViewDocumentDialogOpen(true);
                        }}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedDocument(document);
                          setIsEditDocumentDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      {document.status === 'uploaded' && (
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => handleProcessDocument(document)}
                        >
                          Process
                        </Button>
                      )}
                      {document.status === 'processing' && (
                        <Button
                          size="small"
                          variant="outlined"
                          color="warning"
                          onClick={() => handleStopProcessing(document)}
                        >
                          Stop
                        </Button>
                      )}
                      {document.status === 'processed' && (
                        <Button
                          size="small"
                          variant="outlined"
                          color="success"
                        >
                          View Data
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                Extraction Results ({extractions.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AutoFixIcon />}
                onClick={() => setIsProcessingDialogOpen(true)}
              >
                Process New Documents
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Document</TableCell>
                    <TableCell>Phenotypes</TableCell>
                    <TableCell>Genes</TableCell>
                    <TableCell>Treatments</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {extractions.map((extraction) => (
                    <TableRow key={extraction.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {documents.find(d => d.id === extraction.documentId)?.metadata.title || 'Unknown'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {extraction.phenotypes.slice(0, 2).map((phenotype, index) => (
                            <Chip key={index} label={phenotype} size="small" variant="outlined" />
                          ))}
                          {extraction.phenotypes.length > 2 && (
                            <Chip label={`+${extraction.phenotypes.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {extraction.genes.slice(0, 2).map((gene, index) => (
                            <Chip key={index} label={gene} size="small" variant="outlined" />
                          ))}
                          {extraction.genes.length > 2 && (
                            <Chip label={`+${extraction.genes.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {extraction.treatments.slice(0, 2).map((treatment, index) => (
                            <Chip key={index} label={treatment} size="small" variant="outlined" />
                          ))}
                          {extraction.treatments.length > 2 && (
                            <Chip label={`+${extraction.treatments.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {extraction.confidence}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={extraction.confidence} 
                            sx={{ width: 60, height: 6 }}
                            color={extraction.confidence > 90 ? 'success' : extraction.confidence > 70 ? 'warning' : 'error'}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={extraction.status}
                          color={extraction.status === 'validated' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Extraction">
                            <IconButton size="small" color="secondary">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Validate">
                            <IconButton size="small" color="success">
                              <ValidIcon />
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
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          {collections.map((collection) => (
            <Grid item xs={12} md={6} lg={4} key={collection.name}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2">
                      {collection.name}
                    </Typography>
                    <Chip label={collection.count} size="small" color="primary" />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Collection of {collection.count} documents
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button size="small" variant="outlined">
                      View Documents
                    </Button>
                    <Button size="small" variant="outlined">
                      Edit Collection
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing Queue
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Documents currently being processed
            </Typography>
            {documents.filter(d => d.status === 'processing').map((document) => (
              <Box key={document.id} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {document.metadata.title || document.originalName}
                  </Typography>
                  <Chip label="Processing" size="small" color="warning" />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getProcessingProgress(document)}
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {document.processingHistory.filter(step => step.status === 'completed').length} of {document.processingHistory.length} steps completed
                </Typography>
                <Box sx={{ mt: 1 }}>
                  {document.processingHistory.map((step) => (
                    <Box key={step.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Chip
                        label={step.step}
                        size="small"
                        color={step.status === 'completed' ? 'success' : step.status === 'running' ? 'warning' : 'default'}
                        variant="outlined"
                      />
                      {step.status === 'completed' && step.duration && (
                        <Typography variant="caption" color="text.secondary">
                          ({step.duration}s)
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              </Box>
            ))}
            {documents.filter(d => d.status === 'processing').length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No documents currently processing
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Drag and drop files or click to browse
            </Typography>
            
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <input {...getInputProps()} />
              <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                or click to browse files
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supported formats: PDF, DOC, DOCX, TXT
              </Typography>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                startIcon={<UploadIcon />}
                onClick={() => setIsUploadDialogOpen(true)}
                fullWidth
              >
                Manual Upload
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Upload Dialog */}
      <Dialog open={isUploadDialogOpen} onClose={() => setIsUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <form onSubmit={handleSubmit(handleUploadDocument)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Controller
                  name="title"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Document Title"
                      error={!!errors.title}
                      helperText={errors.title?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="authors"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Authors (comma-separated)"
                      error={!!errors.authors}
                      helperText={errors.authors?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="journal"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Journal"
                      error={!!errors.journal}
                      helperText={errors.journal?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="year"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Year"
                      type="number"
                      error={!!errors.year}
                      helperText={errors.year?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="doi"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="DOI"
                      error={!!errors.doi}
                      helperText={errors.doi?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="abstract"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Abstract"
                      multiline
                      rows={4}
                      error={!!errors.abstract}
                      helperText={errors.abstract?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsUploadDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Upload</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Document Dialog */}
      <Dialog open={isEditDocumentDialogOpen} onClose={() => setIsEditDocumentDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Document</DialogTitle>
        <form onSubmit={handleSubmit(handleEditDocument)}>
          <DialogContent>
            {selectedDocument && (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Document Title"
                    defaultValue={selectedDocument.metadata.title}
                    name="title"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Authors (comma-separated)"
                    defaultValue={selectedDocument.metadata.authors?.join(', ')}
                    name="authors"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Journal"
                    defaultValue={selectedDocument.metadata.journal}
                    name="journal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Year"
                    type="number"
                    defaultValue={selectedDocument.metadata.year}
                    name="year"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="DOI"
                    defaultValue={selectedDocument.metadata.doi}
                    name="doi"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Abstract"
                    multiline
                    rows={4}
                    defaultValue={selectedDocument.metadata.abstract}
                    name="abstract"
                  />
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditDocumentDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save Changes</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Document Dialog */}
      <Dialog open={isViewDocumentDialogOpen} onClose={() => setIsViewDocumentDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Document Details</DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>{selectedDocument.metadata.title || selectedDocument.originalName}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedDocument.metadata.abstract || 'No abstract available'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>File Information</Typography>
                <Typography variant="body2">Filename: {selectedDocument.filename}</Typography>
                <Typography variant="body2">Size: {formatFileSize(selectedDocument.size)}</Typography>
                <Typography variant="body2">Type: {selectedDocument.type}</Typography>
                <Typography variant="body2">Status: {selectedDocument.status}</Typography>
                <Typography variant="body2">Upload Date: {selectedDocument.uploadDate}</Typography>
                {selectedDocument.processedDate && (
                  <Typography variant="body2">Processed Date: {selectedDocument.processedDate}</Typography>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Metadata</Typography>
                <Typography variant="body2">Authors: {selectedDocument.metadata.authors?.join(', ')}</Typography>
                <Typography variant="body2">Journal: {selectedDocument.metadata.journal}</Typography>
                <Typography variant="body2">Year: {selectedDocument.metadata.year}</Typography>
                <Typography variant="body2">DOI: {selectedDocument.metadata.doi}</Typography>
                <Typography variant="body2">PMID: {selectedDocument.metadata.pmid}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Processing History</Typography>
                {selectedDocument.processingHistory.length > 0 ? (
                  <List dense>
                    {selectedDocument.processingHistory.map((step) => (
                      <ListItem key={step.id}>
                        <ListItemIcon>
                          {step.status === 'completed' ? <ValidIcon color="success" /> : 
                           step.status === 'running' ? <ProcessIcon color="warning" /> : 
                           step.status === 'failed' ? <InvalidIcon color="error" /> : 
                           <InfoIcon color="disabled" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={step.step}
                          secondary={`${step.startTime}${step.endTime ? ` - ${step.endTime}` : ''}${step.duration ? ` (${step.duration}s)` : ''}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">No processing history available</Typography>
                )}
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsViewDocumentDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setIsViewDocumentDialogOpen(false);
              setIsEditDocumentDialogOpen(true);
            }}
          >
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DocumentManager;