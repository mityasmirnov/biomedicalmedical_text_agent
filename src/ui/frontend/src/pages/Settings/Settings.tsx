import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  InputAdornment,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Notifications as NotificationsIcon,
  Language as LanguageIcon,
  Palette as PaletteIcon,
  Backup as BackupIcon,
  RestoreFromTrash as RestoreIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    // System Settings
    autoBackup: true,
    backupInterval: 24,
    maxFileSize: 50,
    enableLogging: true,
    logLevel: 'info',
    
    // Performance Settings
    maxConcurrentProcesses: 4,
    memoryLimit: 8,
    enableCaching: true,
    cacheSize: 2,
    
    // Security Settings
    requireAuthentication: true,
    sessionTimeout: 30,
    enableAuditLog: true,
    maxLoginAttempts: 3,
    
    // UI Settings
    theme: 'light',
    language: 'en',
    enableNotifications: true,
    notificationSound: true,
    
    // AI Settings
    enableAutoLearning: true,
    confidenceThreshold: 0.8,
    maxProcessingTime: 60,
    enableModelUpdates: true,
  });

  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);
  const [isRestoreDialogOpen, setIsRestoreDialogOpen] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSaveSettings = () => {
    // Simulate saving settings
    console.log('Saving settings:', settings);
    setHasUnsavedChanges(false);
    // In a real app, this would make an API call
  };

  const handleResetSettings = () => {
    // Reset to default values
    setSettings({
      autoBackup: true,
      backupInterval: 24,
      maxFileSize: 50,
      enableLogging: true,
      logLevel: 'info',
      maxConcurrentProcesses: 4,
      memoryLimit: 8,
      enableCaching: true,
      cacheSize: 2,
      requireAuthentication: true,
      sessionTimeout: 30,
      enableAuditLog: true,
      maxLoginAttempts: 3,
      theme: 'light',
      language: 'en',
      enableNotifications: true,
      notificationSound: true,
      enableAutoLearning: true,
      confidenceThreshold: 0.8,
      maxProcessingTime: 60,
      enableModelUpdates: true,
    });
    setHasUnsavedChanges(false);
  };

  const systemStatus = {
    database: 'healthy',
    aiModels: 'loaded',
    ontologies: 'up-to-date',
    lastBackup: '2 hours ago',
    nextBackup: '22 hours',
    systemUptime: '15 days',
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure system preferences, performance, security, and AI behavior
        </Typography>
      </Box>

      {/* System Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Database</Typography>
              </Box>
              <Chip 
                label={systemStatus.database} 
                color="success" 
                size="small" 
                icon={<CheckIcon />}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">AI Models</Typography>
              </Box>
              <Chip 
                label={systemStatus.aiModels} 
                color="success" 
                size="small" 
                icon={<CheckIcon />}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SettingsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Ontologies</Typography>
              </Box>
              <Chip 
                label={systemStatus.ontologies} 
                color="success" 
                size="small" 
                icon={<CheckIcon />}
              />
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
              <Typography variant="body2" color="text.secondary">
                {systemStatus.lastBackup}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Settings Sections */}
      <Grid container spacing={3}>
        {/* System Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                System Settings
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoBackup}
                    onChange={(e) => handleSettingChange('autoBackup', e.target.checked)}
                  />
                }
                label="Enable automatic backups"
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Backup Interval (hours)</InputLabel>
                <Select
                  value={settings.backupInterval}
                  label="Backup Interval (hours)"
                  onChange={(e) => handleSettingChange('backupInterval', e.target.value)}
                  disabled={!settings.autoBackup}
                >
                  <MenuItem value={6}>6 hours</MenuItem>
                  <MenuItem value={12}>12 hours</MenuItem>
                  <MenuItem value={24}>24 hours</MenuItem>
                  <MenuItem value={48}>48 hours</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Maximum file size (MB)"
                type="number"
                value={settings.maxFileSize}
                onChange={(e) => handleSettingChange('maxFileSize', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: <InputAdornment position="end">MB</InputAdornment>,
                }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableLogging}
                    onChange={(e) => handleSettingChange('enableLogging', e.target.checked)}
                  />
                }
                label="Enable system logging"
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth>
                <InputLabel>Log Level</InputLabel>
                <Select
                  value={settings.logLevel}
                  label="Log Level"
                  onChange={(e) => handleSettingChange('logLevel', e.target.value)}
                  disabled={!settings.enableLogging}
                >
                  <MenuItem value="debug">Debug</MenuItem>
                  <MenuItem value="info">Info</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance Settings
              </Typography>
              
              <TextField
                fullWidth
                label="Max concurrent processes"
                type="number"
                value={settings.maxConcurrentProcesses}
                onChange={(e) => handleSettingChange('maxConcurrentProcesses', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                inputProps={{ min: 1, max: 16 }}
              />
              
              <TextField
                fullWidth
                label="Memory limit (GB)"
                type="number"
                value={settings.memoryLimit}
                onChange={(e) => handleSettingChange('memoryLimit', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: <InputAdornment position="end">GB</InputAdornment>,
                }}
                inputProps={{ min: 1, max: 32 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableCaching}
                    onChange={(e) => handleSettingChange('enableCaching', e.target.checked)}
                  />
                }
                label="Enable result caching"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Cache size (GB)"
                type="number"
                value={settings.cacheSize}
                onChange={(e) => handleSettingChange('cacheSize', parseInt(e.target.value))}
                disabled={!settings.enableCaching}
                InputProps={{
                  endAdornment: <InputAdornment position="end">GB</InputAdornment>,
                }}
                inputProps={{ min: 1, max: 10 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Security Settings
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.requireAuthentication}
                    onChange={(e) => handleSettingChange('requireAuthentication', e.target.checked)}
                  />
                }
                label="Require authentication"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Session timeout (minutes)"
                type="number"
                value={settings.sessionTimeout}
                onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                inputProps={{ min: 5, max: 480 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableAuditLog}
                    onChange={(e) => handleSettingChange('enableAuditLog', e.target.checked)}
                  />
                }
                label="Enable audit logging"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Max login attempts"
                type="number"
                value={settings.maxLoginAttempts}
                onChange={(e) => handleSettingChange('maxLoginAttempts', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 10 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* AI Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Settings
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableAutoLearning}
                    onChange={(e) => handleSettingChange('enableAutoLearning', e.target.checked)}
                  />
                }
                label="Enable auto-learning"
                sx={{ mb: 2 }}
              />
              
              <Typography gutterBottom>Confidence threshold</Typography>
              <Slider
                value={settings.confidenceThreshold}
                onChange={(_, value) => handleSettingChange('confidenceThreshold', value)}
                min={0.5}
                max={1.0}
                step={0.1}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Max processing time (seconds)"
                type="number"
                value={settings.maxProcessingTime}
                onChange={(e) => handleSettingChange('maxProcessingTime', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                inputProps={{ min: 10, max: 300 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableModelUpdates}
                    onChange={(e) => handleSettingChange('enableModelUpdates', e.target.checked)}
                  />
                }
                label="Enable automatic model updates"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          disabled={!hasUnsavedChanges}
          size="large"
        >
          Save Settings
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleResetSettings}
          size="large"
        >
          Reset to Defaults
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<BackupIcon />}
          onClick={() => setIsBackupDialogOpen(true)}
          size="large"
        >
          Backup Settings
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<RestoreIcon />}
          onClick={() => setIsRestoreDialogOpen(true)}
          size="large"
        >
          Restore Settings
        </Button>
      </Box>

      {/* Unsaved Changes Alert */}
      {hasUnsavedChanges && (
        <Alert severity="warning" sx={{ mt: 3 }}>
          You have unsaved changes. Click "Save Settings" to apply your changes.
        </Alert>
      )}

      {/* Backup Dialog */}
      <Dialog open={isBackupDialogOpen} onClose={() => setIsBackupDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Backup Settings</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will create a backup of your current settings configuration.
          </Alert>
          <TextField
            fullWidth
            label="Backup Name"
            margin="normal"
            placeholder="settings_backup_2024_01_15"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsBackupDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsBackupDialogOpen(false)}>
            Create Backup
          </Button>
        </DialogActions>
      </Dialog>

      {/* Restore Dialog */}
      <Dialog open={isRestoreDialogOpen} onClose={() => setIsRestoreDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Restore Settings</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will overwrite your current settings. This action cannot be undone.
          </Alert>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select Backup</InputLabel>
            <Select label="Select Backup">
              <MenuItem value="backup1">settings_backup_2024_01_14</MenuItem>
              <MenuItem value="backup2">settings_backup_2024_01_10</MenuItem>
              <MenuItem value="backup3">settings_backup_2024_01_05</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRestoreDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={() => setIsRestoreDialogOpen(false)}>
            Restore Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;
