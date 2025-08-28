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
  // TreeView and TreeItem are imported separately
  Autocomplete,
  Checkbox,
  FormGroup,
} from '@mui/material';
import { TreeView, TreeItem } from '@mui/x-tree-view';
import {
  School as SchoolIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Category as CategoryIcon,
  Science as ScienceIcon,
  AutoFixHigh as AutoFixIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  PlayArrow as TestIcon,
  History as HistoryIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Link as LinkIcon,
  LinkOff as UnlinkIcon,
  Schema as SchemaIcon,
  DataObject as DataObjectIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface OntologyConcept {
  id: string;
  name: string;
  description: string;
  category: 'phenotype' | 'gene' | 'disease' | 'treatment' | 'anatomy' | 'process';
  synonyms: string[];
  parentConcepts: string[];
  childConcepts: string[];
  relatedConcepts: string[];
  externalIds: { source: string; id: string }[];
  status: 'active' | 'draft' | 'deprecated' | 'proposed';
  confidence: number;
  lastUpdated: string;
  createdBy: string;
  usageCount: number;
  properties: { [key: string]: any };
}

interface OntologyCategory {
  name: string;
  description: string;
  conceptCount: number;
  lastUpdated: string;
  status: 'active' | 'archived' | 'processing';
}

interface OntologyRelationship {
  id: string;
  sourceConcept: string;
  targetConcept: string;
  relationshipType: 'is_a' | 'part_of' | 'regulates' | 'associated_with' | 'treats' | 'causes';
  confidence: number;
  evidence: string[];
  status: 'validated' | 'proposed' | 'deprecated';
}

const validationSchema = yup.object({
  name: yup.string().required('Concept name is required'),
  description: yup.string().required('Description is required'),
  category: yup.string().required('Category is required'),
  synonyms: yup.array().of(yup.string()),
  parentConcepts: yup.array().of(yup.string()),
});

const KnowledgeBaseManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [isAddConceptDialogOpen, setIsAddConceptDialogOpen] = useState(false);
  const [isEditConceptDialogOpen, setIsEditConceptDialogOpen] = useState(false);
  const [isViewConceptDialogOpen, setIsViewConceptDialogOpen] = useState(false);
  const [isAddRelationshipDialogOpen, setIsAddRelationshipDialogOpen] = useState(false);
  const [selectedConcept, setSelectedConcept] = useState<OntologyConcept | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [expandedConcepts, setExpandedConcepts] = useState<string[]>([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      name: '',
      description: '',
      category: 'phenotype',
      synonyms: [],
      parentConcepts: [],
    }
  });

  // Sample data
  const [concepts] = useState<OntologyConcept[]>([
    {
      id: '1',
      name: 'Seizure',
      description: 'A sudden, uncontrolled electrical disturbance in the brain that can cause changes in behavior, movements, feelings, and levels of consciousness.',
      category: 'phenotype',
      synonyms: ['Epileptic seizure', 'Convulsion', 'Fit'],
      parentConcepts: ['Neurological phenotype'],
      childConcepts: ['Generalized seizure', 'Focal seizure', 'Absence seizure'],
      relatedConcepts: ['Epilepsy', 'Brain disorder', 'Neurological symptom'],
      externalIds: [
        { source: 'HPO', id: 'HP:0001250' },
        { source: 'SNOMED', id: '91175000' },
      ],
      status: 'active',
      confidence: 95.2,
      lastUpdated: '2024-01-15',
      createdBy: 'System Admin',
      usageCount: 1250,
      properties: {
        severity: 'variable',
        onset: 'any age',
        frequency: 'variable',
      },
    },
    {
      id: '2',
      name: 'MT-ATP6',
      description: 'Mitochondrial ATP synthase 6 gene, involved in oxidative phosphorylation and energy production.',
      category: 'gene',
      synonyms: ['ATP6', 'ATP synthase 6', 'Mitochondrial ATP6'],
      parentConcepts: ['Mitochondrial gene', 'Energy metabolism gene'],
      childConcepts: [],
      relatedConcepts: ['ATP synthase', 'Mitochondrial disorder', 'Energy metabolism'],
      externalIds: [
        { source: 'HGNC', id: 'HGNC:741' },
        { source: 'Ensembl', id: 'ENSG00000198899' },
      ],
      status: 'active',
      confidence: 98.7,
      lastUpdated: '2024-01-14',
      createdBy: 'Gene Curator',
      usageCount: 890,
      properties: {
        chromosome: 'MT',
        function: 'ATP synthesis',
        disease_association: 'Leigh syndrome',
      },
    },
    {
      id: '3',
      name: 'Leigh Syndrome',
      description: 'A severe neurological disorder that typically arises in the first year of life, characterized by progressive loss of mental and movement abilities.',
      category: 'disease',
      synonyms: ['Leigh disease', 'Subacute necrotizing encephalomyelopathy'],
      parentConcepts: ['Mitochondrial disorder', 'Neurological disease'],
      childConcepts: ['Classic Leigh syndrome', 'Atypical Leigh syndrome'],
      relatedConcepts: ['Mitochondrial dysfunction', 'Neurological degeneration'],
      externalIds: [
        { source: 'OMIM', id: '256000' },
        { source: 'Orphanet', id: 'ORPHA506' },
      ],
      status: 'active',
      confidence: 92.1,
      lastUpdated: '2024-01-13',
      createdBy: 'Disease Curator',
      usageCount: 720,
      properties: {
        inheritance: 'autosomal recessive',
        age_of_onset: 'infancy',
        prognosis: 'poor',
      },
    },
  ]);

  const [categories] = useState<OntologyCategory[]>([
    {
      name: 'Phenotypes',
      description: 'Observable characteristics and clinical features',
      conceptCount: 1250,
      lastUpdated: '2024-01-15',
      status: 'active',
    },
    {
      name: 'Genes',
      description: 'Genetic elements and their functions',
      conceptCount: 890,
      lastUpdated: '2024-01-14',
      status: 'active',
    },
    {
      name: 'Diseases',
      description: 'Medical conditions and disorders',
      conceptCount: 720,
      lastUpdated: '2024-01-13',
      status: 'active',
    },
    {
      name: 'Treatments',
      description: 'Therapeutic interventions and medications',
      conceptCount: 450,
      lastUpdated: '2024-01-12',
      status: 'active',
    },
  ]);

  const [relationships] = useState<OntologyRelationship[]>([
    {
      id: '1',
      sourceConcept: 'Seizure',
      targetConcept: 'Epilepsy',
      relationshipType: 'is_a',
      confidence: 95.2,
      evidence: ['Clinical guidelines', 'Literature review'],
      status: 'validated',
    },
    {
      id: '2',
      sourceConcept: 'MT-ATP6',
      targetConcept: 'Leigh Syndrome',
      relationshipType: 'causes',
      confidence: 87.3,
      evidence: ['Genetic studies', 'Case reports'],
      status: 'validated',
    },
  ]);

  const filteredConcepts = concepts.filter(concept =>
    (selectedCategory === 'all' || concept.category === selectedCategory) &&
    (selectedStatus === 'all' || concept.status === selectedStatus) &&
    (searchQuery === '' || 
     concept.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     concept.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
     concept.synonyms.some(synonym => synonym.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleAddConcept = (data: any) => {
    console.log('Adding new concept:', data);
    setIsAddConceptDialogOpen(false);
    reset();
    setSnackbar({ open: true, message: 'Concept added successfully', severity: 'success' });
  };

  const handleEditConcept = (data: any) => {
    console.log('Editing concept:', data);
    setIsEditConceptDialogOpen(false);
    setSnackbar({ open: true, message: 'Concept updated successfully', severity: 'success' });
  };

  const handleDeleteConcept = (id: string) => {
    if (window.confirm('Are you sure you want to delete this concept?')) {
      console.log('Deleting concept:', id);
      setSnackbar({ open: true, message: 'Concept deleted successfully', severity: 'success' });
    }
  };

  const handleToggleExpansion = (conceptId: string) => {
    setExpandedConcepts(prev => 
      prev.includes(conceptId) 
        ? prev.filter(id => id !== conceptId)
        : [...prev, conceptId]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'deprecated': return 'error';
      case 'proposed': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <ValidIcon />;
      case 'draft': return <WarningIcon />;
      case 'deprecated': return <InvalidIcon />;
      case 'proposed': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'phenotype': return <ScienceIcon />;
      case 'gene': return <DataObjectIcon />;
      case 'disease': return <WarningIcon />;
      case 'treatment': return <AutoFixIcon />;
      case 'anatomy': return <CategoryIcon />;
      case 'process': return <SchemaIcon />;
      default: return <SchoolIcon />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'phenotype': return 'primary';
      case 'gene': return 'secondary';
      case 'disease': return 'error';
      case 'treatment': return 'success';
      case 'anatomy': return 'warning';
      case 'process': return 'info';
      default: return 'default';
    }
  };

  const renderConceptTree = () => {
    const renderConcept = (concept: OntologyConcept, level: number = 0) => (
      <Box key={concept.id} sx={{ ml: level * 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5 }}>
          {concept.childConcepts.length > 0 && (
            <IconButton
              size="small"
              onClick={() => handleToggleExpansion(concept.id)}
            >
              {expandedConcepts.includes(concept.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          )}
          {getCategoryIcon(concept.category)}
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            {concept.name}
          </Typography>
          <Chip
            label={concept.status}
            size="small"
            color={getStatusColor(concept.status) as any}
          />
        </Box>
        {expandedConcepts.includes(concept.id) && concept.childConcepts.length > 0 && (
          <Box sx={{ ml: 2 }}>
            {concept.childConcepts.map(childId => {
              const childConcept = concepts.find(c => c.id === childId);
              return childConcept ? renderConcept(childConcept, level + 1) : null;
            })}
          </Box>
        )}
      </Box>
    );

    return (
      <Box>
        {concepts.filter(c => !c.parentConcepts.length).map(concept => renderConcept(concept))}
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Knowledge Base Manager
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse, edit, and manage biomedical ontology concepts and relationships
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Concepts" icon={<SchoolIcon />} />
          <Tab label="Relationships" icon={<LinkIcon />} />
          <Tab label="Categories" icon={<CategoryIcon />} />
          <Tab label="Tree View" icon={<SchemaIcon />} />
          <Tab label="Import/Export" icon={<AutoFixIcon />} />
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
                    placeholder="Search concepts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={selectedCategory}
                      label="Category"
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      <MenuItem value="all">All Categories</MenuItem>
                      {categories.map((category) => (
                        <MenuItem key={category.name} value={category.name.toLowerCase()}>
                          {category.name}
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
                      <MenuItem value="active">Active</MenuItem>
                      <MenuItem value="draft">Draft</MenuItem>
                      <MenuItem value="deprecated">Deprecated</MenuItem>
                      <MenuItem value="proposed">Proposed</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setIsAddConceptDialogOpen(true)}
                    fullWidth
                  >
                    Add Concept
                  </Button>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={() => {
                      setSearchQuery('');
                      setSelectedCategory('all');
                      setSelectedStatus('all');
                    }}
                    fullWidth
                  >
                    Clear Filters
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Concepts Grid */}
          <Grid container spacing={3}>
            {filteredConcepts.map((concept) => (
              <Grid item xs={12} md={6} lg={4} key={concept.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getCategoryIcon(concept.category)}
                        <Typography variant="h6" component="h2" noWrap sx={{ maxWidth: 200 }}>
                          {concept.name}
                        </Typography>
                      </Box>
                      <Chip
                        icon={getStatusIcon(concept.status)}
                        label={concept.status}
                        color={getStatusColor(concept.status) as any}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                      {concept.description}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Category & Status
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                        <Chip 
                          label={concept.category} 
                          size="small" 
                          color={getCategoryColor(concept.category) as any}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {concept.synonyms.slice(0, 3).map((synonym, index) => (
                          <Chip key={index} label={synonym} size="small" variant="outlined" />
                        ))}
                        {concept.synonyms.length > 3 && (
                          <Chip label={`+${concept.synonyms.length - 3}`} size="small" />
                        )}
                      </Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Confidence & Usage
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {concept.confidence}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={concept.confidence} 
                          sx={{ flexGrow: 1, height: 6 }}
                          color={concept.confidence > 90 ? 'success' : concept.confidence > 70 ? 'warning' : 'error'}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Used {concept.usageCount} times
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Updated: {concept.lastUpdated}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        By: {concept.createdBy}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedConcept(concept);
                          setIsViewConceptDialogOpen(true);
                        }}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedConcept(concept);
                          setIsEditConceptDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => setIsAddRelationshipDialogOpen(true)}
                      >
                        Add Relationship
                      </Button>
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
                Concept Relationships ({relationships.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsAddRelationshipDialogOpen(true)}
              >
                Add Relationship
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Source Concept</TableCell>
                    <TableCell>Relationship Type</TableCell>
                    <TableCell>Target Concept</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Evidence</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {relationships.map((relationship) => (
                    <TableRow key={relationship.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {relationship.sourceConcept}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={relationship.relationshipType.replace('_', ' ')} 
                          size="small" 
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {relationship.targetConcept}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {relationship.confidence}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={relationship.confidence} 
                            sx={{ width: 60, height: 6 }}
                            color={relationship.confidence > 90 ? 'success' : relationship.confidence > 70 ? 'warning' : 'error'}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={relationship.status}
                          color={relationship.status === 'validated' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {relationship.evidence.slice(0, 2).map((evidence, index) => (
                            <Chip key={index} label={evidence} size="small" variant="outlined" />
                          ))}
                          {relationship.evidence.length > 2 && (
                            <Chip label={`+${relationship.evidence.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit Relationship">
                            <IconButton size="small" color="secondary">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Relationship">
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
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          {categories.map((category) => (
            <Grid item xs={12} md={6} lg={4} key={category.name}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2">
                      {category.name}
                    </Typography>
                    <Chip 
                      label={category.status} 
                      size="small" 
                      color={category.status === 'active' ? 'success' : 'default'}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {category.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">
                      {category.conceptCount} concepts
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Updated: {category.lastUpdated}
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button size="small" variant="outlined">
                      View Concepts
                    </Button>
                    <Button size="small" variant="outlined">
                      Edit Category
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
              Ontology Tree View
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Hierarchical view of concepts and their relationships
            </Typography>
            {renderConceptTree()}
          </CardContent>
        </Card>
      )}

      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Import Ontology
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Import concepts and relationships from external sources including OBO, OWL, and CSV files.
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button variant="contained" startIcon={<AutoFixIcon />}>
                    Import from OBO File
                  </Button>
                  <Button variant="outlined" startIcon={<AutoFixIcon />}>
                    Import from OWL File
                  </Button>
                  <Button variant="outlined" startIcon={<AutoFixIcon />}>
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
                  Export Ontology
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Export the knowledge base in various formats for analysis and sharing.
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button variant="contained" startIcon={<AutoFixIcon />}>
                    Export as OBO
                  </Button>
                  <Button variant="outlined" startIcon={<AutoFixIcon />}>
                    Export as OWL
                  </Button>
                  <Button variant="outlined" startIcon={<AutoFixIcon />}>
                    Export as CSV
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add Concept Dialog */}
      <Dialog open={isAddConceptDialogOpen} onClose={() => setIsAddConceptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Add New Concept</DialogTitle>
        <form onSubmit={handleSubmit(handleAddConcept)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Concept Name"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="category"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.category}>
                      <InputLabel>Category</InputLabel>
                      <Select {...field} label="Category">
                        <MenuItem value="phenotype">Phenotype</MenuItem>
                        <MenuItem value="gene">Gene</MenuItem>
                        <MenuItem value="disease">Disease</MenuItem>
                        <MenuItem value="treatment">Treatment</MenuItem>
                        <MenuItem value="anatomy">Anatomy</MenuItem>
                        <MenuItem value="process">Process</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Description"
                      multiline
                      rows={3}
                      error={!!errors.description}
                      helperText={errors.description?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="synonyms"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      multiple
                      freeSolo
                      options={[]}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Synonyms"
                          error={!!errors.synonyms}
                          helperText={errors.synonyms?.message}
                        />
                      )}
                      onChange={(event, newValue) => field.onChange(newValue)}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsAddConceptDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Add Concept</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Concept Dialog */}
      <Dialog open={isEditConceptDialogOpen} onClose={() => setIsEditConceptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Edit Concept</DialogTitle>
        <form onSubmit={handleSubmit(handleEditConcept)}>
          <DialogContent>
            {selectedConcept && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Concept Name"
                    defaultValue={selectedConcept.name}
                    name="name"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select defaultValue={selectedConcept.category} label="Category">
                      <MenuItem value="phenotype">Phenotype</MenuItem>
                      <MenuItem value="gene">Gene</MenuItem>
                      <MenuItem value="disease">Disease</MenuItem>
                      <MenuItem value="treatment">Treatment</MenuItem>
                      <MenuItem value="anatomy">Anatomy</MenuItem>
                      <MenuItem value="process">Process</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    defaultValue={selectedConcept.description}
                    name="description"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Autocomplete
                    multiple
                    freeSolo
                    options={[]}
                    defaultValue={selectedConcept.synonyms}
                    renderInput={(params) => (
                      <TextField {...params} label="Synonyms" />
                    )}
                  />
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditConceptDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save Changes</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Concept Dialog */}
      <Dialog open={isViewConceptDialogOpen} onClose={() => setIsViewConceptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Concept Details</DialogTitle>
        <DialogContent>
          {selectedConcept && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>{selectedConcept.name}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedConcept.description}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Basic Information</Typography>
                <Typography variant="body2">Category: {selectedConcept.category}</Typography>
                <Typography variant="body2">Status: {selectedConcept.status}</Typography>
                <Typography variant="body2">Confidence: {selectedConcept.confidence}%</Typography>
                <Typography variant="body2">Created by: {selectedConcept.createdBy}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Usage & Updates</Typography>
                <Typography variant="body2">Usage Count: {selectedConcept.usageCount}</Typography>
                <Typography variant="body2">Last Updated: {selectedConcept.lastUpdated}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Synonyms</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedConcept.synonyms.map((synonym, index) => (
                    <Chip key={index} label={synonym} size="small" variant="outlined" />
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>External IDs</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedConcept.externalIds.map((externalId, index) => (
                    <Chip 
                      key={index} 
                      label={`${externalId.source}: ${externalId.id}`} 
                      size="small" 
                      variant="outlined" 
                    />
                  ))}
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsViewConceptDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setIsViewConceptDialogOpen(false);
              setIsEditConceptDialogOpen(true);
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

export default KnowledgeBaseManager;