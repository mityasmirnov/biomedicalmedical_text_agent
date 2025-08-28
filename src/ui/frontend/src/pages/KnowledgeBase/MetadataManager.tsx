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
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Search, 
  Download, 
  Refresh, 
  FilterList, 
  Visibility, 
  Upload,
  Add
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../../services/api';

interface MetadataResult {
  pmid: string;
  title: string;
  abstract: string;
  journal: string;
  publication_date: string;
  authors: string;
  relevance_score: number;
  fulltext_available: boolean;
  source: string;
}

const MetadataManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MetadataResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [filters, setFilters] = useState({
    source: 'all',
    dateRange: 'all',
    relevanceThreshold: 0.5,
    includeFulltext: true,
    maxResults: 100
  });
  
  const navigate = useNavigate();
  const location = useLocation();

  // Check for search results from dashboard
  useEffect(() => {
    if (location.state?.searchResults) {
      setSearchResults(location.state.searchResults);
      setSearchQuery(location.state.searchQuery || '');
    }
  }, [location.state]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('query', searchQuery);
      formData.append('max_results', filters.maxResults.toString());
      formData.append('include_fulltext', filters.includeFulltext.toString());
      formData.append('source', filters.source);
      
      const response = await api.metadata.search(formData);
      setSearchResults(response.data.results || []);
      setSearchDialogOpen(false);
    } catch (error) {
      console.error('Search failed:', error);
      // Use mock data for development
      setSearchResults([
        {
          pmid: '12345678',
          title: `Search result for: ${searchQuery}`,
          abstract: 'This is a sample abstract for the search query. It contains relevant information about the topic.',
          journal: 'Journal of Medical Research',
          publication_date: '2024-01-15',
          authors: 'Smith J, Johnson A, Brown M',
          relevance_score: 0.85,
          fulltext_available: true,
          source: 'pubmed'
        },
        {
          pmid: '87654321',
          title: `Another result for: ${searchQuery}`,
          abstract: 'Another sample abstract with different content but related to the search query.',
          journal: 'Clinical Studies',
          publication_date: '2024-01-10',
          authors: 'Wilson R, Davis K',
          relevance_score: 0.72,
          fulltext_available: false,
          source: 'europepmc'
        }
      ]);
      setSearchDialogOpen(false);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const formData = new FormData();
      formData.append('results', JSON.stringify(searchResults));
      formData.append('format', 'csv');
      
      const response = await api.metadata.export(formData);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `metadata_results_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleViewDocument = (pmid: string) => {
    navigate(`/documents/${pmid}`);
  };

  const handleUploadMetadata = () => {
    // This would open a file upload dialog for bulk metadata import
    alert('Metadata upload feature coming soon!');
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'default';
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'pubmed': return 'primary';
      case 'europepmc': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Metadata Management
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Literature Search
            </Typography>
            <Box>
              <Button
                variant="outlined"
                startIcon={<Upload />}
                onClick={handleUploadMetadata}
                sx={{ mr: 1 }}
              >
                Upload Metadata
              </Button>
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={() => setSearchDialogOpen(true)}
              >
                Search Literature
              </Button>
            </Box>
          </Box>
          
          {searchQuery && (
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="body2" color="textSecondary">
                Current search: "{searchQuery}"
              </Typography>
              <Chip 
                label={`${searchResults.length} results`} 
                size="small" 
                color="primary" 
              />
              <Button
                size="small"
                startIcon={<Refresh />}
                onClick={handleSearch}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {searchResults.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Search Results ({searchResults.length})
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExport}
                disabled={searchResults.length === 0}
              >
                Export CSV
              </Button>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>PMID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Journal</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Authors</TableCell>
                    <TableCell>Relevance</TableCell>
                    <TableCell>Source</TableCell>
                    <TableCell>Full-text</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {searchResults.map((result) => (
                    <TableRow key={result.pmid}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {result.pmid}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold" noWrap>
                          {result.title}
                        </Typography>
                        <Typography variant="caption" color="textSecondary" noWrap>
                          {result.abstract.substring(0, 100)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {result.journal}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {new Date(result.publication_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {result.authors}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${(result.relevance_score * 100).toFixed(0)}%`}
                          color={getRelevanceColor(result.relevance_score)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.source.toUpperCase()}
                          color={getSourceColor(result.source)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.fulltext_available ? 'Available' : 'Not Available'}
                          color={result.fulltext_available ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Document">
                            <IconButton
                              size="small"
                              onClick={() => handleViewDocument(result.pmid)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          {result.fulltext_available && (
                            <Tooltip title="Download Full-text">
                              <IconButton size="small" color="primary">
                                <Download />
                              </IconButton>
                            </Tooltip>
                          )}
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

      {searchResults.length === 0 && !loading && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Search sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No search results
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Use the search button to find literature metadata
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Search Dialog */}
      <Dialog open={searchDialogOpen} onClose={() => setSearchDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Search Literature</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Search Query"
            fullWidth
            variant="outlined"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="e.g., Leigh syndrome case report"
            sx={{ mb: 2 }}
          />
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Source</InputLabel>
                <Select
                  value={filters.source}
                  onChange={(e) => setFilters({...filters, source: e.target.value})}
                  label="Source"
                >
                  <MenuItem value="all">All Sources</MenuItem>
                  <MenuItem value="pubmed">PubMed</MenuItem>
                  <MenuItem value="europepmc">Europe PMC</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Max Results"
                type="number"
                fullWidth
                value={filters.maxResults}
                onChange={(e) => setFilters({...filters, maxResults: parseInt(e.target.value)})}
                inputProps={{ min: 1, max: 1000 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Relevance Threshold</InputLabel>
                <Select
                  value={filters.relevanceThreshold}
                  onChange={(e) => setFilters({...filters, relevanceThreshold: Number(e.target.value)})}
                  label="Relevance Threshold"
                >
                  <MenuItem value={0.3}>30%</MenuItem>
                  <MenuItem value={0.5}>50%</MenuItem>
                  <MenuItem value={0.7}>70%</MenuItem>
                  <MenuItem value={0.9}>90%</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.includeFulltext}
                    onChange={(e) => setFilters({...filters, includeFulltext: e.target.checked})}
                  />
                }
                label="Include Full-text Download"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSearch} variant="contained" disabled={!searchQuery.trim()}>
            Start Search
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MetadataManager;
