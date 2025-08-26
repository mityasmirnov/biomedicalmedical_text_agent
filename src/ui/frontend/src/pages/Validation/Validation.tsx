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
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search as SearchIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  AutoFixHigh as AutoFixIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  BugReport as BugIcon,
  VerifiedUser as VerifiedIcon,
  ExpandMore as ExpandMoreIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

const Validation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isValidationDialogOpen, setIsValidationDialogOpen] = useState(false);
  const [isAutoFixDialogOpen, setIsAutoFixDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const validationItems = [
    {
      id: 1,
      type: 'phenotype',
      value: 'HP:0001250',
      description: 'Seizure',
      status: 'valid',
      confidence: 95.2,
      source: 'PMID32679198.pdf',
      patient: 'P001',
      category: 'Neurological',
      validation_date: '2024-01-15 10:35',
      validator: 'AI Agent',
      notes: 'HPO term correctly normalized',
    },
    {
      id: 2,
      type: 'gene',
      value: 'MT-ATP6',
      description: 'Mitochondrial ATP synthase 6',
      status: 'valid',
      confidence: 98.7,
      source: 'PMID32679198.pdf',
      patient: 'P001',
      category: 'Genetic',
      validation_date: '2024-01-15 10:35',
      validator: 'AI Agent',
      notes: 'HGNC gene symbol confirmed',
    },
    {
      id: 3,
      type: 'phenotype',
      value: 'HP:0001344',
      description: 'Abnormality of the cerebellum',
      status: 'warning',
      confidence: 78.3,
      source: 'leigh_syndrome_study.pdf',
      patient: 'P002',
      category: 'Neurological',
      validation_date: '2024-01-15 09:20',
      validator: 'Human Reviewer',
      notes: 'Low confidence - needs manual review',
    },
    {
      id: 4,
      type: 'treatment',
      value: 'Coenzyme Q10',
      description: 'Coenzyme Q10 supplementation',
      status: 'invalid',
      confidence: 45.2,
      source: 'clinical_trial_001.pdf',
      patient: 'P003',
      category: 'Treatment',
      validation_date: '2024-01-15 08:15',
      validator: 'AI Agent',
      notes: 'Not a standard treatment code - requires mapping',
    },
    {
      id: 5,
      type: 'demographics',
      value: 'Age: 32',
      description: 'Patient age at diagnosis',
      status: 'valid',
      confidence: 99.1,
      source: 'patient_case_series.pdf',
      patient: 'P004',
      category: 'Demographics',
      validation_date: '2024-01-15 07:45',
      validator: 'AI Agent',
      notes: 'Age value within expected range',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid': return 'success';
      case 'warning': return 'warning';
      case 'invalid': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valid': return <ValidIcon />;
      case 'warning': return <WarningIcon />;
      case 'invalid': return <InvalidIcon />;
      default: return <WarningIcon />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'phenotype': return <AssessmentIcon />;
      case 'gene': return <TrendingUpIcon />;
      case 'treatment': return <VerifiedIcon />;
      case 'demographics': return <ValidIcon />;
      default: return <AssessmentIcon />;
    }
  };

  const filteredItems = validationItems.filter(item =>
    (selectedStatus === 'all' || item.status === selectedStatus) &&
    (selectedCategory === 'all' || item.category === selectedCategory) &&
    (searchQuery === '' || 
     item.value.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.source.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const statusCounts = {
    valid: validationItems.filter(item => item.status === 'valid').length,
    warning: validationItems.filter(item => item.status === 'warning').length,
    invalid: validationItems.filter(item => item.status === 'invalid').length,
  };

  const averageConfidence = validationItems.reduce((sum, item) => sum + item.confidence, 0) / validationItems.length;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Data Validation & Quality Control
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review, validate, and ensure the quality of extracted biomedical data
        </Typography>
      </Box>

      {/* Validation Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Items</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {validationItems.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Items requiring validation
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ValidIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Valid</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {statusCounts.valid}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {Math.round((statusCounts.valid / validationItems.length) * 100)}% of total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Warnings</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {statusCounts.warning}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Needs review
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg Confidence</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {averageConfidence.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overall data quality
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search validation items..."
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
                  <MenuItem value="valid">Valid</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="invalid">Invalid</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Category Filter</InputLabel>
                <Select
                  value={selectedCategory}
                  label="Category Filter"
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <MenuItem value="all">All Categories</MenuItem>
                  <MenuItem value="Neurological">Neurological</MenuItem>
                  <MenuItem value="Genetic">Genetic</MenuItem>
                  <MenuItem value="Treatment">Treatment</MenuItem>
                  <MenuItem value="Demographics">Demographics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<AutoFixIcon />}
                  onClick={() => setIsAutoFixDialogOpen(true)}
                >
                  Auto-Fix
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

      {/* Validation Items Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Validation Items ({filteredItems.length})
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell>Patient</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getTypeIcon(item.type)}
                        <Box sx={{ ml: 1 }}>
                          <Typography variant="body2" fontWeight="medium">
                            {item.value}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {item.description}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={item.type} 
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
                      <Chip 
                        label={item.category} 
                        size="small" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 120 }}>
                        {item.source}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={item.patient} 
                        size="small" 
                        color="secondary" 
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => {
                              setSelectedItem(item);
                              setIsValidationDialogOpen(true);
                            }}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Validation">
                          <IconButton size="small" color="secondary">
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        {item.status === 'invalid' && (
                          <Tooltip title="Auto-Fix">
                            <IconButton size="small" color="warning">
                              <AutoFixIcon />
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

      {/* Validation Details Dialog */}
      <Dialog open={isValidationDialogOpen} onClose={() => setIsValidationDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Validation Details</DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Item Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Value" 
                      secondary={selectedItem.value} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Description" 
                      secondary={selectedItem.description} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Type" 
                      secondary={selectedItem.type} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Category" 
                      secondary={selectedItem.category} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Validation Details</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Status" 
                      secondary={
                        <Chip
                          icon={getStatusIcon(selectedItem.status)}
                          label={selectedItem.status}
                          color={getStatusColor(selectedItem.status) as any}
                          size="small"
                        />
                      } 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Confidence" 
                      secondary={`${selectedItem.confidence}%`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Validator" 
                      secondary={selectedItem.validator} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Validation Date" 
                      secondary={selectedItem.validation_date} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>Notes</Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedItem.notes}
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsValidationDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => setIsValidationDialogOpen(false)}>
            Update Validation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Auto-Fix Dialog */}
      <Dialog open={isAutoFixDialogOpen} onClose={() => setIsAutoFixDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Auto-Fix Validation Issues</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will attempt to automatically fix common validation issues using AI-powered suggestions.
          </Alert>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Currently {statusCounts.invalid + statusCounts.warning} items can be auto-fixed.
          </Typography>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Fix Strategy</InputLabel>
            <Select label="Fix Strategy" defaultValue="conservative">
              <MenuItem value="conservative">Conservative (High confidence only)</MenuItem>
              <MenuItem value="balanced">Balanced (Medium confidence)</MenuItem>
              <MenuItem value="aggressive">Aggressive (All possible fixes)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAutoFixDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsAutoFixDialogOpen(false)}>
            Start Auto-Fix
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Validation;
