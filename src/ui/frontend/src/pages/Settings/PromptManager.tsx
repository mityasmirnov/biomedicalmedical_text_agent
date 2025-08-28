import React, { useState, useEffect } from 'react';
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
  Tabs,
  Tab,
  Tooltip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  InputAdornment
} from '@mui/material';
import {
  Edit,
  Save,
  Delete,
  Add,
  ContentCopy,
  Refresh,
  Code,
  Settings,
  Psychology,
  Description,
  Visibility,
  VisibilityOff,
  Download,
  Upload,
  PlayArrow,
  Stop
} from '@mui/icons-material';
import { api } from '../../services/api';

interface Prompt {
  id: string;
  name: string;
  description: string;
  content: string;
  type: 'system' | 'agent' | 'langextract' | 'custom';
  agent_id?: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

interface Agent {
  id: string;
  name: string;
  description: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
}

interface LangExtractInstruction {
  id: string;
  name: string;
  description: string;
  schema: string;
  examples: string[];
  instructions: string;
  is_default: boolean;
}

const PromptManager: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [langextractInstructions, setLangExtractInstructions] = useState<LangExtractInstruction[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [instructionDialogOpen, setInstructionDialogOpen] = useState(false);
  const [editingInstruction, setEditingInstruction] = useState<LangExtractInstruction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [promptsRes, agentsRes, instructionsRes] = await Promise.all([
        api.prompts.getAll(),
        api.agents.getAll(),
        api.prompts.getLangExtractInstructions()
      ]);
      setPrompts(promptsRes.data.prompts || []);
      setAgents(agentsRes.data.agents || []);
      setLangExtractInstructions(instructionsRes.data.instructions || []);
      setError(null);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to load data - using mock data');
      // Set mock data for development
      setPrompts([
        {
          id: 'system-main',
          name: 'Main System Prompt',
          description: 'Primary system prompt for the biomedical text agent',
          content: `You are a biomedical text analysis agent specialized in extracting structured information from medical literature. Your task is to identify and extract relevant medical concepts, phenotypes, and clinical information from the provided text. Always provide confidence scores for your extractions and cite the specific text spans that support your findings.`,
          type: 'system',
          version: '1.0.0',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 'agent-extraction',
          name: 'Extraction Agent Prompt',
          description: 'Prompt for the main extraction agent',
          content: `Extract the following information from the medical text: patient demographics, clinical symptoms, laboratory findings, genetic variants, and treatment information. Format your response as structured JSON with confidence scores.`,
          type: 'agent',
          agent_id: 'extraction-agent',
          version: '1.0.0',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        }
      ]);
      setAgents([
        {
          id: 'extraction-agent',
          name: 'Extraction Agent',
          description: 'Main agent for extracting structured data from medical texts',
          type: 'extraction',
          status: 'active'
        },
        {
          id: 'validation-agent',
          name: 'Validation Agent',
          description: 'Agent for validating and cross-checking extracted information',
          type: 'validation',
          status: 'active'
        }
      ]);
      setLangExtractInstructions([
        {
          id: 'patient-extraction',
          name: 'Patient Information Extraction',
          description: 'Extract patient demographics and clinical information',
          schema: `{
            "patient": {
              "age": "number",
              "gender": "string",
              "symptoms": ["string"],
              "diagnosis": "string"
            }
          }`,
          examples: [
            'Patient is a 25-year-old male presenting with muscle weakness and fatigue.',
            '45-year-old female diagnosed with Leigh syndrome.'
          ],
          instructions: 'Identify patient age, gender, symptoms, and diagnosis from the text.',
          is_default: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrompt = async () => {
    if (!editingPrompt) return;
    
    try {
      if (editingPrompt.id.startsWith('new-')) {
        // Create new prompt
        const response = await api.prompts.create(editingPrompt);
        setPrompts(prev => [...prev, response.data.prompt]);
      } else {
        // Update existing prompt
        await api.prompts.update(editingPrompt.id, editingPrompt);
        setPrompts(prev => prev.map(p => 
          p.id === editingPrompt.id ? editingPrompt : p
        ));
      }
      
      setEditDialogOpen(false);
      setEditingPrompt(null);
    } catch (error) {
      console.error('Failed to save prompt:', error);
      alert('Failed to save prompt. Please try again.');
    }
  };

  const handleSaveInstruction = async () => {
    if (!editingInstruction) return;
    
    try {
      if (editingInstruction.id.startsWith('new-')) {
        // Create new instruction
        const response = await api.prompts.createLangExtractInstruction(editingInstruction);
        setLangExtractInstructions(prev => [...prev, response.data.instruction]);
      } else {
        // Update existing instruction
        await api.prompts.updateLangExtractInstruction(editingInstruction.id, editingInstruction);
        setLangExtractInstructions(prev => prev.map(i => 
          i.id === editingInstruction.id ? editingInstruction : i
        ));
      }
      
      setInstructionDialogOpen(false);
      setEditingInstruction(null);
    } catch (error) {
      console.error('Failed to save instruction:', error);
      alert('Failed to save instruction. Please try again.');
    }
  };

  const handleDeletePrompt = async (promptId: string) => {
    if (!window.confirm('Are you sure you want to delete this prompt?')) return;
    
    try {
      await api.prompts.delete(promptId);
      setPrompts(prev => prev.filter(p => p.id !== promptId));
    } catch (error) {
      console.error('Failed to delete prompt:', error);
      alert('Failed to delete prompt. Please try again.');
    }
  };

  const handleCopyPrompt = (prompt: Prompt) => {
    const newPrompt: Prompt = {
      ...prompt,
      id: `new-${Date.now()}`,
      name: `${prompt.name} (Copy)`,
      version: '1.0.0',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    setEditingPrompt(newPrompt);
    setEditDialogOpen(true);
  };

  const handleTestPrompt = async (prompt: Prompt) => {
    try {
      const response = await api.prompts.test(prompt.id, {
        test_text: 'Sample medical text for testing prompt effectiveness.'
      });
      alert(`Prompt test completed. Response: ${response.data.result}`);
    } catch (error) {
      console.error('Failed to test prompt:', error);
      alert('Failed to test prompt. Please try again.');
    }
  };

  const getPromptTypeIcon = (type: string) => {
    switch (type) {
      case 'system': return '⚙️';
      case 'agent': return '🤖';
      case 'langextract': return '📋';
      case 'custom': return '🔧';
      default: return '📝';
    }
  };

  const getPromptTypeColor = (type: string) => {
    switch (type) {
      case 'system': return 'primary';
      case 'agent': return 'secondary';
      case 'langextract': return 'success';
      case 'custom': return 'warning';
      default: return 'default';
    }
  };

  const filteredPrompts = prompts.filter(prompt =>
    prompt.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Prompt Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Description />
                </InputAdornment>
              )
            }}
          />
        </CardContent>
      </Card>

      {/* Main Content */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="System Prompts" />
          <Tab label="Agent Prompts" />
          <Tab label="LangExtract Instructions" />
          <Tab label="Custom Prompts" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {selectedTab === 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">System Prompts</Typography>
              <Button
                startIcon={<Add />}
                variant="contained"
                onClick={() => {
                  setEditingPrompt({
                    id: `new-${Date.now()}`,
                    name: '',
                    description: '',
                    content: '',
                    type: 'system',
                    version: '1.0.0',
                    is_active: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                  });
                  setEditDialogOpen(true);
                }}
              >
                New System Prompt
              </Button>
            </Box>
            
            <List>
              {filteredPrompts.filter(p => p.type === 'system').map((prompt) => (
                <ListItem key={prompt.id} divider>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">{prompt.name}</Typography>
                        <Chip
                          label={prompt.type}
                          size="small"
                          color={getPromptTypeColor(prompt.type)}
                        />
                        {prompt.is_active && <Chip label="Active" size="small" color="success" />}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {prompt.description}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Version: {prompt.version} | Updated: {new Date(prompt.updated_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box display="flex" gap={1}>
                      <Tooltip title="Test Prompt">
                        <IconButton onClick={() => handleTestPrompt(prompt)}>
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Copy Prompt">
                        <IconButton onClick={() => handleCopyPrompt(prompt)}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Prompt">
                        <IconButton onClick={() => {
                          setEditingPrompt(prompt);
                          setEditDialogOpen(true);
                        }}>
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Prompt">
                        <IconButton onClick={() => handleDeletePrompt(prompt.id)}>
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {selectedTab === 1 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Agent Prompts</Typography>
              <Button
                startIcon={<Add />}
                variant="contained"
                onClick={() => {
                  setEditingPrompt({
                    id: `new-${Date.now()}`,
                    name: '',
                    description: '',
                    content: '',
                    type: 'agent',
                    agent_id: '',
                    version: '1.0.0',
                    is_active: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                  });
                  setEditDialogOpen(true);
                }}
              >
                New Agent Prompt
              </Button>
            </Box>
            
            <List>
              {filteredPrompts.filter(p => p.type === 'agent').map((prompt) => (
                <ListItem key={prompt.id} divider>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">{prompt.name}</Typography>
                        <Chip
                          label={prompt.type}
                          size="small"
                          color={getPromptTypeColor(prompt.type)}
                        />
                        <Chip
                          label={agents.find(a => a.id === prompt.agent_id)?.name || 'Unknown Agent'}
                          size="small"
                          color="info"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {prompt.description}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Agent: {agents.find(a => a.id === prompt.agent_id)?.description || 'No description'}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box display="flex" gap={1}>
                      <Tooltip title="Test Prompt">
                        <IconButton onClick={() => handleTestPrompt(prompt)}>
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Copy Prompt">
                        <IconButton onClick={() => handleCopyPrompt(prompt)}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Prompt">
                        <IconButton onClick={() => {
                          setEditingPrompt(prompt);
                          setEditDialogOpen(true);
                        }}>
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Prompt">
                        <IconButton onClick={() => handleDeletePrompt(prompt.id)}>
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {selectedTab === 2 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">LangExtract Instructions</Typography>
              <Button
                startIcon={<Add />}
                variant="contained"
                onClick={() => {
                  setEditingInstruction({
                    id: `new-${Date.now()}`,
                    name: '',
                    description: '',
                    schema: '',
                    examples: [''],
                    instructions: '',
                    is_default: false
                  });
                  setInstructionDialogOpen(true);
                }}
              >
                New Instruction
              </Button>
            </Box>
            
            <List>
              {langextractInstructions.map((instruction) => (
                <ListItem key={instruction.id} divider>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">{instruction.name}</Typography>
                        {instruction.is_default && <Chip label="Default" size="small" color="success" />}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {instruction.description}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Examples: {instruction.examples.length} | Schema: {instruction.schema.length} chars
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box display="flex" gap={1}>
                      <Tooltip title="Edit Instruction">
                        <IconButton onClick={() => {
                          setEditingInstruction(instruction);
                          setInstructionDialogOpen(true);
                        }}>
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Instruction">
                        <IconButton onClick={() => {
                          setLangExtractInstructions(prev => prev.filter(i => i.id !== instruction.id));
                        }}>
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Edit Prompt Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {editingPrompt?.id.startsWith('new-') ? 'New Prompt' : 'Edit Prompt'}
        </DialogTitle>
        <DialogContent>
          {editingPrompt && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Prompt Name"
                    value={editingPrompt.name}
                    onChange={(e) => setEditingPrompt({ ...editingPrompt, name: e.target.value })}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Prompt Type</InputLabel>
                    <Select
                      value={editingPrompt.type}
                      onChange={(e) => setEditingPrompt({ ...editingPrompt, type: e.target.value as any })}
                      label="Prompt Type"
                    >
                      <MenuItem value="system">System</MenuItem>
                      <MenuItem value="agent">Agent</MenuItem>
                      <MenuItem value="langextract">LangExtract</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                {editingPrompt.type === 'agent' && (
                  <Grid item xs={12}>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Agent</InputLabel>
                      <Select
                        value={editingPrompt.agent_id || ''}
                        onChange={(e) => setEditingPrompt({ ...editingPrompt, agent_id: e.target.value })}
                        label="Agent"
                      >
                        {agents.map(agent => (
                          <MenuItem key={agent.id} value={agent.id}>
                            {agent.name} - {agent.description}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={editingPrompt.description}
                    onChange={(e) => setEditingPrompt({ ...editingPrompt, description: e.target.value })}
                    multiline
                    rows={2}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Prompt Content"
                    value={editingPrompt.content}
                    onChange={(e) => setEditingPrompt({ ...editingPrompt, content: e.target.value })}
                    multiline
                    rows={8}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={editingPrompt.is_active}
                        onChange={(e) => setEditingPrompt({ ...editingPrompt, is_active: e.target.checked })}
                      />
                    }
                    label="Active"
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePrompt} variant="contained" disabled={!editingPrompt?.name.trim() || !editingPrompt?.content.trim()}>
            Save Prompt
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Instruction Dialog */}
      <Dialog open={instructionDialogOpen} onClose={() => setInstructionDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {editingInstruction?.id.startsWith('new-') ? 'New LangExtract Instruction' : 'Edit LangExtract Instruction'}
        </DialogTitle>
        <DialogContent>
          {editingInstruction && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Instruction Name"
                    value={editingInstruction.name}
                    onChange={(e) => setEditingInstruction({ ...editingInstruction, name: e.target.value })}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={editingInstruction.is_default}
                        onChange={(e) => setEditingInstruction({ ...editingInstruction, is_default: e.target.checked })}
                      />
                    }
                    label="Default Instruction"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={editingInstruction.description}
                    onChange={(e) => setEditingInstruction({ ...editingInstruction, description: e.target.value })}
                    multiline
                    rows={2}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="JSON Schema"
                    value={editingInstruction.schema}
                    onChange={(e) => setEditingInstruction({ ...editingInstruction, schema: e.target.value })}
                    multiline
                    rows={6}
                    sx={{ mb: 2 }}
                    placeholder='{"field": "type"}'
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Instructions"
                    value={editingInstruction.instructions}
                    onChange={(e) => setEditingInstruction({ ...editingInstruction, instructions: e.target.value })}
                    multiline
                    rows={3}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Examples
                  </Typography>
                  {editingInstruction.examples.map((example, index) => (
                    <TextField
                      key={index}
                      fullWidth
                      label={`Example ${index + 1}`}
                      value={example}
                      onChange={(e) => {
                        const newExamples = [...editingInstruction.examples];
                        newExamples[index] = e.target.value;
                        setEditingInstruction({ ...editingInstruction, examples: newExamples });
                      }}
                      sx={{ mb: 1 }}
                    />
                  ))}
                  <Button
                    startIcon={<Add />}
                    onClick={() => setEditingInstruction({
                      ...editingInstruction,
                      examples: [...editingInstruction.examples, '']
                    })}
                    sx={{ mt: 1 }}
                  >
                    Add Example
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInstructionDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveInstruction} variant="contained" disabled={!editingInstruction?.name.trim() || !editingInstruction?.schema.trim()}>
            Save Instruction
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PromptManager;
