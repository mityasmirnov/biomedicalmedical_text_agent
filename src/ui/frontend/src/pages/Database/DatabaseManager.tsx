import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import { 
  Storage, 
  Visibility, 
  Download, 
  Refresh, 
  Search, 
  Edit,
  Add,
  Delete
} from '@mui/icons-material';
import { api } from '../../services/api';

interface DatabaseTable {
  name: string;
  row_count: number;
  description?: string;
}

interface TableSchema {
  columns: Array<{
    name: string;
    type: string;
    primary_key?: boolean;
    unique?: boolean;
    not_null?: boolean;
    default_value?: string;
  }>;
}

interface DatabaseStatistics {
  total_records: number;
  database_size: string;
  last_updated: string;
  table_stats: DatabaseTable[];
}

const DatabaseManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [tables, setTables] = useState<DatabaseTable[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<any[]>([]);
  const [schema, setSchema] = useState<TableSchema | null>(null);
  const [statistics, setStatistics] = useState<DatabaseStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryDialogOpen, setQueryDialogOpen] = useState(false);
  const [customQuery, setCustomQuery] = useState('SELECT * FROM metadata LIMIT 10');

  useEffect(() => {
    loadDatabaseInfo();
  }, []);

  const loadDatabaseInfo = async () => {
    setLoading(true);
    try {
      const [tablesRes, statsRes] = await Promise.all([
        api.database.getTables(),
        api.database.getStatistics()
      ]);
      setTables(tablesRes.data.tables || []);
      setStatistics(statsRes.data);
      setError(null);
    } catch (error) {
      console.error('Failed to load database info:', error);
      setError('Failed to load database info - using mock data');
      // Set mock data for development
      setTables([
        { name: 'metadata', row_count: 1000, description: 'Literature metadata' },
        { name: 'fulltext_documents', row_count: 500, description: 'Full-text documents' },
        { name: 'extractions', row_count: 2000, description: 'Extraction results' },
        { name: 'validation_data', row_count: 1500, description: 'Validation data' },
        { name: 'patient_records', row_count: 3000, description: 'Patient records' }
      ]);
      setStatistics({
        total_records: 8000,
        database_size: '15.2 MB',
        last_updated: new Date().toISOString(),
        table_stats: []
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async (tableName: string) => {
    setLoading(true);
    try {
      const [dataRes, schemaRes] = await Promise.all([
        api.database.getTableData(tableName, { limit: 100 }),
        api.database.getTableSchema(tableName)
      ]);
      setTableData(dataRes.data.data || []);
      setSchema(schemaRes.data.schema);
      setSelectedTable(tableName);
      setError(null);
    } catch (error) {
      console.error('Failed to load table data:', error);
      setError(`Failed to load table data for ${tableName}`);
      // Set mock data for development
      if (tableName === 'metadata') {
        setTableData([
          {
            id: 1,
            pmid: '12345678',
            title: 'Sample Article',
            abstract: 'Sample abstract text...',
            journal: 'Journal Name',
            publication_date: '2024-01-15'
          }
        ]);
        setSchema({
          columns: [
            { name: 'id', type: 'INTEGER', primary_key: true },
            { name: 'pmid', type: 'TEXT', unique: true },
            { name: 'title', type: 'TEXT', not_null: true },
            { name: 'abstract', type: 'TEXT' },
            { name: 'journal', type: 'TEXT' },
            { name: 'publication_date', type: 'TEXT' }
          ]
        });
        setSelectedTable(tableName);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExportTable = async (tableName: string) => {
    try {
      const response = await api.database.exportTable(tableName);
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${tableName}_export.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    }
  };

  const handleCustomQuery = async () => {
    if (!customQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await api.database.query(customQuery);
      setTableData(response.data.results || []);
      setSchema(null); // Custom query results don't have schema
      setSelectedTable('custom_query');
      setQueryDialogOpen(false);
    } catch (error) {
      console.error('Query failed:', error);
      alert('Query failed. Please check your SQL syntax.');
    } finally {
      setLoading(false);
    }
  };

  const getTableTypeColor = (tableName: string) => {
    if (tableName.includes('metadata')) return 'primary';
    if (tableName.includes('extraction')) return 'secondary';
    if (tableName.includes('validation')) return 'success';
    if (tableName.includes('patient')) return 'warning';
    return 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Tables" />
        <Tab label="Schema" />
        <Tab label="Statistics" />
        <Tab label="Query" />
      </Tabs>

      {/* Tables Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Database Tables
                  </Typography>
                  <Button
                    size="small"
                    startIcon={<Refresh />}
                    onClick={loadDatabaseInfo}
                    disabled={loading}
                  >
                    Refresh
                  </Button>
                </Box>
                
                {tables.map((table) => (
                  <Box key={table.name} mb={1}>
                    <Button
                      fullWidth
                      variant={selectedTable === table.name ? 'contained' : 'outlined'}
                      onClick={() => loadTableData(table.name)}
                      startIcon={<Storage />}
                      sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                    >
                      <Box sx={{ textAlign: 'left', width: '100%' }}>
                        <Typography variant="body2" fontWeight="bold">
                          {table.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {table.row_count.toLocaleString()} rows
                        </Typography>
                      </Box>
                    </Button>
                    {table.description && (
                      <Typography variant="caption" color="textSecondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                        {table.description}
                      </Typography>
                    )}
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {selectedTable && (
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {selectedTable} Data
                    </Typography>
                    <Box>
                      <Button
                        variant="outlined"
                        startIcon={<Download />}
                        onClick={() => handleExportTable(selectedTable)}
                        sx={{ mr: 1 }}
                      >
                        Export
                      </Button>
                      <Chip
                        label={`${tableData.length} rows`}
                        size="small"
                        color="primary"
                      />
                    </Box>
                  </Box>
                  
                  {loading && <LinearProgress sx={{ mb: 2 }} />}
                  
                  {schema && (
                    <TableContainer component={Paper} sx={{ mb: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Column</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Constraints</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {schema.columns.map((column) => (
                            <TableRow key={column.name}>
                              <TableCell>
                                <Typography variant="body2" fontWeight="bold">
                                  {column.name}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Chip label={column.type} size="small" />
                              </TableCell>
                              <TableCell>
                                <Box display="flex" gap={0.5}>
                                  {column.primary_key && <Chip label="PK" size="small" color="primary" />}
                                  {column.unique && <Chip label="UNIQUE" size="small" color="secondary" />}
                                  {column.not_null && <Chip label="NOT NULL" size="small" color="warning" />}
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                  
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          {schema?.columns.map((column) => (
                            <TableCell key={column.name}>
                              {column.name}
                              <Typography variant="caption" display="block" color="textSecondary">
                                {column.type}
                              </Typography>
                            </TableCell>
                          )) || tableData.length > 0 && Object.keys(tableData[0]).map((key) => (
                            <TableCell key={key}>{key}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tableData.map((row, index) => (
                          <TableRow key={index}>
                            {schema?.columns.map((column) => (
                              <TableCell key={column.name}>
                                <Typography variant="body2" noWrap>
                                  {String(row[column.name] || '')}
                                </Typography>
                              </TableCell>
                            )) || Object.values(row).map((value, i) => (
                              <TableCell key={i}>
                                <Typography variant="body2" noWrap>
                                  {String(value || '')}
                                </Typography>
                              </TableCell>
                            ))}
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

      {/* Schema Tab */}
      {selectedTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Database Schema Overview
            </Typography>
            <Grid container spacing={2}>
              {tables.map((table) => (
                <Grid item xs={12} md={6} key={table.name}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {table.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {table.description || 'No description available'}
                      </Typography>
                      <Chip
                        label={`${table.row_count.toLocaleString()} rows`}
                        size="small"
                        color={getTableTypeColor(table.name)}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Statistics Tab */}
      {selectedTab === 2 && statistics && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Statistics
                </Typography>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Total Records: {statistics.total_records.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Database Size: {statistics.database_size}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Last Updated: {new Date(statistics.last_updated).toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Table Statistics
                </Typography>
                {tables.map((table) => (
                  <Box key={table.name} mb={1}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">
                        {table.name}
                      </Typography>
                      <Chip
                        label={table.row_count.toLocaleString()}
                        size="small"
                        color={getTableTypeColor(table.name)}
                      />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(table.row_count / Math.max(...tables.map(t => t.row_count))) * 100}
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Query Tab */}
      {selectedTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Custom SQL Query
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Execute custom SQL queries against the database. Be careful with write operations.
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={4}
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="SELECT * FROM metadata LIMIT 10"
              variant="outlined"
              sx={{ mb: 2, fontFamily: 'monospace' }}
            />
            
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={handleCustomQuery}
                disabled={!customQuery.trim() || loading}
              >
                Execute Query
              </Button>
              <Button
                variant="outlined"
                onClick={() => setCustomQuery('SELECT * FROM metadata LIMIT 10')}
              >
                Reset
              </Button>
            </Box>
            
            {selectedTable === 'custom_query' && tableData.length > 0 && (
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Query Results
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {Object.keys(tableData[0]).map((key) => (
                          <TableCell key={key}>{key}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tableData.slice(0, 20).map((row, index) => (
                        <TableRow key={index}>
                          {Object.values(row).map((value, i) => (
                            <TableCell key={i}>
                              <Typography variant="body2" noWrap>
                                {String(value || '')}
                              </Typography>
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {tableData.length > 20 && (
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    Showing first 20 results of {tableData.length} total
                  </Typography>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DatabaseManager;
