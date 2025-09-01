import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material';
import { 
  Key,
  Assessment,
  Visibility
} from '@mui/icons-material';
import { api } from '../../services/api';

interface APIProvider {
  name: string;
  display_name: string;
  description: string;
  enabled: boolean;
  api_key_configured: boolean;
  base_url?: string;
  rate_limit?: number;
}

interface APIModel {
  id: string;
  name: string;
  provider: string;
  type: 'free' | 'paid' | 'enterprise';
  available: boolean;
  cost_per_token?: number;
  max_tokens?: number;
  context_length?: number;
}

interface APIUsage {
  [provider: string]: {
    total_requests: number;
    total_cost: number;
    limit: number;
    reset_date: string;
  };
}

const APIManager: React.FC = () => {
  const [providers, setProviders] = useState<APIProvider[]>([]);
  const [usage, setUsage] = useState<APIUsage>({});
  const [models, setModels] = useState<APIModel[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAPIData();
  }, []);

  const loadAPIData = async () => {
    setLoading(true);
    try {
      const [providersRes, usageRes, modelsRes] = await Promise.all([
        api.config.getProviders(),
        api.config.getUsage(),
        api.config.getModels()
      ]);
      setProviders(providersRes.data.providers || []);
      setUsage(usageRes.data || {});
      setModels(modelsRes.data.models || []);
      setError(null);
    } catch (error) {
      console.error('Failed to load API data:', error);
      setError('Failed to load API data - using mock data');
      // Set mock data for development
      setProviders([
        {
          name: 'openrouter',
          display_name: 'OpenRouter',
          description: 'Access to multiple LLM models including GPT, Claude, and others',
          enabled: true,
          api_key_configured: true,
          base_url: 'https://openrouter.ai/api/v1',
          rate_limit: 100
        },
        {
          name: 'huggingface',
          display_name: 'Hugging Face',
          description: 'Open source model hosting and inference API',
          enabled: true,
          api_key_configured: false,
          base_url: 'https://api-inference.huggingface.co',
          rate_limit: 50
        },
        {
          name: 'ollama',
          display_name: 'Ollama',
          description: 'Local model deployment and inference',
          enabled: false,
          api_key_configured: false,
          base_url: 'http://localhost:11434',
          rate_limit: 1000
        }
      ]);
      setUsage({
        'openrouter': {
          total_requests: 150,
          total_cost: 0.25,
          limit: 1000,
          reset_date: '2024-02-01'
        },
        'huggingface': {
          total_requests: 75,
          total_cost: 0.00,
          limit: 500,
          reset_date: '2024-02-01'
        }
      });
      setModels([
        {
          id: 'google/gemma-2-27b-it:free',
          name: 'Gemma 2 27B',
          provider: 'openrouter',
          type: 'free',
          available: true,
          max_tokens: 8192,
          context_length: 32768
        },
        {
          id: 'microsoft/phi-3-mini-128k-instruct:free',
          name: 'Phi-3 Mini',
          provider: 'openrouter',
          type: 'free',
          available: true,
          max_tokens: 4096,
          context_length: 128000
        },
        {
          id: 'meta-llama/llama-3.1-8b-instruct:free',
          name: 'Llama 3.1 8B',
          provider: 'openrouter',
          type: 'free',
          available: true,
          max_tokens: 8192,
          context_length: 8192
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    if (!selectedProvider || !newApiKey.trim()) return;
    
    try {
      await api.config.updateApiKey(selectedProvider, newApiKey);
      
      // Update local state
      setApiKeys(prev => ({ ...prev, [selectedProvider]: newApiKey }));
      setShowApiKeys(prev => ({ ...prev, [selectedProvider]: false }));
      
      // Update providers
      setProviders(prev => prev.map(p => 
        p.name === selectedProvider 
          ? { ...p, api_key_configured: true }
          : p
      ));
      
      setConfigDialogOpen(false);
      setNewApiKey('');
      setSelectedProvider('');
      
      // Reload data
      loadAPIData();
    } catch (error) {
      console.error('Failed to save API key:', error);
      alert('Failed to save API key. Please try again.');
    }
  };

  const handleToggleProvider = async (provider: string, enabled: boolean) => {
    try {
      await api.config.updateProvider(provider, { enabled });
      
      // Update local state
      setProviders(prev => prev.map(p => 
        p.name === provider 
          ? { ...p, enabled }
          : p
      ));
    } catch (error) {
      console.error('Failed to update provider:', error);
      alert('Failed to update provider. Please try again.');
    }
  };

  const toggleApiKeyVisibility = (provider: string) => {
    setShowApiKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'openrouter': return '🔗';
      case 'huggingface': return '🤗';
      case 'ollama': return '🦙';
      default: return '⚙️';
    }
  };

  const getModelTypeColor = (type: string) => {
    switch (type) {
      case 'free': return 'success';
      case 'paid': return 'warning';
      case 'enterprise': return 'error';
      default: return 'default';
    }
  };

  const getUsagePercentage = (provider: string) => {
    const providerUsage = usage[provider];
    if (!providerUsage) return 0;
    return (providerUsage.total_requests / providerUsage.limit) * 100;
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'error';
    if (percentage >= 70) return 'warning';
    return 'success';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        API Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Provider Configuration */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Providers
              </Typography>
              {providers.map((provider) => (
                <Box key={provider.name} mb={2} p={2} border="1px solid #ddd" borderRadius={1}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">{getProviderIcon(provider.name)}</Typography>
                      <Typography variant="subtitle1">{provider.display_name}</Typography>
                    </Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={provider.enabled}
                          onChange={(e) => handleToggleProvider(provider.name, e.target.checked)}
                        />
                      }
                      label="Enabled"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" mb={1}>
                    {provider.description}
                  </Typography>
                  
                  {provider.base_url && (
                    <Typography variant="caption" color="textSecondary" display="block" mb={1}>
                      Base URL: {provider.base_url}
                    </Typography>
                  )}
                  
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box display="flex" gap={1}>
                      <Chip
                        label={provider.api_key_configured ? 'API Key Set' : 'No API Key'}
                        color={provider.api_key_configured ? 'success' : 'error'}
                        size="small"
                      />
                      {provider.rate_limit && (
                        <Chip
                          label={`${provider.rate_limit}/min`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                    <Button
                      size="small"
                      startIcon={<Key />}
                      onClick={() => {
                        setSelectedProvider(provider.name);
                        setConfigDialogOpen(true);
                      }}
                    >
                      Configure
                    </Button>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Usage Statistics
              </Typography>
              {Object.entries(usage).map(([provider, stats]) => (
                <Box key={provider} mb={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="subtitle2" textTransform="capitalize">
                      {provider}
                    </Typography>
                    <Chip
                      label={`${stats.total_requests}/${stats.limit}`}
                      size="small"
                      color={getUsageColor(getUsagePercentage(provider))}
                    />
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">
                      Requests: {stats.total_requests.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Cost: ${stats.total_cost?.toFixed(2) || '0.00'}
                    </Typography>
                  </Box>
                  
                  <LinearProgress
                    variant="determinate"
                    value={getUsagePercentage(provider)}
                    color={getUsageColor(getUsagePercentage(provider))}
                    sx={{ mb: 1 }}
                  />
                  
                  <Typography variant="caption" color="textSecondary">
                    Resets: {new Date(stats.reset_date).toLocaleDateString()}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Available Models */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Models
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell>Provider</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Context Length</TableCell>
                  <TableCell>Max Tokens</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {model.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary" fontFamily="monospace">
                        {model.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.provider}
                        size="small"
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.type}
                        size="small"
                        color={getModelTypeColor(model.type)}
                      />
                    </TableCell>
                    <TableCell>
                      {model.context_length ? model.context_length.toLocaleString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {model.max_tokens ? model.max_tokens.toLocaleString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.available ? 'Available' : 'Unavailable'}
                        color={model.available ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <IconButton size="small" aria-label="test model">
                          <Assessment />
                        </IconButton>
                        <IconButton size="small" aria-label="view details">
                          <Visibility />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* API Key Configuration Dialog */}
      <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Configure API Key - {selectedProvider}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="API Key"
            type="password"
            fullWidth
            variant="outlined"
            value={newApiKey}
            onChange={(e) => setNewApiKey(e.target.value)}
            placeholder="Enter your API key"
            sx={{ mb: 2 }}
          />
          
          <Alert severity="info" sx={{ mb: 2 }}>
            API keys are stored securely and encrypted. They are only used for making requests to the respective services.
          </Alert>
          
          <Typography variant="body2" color="textSecondary">
            <strong>Provider:</strong> {selectedProvider}<br/>
            <strong>Base URL:</strong> {providers.find(p => p.name === selectedProvider)?.base_url || 'N/A'}<br/>
            <strong>Rate Limit:</strong> {providers.find(p => p.name === selectedProvider)?.rate_limit || 'N/A'} requests per minute
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveApiKey} variant="contained" disabled={!newApiKey.trim()}>
            Save API Key
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default APIManager;
