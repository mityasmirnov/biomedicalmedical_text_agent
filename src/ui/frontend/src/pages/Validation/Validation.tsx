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
  Tabs,
  Tab,
  Divider,
  Switch,
  FormControlLabel,
  Slider,
  Stack,
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
  Highlight as HighlightIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface ValidationItem {
  id: number;
  type: string;
  value: string;
  description: string;
  status: string;
  confidence: number;
  source: string;
  patient: string;
  category: string;
  validation_date: string;
  validator: string;
  notes: string;
  originalText?: string;
  highlightedText?: string;
  suggestions?: string[];
  corrections?: string[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`validation-tabpanel-${index}`}
      aria-labelledby={`validation-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Validation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isValidationDialogOpen, setIsValidationDialogOpen] = useState(false);
  const [isAutoFixDialogOpen, setIsAutoFixDialogOpen] = useState(false);
  const [isInteractiveValidationOpen, setIsInteractiveValidationOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ValidationItem | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [isHighlightingEnabled, setIsHighlightingEnabled] = useState(true);
  const [highlightColor, setHighlightColor] = useState('#ffeb3b');
  const [correctionMode, setCorrectionMode] = useState(false);
  const [autoValidationEnabled, setAutoValidationEnabled] = useState(false);
  const [validationThreshold, setValidationThreshold] = useState(80);

  const validationItems: ValidationItem[] = [
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
      originalText: 'The patient experienced frequent seizures with loss of consciousness.',
      highlightedText: 'The patient experienced frequent <mark style="background-color: #4caf50; color: white; padding: 2px 4px; border-radius: 3px;">seizures</mark> with loss of consciousness.',
      suggestions: ['HP:0001250 - Seizure', 'HP:0001251 - Generalized tonic-clonic seizure'],
      corrections: ['HP:0001250']
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
      originalText: 'Genetic analysis revealed a mutation in MT-ATP6 gene.',
      highlightedText: 'Genetic analysis revealed a mutation in <mark style="background-color: #4caf50; color: white; padding: 2px 4px; border-radius: 3px;">MT-ATP6</mark> gene.',
      suggestions: ['MT-ATP6 - Mitochondrial ATP synthase 6', 'MT-ATP8 - Mitochondrial ATP synthase 8'],
      corrections: ['MT-ATP6']
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
      originalText: 'MRI showed cerebellar atrophy and hypoplasia.',
      highlightedText: 'MRI showed <mark style="background-color: #ff9800; color: white; padding: 2px 4px; border-radius: 3px;">cerebellar atrophy</mark> and <mark style="background-color: #ff9800; color: white; padding: 2px 4px; border-radius: 3px;">hypoplasia</mark>.',
      suggestions: ['HP:0001344 - Abnormality of the cerebellum', 'HP:0001273 - Cerebellar hypoplasia'],
      corrections: ['HP:0001344', 'HP:0001273']
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
      originalText: 'Patient was treated with Coenzyme Q10 supplements.',
      highlightedText: 'Patient was treated with <mark style="background-color: #f44336; color: white; padding: 2px 4px; border-radius: 3px;">Coenzyme Q10</mark> supplements.',
      suggestions: ['CHEBI:46245 - Coenzyme Q10', 'ATC:C01EB09 - Coenzyme Q10'],
      corrections: ['CHEBI:46245']
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
      originalText: 'The patient was diagnosed at age 32 years.',
      highlightedText: 'The patient was diagnosed at <mark style="background-color: #4caf50; color: white; padding: 2px 4px; border-radius: 3px;">age 32</mark> years.',
      suggestions: ['Age: 32 years', 'Age: 32'],
      corrections: ['Age: 32']
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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleInteractiveValidation = (item: ValidationItem) => {
    setSelectedItem(item);
    setIsInteractiveValidationOpen(true);
  };

  const handleAutoValidation = () => {
    // Simulate auto-validation process
    console.log('Starting auto-validation with threshold:', validationThreshold);
    // In a real implementation, this would call the backend API
  };

  const handleCorrection = (itemId: number, correction: string) => {
    // Simulate applying correction
    console.log(`Applying correction ${correction} to item ${itemId}`);
    // In a real implementation, this would update the backend
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Interactive Data Validation & Quality Control
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review, validate, and ensure the quality of extracted biomedical data with interactive highlighting and correction
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

      {/* Interactive Validation Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={isHighlightingEnabled}
                    onChange={(e) => setIsHighlightingEnabled(e.target.checked)}
                  />
                }
                label="Enable Text Highlighting"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={correctionMode}
                    onChange={(e) => setCorrectionMode(e.target.checked)}
                  />
                }
                label="Correction Mode"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoValidationEnabled}
                    onChange={(e) => setAutoValidationEnabled(e.target.checked)}
                  />
                }
                label="Auto-Validation"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={handleAutoValidation}
                  disabled={!autoValidationEnabled}
                >
                  Start Auto-Validation
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                >
                  Settings
                </Button>
              </Box>
            </Grid>
          </Grid>
          
          {autoValidationEnabled && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Validation Threshold: {validationThreshold}%
              </Typography>
              <Slider
                value={validationThreshold}
                onChange={(_, value) => setValidationThreshold(value as number)}
                min={50}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
              />
            </Box>
          )}
        </CardContent>
      </Card>

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

      {/* Main Content with Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="validation tabs">
            <Tab label="Validation Items" />
            <Tab label="Interactive Validation" />
            <Tab label="Corrections" />
            <Tab label="Settings" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {/* Validation Items Table */}
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
                        <Tooltip title="Interactive Validation">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleInteractiveValidation(item)}
                          >
                            <HighlightIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            color="info"
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
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Interactive Validation Interface */}
          <Typography variant="h6" gutterBottom>
            Interactive Text Validation
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Click on any validation item to see the original text with highlighted entities and interactive correction options.
          </Typography>
          
          <Grid container spacing={2}>
            {filteredItems.slice(0, 6).map((item) => (
              <Grid item xs={12} md={6} key={item.id}>
                <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={() => handleInteractiveValidation(item)}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {getTypeIcon(item.type)}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {item.value}
                      </Typography>
                      <Chip
                        icon={getStatusIcon(item.status)}
                        label={item.status}
                        color={getStatusColor(item.status) as any}
                        size="small"
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {item.description}
                    </Typography>
                    {item.originalText && (
                      <Box sx={{ 
                        p: 2, 
                        bgcolor: 'grey.50', 
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'grey.300'
                      }}>
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          Original Text:
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          lineHeight: 1.6,
                          maxHeight: 80,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {item.originalText}
                        </Typography>
                      </Box>
                    )}
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        startIcon={<HighlightIcon />}
                        variant="outlined"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleInteractiveValidation(item);
                        }}
                      >
                        Interactive Validation
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Corrections Management */}
          <Typography variant="h6" gutterBottom>
            Applied Corrections
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Track and manage all corrections applied to validation items.
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Original Value</TableCell>
                  <TableCell>Corrected Value</TableCell>
                  <TableCell>Correction Type</TableCell>
                  <TableCell>Applied By</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredItems.filter(item => item.corrections && item.corrections.length > 0).map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getTypeIcon(item.type)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {item.value}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {item.value}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {item.corrections?.map((correction, index) => (
                        <Chip 
                          key={index}
                          label={correction} 
                          size="small" 
                          color="success" 
                          sx={{ mr: 0.5 }}
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label="Manual" 
                        size="small" 
                        variant="outlined" 
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {item.validator}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {item.validation_date}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary">
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Revert">
                          <IconButton size="small" color="warning">
                            <CloseIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Validation Settings */}
          <Typography variant="h6" gutterBottom>
            Validation Settings
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Highlighting Options
                  </Typography>
                  <Stack spacing={2}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={isHighlightingEnabled}
                          onChange={(e) => setIsHighlightingEnabled(e.target.checked)}
                        />
                      }
                      label="Enable Text Highlighting"
                    />
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Highlight Color
                      </Typography>
                      <input
                        type="color"
                        value={highlightColor}
                        onChange={(e) => setHighlightColor(e.target.value)}
                        style={{ width: '100%', height: 40 }}
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Auto-Validation Settings
                  </Typography>
                  <Stack spacing={2}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={autoValidationEnabled}
                          onChange={(e) => setAutoValidationEnabled(e.target.checked)}
                        />
                      }
                      label="Enable Auto-Validation"
                    />
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Confidence Threshold: {validationThreshold}%
                      </Typography>
                      <Slider
                        value={validationThreshold}
                        onChange={(_, value) => setValidationThreshold(value as number)}
                        min={50}
                        max={100}
                        step={5}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>

      {/* Interactive Validation Dialog */}
      <Dialog 
        open={isInteractiveValidationOpen} 
        onClose={() => setIsInteractiveValidationOpen(false)} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>
          Interactive Validation - {selectedItem?.value}
          <IconButton
            aria-label="close"
            onClick={() => setIsInteractiveValidationOpen(false)}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Original Text</Typography>
                <Box sx={{ 
                  p: 2, 
                  bgcolor: 'grey.50', 
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.300',
                  minHeight: 200
                }}>
                  {isHighlightingEnabled && selectedItem.highlightedText ? (
                    <div dangerouslySetInnerHTML={{ __html: selectedItem.highlightedText }} />
                  ) : (
                    <Typography variant="body2">
                      {selectedItem.originalText || 'No original text available'}
                    </Typography>
                  )}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Validation Details</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Current Value" 
                      secondary={selectedItem.value} 
                    />
                  </ListItem>
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
                </List>
                
                {selectedItem.suggestions && selectedItem.suggestions.length > 0 && (
                  <>
                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                      Suggested Corrections
                    </Typography>
                    <Stack spacing={1}>
                      {selectedItem.suggestions.map((suggestion, index) => (
                        <Chip
                          key={index}
                          label={suggestion}
                          variant="outlined"
                          onClick={() => handleCorrection(selectedItem.id, suggestion)}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Stack>
                  </>
                )}
              </Grid>
              
              {correctionMode && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>Manual Correction</Typography>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={8}>
                      <TextField
                        fullWidth
                        label="Corrected Value"
                        placeholder="Enter corrected value..."
                        variant="outlined"
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Button
                        variant="contained"
                        startIcon={<CheckIcon />}
                        fullWidth
                      >
                        Apply Correction
                      </Button>
                    </Grid>
                  </Grid>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsInteractiveValidationOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => setIsInteractiveValidationOpen(false)}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

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
