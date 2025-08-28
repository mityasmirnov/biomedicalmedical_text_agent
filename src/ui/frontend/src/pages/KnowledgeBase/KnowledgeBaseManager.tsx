import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,

  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tabs,
  Tab,
  Tooltip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Search,
  Add,
  Edit,
  Delete,
  ExpandMore,
  ExpandLess,
  Science,
  Category,
  Description,
  Code,
  Visibility,
  VisibilityOff,
  Refresh,
  Download,
  Upload,
  Save,
  Cancel
} from '@mui/icons-material';
import { api } from '../../services/api';

interface OntologyTerm {
  id: string;
  name: string;
  description?: string;
  synonyms?: string[];
  parent_id?: string;
  children?: OntologyTerm[];
  metadata?: Record<string, any>;
  is_leaf?: boolean;
}

interface Ontology {
  id: string;
  name: string;
  description: string;
  version: string;
  source: string;
  term_count: number;
  last_updated: string;
  terms: OntologyTerm[];
}

interface SearchResult {
  term: OntologyTerm;
  ontology: string;
  relevance: number;
  matched_fields: string[];
}

const KnowledgeBaseManager: React.FC = () => {
  const [ontologies, setOntologies] = useState<Ontology[]>([]);
  const [selectedOntology, setSelectedOntology] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTerm, setEditingTerm] = useState<OntologyTerm | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadOntologies();
  }, []);

  const loadOntologies = async () => {
    setLoading(true);
    try {
      const response = await api.ontologies.getAll();
      setOntologies(response.data.ontologies || []);
      setError(null);
    } catch (error) {
      console.error('Failed to load ontologies:', error);
      setError('Failed to load ontologies - using mock data');
      // Set mock data for development
      setOntologies([
        {
          id: 'hpo',
          name: 'Human Phenotype Ontology',
          description: 'Standard vocabulary of phenotypic abnormalities encountered in human disease',
          version: '2024-01-15',
          source: 'https://hpo.jax.org/',
          term_count: 15447,
          last_updated: '2024-01-15',
          terms: [
            {
              id: 'HP:0000001',
              name: 'All',
              description: 'Root term for all phenotypes',
              synonyms: ['All phenotypes'],
              is_leaf: false,
              children: [
                {
                  id: 'HP:0000118',
                  name: 'Phenotypic abnormality',
                  description: 'An abnormality of the phenotype',
                  synonyms: ['Phenotypic abnormality'],
                  parent_id: 'HP:0000001',
                  is_leaf: false,
                  children: [
                    {
                      id: 'HP:0000002',
                      name: 'Abnormality of body height',
                      description: 'Abnormal body height',
                      synonyms: ['Height abnormality', 'Stature abnormality'],
                      parent_id: 'HP:0000118',
                      is_leaf: true
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          id: 'genes',
          name: 'Gene Ontology',
          description: 'Standard representation of gene and gene product attributes',
          version: '2024-01-20',
          source: 'http://geneontology.org/',
          term_count: 45678,
          last_updated: '2024-01-20',
          terms: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await api.ontologies.search(searchQuery);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Failed to search ontologies:', error);
      // Mock search results
      setSearchResults([
        {
          term: {
            id: 'HP:0000002',
            name: 'Abnormality of body height',
            description: 'Abnormal body height'
          },
          ontology: 'hpo',
          relevance: 0.95,
          matched_fields: ['name', 'description']
        }
      ]);
    }
  };

  const handleEditTerm = (term: OntologyTerm) => {
    setEditingTerm(term);
    setEditDialogOpen(true);
  };

  const handleSaveTerm = async () => {
    if (!editingTerm) return;
    
    try {
      // Save term changes
      await api.ontologies.updateTerm(editingTerm.id, editingTerm);
      
      // Update local state
      setOntologies(prev => prev.map(onto => ({
        ...onto,
        terms: updateTermsInOntology(onto.terms, editingTerm)
      })));
      
      setEditDialogOpen(false);
      setEditingTerm(null);
    } catch (error) {
      console.error('Failed to save term:', error);
      alert('Failed to save term. Please try again.');
    }
  };

  const updateTermsInOntology = (terms: OntologyTerm[], updatedTerm: OntologyTerm): OntologyTerm[] => {
    return terms.map(term => {
      if (term.id === updatedTerm.id) {
        return updatedTerm;
      }
      if (term.children) {
        return {
          ...term,
          children: updateTermsInOntology(term.children, updatedTerm)
        };
      }
      return term;
    });
  };

  const renderTermList = (terms: OntologyTerm[], level: number = 0): React.ReactNode => {
    return terms.map(term => (
      <React.Fragment key={term.id}>
        <ListItem sx={{ pl: level * 2 + 2 }}>
          <ListItemIcon>
            <Typography variant="h6">
              {getOntologyIcon('default')}
            </Typography>
          </ListItemIcon>
          <ListItemText
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2">{term.name}</Typography>
                {term.is_leaf && <Chip label="Leaf" size="small" color="primary" />}
              </Box>
            }
            secondary={term.description}
          />
          <ListItemSecondaryAction>
            <Tooltip title="Edit Term">
              <IconButton size="small" onClick={() => handleEditTerm(term)}>
                <Edit fontSize="small" />
              </IconButton>
            </Tooltip>
          </ListItemSecondaryAction>
        </ListItem>
        {term.children && term.children.length > 0 && renderTermList(term.children, level + 1)}
      </React.Fragment>
    ));
  };

  const getOntologyIcon = (ontologyId: string) => {
    switch (ontologyId) {
      case 'hpo': return '🧬';
      case 'genes': return '🧪';
      default: return '📚';
    }
  };

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return 'success';
    if (relevance >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              placeholder="Search ontologies and terms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={!searchQuery.trim()}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Ontology Browser */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ontology Browser
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Ontology</InputLabel>
                <Select
                  value={selectedOntology}
                  onChange={(e) => setSelectedOntology(e.target.value)}
                  label="Select Ontology"
                >
                  {ontologies.map(onto => (
                    <MenuItem key={onto.id} value={onto.id}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography>{getOntologyIcon(onto.id)}</Typography>
                        <Typography>{onto.name}</Typography>
                        <Chip label={onto.term_count} size="small" />
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedOntology && (
                <Box>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    {ontologies.find(o => o.id === selectedOntology)?.description}
                  </Typography>
                  
                  <List>
                    {renderTermList(ontologies.find(o => o.id === selectedOntology)?.terms || [])}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Search Results */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Search Results
              </Typography>
              
              {searchResults.length > 0 ? (
                <List>
                  {searchResults.map((result, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <Typography variant="h6">
                            {getOntologyIcon(result.ontology)}
                          </Typography>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle1">
                                {result.term.name}
                              </Typography>
                              <Chip
                                label={`${(result.relevance * 100).toFixed(0)}%`}
                                size="small"
                                color={getRelevanceColor(result.relevance)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {result.term.description}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                Matched: {result.matched_fields.join(', ')}
                              </Typography>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Tooltip title="Edit Term">
                            <IconButton
                              edge="end"
                              onClick={() => handleEditTerm(result.term)}
                            >
                              <Edit />
                            </IconButton>
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < searchResults.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="textSecondary" align="center">
                  No search results yet. Use the search bar above to find terms.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Ontology Details */}
      {selectedOntology && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Ontology Details: {ontologies.find(o => o.id === selectedOntology)?.name}
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2">
                  <strong>Version:</strong> {ontologies.find(o => o.id === selectedOntology)?.version}
                </Typography>
                <Typography variant="body2">
                  <strong>Source:</strong> {ontologies.find(o => o.id === selectedOntology)?.source}
                </Typography>
                <Typography variant="body2">
                  <strong>Last Updated:</strong> {ontologies.find(o => o.id === selectedOntology)?.last_updated}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box display="flex" gap={1}>
                  <Button
                    startIcon={<Download />}
                    variant="outlined"
                    size="small"
                  >
                    Export
                  </Button>
                  <Button
                    startIcon={<Upload />}
                    variant="outlined"
                    size="small"
                  >
                    Import
                  </Button>
                  <Button
                    startIcon={<Refresh />}
                    variant="outlined"
                    size="small"
                  >
                    Refresh
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Edit Term Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Edit Term: {editingTerm?.name}
        </DialogTitle>
        <DialogContent>
          {editingTerm && (
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                label="Term Name"
                value={editingTerm.name}
                onChange={(e) => setEditingTerm({ ...editingTerm, name: e.target.value })}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Description"
                value={editingTerm.description || ''}
                onChange={(e) => setEditingTerm({ ...editingTerm, description: e.target.value })}
                multiline
                rows={3}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Synonyms (comma-separated)"
                value={editingTerm.synonyms?.join(', ') || ''}
                onChange={(e) => setEditingTerm({
                  ...editingTerm,
                  synonyms: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                })}
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth>
                <InputLabel>Parent Term</InputLabel>
                <Select
                  value={editingTerm.parent_id || ''}
                  onChange={(e) => setEditingTerm({ ...editingTerm, parent_id: e.target.value })}
                  label="Parent Term"
                >
                  <MenuItem value="">No Parent</MenuItem>
                  {/* Add parent term options here */}
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveTerm} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KnowledgeBaseManager;
