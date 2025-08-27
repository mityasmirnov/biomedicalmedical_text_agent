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
  Tabs,
  Tab,
  MenuItem,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  Biotech as BiotechIcon,
  Description as DescriptionIcon,
  Storage as StorageIcon,
  DataObject as DataObjectIcon,
} from '@mui/icons-material';
import MetadataBrowser from '../../components/MetadataBrowser/MetadataBrowser';

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState(0);

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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

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

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="knowledge base tabs">
          <Tab 
            icon={<StorageIcon />} 
            label="Metadata Browser" 
            iconPosition="start"
          />
          <Tab 
            icon={<DataObjectIcon />} 
            label="Knowledge Items" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <MetadataBrowser />
      )}

      {activeTab === 1 && (
        <>
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
                <Grid item xs={12} md={3}>
                  <TextField
                    select
                    fullWidth
                    label="Category"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {category.icon}
                          <Typography sx={{ ml: 1 }}>{category.label}</Typography>
                          <Chip 
                            label={category.count} 
                            size="small" 
                            sx={{ ml: 'auto' }}
                          />
                        </Box>
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<SearchIcon />}
                  >
                    Search
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Knowledge Items */}
          <Grid container spacing={3}>
            {filteredItems.map((item) => (
              <Grid item xs={12} md={6} lg={4} key={item.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {item.category === 'phenotypes' && <PsychologyIcon color="primary" />}
                      {item.category === 'genes' && <BiotechIcon color="secondary" />}
                      {item.category === 'diseases' && <ScienceIcon color="success" />}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {item.title}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {item.description}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip 
                        label={item.category} 
                        size="small" 
                        variant="outlined"
                      />
                      <Typography variant="caption" color="text.secondary">
                        {item.lastUpdated}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Items: {item.count}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </Box>
  );
};

export default KnowledgeBase;
