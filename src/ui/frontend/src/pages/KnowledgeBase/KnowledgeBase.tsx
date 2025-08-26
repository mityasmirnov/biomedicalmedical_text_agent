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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  Biotech as BiotechIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'All', icon: <DescriptionIcon />, count: 1250 },
    { id: 'phenotypes', label: 'Phenotypes', icon: <PsychologyIcon />, count: 456 },
    { id: 'genes', label: 'Genes', icon: <BiotechIcon />, count: 234 },
    { id: 'diseases', label: 'Diseases', icon: <ScienceIcon />, count: 189 },
  ];

  const sampleKnowledgeItems = [
    {
      id: 1,
      title: 'Leigh Syndrome Phenotypes',
      category: 'phenotypes',
      description: 'Collection of phenotypic manifestations associated with Leigh syndrome',
      count: 45,
      lastUpdated: '2024-01-15',
    },
    {
      id: 2,
      title: 'Mitochondrial Disease Genes',
      category: 'genes',
      description: 'Genes associated with mitochondrial disorders and their variants',
      count: 67,
      lastUpdated: '2024-01-14',
    },
    {
      id: 3,
      title: 'Neurological Disorders',
      category: 'diseases',
      description: 'Comprehensive database of neurological conditions and their characteristics',
      count: 123,
      lastUpdated: '2024-01-13',
    },
  ];

  const filteredItems = sampleKnowledgeItems.filter(item => 
    (selectedCategory === 'all' || item.category === selectedCategory) &&
    (searchQuery === '' || 
     item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Knowledge Base
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Explore and manage biomedical knowledge, ontologies, and extracted data
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {categories.map((category) => (
                  <Chip
                    key={category.id}
                    label={`${category.label} (${category.count})`}
                    icon={category.icon}
                    onClick={() => setSelectedCategory(category.id)}
                    color={selectedCategory === category.id ? 'primary' : 'default'}
                    variant={selectedCategory === category.id ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Knowledge Categories */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            Knowledge Items ({filteredItems.length})
          </Typography>
          
          {filteredItems.map((item) => (
            <Card key={item.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {item.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip 
                        label={item.category} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                      <Typography variant="caption" color="text.secondary">
                        {item.count} entries • Updated {item.lastUpdated}
                      </Typography>
                    </Box>
                  </Box>
                  <Button variant="outlined" size="small">
                    Explore
                  </Button>
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
                variant="contained"
                startIcon={<ScienceIcon />}
                sx={{ mb: 2 }}
              >
                Add New Knowledge Item
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<BiotechIcon />}
                sx={{ mb: 2 }}
              >
                Import Ontology
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<DescriptionIcon />}
              >
                Export Knowledge Base
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Statistics
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Total Items" 
                    secondary="1,250" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Categories" 
                    secondary="4" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Last Updated" 
                    secondary="Today" 
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default KnowledgeBase;
