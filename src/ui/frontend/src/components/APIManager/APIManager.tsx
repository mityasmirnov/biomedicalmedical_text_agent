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
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Key as KeyIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Security as SecurityIcon,
  Api as ApiIcon,
  Cloud as CloudIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkIcon,
  Lock as LockIcon,
  VisibilityOff as HideIcon,
  Visibility as ShowIcon,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface APIProvider {
  id: string;
  name: string;
  type: 'openai' | 'anthropic' | 'google' | 'azure' | 'custom';
  baseUrl: string;
  apiKey: string;
  status: 'active' | 'inactive' | 'error';
  rateLimit: number;
  currentUsage: number;
  maxTokens: number;
  models: string[];
  lastUsed: string;
  costPerToken: number;
  totalCost: number;
  isDefault: boolean;
}

interface APIModel {
  id: string;
  name: string;
  provider: string;
  type: 'chat' | 'completion' | 'embedding' | 'vision';
  maxTokens: number;
  costPerToken: number;
  status: 'available' | 'deprecated' | 'beta';
  capabilities: string[];
  lastUpdated: string;
}

interface APIKey {
  id: string;
  name: string;
  key: string;
  provider: string;
  permissions: string[];
  status: 'active' | 'revoked' | 'expired';
  createdAt: string;
  lastUsed: string;
  usageCount: number;
}

const validationSchema = yup.object({
  name: yup.string().required('Provider name is required'),
  type: yup.string().required('Provider type is required'),
  baseUrl: yup.string().url('Must be a valid URL').required('Base URL is required'),
  apiKey: yup.string().required('API key is required'),
  rateLimit: yup.number().min(1, 'Rate limit must be at least 1').required('Rate limit is required'),
  maxTokens: yup.number().min(1000, 'Max tokens must be at least 1000').required('Max tokens is required'),
});

const APIManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [isAddProviderDialogOpen, setIsAddProviderDialogOpen] = useState(false);
  const [isEditProviderDialogOpen, setIsEditProviderDialogOpen] = useState(false);
  const [isViewProviderDialogOpen, setIsViewProviderDialogOpen] = useState(false);
  const [isAddModelDialogOpen, setIsAddModelDialogOpen] = useState(false);
  const [isAddKeyDialogOpen, setIsAddKeyDialogOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<APIProvider | null>(null);
  const [selectedModel, setSelectedProvider] = useState<APIModel | null>(null);
  const [selectedKey, setSelectedKey] = useState<APIKey | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState<{ [key: string]: boolean }>({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as any });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      name: '',
      type: 'openai',
      baseUrl: '',
      apiKey: '',
      rateLimit: 1000,
      maxTokens: 4000,
    }
  });

  // Sample data
  const [providers] = useState<APIProvider[]>([
    {
      id: '1',
      name: 'OpenAI Production',
      type: 'openai',
      baseUrl: 'https://api.openai.com/v1',
      apiKey: 'sk-...',
      status: 'active',
      rateLimit: 1000,
      currentUsage: 750,
      maxTokens: 4000,
      models: ['gpt-4', 'gpt-3.5-turbo', 'text-embedding-ada-002'],
      lastUsed: '2024-01-15 14:30',
      costPerToken: 0.00003,
      totalCost: 45.67,
      isDefault: true,
    },
    {
      id: '2',
      name: 'Anthropic Claude',
      type: 'anthropic',
      baseUrl: 'https://api.anthropic.com/v1',
      apiKey: 'sk-ant-...',
      status: 'active',
      rateLimit: 500,
      currentUsage: 320,
      maxTokens: 100000,
      models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
      lastUsed: '2024-01-15 13:45',
      costPerToken: 0.000015,
      totalCost: 23.45,
      isDefault: false,
    },
    {
      id: '3',
      name: 'Google AI',
      type: 'google',
      baseUrl: 'https://generativelanguage.googleapis.com/v1',
      apiKey: 'AIza...',
      status: 'inactive',
      rateLimit: 800,
      currentUsage: 0,
      maxTokens: 8000,
      models: ['gemini-pro', 'gemini-pro-vision'],
      lastUsed: '2024-01-10 09:15',
      costPerToken: 0.00001,
      totalCost: 12.34,
      isDefault: false,
    },
  ]);

  const [models] = useState<APIModel[]>([
    {
      id: '1',
      name: 'gpt-4',
      provider: 'OpenAI Production',
      type: 'chat',
      maxTokens: 8192,
      costPerToken: 0.00003,
      status: 'available',
      capabilities: ['chat', 'function calling', 'code generation'],
      lastUpdated: '2024-01-15',
    },
    {
      id: '2',
      name: 'claude-3-opus',
      provider: 'Anthropic Claude',
      type: 'chat',
      maxTokens: 200000,
      costPerToken: 0.000015,
      status: 'available',
      capabilities: ['chat', 'vision', 'code generation', 'analysis'],
      lastUpdated: '2024-01-15',
    },
    {
      id: '3',
      name: 'text-embedding-ada-002',
      provider: 'OpenAI Production',
      type: 'embedding',
      maxTokens: 8191,
      costPerToken: 0.0000001,
      status: 'available',
      capabilities: ['text embedding', 'similarity search'],
      lastUpdated: '2024-01-15',
    },
  ]);

  const [apiKeys] = useState<APIKey[]>([
    {
      id: '1',
      name: 'OpenAI Production Key',
      key: 'sk-...',
      provider: 'OpenAI Production',
      permissions: ['chat', 'completion', 'embedding'],
      status: 'active',
      createdAt: '2024-01-01',
      lastUsed: '2024-01-15 14:30',
      usageCount: 1250,
    },
    {
      id: '2',
      name: 'Anthropic Claude Key',
      key: 'sk-ant-...',
      provider: 'Anthropic Claude',
      permissions: ['chat', 'completion'],
      status: 'active',
      createdAt: '2024-01-05',
      lastUsed: '2024-01-15 13:45',
      usageCount: 890,
    },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleAddProvider = (data: any) => {
    console.log('Adding new provider:', data);
    setIsAddProviderDialogOpen(false);
    reset();
    setSnackbar({ open: true, message: 'Provider added successfully', severity: 'success' });
  };

  const handleEditProvider = (data: any) => {
    console.log('Editing provider:', data);
    setIsEditProviderDialogOpen(false);
    setSnackbar({ open: true, message: 'Provider updated successfully', severity: 'success' });
  };

  const handleDeleteProvider = (id: string) => {
    if (window.confirm('Are you sure you want to delete this provider?')) {
      console.log('Deleting provider:', id);
      setSnackbar({ open: true, message: 'Provider deleted successfully', severity: 'success' });
    }
  };

  const handleToggleProvider = (id: string) => {
    console.log('Toggling provider:', id);
    setSnackbar({ open: true, message: 'Provider status updated', severity: 'info' });
  };

  const handleTestConnection = (provider: APIProvider) => {
    setIsLoading(true);
    // Simulate API test
    setTimeout(() => {
      setIsLoading(false);
      setSnackbar({ 
        open: true, 
        message: `Connection test ${Math.random() > 0.5 ? 'successful' : 'failed'}`, 
        severity: Math.random() > 0.5 ? 'success' : 'error' 
      });
    }, 2000);
  };

  const toggleApiKeyVisibility = (providerId: string) => {
    setShowApiKeys(prev => ({
      ...prev,
      [providerId]: !prev[providerId]
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <ValidIcon />;
      case 'inactive': return <InfoIcon />;
      case 'error': return <InvalidIcon />;
      default: return <InfoIcon />;
    }
  };

  const getProviderIcon = (type: string) => {
    switch (type) {
      case 'openai': return <ApiIcon />;
      case 'anthropic': return <CloudIcon />;
      case 'google': return <StorageIcon />;
      case 'azure': return <SpeedIcon />;
      default: return <ApiIcon />;
    }
  };

  const getUsagePercentage = (current: number, max: number) => {
    return Math.min((current / max) * 100, 100);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          API Configuration Manager
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage API providers, models, and authentication keys
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Providers" icon={<CloudIcon />} />
          <Tab label="Models" icon={<ApiIcon />} />
          <Tab label="API Keys" icon={<KeyIcon />} />
          <Tab label="Usage & Costs" icon={<SpeedIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <>
          {/* Providers Header */}
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              API Providers ({providers.length})
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setIsAddProviderDialogOpen(true)}
            >
              Add Provider
            </Button>
          </Box>

          {/* Providers Grid */}
          <Grid container spacing={3}>
            {providers.map((provider) => (
              <Grid item xs={12} md={6} lg={4} key={provider.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getProviderIcon(provider.type)}
                        <Typography variant="h6" component="h2">
                          {provider.name}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {provider.isDefault && (
                          <Chip label="Default" size="small" color="primary" />
                        )}
                        <Chip
                          icon={getStatusIcon(provider.status)}
                          label={provider.status}
                          color={getStatusColor(provider.status) as any}
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {provider.baseUrl}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2">API Key</Typography>
                        <IconButton
                          size="small"
                          onClick={() => toggleApiKeyVisibility(provider.id)}
                        >
                          {showApiKeys[provider.id] ? <HideIcon /> : <ShowIcon />}
                        </IconButton>
                      </Box>
                      <TextField
                        fullWidth
                        size="small"
                        value={showApiKeys[provider.id] ? provider.apiKey : '••••••••••••••••'}
                        InputProps={{ readOnly: true }}
                        variant="outlined"
                      />
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Rate Limit Usage
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={getUsagePercentage(provider.currentUsage, provider.rateLimit)}
                          sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                          color={getUsagePercentage(provider.currentUsage, provider.rateLimit) > 80 ? 'warning' : 'primary'}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {provider.currentUsage}/{provider.rateLimit}
                        </Typography>
                      </Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Models ({provider.models.length})
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {provider.models.slice(0, 3).map((model, index) => (
                          <Chip key={index} label={model} size="small" variant="outlined" />
                        ))}
                        {provider.models.length > 3 && (
                          <Chip label={`+${provider.models.length - 3}`} size="small" />
                        )}
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Last used: {provider.lastUsed}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Cost: ${provider.totalCost.toFixed(2)}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedProvider(provider);
                          setIsViewProviderDialogOpen(true);
                        }}
                      >
                        View Details
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => {
                          setSelectedProvider(provider);
                          setIsEditProviderDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleTestConnection(provider)}
                        disabled={isLoading}
                      >
                        {isLoading ? <CircularProgress size={16} /> : 'Test'}
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
                Available Models ({models.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsAddModelDialogOpen(true)}
              >
                Add Model
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Model Name</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Max Tokens</TableCell>
                    <TableCell>Cost per Token</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Capabilities</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {models.map((model) => (
                    <TableRow key={model.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {model.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={model.provider} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={model.type} 
                          size="small" 
                          color={model.type === 'chat' ? 'primary' : 'secondary'}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {model.maxTokens.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          ${model.costPerToken.toFixed(6)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={model.status}
                          color={model.status === 'available' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {model.capabilities.slice(0, 2).map((capability, index) => (
                            <Chip key={index} label={capability} size="small" variant="outlined" />
                          ))}
                          {model.capabilities.length > 2 && (
                            <Chip label={`+${model.capabilities.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit Model">
                            <IconButton size="small" color="secondary">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Model">
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
        <Card>
          <CardContent>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                API Keys ({apiKeys.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsAddKeyDialogOpen(true)}
              >
                Add API Key
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Key Name</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>API Key</TableCell>
                    <TableCell>Permissions</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Last Used</TableCell>
                    <TableCell>Usage Count</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {apiKeys.map((key) => (
                    <TableRow key={key.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {key.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={key.provider} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <TextField
                            size="small"
                            value={showApiKeys[key.id] ? key.key : '••••••••••••••••'}
                            InputProps={{ readOnly: true }}
                            variant="outlined"
                            sx={{ width: 200 }}
                          />
                          <IconButton
                            size="small"
                            onClick={() => toggleApiKeyVisibility(key.id)}
                          >
                            {showApiKeys[key.id] ? <HideIcon /> : <ShowIcon />}
                          </IconButton>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {key.permissions.map((permission, index) => (
                            <Chip key={index} label={permission} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={key.status}
                          color={key.status === 'active' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {key.createdAt}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {key.lastUsed}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {key.usageCount.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit Key">
                            <IconButton size="small" color="secondary">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Revoke Key">
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

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Usage Overview
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {providers.map((provider) => (
                    <Box key={provider.id}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2">{provider.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {provider.currentUsage}/{provider.rateLimit}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={getUsagePercentage(provider.currentUsage, provider.rateLimit)}
                        sx={{ height: 8, borderRadius: 4 }}
                        color={getUsagePercentage(provider.currentUsage, provider.rateLimit) > 80 ? 'warning' : 'primary'}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cost Summary
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {providers.map((provider) => (
                    <Box key={provider.id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2">{provider.name}</Typography>
                      <Typography variant="body2" fontWeight="medium">
                        ${provider.totalCost.toFixed(2)}
                      </Typography>
                    </Box>
                  ))}
                  <Divider />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Total</Typography>
                    <Typography variant="h6" color="primary">
                      ${providers.reduce((sum, p) => sum + p.totalCost, 0).toFixed(2)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add Provider Dialog */}
      <Dialog open={isAddProviderDialogOpen} onClose={() => setIsAddProviderDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New API Provider</DialogTitle>
        <form onSubmit={handleSubmit(handleAddProvider)}>
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
                      label="Provider Name"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.type}>
                      <InputLabel>Provider Type</InputLabel>
                      <Select {...field} label="Provider Type">
                        <MenuItem value="openai">OpenAI</MenuItem>
                        <MenuItem value="anthropic">Anthropic</MenuItem>
                        <MenuItem value="google">Google AI</MenuItem>
                        <MenuItem value="azure">Azure OpenAI</MenuItem>
                        <MenuItem value="custom">Custom</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="baseUrl"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Base URL"
                      error={!!errors.baseUrl}
                      helperText={errors.baseUrl?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="apiKey"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="API Key"
                      type="password"
                      error={!!errors.apiKey}
                      helperText={errors.apiKey?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="rateLimit"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Rate Limit (requests/min)"
                      type="number"
                      error={!!errors.rateLimit}
                      helperText={errors.rateLimit?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="maxTokens"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Max Tokens"
                      type="number"
                      error={!!errors.maxTokens}
                      helperText={errors.maxTokens?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsAddProviderDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Add Provider</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Provider Dialog */}
      <Dialog open={isEditProviderDialogOpen} onClose={() => setIsEditProviderDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit API Provider</DialogTitle>
        <form onSubmit={handleSubmit(handleEditProvider)}>
          <DialogContent>
            {selectedProvider && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Provider Name"
                    defaultValue={selectedProvider.name}
                    name="name"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Provider Type</InputLabel>
                    <Select defaultValue={selectedProvider.type} label="Provider Type">
                      <MenuItem value="openai">OpenAI</MenuItem>
                      <MenuItem value="anthropic">Anthropic</MenuItem>
                      <MenuItem value="google">Google AI</MenuItem>
                      <MenuItem value="azure">Azure OpenAI</MenuItem>
                      <MenuItem value="custom">Custom</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Base URL"
                    defaultValue={selectedProvider.baseUrl}
                    name="baseUrl"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="API Key"
                    type="password"
                    defaultValue={selectedProvider.apiKey}
                    name="apiKey"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Rate Limit (requests/min)"
                    type="number"
                    defaultValue={selectedProvider.rateLimit}
                    name="rateLimit"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Tokens"
                    type="number"
                    defaultValue={selectedProvider.maxTokens}
                    name="maxTokens"
                  />
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditProviderDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save Changes</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Provider Dialog */}
      <Dialog open={isViewProviderDialogOpen} onClose={() => setIsViewProviderDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Provider Details</DialogTitle>
        <DialogContent>
          {selectedProvider && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>{selectedProvider.name}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Type: {selectedProvider.type}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Configuration</Typography>
                <Typography variant="body2">Base URL: {selectedProvider.baseUrl}</Typography>
                <Typography variant="body2">Rate Limit: {selectedProvider.rateLimit} req/min</Typography>
                <Typography variant="body2">Max Tokens: {selectedProvider.maxTokens.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Status & Usage</Typography>
                <Chip
                  icon={getStatusIcon(selectedProvider.status)}
                  label={selectedProvider.status}
                  color={getStatusColor(selectedProvider.status) as any}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2">Usage: {selectedProvider.currentUsage}/{selectedProvider.rateLimit}</Typography>
                <Typography variant="body2">Total Cost: ${selectedProvider.totalCost.toFixed(2)}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Available Models</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {selectedProvider.models.map((model, index) => (
                    <Chip key={index} label={model} size="small" variant="outlined" />
                  ))}
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsViewProviderDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setIsViewProviderDialogOpen(false);
              setIsEditProviderDialogOpen(true);
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

export default APIManager;