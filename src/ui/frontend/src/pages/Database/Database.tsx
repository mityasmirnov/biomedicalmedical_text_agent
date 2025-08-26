import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
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
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  TableChart as TableChartIcon,
  Backup as BackupIcon,
} from '@mui/icons-material';

const Database: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTable, setSelectedTable] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);

  const tables = [
    { name: 'patients', count: 1250, description: 'Patient demographic and clinical data' },
    { name: 'phenotypes', count: 456, description: 'Extracted phenotypic manifestations' },
    { name: 'genetics', count: 234, description: 'Genetic variants and gene information' },
    { name: 'treatments', count: 189, description: 'Treatment and intervention data' },
    { name: 'outcomes', count: 167, description: 'Clinical outcomes and follow-up data' },
  ];

  const sampleData = [
    {
      id: 1,
      patient_id: 'P001',
      age: 32,
      gender: 'F',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Mitochondrial encephalopathy',
      status: 'active',
    },
    {
      id: 2,
      patient_id: 'P002',
      age: 28,
      gender: 'M',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Progressive neurological deterioration',
      status: 'active',
    },
    {
      id: 3,
      patient_id: 'P003',
      age: 45,
      gender: 'F',
      diagnosis: 'Leigh Syndrome',
      phenotype: 'Seizures, developmental delay',
      status: 'inactive',
    },
  ];

  const filteredTables = tables.filter(table =>
    table.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    table.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Database Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and explore your biomedical data, tables, and database operations
        </Typography>
      </Box>

      {/* Database Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Tables</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {tables.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active database tables
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TableChartIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Records</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {tables.reduce((sum, table) => sum + table.count, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all tables
              </Typography>
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
              <Typography variant="h6" color="primary">
                2 hours ago
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Automated backup
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Status</Typography>
              </Box>
              <Typography variant="h6" color="success.main">
                Healthy
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All systems operational
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search tables..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setIsAddDialogOpen(true)}
                >
                  Add Table
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                >
                  Import Data
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                >
                  Export
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                >
                  Refresh
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tables Overview */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            Database Tables
          </Typography>
          
          {filteredTables.map((table) => (
            <Card key={table.name} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {table.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {table.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip 
                        label={`${table.count} records`} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                      <Typography variant="caption" color="text.secondary">
                        Last updated: Today
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton size="small" color="primary">
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="secondary">
                      <TableChartIcon />
                    </IconButton>
                    <IconButton size="small" color="error">
                      <DeleteIcon />
                    </IconButton>
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
                variant="outlined"
                startIcon={<BackupIcon />}
                onClick={() => setIsBackupDialogOpen(true)}
                sx={{ mb: 2 }}
              >
                Create Backup
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<StorageIcon />}
                sx={{ mb: 2 }}
              >
                Optimize Database
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<TableChartIcon />}
              >
                View Schema
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Database Health
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Storage Usage
                </Typography>
                <LinearProgress variant="determinate" value={65} sx={{ mb: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  65% used (2.3 GB / 3.5 GB)
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Performance
                </Typography>
                <LinearProgress variant="determinate" value={85} sx={{ mb: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  85% optimal
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Table Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Table</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Table Name"
            margin="normal"
            placeholder="e.g., clinical_notes"
          />
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            placeholder="Describe the purpose of this table..."
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Table Type</InputLabel>
            <Select label="Table Type">
              <MenuItem value="patient">Patient Data</MenuItem>
              <MenuItem value="clinical">Clinical Data</MenuItem>
              <MenuItem value="genetic">Genetic Data</MenuItem>
              <MenuItem value="phenotype">Phenotype Data</MenuItem>
              <MenuItem value="custom">Custom</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsAddDialogOpen(false)}>
            Create Table
          </Button>
        </DialogActions>
      </Dialog>

      {/* Backup Dialog */}
      <Dialog open={isBackupDialogOpen} onClose={() => setIsBackupDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Database Backup</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This will create a complete backup of your database including all tables and data.
          </Alert>
          <TextField
            fullWidth
            label="Backup Name"
            margin="normal"
            placeholder="backup_2024_01_15"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Backup Type</InputLabel>
            <Select label="Backup Type">
              <MenuItem value="full">Full Backup</MenuItem>
              <MenuItem value="incremental">Incremental Backup</MenuItem>
              <MenuItem value="schema">Schema Only</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsBackupDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setIsBackupDialogOpen(false)}>
            Start Backup
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Database;
