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
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Stack,
  Switch,
  FormControlLabel,
  InputAdornment,
  Collapse,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  TableChart as TableChartIcon,
  Backup as BackupIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Visibility as ViewIcon,
  Settings as SettingsIcon,
  Storage as DatabaseIcon,
  Schema as SchemaIcon,
  QueryStats as QueryStatsIcon,
  History as HistoryIcon,
  Save as SaveIcon,
  ContentCopy as CopyIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface TableSchema {
  name: string;
  type: string;
  nullable: boolean;
  defaultValue?: string;
  description?: string;
}

interface DatabaseTable {
  name: string;
  count: number;
  description: string;
  schema: TableSchema[];
  lastUpdated: string;
  size: string;
  indexes: string[];
}

interface QueryResult {
  columns: string[];
  data: any[][];
  rowCount: number;
  executionTime: number;
  status: 'success' | 'error' | 'warning';
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
      id={`database-tabpanel-${index}`}
      aria-labelledby={`database-tab-${index}`}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Database: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTable, setSelectedTable] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);
  const [isSchemaDialogOpen, setIsSchemaDialogOpen] = useState(false);
  const [isQueryDialogOpen, setIsQueryDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [selectedTableForSchema, setSelectedTableForSchema] = useState<DatabaseTable | null>(null);
  const [sqlQuery, setSqlQuery] = useState('');
  const [queryResults, setQueryResults] = useState<QueryResult | null>(null);
  const [isQueryRunning, setIsQueryRunning] = useState(false);
  const [savedQueries, setSavedQueries] = useState<string[]>([]);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  const tables: DatabaseTable[] = [
    {
      name: 'patients',
      count: 1250,
      description: 'Patient demographic and clinical data',
      schema: [
        { name: 'id', type: 'INTEGER', nullable: false, description: 'Primary key' },
        { name: 'patient_id', type: 'VARCHAR(50)', nullable: false, description: 'Unique patient identifier' },
        { name: 'age', type: 'INTEGER', nullable: true, description: 'Patient age at diagnosis' },
        { name: 'gender', type: 'VARCHAR(10)', nullable: true, description: 'Patient gender' },
        { name: 'diagnosis', type: 'TEXT', nullable: true, description: 'Primary diagnosis' },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false, defaultValue: 'CURRENT_TIMESTAMP' },
      ],
      lastUpdated: 'Today',
      size: '45.2 MB',
      indexes: ['id', 'patient_id', 'diagnosis']
    },
    {
      name: 'phenotypes',
      count: 456,
      description: 'Extracted phenotypic manifestations',
      schema: [
        { name: 'id', type: 'INTEGER', nullable: false, description: 'Primary key' },
        { name: 'patient_id', type: 'VARCHAR(50)', nullable: false, description: 'Reference to patient' },
        { name: 'hpo_term', type: 'VARCHAR(20)', nullable: false, description: 'HPO phenotype term' },
        { name: 'confidence', type: 'DECIMAL(5,2)', nullable: true, description: 'Extraction confidence score' },
        { name: 'source_text', type: 'TEXT', nullable: true, description: 'Original text source' },
      ],
      lastUpdated: '2 hours ago',
      size: '12.8 MB',
      indexes: ['id', 'patient_id', 'hpo_term']
    },
    {
      name: 'genetics',
      count: 234,
      description: 'Genetic variants and gene information',
      schema: [
        { name: 'id', type: 'INTEGER', nullable: false, description: 'Primary key' },
        { name: 'patient_id', type: 'VARCHAR(50)', nullable: false, description: 'Reference to patient' },
        { name: 'gene_symbol', type: 'VARCHAR(50)', nullable: false, description: 'Gene symbol' },
        { name: 'variant_type', type: 'VARCHAR(50)', nullable: true, description: 'Type of genetic variant' },
        { name: 'chromosome', type: 'VARCHAR(10)', nullable: true, description: 'Chromosome location' },
        { name: 'position', type: 'BIGINT', nullable: true, description: 'Genomic position' },
      ],
      lastUpdated: '1 hour ago',
      size: '8.9 MB',
      indexes: ['id', 'patient_id', 'gene_symbol']
    },
    {
      name: 'treatments',
      count: 189,
      description: 'Treatment and intervention data',
      schema: [
        { name: 'id', type: 'INTEGER', nullable: false, description: 'Primary key' },
        { name: 'patient_id', type: 'VARCHAR(50)', nullable: false, description: 'Reference to patient' },
        { name: 'treatment_name', type: 'VARCHAR(200)', nullable: false, description: 'Name of treatment' },
        { name: 'start_date', type: 'DATE', nullable: true, description: 'Treatment start date' },
        { name: 'end_date', type: 'DATE', nullable: true, description: 'Treatment end date' },
        { name: 'status', type: 'VARCHAR(50)', nullable: true, description: 'Current treatment status' },
      ],
      lastUpdated: '3 hours ago',
      size: '5.6 MB',
      indexes: ['id', 'patient_id', 'treatment_name']
    },
    {
      name: 'outcomes',
      count: 167,
      description: 'Clinical outcomes and follow-up data',
      schema: [
        { name: 'id', type: 'INTEGER', nullable: false, description: 'Primary key' },
        { name: 'patient_id', type: 'VARCHAR(50)', nullable: false, description: 'Reference to patient' },
        { name: 'outcome_type', type: 'VARCHAR(100)', nullable: false, description: 'Type of outcome measured' },
        { name: 'outcome_value', type: 'TEXT', nullable: true, description: 'Outcome value or result' },
        { name: 'measurement_date', type: 'DATE', nullable: true, description: 'Date of outcome measurement' },
        { name: 'notes', type: 'TEXT', nullable: true, description: 'Additional notes' },
      ],
      lastUpdated: '4 hours ago',
      size: '3.2 MB',
      indexes: ['id', 'patient_id', 'outcome_type']
    },
  ];

  const sampleData = [
    {
      id: 1,
      patient_id: 'P001',
      age: 32,
      gender: 'F',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Mitochondrial encephalopathy',
      status: 'active',
    },
    {
      id: 2,
      patient_id: 'P002',
      age: 28,
      gender: 'M',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Progressive neurological deterioration',
      status: 'active',
    },
    {
      id: 3,
      patient_id: 'P003',
      age: 45,
      gender: 'F',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Seizures, developmental delay',
      status: 'inactive',
    },
  ];

  const filteredTables = tables.filter(table =>
    table.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    table.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewSchema = (table: DatabaseTable) => {
    setSelectedTableForSchema(table);
    setIsSchemaDialogOpen(true);
  };

  const handleRunQuery = async () => {
    if (!sqlQuery.trim()) return;
    
    setIsQueryRunning(true);
    
    // Simulate query execution
    setTimeout(() => {
      const mockResults: QueryResult = {
        columns: ['id', 'patient_id', 'age', 'gender', 'diagnosis'],
        data: [
          [1, 'P001', 32, 'F', 'Leigh Syndrome'],
          [2, 'P002', 28, 'M', 'Leigh Syndrome'],
          [3, 'P003', 45, 'F', 'Leigh Syndrome'],
        ],
        rowCount: 3,
        executionTime: 0.045,
        status: 'success'
      };
      
      setQueryResults(mockResults);
      setIsQueryRunning(false);
    }, 1500);
  };

  const handleSaveQuery = () => {
    if (sqlQuery.trim() && !savedQueries.includes(sqlQuery)) {
      setSavedQueries([...savedQueries, sqlQuery]);
    }
  };

  const handleLoadQuery = (query: string) => {
    setSqlQuery(query);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckIcon color="success" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      default: return <InfoIcon color="info" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Database Management & Query Interface
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and explore your biomedical data, tables, schema, and execute custom queries
        </Typography>
      </Box>

      {/* Database Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Tables</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {tables.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active database tables
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TableChartIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Records</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {tables.reduce((sum, table) => sum + table.count, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all tables
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BackupIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Last Backup</Typography>
              </Box>
              <Typography variant="h6" color="primary">
                2 hours ago
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Automated backup
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Status</Typography>
              </Box>
              <Typography variant="h6" color="success.main">
                Healthy
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All systems operational
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content with Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="database tabs">
            <Tab label="Tables Overview" />
            <Tab label="Schema Browser" />
            <Tab label="Query Interface" />
            <Tab label="Data Explorer" />
            <Tab label="Maintenance" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {/* Tables Overview */}
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  placeholder="Search tables..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setIsAddDialogOpen(true)}
                  >
                    Add Table
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<UploadIcon />}
                  >
                    Import Data
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                  >
                    Export
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
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              {filteredTables.map((table) => (
                <Card key={table.name} sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {table.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {table.description}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                          <Chip 
                            label={`${table.count} records`} 
                            size="small" 
                            color="primary" 
                            variant="outlined" 
                          />
                          <Chip 
                            label={table.size} 
                            size="small" 
                            color="secondary" 
                            variant="outlined" 
                          />
                          <Typography variant="caption" color="text.secondary">
                            Last updated: {table.lastUpdated}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Schema">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleViewSchema(table)}
                          >
                            <SchemaIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Browse Data">
                          <IconButton size="small" color="secondary">
                            <TableChartIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Table">
                          <IconButton size="small" color="info">
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Table">
                          <IconButton size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<BackupIcon />}
                    onClick={() => setIsBackupDialogOpen(true)}
                    sx={{ mb: 2 }}
                  >
                    Create Backup
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<StorageIcon />}
                    sx={{ mb: 2 }}
                  >
                    Optimize Database
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<CodeIcon />}
                    onClick={() => setIsQueryDialogOpen(true)}
                  >
                    Run Query
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Database Health
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Storage Usage
                    </Typography>
                    <LinearProgress variant="determinate" value={65} sx={{ mb: 1 }} />
                    <Typography variant="caption" color="text.secondary">
                      65% used (2.3 GB / 3.5 GB)
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Performance
                    </Typography>
                    <LinearProgress variant="determinate" value={85} sx={{ mb: 1 }} />
                    <Typography variant="caption" color="text.secondary">
                      85% optimal
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Schema Browser */}
          <Typography variant="h6" gutterBottom>
            Database Schema Browser
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Explore the structure and relationships of your database tables.
          </Typography>

          <Grid container spacing={3}>
            {tables.map((table) => (
              <Grid item xs={12} md={6} key={table.name}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <DatabaseIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">
                        {table.name}
                      </Typography>
                      <Chip 
                        label={`${table.schema.length} columns`} 
                        size="small" 
                        color="primary" 
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                    
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="body2">View Schema</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Column</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Nullable</TableCell>
                                <TableCell>Default</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {table.schema.map((column) => (
                                <TableRow key={column.name}>
                                  <TableCell>
                                    <Typography variant="body2" fontWeight="medium">
                                      {column.name}
                                    </Typography>
                                    {column.description && (
                                      <Typography variant="caption" color="text.secondary" display="block">
                                        {column.description}
                                      </Typography>
                                    )}
                                  </TableCell>
                                  <TableCell>
                                    <Chip 
                                      label={column.type} 
                                      size="small" 
                                      variant="outlined" 
                                    />
                                  </TableCell>
                                  <TableCell>
                                    <Chip 
                                      label={column.nullable ? 'Yes' : 'No'} 
                                      size="small" 
                                      color={column.nullable ? 'warning' : 'success'} 
                                    />
                                  </TableCell>
                                  <TableCell>
                                    {column.defaultValue ? (
                                      <Chip 
                                        label={column.defaultValue} 
                                        size="small" 
                                        variant="outlined" 
                                      />
                                    ) : (
                                      <Typography variant="caption" color="text.secondary">
                                        None
                                      </Typography>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                        
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Indexes: {table.indexes.join(', ')}
                          </Typography>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Query Interface */}
          <Typography variant="h6" gutterBottom>
            SQL Query Interface
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Execute custom SQL queries against your database. Use the query builder or write raw SQL.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      SQL Query Editor
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={8}
                      value={sqlQuery}
                      onChange={(e) => setSqlQuery(e.target.value)}
                      placeholder="Enter your SQL query here...\nExample: SELECT * FROM patients WHERE age > 30"
                      variant="outlined"
                      sx={{ fontFamily: 'monospace' }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      startIcon={isQueryRunning ? <StopIcon /> : <PlayIcon />}
                      onClick={handleRunQuery}
                      disabled={isQueryRunning || !sqlQuery.trim()}
                    >
                      {isQueryRunning ? 'Running...' : 'Execute Query'}
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveQuery}
                      disabled={!sqlQuery.trim()}
                    >
                      Save Query
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<CopyIcon />}
                      onClick={() => navigator.clipboard.writeText(sqlQuery)}
                      disabled={!sqlQuery.trim()}
                    >
                      Copy
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => setSqlQuery('')}
                      disabled={!sqlQuery.trim()}
                    >
                      Clear
                    </Button>
                  </Box>
                </CardContent>
              </Card>

              {/* Query Results */}
              {queryResults && (
                <Card variant="outlined" sx={{ mt: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ mr: 2 }}>
                        Query Results
                      </Typography>
                      <Chip 
                        icon={getStatusIcon(queryResults.status)} 
                        label={queryResults.status} 
                        color={queryResults.status === 'success' ? 'success' : queryResults.status === 'error' ? 'error' : 'warning'} 
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                        {queryResults.rowCount} rows in {queryResults.executionTime}s
                      </Typography>
                    </Box>
                    
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            {queryResults.columns.map((column) => (
                              <TableCell key={column}>{column}</TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {queryResults.data.map((row, index) => (
                            <TableRow key={index}>
                              {row.map((cell, cellIndex) => (
                                <TableCell key={cellIndex}>{cell}</TableCell>
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

            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Saved Queries
                  </Typography>
                  {savedQueries.length > 0 ? (
                    <List dense>
                      {savedQueries.map((query, index) => (
                        <ListItem key={index} sx={{ px: 0 }}>
                          <ListItemText
                            primary={
                              <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                                {query.substring(0, 50)}...
                              </Typography>
                            }
                          />
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <IconButton 
                              size="small" 
                              onClick={() => handleLoadQuery(query)}
                            >
                              <PlayIcon />
                            </IconButton>
                            <IconButton size="small">
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No saved queries yet
                    </Typography>
                  )}
                </CardContent>
              </Card>

              <Card variant="outlined" sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Query Templates
                  </Typography>
                  <Stack spacing={1}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setSqlQuery('SELECT * FROM patients LIMIT 10')}
                    >
                      Basic Select
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setSqlQuery('SELECT COUNT(*) as total FROM patients')}
                    >
                      Count Records
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setSqlQuery('SELECT * FROM patients WHERE age > 30')}
                    >
                      Filter by Age
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setSqlQuery('SELECT diagnosis, COUNT(*) as count FROM patients GROUP BY diagnosis')}
                    >
                      Group by Diagnosis
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Data Explorer */}
          <Typography variant="h6" gutterBottom>
            Data Explorer
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Browse and explore data from your database tables with filtering and pagination.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Table</InputLabel>
                <Select
                  value={selectedTable}
                  label="Select Table"
                  onChange={(e) => setSelectedTable(e.target.value)}
                >
                  <MenuItem value="all">All Tables</MenuItem>
                  {tables.map((table) => (
                    <MenuItem key={table.name} value={table.name}>
                      {table.name} ({table.count} records)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {selectedTable !== 'all' && (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {selectedTable} - Sample Data
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        {Object.keys(sampleData[0] || {}).map((key) => (
                          <TableCell key={key}>{key}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sampleData.map((row, index) => (
                        <TableRow key={index}>
                          {Object.values(row).map((value, cellIndex) => (
                            <TableCell key={cellIndex}>{value}</TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          {/* Database Maintenance */}
          <Typography variant="h6" gutterBottom>
            Database Maintenance
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Perform maintenance tasks to keep your database healthy and optimized.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Backup & Recovery
                  </Typography>
                  <Stack spacing={2}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<BackupIcon />}
                      onClick={() => setIsBackupDialogOpen(true)}
                    >
                      Create Backup
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<UploadIcon />}
                    >
                      Restore from Backup
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                    >
                      Download Backup
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Optimization
                  </Typography>
                  <Stack spacing={2}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<StorageIcon />}
                    >
                      Optimize Tables
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<TableChartIcon />}
                    >
                      Analyze Tables
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                    >
                      Update Statistics
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>

      {/* Add Table Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Table</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Table Name"
            margin="normal"
            placeholder="e.g., clinical_notes"
          />
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            placeholder="Describe the purpose of this table..."
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Table Type</InputLabel>
            <Select label="Table Type">
              <MenuItem value="patient">Patient Data</MenuItem>
              <MenuItem value="clinical">Clinical Data</MenuItem>
              <MenuItem value="genetic">Genetic Data</MenuItem>
              <MenuItem value="phenotype">Phenotype Data</MenuItem>
              <MenuItem value="custom">Custom</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsAddDialogOpen(false)}>
            Create Table
          </Button>
        </DialogActions>
      </Dialog>

      {/* Backup Dialog */}
      <Dialog open={isBackupDialogOpen} onClose={() => setIsBackupDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Database Backup</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will create a complete backup of your database including all tables and data.
          </Alert>
          <TextField
            fullWidth
            label="Backup Name"
            margin="normal"
            placeholder="backup_2024_01_15"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Backup Type</InputLabel>
            <Select label="Backup Type">
              <MenuItem value="full">Full Backup</MenuItem>
              <MenuItem value="incremental">Incremental Backup</MenuItem>
              <MenuItem value="schema">Schema Only</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsBackupDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsBackupDialogOpen(false)}>
            Start Backup
          </Button>
        </DialogActions>
      </Dialog>

      {/* Schema Dialog */}
      <Dialog open={isSchemaDialogOpen} onClose={() => setIsSchemaDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          Table Schema - {selectedTableForSchema?.name}
          <IconButton
            aria-label="close"
            onClick={() => setIsSchemaDialogOpen(false)}
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
          {selectedTableForSchema && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Table Information
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Records:</Typography>
                  <Typography variant="body1">{selectedTableForSchema.count}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Size:</Typography>
                  <Typography variant="body1">{selectedTableForSchema.size}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Last Updated:</Typography>
                  <Typography variant="body1">{selectedTableForSchema.lastUpdated}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Indexes:</Typography>
                  <Typography variant="body1">{selectedTableForSchema.indexes.length}</Typography>
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom>
                Column Schema
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Column Name</TableCell>
                      <TableCell>Data Type</TableCell>
                      <TableCell>Nullable</TableCell>
                      <TableCell>Default Value</TableCell>
                      <TableCell>Description</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedTableForSchema.schema.map((column) => (
                      <TableRow key={column.name}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {column.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={column.type} 
                            size="small" 
                            variant="outlined" 
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={column.nullable ? 'Yes' : 'No'} 
                            size="small" 
                            color={column.nullable ? 'warning' : 'success'} 
                          />
                        </TableCell>
                        <TableCell>
                          {column.defaultValue ? (
                            <Chip 
                              label={column.defaultValue} 
                              size="small" 
                              variant="outlined" 
                            />
                          ) : (
                            <Typography variant="caption" color="text.secondary">
                              None
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {column.description || 'No description'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Indexes
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedTableForSchema.indexes.map((index) => (
                    <Chip 
                      key={index} 
                      label={index} 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsSchemaDialogOpen(false)}>Close</Button>
          <Button variant="outlined">
            Export Schema
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Database;
