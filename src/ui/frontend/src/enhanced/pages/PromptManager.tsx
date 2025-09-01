import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Edit, Add, Delete } from '@mui/icons-material';
import { api } from '../services/api';

const PromptManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [prompts, setPrompts] = useState<any[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<any | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [promptName, setPromptName] = useState('');
  const [promptType, setPromptType] = useState('system');
  const [agentType, setAgentType] = useState('demographics');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    setLoading(true);
    try {
      const response = await api.prompts.getAll();
      setPrompts(response.data);
    } catch (error) {
      console.error('Failed to load prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditPrompt = (prompt: any) => {
    setSelectedPrompt(prompt);
    setPromptName(prompt.name);
    setPromptText(prompt.content);
    setPromptType(prompt.type);
    setAgentType(prompt.agent_type);
    setEditDialogOpen(true);
  };

  const handleSavePrompt = async () => {
    try {
      const promptData = {
        name: promptName,
        content: promptText,
        type: promptType,
        agent_type: agentType
      };

      if (selectedPrompt) {
        await api.prompts.update(selectedPrompt.id, promptData);
      } else {
        await api.prompts.create(promptData);
      }

      setEditDialogOpen(false);
      resetForm();
      loadPrompts();
    } catch (error) {
      console.error('Failed to save prompt:', error);
    }
  };

  const resetForm = () => {
    setSelectedPrompt(null);
    setPromptName('');
    setPromptText('');
    setPromptType('system');
    setAgentType('demographics');
  };

  const handleDeletePrompt = async (promptId: string) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await api.prompts.delete(promptId);
        loadPrompts();
      } catch (error) {
        console.error('Failed to delete prompt:', error);
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Prompt Management (Enhanced)
      </Typography>

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="System Prompts" />
        <Tab label="Agent Prompts" />
        <Tab label="LangExtract Schemas" />
      </Tabs>

      <Box mb={3}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            resetForm();
            setEditDialogOpen(true);
          }}
        >
          Add New Prompt
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Prompts ({prompts.length})
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Agent</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Modified</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {prompts.map((prompt: any) => (
                  <TableRow key={prompt.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {prompt.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {prompt.content?.substring(0, 100)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={prompt.type}
                        size="small"
                        color={prompt.type === 'system' ? 'primary' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={prompt.agent_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={prompt.active ? 'Active' : 'Inactive'}
                        color={prompt.active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {prompt.updated_at ? new Date(prompt.updated_at).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          startIcon={<Edit />}
                          onClick={() => handleEditPrompt(prompt)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Delete />}
                          color="error"
                          onClick={() => handleDeletePrompt(prompt.id)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {selectedPrompt ? 'Edit Prompt' : 'Add New Prompt'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Prompt Name"
                value={promptName}
                onChange={(e) => setPromptName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={promptType}
                  onChange={(e) => setPromptType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="system">System</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="schema">Schema</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Agent Type</InputLabel>
                <Select
                  value={agentType}
                  onChange={(e) => setAgentType(e.target.value)}
                  label="Agent Type"
                >
                  <MenuItem value="demographics">Demographics</MenuItem>
                  <MenuItem value="genetics">Genetics</MenuItem>
                  <MenuItem value="phenotypes">Phenotypes</MenuItem>
                  <MenuItem value="treatments">Treatments</MenuItem>
                  <MenuItem value="outcomes">Outcomes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={15}
                label="Prompt Content"
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder="Enter your prompt content here..."
                variant="outlined"
                sx={{ fontFamily: 'monospace' }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePrompt} variant="contained" disabled={!promptName || !promptText}>
            Save Prompt
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PromptManager;



