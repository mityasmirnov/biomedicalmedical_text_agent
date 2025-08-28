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
  Pagination,
  InputAdornment,
  Switch,
  FormControlLabel,
  Divider,
  Tabs,
  Tab,
  Collapse,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  Sort as SortIcon,
  Clear as ClearIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Book as BookIcon,
  Article as ArticleIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface MetadataItem {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  doi: string;
  pmid: string;
  abstract: string;
  keywords: string[];
  collection: string;
  status: 'validated' | 'pending' | 'invalid' | 'duplicate';
  lastUpdated: string;
  source: string;
  confidence: number;
  tags: string[];
}

interface Collection {
  name: string;
  description: string;
  documentCount: number;
  lastUpdated: string;
  status: 'active' | 'archived' | 'processing';
}

interface SearchFilters {
  query: string;
  collection: string;
  yearFrom: number;
  yearTo: number;
  status: string;
  authors: string;
  journal: string;
  tags: string[];
}

const validationSchema = yup.object({
  title: yup.string().required('Title is required'),
  authors: yup.string().required('Authors are required'),
  journal: yup.string().required('Journal is required'),
  year: yup.number().min(1900).max(new Date().getFullYear()).required('Valid year is required'),
  doi: yup.string().url('Must be a valid URL').required('DOI is required'),
  abstract: yup.string().min(50, 'Abstract must be at least 50 characters'),
});

const MetadataManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCollection, setSelectedCollection] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<MetadataItem | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      title: '',
      authors: '',
      journal: '',
      year: new Date().getFullYear(),
      doi: '',
      abstract: '',
      keywords: '',
      tags: '',
    }
  });

  // Sample data
  const [metadataItems] = useState<MetadataItem[]>([
    {
      id: '1',
      title: 'Novel genetic variants associated with mitochondrial disorders',
      authors: ['Smith J', 'Johnson A', 'Brown K'],
      journal: 'Nature Genetics',
      year: 2023,
      doi: 'https://doi.org/10.1038/ng.1234',
      pmid: '12345678',
      abstract: 'This study identifies novel genetic variants associated with mitochondrial disorders through comprehensive genome sequencing...',
      keywords: ['mitochondrial disorders', 'genetics', 'genome sequencing'],
      collection: 'Mitochondrial Research',
      status: 'validated',
      lastUpdated: '2024-01-15',
      source: 'PubMed Central',
      confidence: 95.2,
      tags: ['genetics', 'mitochondrial', 'disorders'],
    },
    {
      id: '2',
      title: 'Machine learning approaches for phenotype extraction from clinical texts',
      authors: ['Davis M', 'Wilson R', 'Taylor S'],
      journal: 'Bioinformatics',
      year: 2023,
      doi: 'https://doi.org/10.1093/bioinformatics/bt123',
      pmid: '87654321',
      abstract: 'We present a novel machine learning approach for extracting phenotypic information from clinical text documents...',
      keywords: ['machine learning', 'phenotype extraction', 'clinical text'],
      collection: 'AI in Medicine',
      status: 'pending',
      lastUpdated: '2024-01-14',
      source: 'PubMed Central',
      confidence: 87.3,
      tags: ['AI', 'phenotype', 'clinical'],
    },
    {
      id: '3',
      title: 'Comparative analysis of treatment outcomes in rare diseases',
      authors: ['Anderson L', 'Martinez P', 'Lee J'],
      journal: 'Journal of Rare Diseases',
      year: 2022,
      doi: 'https://doi.org/10.1002/jrd.456',
      pmid: '11223344',
      abstract: 'This comparative study analyzes treatment outcomes across multiple rare disease categories...',
      keywords: ['rare diseases', 'treatment outcomes', 'comparative analysis'],
      collection: 'Rare Diseases',
      status: 'validated',
      lastUpdated: '2024-01-13',
      source: 'PubMed Central',
      confidence: 92.1,
      tags: ['rare diseases', 'treatment', 'outcomes'],
    },
  ]);

  const [collections] = useState<Collection[]>([
    {
      name: 'Mitochondrial Research',
      description: 'Research papers on mitochondrial disorders and related genetic conditions',
      documentCount: 1250,
      lastUpdated: '2024-01-15',
      status: 'active',
    },
    {
      name: 'AI in Medicine',
      description: 'Applications of artificial intelligence in medical research and clinical practice',
      documentCount: 890,
      lastUpdated: '2024-01-14',
      status: 'active',
    },
    {
      name: 'Rare Diseases',
      description: 'Research on rare genetic and acquired diseases',
      documentCount: 2100,
      lastUpdated: '2024-01-13',
      status: 'active',
    },
  ]);

  const filteredItems = metadataItems.filter(item =>
    (selectedCollection === 'all' || item.collection === selectedCollection) &&
    (selectedStatus === 'all' || item.status === selectedStatus) &&
    (searchQuery === '' || 
     item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.authors.some(author => author.toLowerCase().includes(searchQuery.toLowerCase())) ||
     item.journal.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const paginatedItems = filteredItems.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);

  const handleSearch = () => {
    setCurrentPage(1);
    // In a real app, this would trigger an API call
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCollection('all');
    setSelectedStatus('all');
    setCurrentPage(1);
  };

  const handleAddItem = (data: any) => {
    console.log('Adding new item:', data);
    setIsAddDialogOpen(false);
    reset();
    // In a real app, this would make an API call
  };

  const handleEditItem = (data: any) => {
    console.log('Editing item:', data);
    setIsEditDialogOpen(false);
    // In a real app, this would make an API call
  };

  const handleDeleteItem = (id: string) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      console.log('Deleting item:', id);
      // In a real app, this would make an API call
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated': return 'success';
      case 'pending': return 'warning';
      case 'invalid': return 'error';
      case 'duplicate': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'validated': return <ValidIcon />;
      case 'pending': return <WarningIcon />;
      case 'invalid': return <InvalidIcon />;
      case 'duplicate': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Metadata Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Search, filter, and manage biomedical literature metadata
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Search & Browse" icon={<SearchIcon />} />
          <Tab label="Collections" icon={<BookIcon />} />
          <Tab label="Import/Export" icon={<UploadIcon />} />
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
                    placeholder="Search metadata..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
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
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={selectedStatus}
                      label="Status"
                      onChange={(e) => setSelectedStatus(e.target.value)}
                    >
                      <MenuItem value="all">All Statuses</MenuItem>
                      <MenuItem value="validated">Validated</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="invalid">Invalid</MenuItem>
                      <MenuItem value="duplicate">Duplicate</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      onClick={handleSearch}
                      startIcon={<SearchIcon />}
                    >
                      Search
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={handleClearFilters}
                      startIcon={<ClearIcon />}
                    >
                      Clear
                    </Button>
                  </Box>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    variant="outlined"
                    onClick={() => setIsAddDialogOpen(true)}
                    startIcon={<AddIcon />}
                    fullWidth
                  >
                    Add New
                  </Button>
                </Grid>
              </Grid>

              {/* Advanced Filters */}
              <Box sx={{ mt: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showAdvancedFilters}
                      onChange={(e) => setShowAdvancedFilters(e.target.checked)}
                    />
                  }
                  label="Advanced Filters"
                />
                
                <Collapse in={showAdvancedFilters}>
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Year From"
                        type="number"
                        placeholder="1900"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Year To"
                        type="number"
                        placeholder="2024"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Authors"
                        placeholder="Author name"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Journal"
                        placeholder="Journal name"
                      />
                    </Grid>
                  </Grid>
                </Collapse>
              </Box>
            </CardContent>
          </Card>

          {/* Results Summary */}
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Showing {paginatedItems.length} of {filteredItems.length} results
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                size="small"
              >
                Export Results
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                size="small"
                onClick={handleSearch}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {/* Results Table */}
          <Card>
            <CardContent>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Title & Authors</TableCell>
                      <TableCell>Journal & Year</TableCell>
                      <TableCell>Collection</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Last Updated</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedItems.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="medium" noWrap sx={{ maxWidth: 300 }}>
                              {item.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {item.authors.join(', ')}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                              {item.journal}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {item.year}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={item.collection} 
                            size="small" 
                            variant="outlined" 
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(item.status)}
                            label={item.status}
                            color={getStatusColor(item.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {item.confidence}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={item.confidence} 
                              sx={{ width: 60, height: 6 }}
                              color={item.confidence > 90 ? 'success' : item.confidence > 70 ? 'warning' : 'error'}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap>
                            {item.lastUpdated}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="View Details">
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  setSelectedItem(item);
                                  setIsViewDialogOpen(true);
                                }}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Edit">
                              <IconButton 
                                size="small" 
                                color="secondary"
                                onClick={() => {
                                  setSelectedItem(item);
                                  setIsEditDialogOpen(true);
                                }}
                              >
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleDeleteItem(item.id)}
                              >
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

              {/* Pagination */}
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={currentPage}
                  onChange={(event, page) => setCurrentPage(page)}
                  color="primary"
                  showFirstButton
                  showLastButton
                />
              </Box>
            </CardContent>
          </Card>
        </>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          {collections.map((collection) => (
            <Grid item xs={12} md={6} lg={4} key={collection.name}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2">
                      {collection.name}
                    </Typography>
                    <Chip 
                      label={collection.status} 
                      size="small" 
                      color={collection.status === 'active' ? 'success' : 'default'}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {collection.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">
                      {collection.documentCount} documents
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Updated: {collection.lastUpdated}
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
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

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Import Metadata
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Import metadata from various sources including PubMed, CrossRef, and custom CSV files.
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button variant="contained" startIcon={<UploadIcon />}>
                    Import from PubMed
                  </Button>
                  <Button variant="outlined" startIcon={<UploadIcon />}>
                    Import from CrossRef
                  </Button>
                  <Button variant="outlined" startIcon={<UploadIcon />}>
                    Upload CSV File
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Export Metadata
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Export metadata in various formats for analysis and sharing.
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button variant="contained" startIcon={<DownloadIcon />}>
                    Export as CSV
                  </Button>
                  <Button variant="outlined" startIcon={<DownloadIcon />}>
                    Export as JSON
                  </Button>
                  <Button variant="outlined" startIcon={<DownloadIcon />}>
                    Export as XML
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add New Item Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Metadata Item</DialogTitle>
        <form onSubmit={handleSubmit(handleAddItem)}>
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
                      label="Title"
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
            <Button onClick={() => setIsAddDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Add Item</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Item Dialog */}
      <Dialog open={isViewDialogOpen} onClose={() => setIsViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Metadata Details</DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>{selectedItem.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Authors: {selectedItem.authors.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Journal Information</Typography>
                <Typography variant="body2">{selectedItem.journal} ({selectedItem.year})</Typography>
                <Typography variant="body2" color="text.secondary">DOI: {selectedItem.doi}</Typography>
                <Typography variant="body2" color="text.secondary">PMID: {selectedItem.pmid}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Collection & Status</Typography>
                <Chip label={selectedItem.collection} size="small" sx={{ mb: 1 }} />
                <br />
                <Chip
                  icon={getStatusIcon(selectedItem.status)}
                  label={selectedItem.status}
                  color={getStatusColor(selectedItem.status) as any}
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Abstract</Typography>
                <Typography variant="body2">{selectedItem.abstract}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Keywords & Tags</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedItem.keywords.map((keyword, index) => (
                    <Chip key={index} label={keyword} size="small" variant="outlined" />
                  ))}
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsViewDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setIsViewDialogOpen(false);
              setIsEditDialogOpen(true);
            }}
          >
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Item Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Metadata Item</DialogTitle>
        <form onSubmit={handleSubmit(handleEditItem)}>
          <DialogContent>
            {selectedItem && (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Title"
                    defaultValue={selectedItem.title}
                    name="title"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Authors"
                    defaultValue={selectedItem.authors.join(', ')}
                    name="authors"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Journal"
                    defaultValue={selectedItem.journal}
                    name="journal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Year"
                    type="number"
                    defaultValue={selectedItem.year}
                    name="year"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="DOI"
                    defaultValue={selectedItem.doi}
                    name="doi"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Abstract"
                    multiline
                    rows={4}
                    defaultValue={selectedItem.abstract}
                    name="abstract"
                  />
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save Changes</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default MetadataManager;