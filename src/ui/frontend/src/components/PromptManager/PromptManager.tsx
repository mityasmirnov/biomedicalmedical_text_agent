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
} from '@mui/material';
import {
  Chat as ChatIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Code as CodeIcon,
  Psychology as PsychologyIcon,
  AutoFixHigh as AutoFixIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  PlayArrow as TestIcon,
  History as HistoryIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface Prompt {
  id: string;
  name: string;
  description: string;
  content: string;
  category: 'system' | 'agent' | 'langextract' | 'validation' | 'custom';
  tags: string[];
  version: string;
  status: 'active' | 'draft' | 'archived' | 'testing';
  createdAt: string;
  lastModified: string;
  lastUsed: string;
  usageCount: number;
  isDefault: boolean;
  isPublic: boolean;
  author: string;
  variables: PromptVariable[];
  examples: PromptExample[];
  performance: PromptPerformance;
}

interface PromptVariable {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  defaultValue?: string;
  validation?: string;
}

interface PromptExample {
  id: string;
  title: string;
  input: string;
  output: string;
  description: string;
}

interface PromptPerformance {
  successRate: number;
  averageResponseTime: number;
  tokenUsage: number;
  costPerRequest: number;
  lastTested: string;
}

const validationSchema = yup.object({
  name: yup.string().required('Prompt name is required'),
  description: yup.string().required('Description is required'),
  content: yup.string().min(10, 'Content must be at least 10 characters').required('Content is required'),
  category: yup.string().required('Category is required'),
  tags: yup.array().of(yup.string()).min(1, 'At least one tag is required'),
});

const PromptManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [isAddPromptDialogOpen, setIsAddPromptDialogOpen] = useState(false);
  const [isEditPromptDialogOpen, setIsEditPromptDialogOpen] = useState(false);
  const [isViewPromptDialogOpen, setIsViewPromptDialogOpen(false);
  const [isTestPromptDialogOpen, setIsTestPromptDialogOpen] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      name: '',
      description: '',
      content: '',
      category: 'system',
      tags: [],
    }
  });

  // Sample data
  const [prompts] = useState<Prompt[]>([
    {
      id: '1',
      name: 'Biomedical Literature Extractor',
      description: 'Extract structured data from biomedical research papers',
      content: `You are a biomedical literature extraction expert. Your task is to extract structured information from research papers.

Please extract the following information:
- Phenotypes (HPO terms)
- Genes (HGNC symbols)
- Treatments
- Demographics
- Study design

Format the output as JSON with the following structure:
{
  "phenotypes": [],
  "genes": [],
  "treatments": [],
  "demographics": {},
  "study_design": {}
}

Paper text: {{paper_text}}`,
      category: 'langextract',
      tags: ['biomedical', 'extraction', 'phenotypes', 'genes'],
      version: '1.2.0',
      status: 'active',
      createdAt: '2024-01-01',
      lastModified: '2024-01-15',
      lastUsed: '2024-01-15 14:30',
      usageCount: 1250,
      isDefault: true,
      isPublic: true,
      author: 'System Admin',
      variables: [
        {
          name: 'paper_text',
          description: 'The full text of the research paper',
          type: 'string',
          required: true,
        },
        {
          name: 'extraction_level',
          description: 'Level of detail for extraction (basic, detailed, comprehensive)',
          type: 'string',
          required: false,
          defaultValue: 'detailed',
        }
      ],
      examples: [
        {
          id: '1',
          title: 'Mitochondrial Disorder Paper',
          input: 'A patient with mitochondrial disorder presented with...',
          output: '{"phenotypes": ["HP:0001250"], "genes": ["MT-ATP6"]}',
          description: 'Example extraction from mitochondrial disorder research',
        }
      ],
      performance: {
        successRate: 94.2,
        averageResponseTime: 2.3,
        tokenUsage: 1250,
        costPerRequest: 0.0375,
        lastTested: '2024-01-15',
      },
    },
    {
      id: '2',
      name: 'Data Validation Agent',
      description: 'Validate and verify extracted biomedical data',
      content: `You are a data validation specialist. Review the extracted data for accuracy and completeness.

Validation tasks:
1. Check phenotype terms against HPO database
2. Verify gene symbols against HGNC
3. Validate treatment names
4. Ensure demographic data consistency

Data to validate: {{extracted_data}}

Provide validation results with confidence scores and suggestions for corrections.`,
      category: 'validation',
      tags: ['validation', 'quality control', 'data verification'],
      version: '1.0.0',
      status: 'active',
      createdAt: '2024-01-05',
      lastModified: '2024-01-10',
      lastUsed: '2024-01-15 13:45',
      usageCount: 890,
      isDefault: false,
      isPublic: true,
      author: 'Data Team',
      variables: [
        {
          name: 'extracted_data',
          description: 'The extracted data to validate',
          type: 'object',
          required: true,
        }
      ],
      examples: [],
      performance: {
        successRate: 96.8,
        averageResponseTime: 1.8,
        tokenUsage: 890,
        costPerRequest: 0.0267,
        lastTested: '2024-01-10',
      },
    },
    {
      id: '3',
      name: 'System Orchestrator',
      description: 'Coordinate system operations and agent interactions',
      content: `You are the system orchestrator responsible for coordinating the biomedical text processing pipeline.

Your responsibilities:
- Monitor agent status and performance
- Route documents to appropriate agents
- Handle error recovery and retries
- Optimize resource allocation

Current system status: {{system_status}}
Active agents: {{active_agents}}
Queue length: {{queue_length}}

Provide recommendations for system optimization.`,
      category: 'system',
      tags: ['orchestration', 'system management', 'monitoring'],
      version: '2.1.0',
      status: 'active',
      createdAt: '2023-12-01',
      lastModified: '2024-01-12',
      lastUsed: '2024-01-15 12:00',
      usageCount: 567,
      isDefault: true,
      isPublic: false,
      author: 'System Admin',
      variables: [
        {
          name: 'system_status',
          description: 'Current system health status',
          type: 'string',
          required: true,
        },
        {
          name: 'active_agents',
          description: 'List of currently active agents',
          type: 'array',
          required: true,
        },
        {
          name: 'queue_length',
          description: 'Number of items in processing queue',
          type: 'number',
          required: true,
        }
      ],
      examples: [],
      performance: {
        successRate: 99.1,
        averageResponseTime: 0.5,
        tokenUsage: 450,
        costPerRequest: 0.0135,
        lastTested: '2024-01-12',
      },
    },
  ]);

  const filteredPrompts = prompts.filter(prompt =>
    (selectedCategory === 'all' || prompt.category === selectedCategory) &&
    (selectedStatus === 'all' || prompt.status === selectedStatus) &&
    (searchQuery === '' || 
     prompt.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     prompt.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
     prompt.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleAddPrompt = (data: any) => {
    console.log('Adding new prompt:', data);
    setIsAddPromptDialogOpen(false);
    reset();
    setSnackbar({ open: true, message: 'Prompt added successfully', severity: 'success' });
  };

  const handleEditPrompt = (data: any) => {
    console.log('Editing prompt:', data);
    setIsEditPromptDialogOpen(false);
    setSnackbar({ open: true, message: 'Prompt updated successfully', severity: 'success' });
  };

  const handleDeletePrompt = (id: string) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      console.log('Deleting prompt:', id);
      setSnackbar({ open: true, message: 'Prompt deleted successfully', severity: 'success' });
    }
  };

  const handleTestPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setIsTestPromptDialogOpen(true);
  };

  const handleCopyPrompt = (prompt: Prompt) => {
    navigator.clipboard.writeText(prompt.content);
    setSnackbar({ open: true, message: 'Prompt content copied to clipboard', severity: 'info' });
  };

  const handleToggleDefault = (prompt: Prompt) => {
    console.log('Toggling default status for:', prompt.id);
    setSnackbar({ open: true, message: 'Default status updated', severity: 'info' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'archived': return 'default';
      case 'testing': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <ValidIcon />;
      case 'draft': return <WarningIcon />;
      case 'archived': return <InfoIcon />;
      case 'testing': return <AutoFixIcon />;
      default: return <InfoIcon />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'system': return <SettingsIcon />;
      case 'agent': return <PsychologyIcon />;
      case 'langextract': return <CodeIcon />;
      case 'validation': return <ValidIcon />;
      default: return <ChatIcon />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'system': return 'primary';
      case 'agent': return 'secondary';
      case 'langextract': return 'success';
      case 'validation': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Prompt Management System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage system prompts, agent prompts, and LangExtract instructions
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="All Prompts" icon={<ChatIcon />} />
          <Tab label="System Prompts" icon={<SettingsIcon />} />
          <Tab label="Agent Prompts" icon={<PsychologyIcon />} />
          <Tab label="LangExtract" icon={<CodeIcon />} />
          <Tab label="Templates" icon={<AutoFixIcon />} />
        </Tabs>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search prompts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <ChatIcon sx={{ mr: 1, color: 'text.secondary' }} />,
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
                  <MenuItem value="system">System</MenuItem>
                  <MenuItem value="agent">Agent</MenuItem>
                  <MenuItem value="langextract">LangExtract</MenuItem>
                  <MenuItem value="validation">Validation</MenuItem>
                  <MenuItem value="custom">Custom</MenuItem>
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
                  <MenuItem value="archived">Archived</MenuItem>
                  <MenuItem value="testing">Testing</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsAddPromptDialogOpen(true)}
                fullWidth
              >
                Add Prompt
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

      {/* Prompts Grid */}
      <Grid container spacing={3}>
        {filteredPrompts.map((prompt) => (
          <Grid item xs={12} md={6} lg={4} key={prompt.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getCategoryIcon(prompt.category)}
                    <Typography variant="h6" component="h2" noWrap sx={{ maxWidth: 200 }}>
                      {prompt.name}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {prompt.isDefault && (
                      <Chip label="Default" size="small" color="primary" />
                    )}
                    <Chip
                      icon={getStatusIcon(prompt.status)}
                      label={prompt.status}
                      color={getStatusColor(prompt.status) as any}
                      size="small"
                    />
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                  {prompt.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Category & Tags
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    <Chip 
                      label={prompt.category} 
                      size="small" 
                      color={getCategoryColor(prompt.category) as any}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {prompt.tags.slice(0, 3).map((tag, index) => (
                      <Chip key={index} label={tag} size="small" variant="outlined" />
                    ))}
                    {prompt.tags.length > 3 && (
                      <Chip label={`+${prompt.tags.length - 3}`} size="small" />
                    )}
                  </Box>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Performance
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Success Rate
                    </Typography>
                    <Typography variant="caption" fontWeight="medium">
                      {prompt.performance.successRate}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={prompt.performance.successRate}
                    sx={{ height: 6, borderRadius: 3 }}
                    color={prompt.performance.successRate > 90 ? 'success' : prompt.performance.successRate > 70 ? 'warning' : 'error'}
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    v{prompt.version} • {prompt.usageCount} uses
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {prompt.lastUsed}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setSelectedPrompt(prompt);
                      setIsViewPromptDialogOpen(true);
                    }}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setSelectedPrompt(prompt);
                      setIsEditPromptDialogOpen(true);
                    }}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleTestPrompt(prompt)}
                  >
                    Test
                  </Button>
                  <IconButton
                    size="small"
                    onClick={() => handleCopyPrompt(prompt)}
                    title="Copy prompt content"
                  >
                    <CopyIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleToggleDefault(prompt)}
                    title={prompt.isDefault ? 'Remove as default' : 'Set as default'}
                  >
                    {prompt.isDefault ? <StarIcon color="primary" /> : <StarBorderIcon />}
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Add Prompt Dialog */}
      <Dialog open={isAddPromptDialogOpen} onClose={() => setIsAddPromptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Add New Prompt</DialogTitle>
        <form onSubmit={handleSubmit(handleAddPrompt)}>
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
                      label="Prompt Name"
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
                        <MenuItem value="system">System</MenuItem>
                        <MenuItem value="agent">Agent</MenuItem>
                        <MenuItem value="langextract">LangExtract</MenuItem>
                        <MenuItem value="validation">Validation</MenuItem>
                        <MenuItem value="custom">Custom</MenuItem>
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
                      rows={2}
                      error={!!errors.description}
                      helperText={errors.description?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="tags"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      multiple
                      freeSolo
                      options={['biomedical', 'extraction', 'validation', 'system', 'agent']}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Tags"
                          error={!!errors.tags}
                          helperText={errors.tags?.message}
                        />
                      )}
                      onChange={(event, newValue) => field.onChange(newValue)}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="content"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Prompt Content"
                      multiline
                      rows={8}
                      error={!!errors.content}
                      helperText={errors.content?.message}
                      placeholder="Enter your prompt content here. Use {{variable_name}} for dynamic variables."
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsAddPromptDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Add Prompt</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Prompt Dialog */}
      <Dialog open={isEditPromptDialogOpen} onClose={() => setIsEditPromptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Edit Prompt</DialogTitle>
        <form onSubmit={handleSubmit(handleEditPrompt)}>
          <DialogContent>
            {selectedPrompt && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Prompt Name"
                    defaultValue={selectedPrompt.name}
                    name="name"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select defaultValue={selectedPrompt.category} label="Category">
                      <MenuItem value="system">System</MenuItem>
                      <MenuItem value="agent">Agent</MenuItem>
                      <MenuItem value="langextract">LangExtract</MenuItem>
                      <MenuItem value="validation">Validation</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={2}
                    defaultValue={selectedPrompt.description}
                    name="description"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Autocomplete
                    multiple
                    freeSolo
                    options={['biomedical', 'extraction', 'validation', 'system', 'agent']}
                    defaultValue={selectedPrompt.tags}
                    renderInput={(params) => (
                      <TextField {...params} label="Tags" />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Prompt Content"
                    multiline
                    rows={8}
                    defaultValue={selectedPrompt.content}
                    name="content"
                  />
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditPromptDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save Changes</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Prompt Dialog */}
      <Dialog open={isViewPromptDialogOpen} onClose={() => setIsViewPromptDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Prompt Details</DialogTitle>
        <DialogContent>
          {selectedPrompt && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>{selectedPrompt.name}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedPrompt.description}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Basic Information</Typography>
                <Typography variant="body2">Category: {selectedPrompt.category}</Typography>
                <Typography variant="body2">Version: {selectedPrompt.version}</Typography>
                <Typography variant="body2">Status: {selectedPrompt.status}</Typography>
                <Typography variant="body2">Author: {selectedPrompt.author}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Usage & Performance</Typography>
                <Typography variant="body2">Usage Count: {selectedPrompt.usageCount}</Typography>
                <Typography variant="body2">Success Rate: {selectedPrompt.performance.successRate}%</Typography>
                <Typography variant="body2">Last Used: {selectedPrompt.lastUsed}</Typography>
                <Typography variant="body2">Last Modified: {selectedPrompt.lastModified}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Tags</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedPrompt.tags.map((tag, index) => (
                    <Chip key={index} label={tag} size="small" variant="outlined" />
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Variables</Typography>
                {selectedPrompt.variables.length > 0 ? (
                  <List dense>
                    {selectedPrompt.variables.map((variable, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={`{{${variable.name}}} - ${variable.type}`}
                          secondary={variable.description}
                        />
                        {variable.required && <Chip label="Required" size="small" color="primary" />}
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">No variables defined</Typography>
                )}
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Prompt Content</Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  value={selectedPrompt.content}
                  InputProps={{ readOnly: true }}
                  variant="outlined"
                  sx={{ fontFamily: 'monospace' }}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsViewPromptDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setIsViewPromptDialogOpen(false);
              setIsEditPromptDialogOpen(true);
            }}
          >
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Prompt Dialog */}
      <Dialog open={isTestPromptDialogOpen} onClose={() => setIsTestPromptDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Test Prompt: {selectedPrompt?.name}</DialogTitle>
        <DialogContent>
          {selectedPrompt && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Prompt Content</Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={selectedPrompt.content}
                  InputProps={{ readOnly: true }}
                  variant="outlined"
                  sx={{ fontFamily: 'monospace', mb: 2 }}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Test Variables</Typography>
                {selectedPrompt.variables.map((variable, index) => (
                  <TextField
                    key={index}
                    fullWidth
                    label={`${variable.name} (${variable.type})`}
                    placeholder={variable.description}
                    defaultValue={variable.defaultValue || ''}
                    sx={{ mb: 2 }}
                  />
                ))}
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="contained"
                  startIcon={<TestIcon />}
                  onClick={() => {
                    setSnackbar({ open: true, message: 'Prompt test executed successfully', severity: 'success' });
                  }}
                  fullWidth
                >
                  Execute Test
                </Button>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsTestPromptDialogOpen(false)}>Close</Button>
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

export default PromptManager;