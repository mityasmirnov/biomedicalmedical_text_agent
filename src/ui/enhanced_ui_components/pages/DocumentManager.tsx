
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
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Upload, Visibility, Download, Delete, PlayArrow, Stop } from '@mui/icons-material';
import { api } from '../services/api';

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState([]);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [extractionModel, setExtractionModel] = useState('google/gemma-2-27b-it:free');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.documents.getAll();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles) return;

    const formData = new FormData();
    Array.from(selectedFiles).forEach(file => {
      formData.append('files', file);
    });
    formData.append('extraction_model', extractionModel);

    try {
      await api.documents.upload(formData);
      setUploadDialogOpen(false);
      setSelectedFiles(null);
      loadDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleExtraction = async (documentId: string) => {
    try {
      await api.documents.startExtraction(documentId, {
        model: extractionModel
      });
      loadDocuments();
    } catch (error) {
      console.error('Extraction failed:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Management
      </Typography>

      {/* Upload Button */}
      <Box mb={3}>
        <Button
          variant="contained"
          startIcon={<Upload />}
          onClick={() => setUploadDialogOpen(true)}
        >
          Upload Documents
        </Button>
      </Box>

      {/* Documents Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Documents ({documents.length})
          </Typography>
          
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Patients</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documents.map((doc: any) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {doc.filename}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {doc.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={doc.file_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={doc.status}
                        color={getStatusColor(doc.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {doc.status === 'processing' ? (
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={doc.progress || 0}
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">
                            {doc.progress || 0}%
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2">
                          {doc.status === 'completed' ? '100%' : '-'}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.patient_count || 0}
                    </TableCell>
                    <TableCell>
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          href={`/documents/${doc.id}`}
                        >
                          View
                        </Button>
                        {doc.status === 'uploaded' && (
                          <Button
                            size="small"
                            startIcon={<PlayArrow />}
                            onClick={() => handleExtraction(doc.id)}
                          >
                            Extract
                          </Button>
                        )}
                        {doc.status === 'processing' && (
                          <Button
                            size="small"
                            startIcon={<Stop />}
                            color="error"
                          >
                            Stop
                          </Button>
                        )}
                        {doc.status === 'completed' && (
                          <Button
                            size="small"
                            startIcon={<Download />}
                            href={`/api/documents/${doc.id}/export`}
                          >
                            Export
                          </Button>
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

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Box mb={3}>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              onChange={(e) => setSelectedFiles(e.target.files)}
              style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
            />
          </Box>
          
          <FormControl fullWidth>
            <InputLabel>Extraction Model</InputLabel>
            <Select
              value={extractionModel}
              onChange={(e) => setExtractionModel(e.target.value)}
              label="Extraction Model"
            >
              <MenuItem value="google/gemma-2-27b-it:free">Gemma 2 27B (Free)</MenuItem>
              <MenuItem value="microsoft/phi-3-mini-128k-instruct:free">Phi-3 Mini (Free)</MenuItem>
              <MenuItem value="meta-llama/llama-3.1-8b-instruct:free">Llama 3.1 8B (Free)</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpload} variant="contained" disabled={!selectedFiles}>
            Upload & Process
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentManager;
