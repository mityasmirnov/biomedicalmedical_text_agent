import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  SmartToy as AgentIcon,
  Psychology as PsychologyIcon,
  Biotech as BiotechIcon,
  Person as PersonIcon,
  LocalHospital as TreatmentIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

const Agents: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [isStartDialogOpen, setIsStartDialogOpen] = useState(false);

  const agents = [
    {
      id: 'demographics',
      name: 'Demographics Agent',
      description: 'Extracts patient demographic information from medical documents',
      status: 'active',
      performance: 95.2,
      accuracy: 94.8,
      speed: 2.3,
      icon: <PersonIcon />,
      color: 'primary',
      lastRun: '2 minutes ago',
      totalRuns: 1250,
      successRate: 94.2,
    },
    {
      id: 'genetics',
      name: 'Genetics Agent',
      description: 'Identifies and normalizes genetic variants and gene information',
      status: 'active',
      performance: 88.7,
      accuracy: 87.3,
      speed: 3.1,
      icon: <BiotechIcon />,
      color: 'secondary',
      lastRun: '5 minutes ago',
      totalRuns: 890,
      successRate: 87.3,
    },
    {
      id: 'phenotypes',
      name: 'Phenotypes Agent',
      description: 'Extracts phenotypic manifestations using HPO ontology',
      status: 'active',
      performance: 92.1,
      accuracy: 91.5,
      speed: 2.8,
      icon: <PsychologyIcon />,
      color: 'success',
      lastRun: '1 minute ago',
      totalRuns: 1560,
      successRate: 91.5,
    },
    {
      id: 'treatments',
      name: 'Treatments Agent',
      description: 'Identifies treatment interventions and clinical procedures',
      status: 'idle',
      performance: 85.4,
      accuracy: 84.2,
      speed: 2.9,
      icon: <TreatmentIcon />,
      color: 'warning',
      lastRun: '15 minutes ago',
      totalRuns: 720,
      successRate: 84.2,
    },
    {
      id: 'outcomes',
      name: 'Outcomes Agent',
      description: 'Extracts clinical outcomes and follow-up information',
      status: 'error',
      performance: 78.9,
      accuracy: 77.1,
      speed: 3.5,
      icon: <AssessmentIcon />,
      color: 'error',
      lastRun: '1 hour ago',
      totalRuns: 450,
      successRate: 77.1,
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'idle': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircleIcon />;
      case 'idle': return <WarningIcon />;
      case 'error': return <ErrorIcon />;
      default: return <WarningIcon />;
    }
  };

  const handleAgentAction = (agentId: string, action: string) => {
    if (action === 'start') {
      setIsStartDialogOpen(true);
    } else if (action === 'stop') {
      // Handle stop action
    } else if (action === 'config') {
      setSelectedAgent(agentId);
      setIsConfigDialogOpen(true);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Agents Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor and manage your AI extraction agents, their performance, and configurations
        </Typography>
      </Box>

      {/* Agent Status Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AgentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Agents</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {agents.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI extraction agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Active</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {agents.filter(a => a.status === 'active').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Currently running
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg Performance</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {Math.round(agents.reduce((sum, a) => sum + a.performance, 0) / agents.length)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Runs</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {agents.reduce((sum, a) => sum + a.totalRuns, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Document extractions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agents List */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            Agent Status & Performance
          </Typography>
          
          {agents.map((agent) => (
            <Card key={agent.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', flex: 1 }}>
                    <Box sx={{ mr: 2, mt: 0.5 }}>
                      {React.cloneElement(agent.icon, { color: agent.color as any })}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6" sx={{ mr: 2 }}>
                          {agent.name}
                        </Typography>
                        <Chip
                          icon={getStatusIcon(agent.status)}
                          label={agent.status}
                          color={getStatusColor(agent.status) as any}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {agent.description}
                      </Typography>
                      
                      {/* Performance Metrics */}
                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="text.secondary">
                            Performance
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {agent.performance}%
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="text.secondary">
                            Accuracy
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {agent.accuracy}%
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="text.secondary">
                            Speed (sec)
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {agent.speed}s
                          </Typography>
                        </Grid>
                      </Grid>
                      
                      {/* Progress Bars */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption">Success Rate</Typography>
                          <Typography variant="caption">{agent.successRate}%</Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={agent.successRate} 
                          color={agent.successRate > 90 ? 'success' : agent.successRate > 80 ? 'warning' : 'error'}
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Typography variant="caption" color="text.secondary">
                          Last run: {agent.lastRun} • Total runs: {agent.totalRuns}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                    <IconButton 
                      color="primary" 
                      onClick={() => handleAgentAction(agent.id, 'config')}
                    >
                      <SettingsIcon />
                    </IconButton>
                    {agent.status === 'active' ? (
                      <IconButton 
                        color="error" 
                        onClick={() => handleAgentAction(agent.id, 'stop')}
                      >
                        <StopIcon />
                      </IconButton>
                    ) : (
                      <IconButton 
                        color="success" 
                        onClick={() => handleAgentAction(agent.id, 'start')}
                      >
                        <PlayIcon />
                      </IconButton>
                    )}
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
                variant="contained"
                startIcon={<PlayIcon />}
                sx={{ mb: 2 }}
                onClick={() => setIsStartDialogOpen(true)}
              >
                Start All Agents
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<StopIcon />}
                sx={{ mb: 2 }}
              >
                Stop All Agents
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<RefreshIcon />}
                sx={{ mb: 2 }}
              >
                Refresh Status
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<TrendingUpIcon />}
              >
                View Analytics
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="AI Models" 
                    secondary="All models loaded successfully" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Ontologies" 
                    secondary="HPO and HGNC loaded" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Memory Usage" 
                    secondary="75% - Consider optimization" 
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Configuration Dialog */}
      <Dialog open={isConfigDialogOpen} onClose={() => setIsConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Agent Configuration</DialogTitle>
        <DialogContent>
          {selectedAgent && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Confidence Threshold"
                  type="number"
                  margin="normal"
                  defaultValue={0.8}
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                />
                <TextField
                  fullWidth
                  label="Max Processing Time (seconds)"
                  type="number"
                  margin="normal"
                  defaultValue={30}
                  inputProps={{ min: 1, max: 300 }}
                />
                <FormControl fullWidth margin="normal">
                  <InputLabel>Model Version</InputLabel>
                  <Select label="Model Version" defaultValue="latest">
                    <MenuItem value="latest">Latest (v2.1.0)</MenuItem>
                    <MenuItem value="stable">Stable (v2.0.5)</MenuItem>
                    <MenuItem value="beta">Beta (v2.2.0-beta)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Enable Auto-retry on failure"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Enable performance monitoring"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Enable debug logging"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Enable automatic updates"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsConfigDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsConfigDialogOpen(false)}>
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>

      {/* Start All Dialog */}
      <Dialog open={isStartDialogOpen} onClose={() => setIsStartDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Start All Agents</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will start all idle agents and resume any paused agents. Are you sure?
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Starting agents will begin processing any pending documents in the queue.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsStartDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsStartDialogOpen(false)}>
            Start All Agents
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Agents;
