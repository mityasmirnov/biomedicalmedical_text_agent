
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
  DialogActions
} from '@mui/material';
import { Settings, Key, Assessment, Refresh, Add } from '@mui/icons-material';
import { api } from '../services/api';

const APIManager: React.FC = () => {
  const [providers, setProviders] = useState([]);
  const [usage, setUsage] = useState({});
  const [models, setModels] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [apiKeys, setApiKeys] = useState({});
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [loading, setLoading] = useState(false);

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
      setProviders(providersRes.data);
      setUsage(usageRes.data);
      setModels(modelsRes.data);
    } catch (error) {
      console.error('Failed to load API data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    try {
      await api.config.updateApiKey(selectedProvider, newApiKey);
      setConfigDialogOpen(false);
      setNewApiKey('');
      loadAPIData();
    } catch (error) {
      console.error('Failed to save API key:', error);
    }
  };

  const handleToggleProvider = async (provider: string, enabled: boolean) => {
    try {
      await api.config.updateProvider(provider, { enabled });
      loadAPIData();
    } catch (error) {
      console.error('Failed to update provider:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        API Management
      </Typography>

      {/* Provider Configuration */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Providers
              </Typography>
              {providers.map((provider: any) => (
                <Box key={provider.name} mb={2} p={2} border="1px solid #ddd" borderRadius={1}>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="subtitle1">{provider.display_name}</Typography>
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
                  
                  <Box display="flex" justifyContent="between" alignItems="center">
                    <Chip
                      label={provider.api_key_configured ? 'API Key Set' : 'No API Key'}
                      color={provider.api_key_configured ? 'success' : 'error'}
                      size="small"
                    />
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
              {Object.entries(usage).map(([provider, stats]: [string, any]) => (
                <Box key={provider} mb={2}>
                  <Typography variant="subtitle2">{provider}</Typography>
                  <Box display="flex" justifyContent="between">
                    <Typography variant="body2">
                      Requests: {stats.total_requests}
                    </Typography>
                    <Typography variant="body2">
                      Cost: ${stats.total_cost?.toFixed(2) || '0.00'}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(stats.total_requests / stats.limit) * 100}
                    sx={{ mt: 1 }}
                  />
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
                  <TableCell>Cost</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model: any) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.name}</TableCell>
                    <TableCell>{model.provider}</TableCell>
                    <TableCell>
                      <Chip
                        label={model.type}
                        size="small"
                        color={model.type === 'free' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {model.cost_per_token ? `$${model.cost_per_token}/token` : 'Free'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.available ? 'Available' : 'Unavailable'}
                        color={model.available ? 'success' : 'error'}
                        size="small"
                      />
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
          />
          <Alert severity="info" sx={{ mt: 2 }}>
            API keys are stored securely and encrypted. They are only used for making requests to the respective services.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveApiKey} variant="contained" disabled={!newApiKey}>
            Save API Key
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default APIManager;
