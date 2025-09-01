import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip
} from '@mui/material';
import { Assessment, Download, Refresh } from '@mui/icons-material';
import { api } from '../services/api';

const PlotlyChart = ({ data, layout, config }: any) => (
  <div style={{ width: '100%', height: '400px', border: '1px solid #ddd', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <Typography color="textSecondary">
      Chart: {layout?.title?.text || 'Visualization'}
    </Typography>
  </div>
);

const DataVisualization: React.FC = () => {
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [selectedDataset, setSelectedDataset] = useState('all');
  const [selectedChart, setSelectedChart] = useState('overview');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVisualizations();
  }, [selectedDataset, selectedChart]);

  const loadVisualizations = async () => {
    setLoading(true);
    try {
      const response = await api.analytics.getVisualizations({
        dataset: selectedDataset,
        chart_type: selectedChart
      });
      setVisualizations(response.data);
    } catch (error) {
      console.error('Failed to load visualizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const response = await api.analytics.exportVisualizations({
        dataset: selectedDataset,
        format: format
      });
      const blob = new Blob([response.data], {
        type: format === 'pdf' ? 'application/pdf' : 'text/html'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `visualizations.${format}`;
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Visualization (Enhanced)
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Dataset</InputLabel>
                <Select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  label="Dataset"
                >
                  <MenuItem value="all">All Data</MenuItem>
                  <MenuItem value="leigh_syndrome">Leigh Syndrome</MenuItem>
                  <MenuItem value="mitochondrial">Mitochondrial Diseases</MenuItem>
                  <MenuItem value="recent">Recent Extractions</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Chart Type</InputLabel>
                <Select
                  value={selectedChart}
                  onChange={(e) => setSelectedChart(e.target.value)}
                  label="Chart Type"
                >
                  <MenuItem value="overview">Overview Dashboard</MenuItem>
                  <MenuItem value="demographics">Demographics</MenuItem>
                  <MenuItem value="genetics">Genetic Analysis</MenuItem>
                  <MenuItem value="phenotypes">Phenotype Distribution</MenuItem>
                  <MenuItem value="treatments">Treatment Patterns</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadVisualizations}
                disabled={loading}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => handleExport('html')}
                fullWidth
              >
                Export
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {visualizations.map((viz: any, index: number) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    {viz.title}
                  </Typography>
                  <Chip
                    label={viz.type}
                    size="small"
                    color="primary"
                  />
                </Box>

                <PlotlyChart
                  data={viz.data}
                  layout={viz.layout}
                  config={viz.config}
                />

                {viz.description && (
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                    {viz.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {visualizations.length === 0 && !loading && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No visualizations available
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Select a dataset and chart type to view visualizations
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DataVisualization;



