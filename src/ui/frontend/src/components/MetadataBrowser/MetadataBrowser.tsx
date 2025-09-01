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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Pagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Science as ScienceIcon,
  Link as LinkIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';

const MetadataBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [isDocumentDialogOpen, setIsDocumentDialogOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Fetch metadata overview (local collections)
  const { data: metadataOverview, isLoading: overviewLoading } = useQuery({
    queryKey: ['metadata-overview'],
            queryFn: () => api.metadata.getAll(),
  });

  // Extract data from API response
  const metadataData = metadataOverview?.data || metadataOverview;

  // Fetch collection documents (from local DB)
  const { data: collectionData, isLoading: collectionLoading } = useQuery({
    queryKey: ['collection-documents', selectedCollection, page],
            queryFn: () => selectedCollection ? 
            api.metadata.getById(selectedCollection) :
            null,
    enabled: !!selectedCollection,
  });

  // Extract data from API response
  const collectionDataExtracted = collectionData?.data || collectionData;

  // PubMed/triage search via backend orchestrator
  const {
    mutate: runSearch,
    data: searchResponse,
    isLoading: searchLoading,
  } = useMutation((q: string) => api.metadataTriage.search(q));

  const searchResults = (searchResponse as any)?.data?.results || [];

  const handleCollectionSelect = (collectionName: string) => {
    setSelectedCollection(collectionName);
    setPage(1);
  };

  const handleDocumentView = (document: any) => {
    setSelectedDocument(document);
    setIsDocumentDialogOpen(true);
  };

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    runSearch(searchQuery.trim());
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Metadata Browser
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Browse and search your biomedical metadata triage system
      </Typography>

      {/* Search Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                placeholder="Search metadata (e.g., 'Leigh syndrome', 'mitochondrial', 'NDUFS1')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Search Results */}
        {searchLoading && (
          <Grid item xs={12}>
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography>Searching PubMed…</Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
        {!!searchResults.length && (
          <Grid item xs={12}>
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Search Results ({searchResults.length})
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>PMID</TableCell>
                        <TableCell>Title</TableCell>
                        <TableCell>Journal</TableCell>
                        <TableCell>Year</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {searchResults.map((doc: any) => (
                        <TableRow key={doc.pmid || doc.id} hover>
                          <TableCell>
                            <Chip label={doc.pmid || 'N/A'} size="small" color="primary" />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap sx={{ maxWidth: 500 }}>
                              {doc.title || doc.article_title || 'Untitled'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {doc.journal || doc.journal_title || '—'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {doc.year || doc.publication_year || '—'}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {doc.pmid && (
                              <Tooltip title="View on PubMed">
                                <IconButton size="small" onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${doc.pmid}/`, '_blank')}>
                                  <LinkIcon />
                                </IconButton>
                              </Tooltip>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
        {/* Collections Sidebar */}
        <Grid item xs={12} md={4}>
          <Typography variant="h6" gutterBottom>
            Collections ({metadataData?.total_collections || 0})
          </Typography>
          
          {overviewLoading ? (
            <Typography>Loading collections...</Typography>
          ) : (
            <List>
              {metadataData?.collections?.map((collection: any) => (
                <ListItem
                  key={collection.name}
                  button
                  selected={selectedCollection === collection.name}
                  onClick={() => handleCollectionSelect(collection.name)}
                >
                  <ListItemIcon>
                    <ScienceIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={collection.name}
                    secondary={`${collection.document_count} documents`}
                  />
                  <Chip 
                    label={collection.pipeline_status} 
                    size="small" 
                    color={collection.pipeline_status === 'completed' ? 'success' : 'warning'}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Grid>

        {/* Documents Content */}
        <Grid item xs={12} md={8}>
          {selectedCollection ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedCollection} Documents
              </Typography>
              
              {collectionLoading ? (
                <Typography>Loading documents...</Typography>
              ) : (
                <>
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>PMID</TableCell>
                          <TableCell>Title</TableCell>
                          <TableCell>Study Type</TableCell>
                          <TableCell>Confidence</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {collectionDataExtracted?.documents?.map((doc: any) => (
                          <TableRow key={doc.pmid} hover>
                            <TableCell>
                              <Chip 
                                label={doc.pmid || 'N/A'} 
                                size="small" 
                                color="primary" 
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                                {doc.title}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={doc.study_type || 'Unknown'} 
                                size="small" 
                                variant="outlined" 
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {Math.round((doc.classification_confidence || 0) * 100)}%
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Tooltip title="View Details">
                                <IconButton 
                                  size="small" 
                                  onClick={() => handleDocumentView(doc)}
                                >
                                  <ViewIcon />
                                </IconButton>
                              </Tooltip>
                              {doc.pmc_link && (
                                <Tooltip title="View Full Text">
                                  <IconButton 
                                    size="small" 
                                    onClick={() => window.open(doc.pmc_link, '_blank')}
                                  >
                                    <LinkIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  {/* Pagination */}
                  {collectionDataExtracted?.pagination && (
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                      <Pagination
                        count={Math.ceil(collectionDataExtracted.pagination.total / pageSize)}
                        page={page}
                        onChange={(_, value) => setPage(value)}
                        color="primary"
                      />
                    </Box>
                  )}
                </>
              )}
            </Box>
          ) : (
            <Typography variant="body1" color="text.secondary">
              Select a collection to view documents
            </Typography>
          )}
        </Grid>
      </Grid>

      {/* Document Details Dialog */}
      <Dialog 
        open={isDocumentDialogOpen} 
        onClose={() => setIsDocumentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Document Details</DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {selectedDocument.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  PMID: {selectedDocument.pmid} • {selectedDocument.journal} • {selectedDocument.pub_date}
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>Abstract</Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {selectedDocument.abstract || 'No abstract available'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Authors</Typography>
                <Typography variant="body2">
                  {selectedDocument.authors || 'Unknown'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Study Type</Typography>
                <Typography variant="body2">
                  {selectedDocument.study_type || 'Unknown'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Classification Confidence</Typography>
                <Typography variant="body2">
                  {Math.round((selectedDocument.classification_confidence || 0) * 100)}%
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Concept Density</Typography>
                <Typography variant="body2">
                  {selectedDocument.concept_density?.toFixed(2) || 'N/A'}
                </Typography>
              </Grid>
              
              {selectedDocument.pmc_link && (
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    startIcon={<LinkIcon />}
                    onClick={() => window.open(selectedDocument.pmc_link, '_blank')}
                    fullWidth
                  >
                    View Full Text on PubMed Central
                  </Button>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDocumentDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MetadataBrowser;
