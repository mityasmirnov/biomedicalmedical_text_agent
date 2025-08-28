
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
  LinearProgress
} from '@mui/material';
import { Search, Download, Refresh, FilterList, Visibility } from '@mui/icons-material';
import { api } from '../services/api';

const MetadataManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    source: 'all',
    dateRange: 'all',
    relevanceThreshold: 0.5,
    includeFulltext: true
  });

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await api.metadata.search({
        query: searchQuery,
        filters: filters,
        max_results: 1000
      });
      setSearchResults(response.data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.metadata.export({
        results: searchResults,
        format: 'csv'
      });
      // Download file
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'metadata_results.csv';
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
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
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search Query"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., Leigh syndrome case report"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Source</InputLabel>
                <Select
                  value={filters.source}
                  onChange={(e) => setFilters({...filters, source: e.target.value})}
                >
                  <MenuItem value="all">All Sources</MenuItem>
                  <MenuItem value="pubmed">PubMed</MenuItem>
                  <MenuItem value="europepmc">Europe PMC</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={handleSearch}
                disabled={loading || !searchQuery}
                fullWidth
              >
                Search
              </Button>
            </Grid>
          </Grid>
          
          {/* Advanced Filters */}
          <Box mt={2}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.includeFulltext}
                  onChange={(e) => setFilters({...filters, includeFulltext: e.target.checked})}
                />
              }
              label="Include Full-text Download"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Results */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {searchResults.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Search Results ({searchResults.length})
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExport}
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
                    <TableCell>Relevance</TableCell>
                    <TableCell>Full-text</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {searchResults.map((result: any) => (
                    <TableRow key={result.pmid}>
                      <TableCell>{result.pmid}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {result.title}
                        </Typography>
                      </TableCell>
                      <TableCell>{result.journal}</TableCell>
                      <TableCell>{result.publication_date}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${(result.relevance_score * 100).toFixed(0)}%`}
                          color={result.relevance_score > 0.7 ? 'success' : 'default'}
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
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          href={`/documents/${result.pmid}`}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default MetadataManager;
