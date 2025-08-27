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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentsAPI } from '../../services/api';

const Agents: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [isStartDialogOpen, setIsStartDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch real agents data
  const { data: agentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsAPI.getAgents(),
  });

  // Mutations for agent control
  const startAgentMutation = useMutation({
    mutationFn: (agentId: string) => agentsAPI.startAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const stopAgentMutation = useMutation({
    mutationFn: (agentId: string) => agentsAPI.stopAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  // Extract data from API response
  const agentsDataExtracted = agentsData?.data || agentsData;
  const agents = agentsDataExtracted?.agents || [];
  const systemMetrics = agentsDataExtracted?.system_metrics;

  // Agent icon mapping
  const getAgentIcon = (agentId: string) => {
    const iconMap: { [key: string]: React.ReactElement } = {
      demographics: <PersonIcon />,
      genetics: <BiotechIcon />,
      phenotypes: <PsychologyIcon />,
      treatments: <TreatmentIcon />,
      outcomes: <AssessmentIcon />,
    };
    return iconMap[agentId] || <AgentIcon />;
  };

  // Agent color mapping
  const getAgentColor = (agentId: string) => {
    const colorMap: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'error' } = {
      demographics: 'primary',
      genetics: 'secondary',
      phenotypes: 'success',
      treatments: 'warning',
      outcomes: 'error',
    };
    return colorMap[agentId] || 'primary';
  };

  const handleStartAgent = (agentId: string) => {
    startAgentMutation.mutate(agentId);
  };

  const handleStopAgent = (agentId: string) => {
    stopAgentMutation.mutate(agentId);
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Loading Agents...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load agents: {String(error)}
        </Alert>
        <Button variant="contained" onClick={() => refetch()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          AI Agents Management
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
        >
          Refresh
        </Button>
      </Box>

      {/* System Overview */}
      {systemMetrics && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Overview
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Total Agents</Typography>
                <Typography variant="h4">{systemMetrics.total_agents}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Active Agents</Typography>
                <Typography variant="h4" color="success.main">{systemMetrics.active_agents}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Total Runs</Typography>
                <Typography variant="h4">{systemMetrics.total_runs.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Avg Performance</Typography>
                <Typography variant="h4">{systemMetrics.average_performance}%</Typography>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2 }}>
              <Chip 
                label={`System Status: ${systemMetrics.system_status}`}
                color={systemMetrics.system_status === 'healthy' ? 'success' : 'warning'}
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Agents Grid */}
      <Grid container spacing={3}>
        {agents.map((agent: any) => (
          <Grid item xs={12} sm={6} md={4} key={agent.id}>
            <Card 
              sx={{ 
                height: '100%',
                border: selectedAgent === agent.id ? 2 : 1,
                borderColor: selectedAgent === agent.id ? 'primary.main' : 'divider'
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    color: getAgentColor(agent.id),
                    mr: 1,
                    display: 'flex',
                    alignItems: 'center'
                  }}>
                    {getAgentIcon(agent.id)}
                  </Box>
                  <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                    {agent.name}
                  </Typography>
                  <Chip 
                    label={agent.status} 
                    size="small"
                    color={
                      agent.status === 'active' ? 'success' : 
                      agent.status === 'idle' ? 'warning' : 'error'
                    }
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {agent.description}
                </Typography>

                <Grid container spacing={1} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Performance</Typography>
                    <Typography variant="body2">{agent.performance}%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Accuracy</Typography>
                    <Typography variant="body2">{agent.accuracy}%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Speed</Typography>
                    <Typography variant="body2">{agent.speed}s</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Success Rate</Typography>
                    <Typography variant="body2">{agent.successRate}%</Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">Last Run</Typography>
                  <Typography variant="body2">{agent.lastRun}</Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">Total Runs</Typography>
                  <Typography variant="body2">{agent.totalRuns.toLocaleString()}</Typography>
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={() => handleStartAgent(agent.id)}
                    disabled={agent.status === 'active'}
                    fullWidth
                  >
                    Start
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<StopIcon />}
                    onClick={() => handleStopAgent(agent.id)}
                    disabled={agent.status !== 'active'}
                    fullWidth
                  >
                    Stop
                  </Button>
                </Box>

                <Box sx={{ mt: 1 }}>
                  <Button
                    size="small"
                    variant="text"
                    startIcon={<SettingsIcon />}
                    onClick={() => {
                      setSelectedAgent(agent.id);
                      setIsConfigDialogOpen(true);
                    }}
                    fullWidth
                  >
                    Configure
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Configuration Dialog */}
      <Dialog 
        open={isConfigDialogOpen} 
        onClose={() => setIsConfigDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Configure Agent: {agents.find((a: any) => a.id === selectedAgent)?.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Agent configuration options will be implemented here.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsConfigDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Agents;
