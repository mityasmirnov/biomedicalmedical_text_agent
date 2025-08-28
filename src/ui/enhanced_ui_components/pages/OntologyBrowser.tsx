
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Tree,
  TreeItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { Search, AccountTree, Visibility, Edit } from '@mui/icons-material';
import { api } from '../services/api';

const OntologyBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [termDetails, setTermDetails] = useState(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    setLoading(true);
    try {
      const response = await api.ontologies.search({
        query: searchQuery,
        include_synonyms: true,
        include_definitions: true
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTermClick = async (termId: string) => {
    try {
      const response = await api.ontologies.getTermDetails(termId);
      setTermDetails(response.data);
      setSelectedTerm(termId);
      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Failed to load term details:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Ontology Browser
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              label="Search Terms"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., developmental delay, lactic acidosis"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={handleSearch}
              disabled={loading || !searchQuery}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Search Results ({searchResults.length})
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Term ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Ontology</TableCell>
                    <TableCell>Definition</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {searchResults.map((term: any) => (
                    <TableRow key={term.id}>
                      <TableCell>
                        <Chip label={term.id} size="small" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {term.name}
                        </Typography>
                        {term.synonyms && (
                          <Box mt={0.5}>
                            {term.synonyms.slice(0, 3).map((synonym: string, index: number) => (
                              <Chip
                                key={index}
                                label={synonym}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 0.5, fontSize: '0.7rem' }}
                              />
                            ))}
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={term.ontology}
                          size="small"
                          color={term.ontology === 'HPO' ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {term.definition}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          onClick={() => handleTermClick(term.id)}
                        >
                          Details
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

      {/* Term Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Term Details: {termDetails?.name}
        </DialogTitle>
        <DialogContent>
          {termDetails && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {termDetails.name}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                ID: {termDetails.id} | Ontology: {termDetails.ontology}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Definition
              </Typography>
              <Typography variant="body2" paragraph>
                {termDetails.definition}
              </Typography>
              
              {termDetails.synonyms && termDetails.synonyms.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Synonyms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.synonyms.map((synonym: string, index: number) => (
                      <Chip
                        key={index}
                        label={synonym}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </>
              )}
              
              {termDetails.parents && termDetails.parents.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Parent Terms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.parents.map((parent: any, index: number) => (
                      <Chip
                        key={index}
                        label={`${parent.id}: ${parent.name}`}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </>
              )}
              
              {termDetails.children && termDetails.children.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Child Terms
                  </Typography>
                  <Box mb={2}>
                    {termDetails.children.slice(0, 10).map((child: any, index: number) => (
                      <Chip
                        key={index}
                        label={`${child.id}: ${child.name}`}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                    {termDetails.children.length > 10 && (
                      <Typography variant="caption" color="textSecondary">
                        ... and {termDetails.children.length - 10} more
                      </Typography>
                    )}
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OntologyBrowser;
