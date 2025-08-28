
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
  LinearProgress
} from '@mui/material';
import { Storage, Visibility, Download, Refresh, Search } from '@mui/icons-material';
import { api } from '../services/api';

const DatabaseManager: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [schema, setSchema] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);

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
      setTables(tablesRes.data);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Failed to load database info:', error);
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
      setTableData(dataRes.data);
      setSchema(schemaRes.data);
      setSelectedTable(tableName);
    } catch (error) {
      console.error('Failed to load table data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>

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
                <Typography variant="h6" gutterBottom>
                  Database Tables
                </Typography>
                {tables.map((table: any) => (
                  <Box key={table.name} mb={1}>
                    <Button
                      fullWidth
                      variant={selectedTable === table.name ? 'contained' : 'outlined'}
                      onClick={() => loadTableData(table.name)}
                      startIcon={<Storage />}
                    >
                      {table.name} ({table.row_count})
                    </Button>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {selectedTable && (
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {selectedTable} Data
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={() => api.database.exportTable(selectedTable)}
                    >
                      Export
                    </Button>
                  </Box>
                  
                  {loading && <LinearProgress sx={{ mb: 2 }} />}
                  
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          {schema?.columns.map((column: any) => (
                            <TableCell key={column.name}>
                              {column.name}
                              <Typography variant="caption" display="block">
                                {column.type}
                              </Typography>
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tableData.map((row: any, index: number) => (
                          <TableRow key={index}>
                            {schema?.columns.map((column: any) => (
                              <TableCell key={column.name}>
                                {row[column.name]}
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
                  <Typography variant="body2">
                    Total Records: {statistics.total_records}
                  </Typography>
                  <Typography variant="body2">
                    Database Size: {statistics.database_size}
                  </Typography>
                  <Typography variant="body2">
                    Last Updated: {statistics.last_updated}
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
                {statistics.table_stats?.map((table: any) => (
                  <Box key={table.name} mb={1}>
                    <Typography variant="body2">
                      {table.name}: {table.row_count} rows
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default DatabaseManager;
