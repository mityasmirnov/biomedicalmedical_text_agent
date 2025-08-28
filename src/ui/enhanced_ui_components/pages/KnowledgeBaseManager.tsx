
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Tree,
  TreeItem,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { AccountTree, Add, Edit, Delete, Search, Refresh } from '@mui/icons-material';
import { api } from '../services/api';

const KnowledgeBaseManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [ontologies, setOntologies] = useState([]);
  const [selectedOntology, setSelectedOntology] = useState(null);
  const [ontologyTerms, setOntologyTerms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOntologies();
  }, []);

  const loadOntologies = async () => {
    setLoading(true);
    try {
      const response = await api.ontologies.getAll();
      setOntologies(response.data);
    } catch (error) {
      console.error('Failed to load ontologies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOntologyTerms = async (ontologyId: string) => {
    setLoading(true);
    try {
      const response = await api.ontologies.getTerms(ontologyId);
      setOntologyTerms(response.data);
      setSelectedOntology(ontologyId);
    } catch (error) {
      console.error('Failed to load ontology terms:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchTerms = async () => {
    if (!searchQuery) return;
    
    setLoading(true);
    try {
      const response = await api.ontologies.search({
        query: searchQuery,
        ontology: selectedOntology
      });
      setOntologyTerms(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Management
      </Typography>

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Ontologies" />
        <Tab label="Gene Database" />
        <Tab label="Custom Vocabularies" />
      </Tabs>

      {/* Ontologies Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Available Ontologies
                </Typography>
                {ontologies.map((ontology: any) => (
                  <Box key={ontology.id} mb={1}>
                    <Button
                      fullWidth
                      variant={selectedOntology === ontology.id ? 'contained' : 'outlined'}
                      onClick={() => loadOntologyTerms(ontology.id)}
                      startIcon={<AccountTree />}
                    >
                      {ontology.name}
                    </Button>
                    <Typography variant="caption" display="block" color="textSecondary">
                      {ontology.term_count} terms
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {selectedOntology && (
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      Ontology Terms
                    </Typography>
                    <Box display="flex" gap={1}>
                      <TextField
                        size="small"
                        placeholder="Search terms..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && searchTerms()}
                      />
                      <Button
                        variant="outlined"
                        startIcon={<Search />}
                        onClick={searchTerms}
                      >
                        Search
                      </Button>
                    </Box>
                  </Box>
                  
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Term ID</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Definition</TableCell>
                          <TableCell>Synonyms</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {ontologyTerms.map((term: any) => (
                          <TableRow key={term.id}>
                            <TableCell>
                              <Chip label={term.id} size="small" />
                            </TableCell>
                            <TableCell>{term.name}</TableCell>
                            <TableCell>
                              <Typography variant="body2" noWrap>
                                {term.definition}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              {term.synonyms?.map((synonym: string, index: number) => (
                                <Chip
                                  key={index}
                                  label={synonym}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mr: 0.5, mb: 0.5 }}
                                />
                              ))}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default KnowledgeBaseManager;
