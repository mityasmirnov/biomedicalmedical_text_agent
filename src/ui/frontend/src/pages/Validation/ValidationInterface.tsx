import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Cancel,
  Edit,
  Save,
  Visibility,
  HighlightAlt,
  Assessment
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface ExtractionSpan {
  start: number;
  end: number;
  text: string;
  extraction_type: string;
  field_name: string;
  confidence: number;
  normalized_value?: string;
}

interface ValidationData {
  extraction_id: string;
  original_text: string;
  highlighted_text: string;
  extractions: any[];
  spans: ExtractionSpan[];
  confidence_scores: Record<string, number>;
  validation_status: string;
  validator_notes?: string;
}

interface FieldCorrection {
  field_name: string;
  original_value: any;
  corrected_value: any;
  correction_type: 'value_change' | 'addition' | 'deletion';
}

const ValidationInterface: React.FC = () => {
  const { extractionId } = useParams<{ extractionId: string }>();
  const [validationData, setValidationData] = useState<ValidationData | null>(null);
  const [corrections, setCorrections] = useState<FieldCorrection[]>([]);
  const [validatorNotes, setValidatorNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<ExtractionSpan | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editValue, setEditValue] = useState('');
  
  const navigate = useNavigate();

  useEffect(() => {
    if (extractionId) {
      loadValidationData();
    }
  }, [extractionId]);

  const loadValidationData = async () => {
    try {
      setLoading(true);
      const response = await api.validation.getExtractionData(extractionId!);
      setValidationData(response.data);
      setValidatorNotes(response.data.validator_notes || '');
      setError(null);
    } catch (err) {
      console.error('Validation load error:', err);
      setError('Failed to load validation data - using mock data');
      // Set mock data for development
      setValidationData({
        extraction_id: extractionId!,
        original_text: "Patient was a 3-year-old male with Leigh syndrome due to MT-ATP6 c.8993T>G mutation. He presented with developmental delay and lactic acidosis.",
        highlighted_text: "Patient was a <span class='extraction-highlight' data-field='age_of_onset_years' data-type='demographics' data-confidence='0.9'>3-year-old male</span> with <span class='extraction-highlight' data-field='gene_symbol' data-type='genetics' data-confidence='0.95'>Leigh syndrome</span> due to <span class='extraction-highlight' data-field='mutation_description' data-type='genetics' data-confidence='0.85'>MT-ATP6 c.8993T>G</span> mutation. He presented with <span class='extraction-highlight' data-field='phenotype_description' data-type='phenotypes' data-confidence='0.8'>developmental delay and lactic acidosis</span>.",
        extractions: [
          { field_name: 'age_of_onset_years', value: '3', confidence: 0.9 },
          { field_name: 'sex', value: 'male', confidence: 0.95 },
          { field_name: 'gene_symbol', value: 'MT-ATP6', confidence: 0.95 },
          { field_name: 'mutation_description', value: 'c.8993T>G', confidence: 0.85 },
          { field_name: 'phenotype_description', value: 'developmental delay and lactic acidosis', confidence: 0.8 }
        ],
        spans: [
          {
            start: 8,
            end: 20,
            text: '3-year-old male',
            extraction_type: 'demographics',
            field_name: 'age_of_onset_years',
            confidence: 0.9,
            normalized_value: '3'
          },
          {
            start: 26,
            end: 38,
            text: 'Leigh syndrome',
            extraction_type: 'genetics',
            field_name: 'gene_symbol',
            confidence: 0.95,
            normalized_value: 'MT-ATP6'
          }
        ],
        confidence_scores: {
          'age_of_onset_years': 0.9,
          'sex': 0.95,
          'gene_symbol': 0.95,
          'mutation_description': 0.85,
          'phenotype_description': 0.8
        },
        validation_status: 'pending'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSpanClick = (span: ExtractionSpan) => {
    setSelectedSpan(span);
    setEditValue(span.normalized_value || span.text);
    setEditDialogOpen(true);
  };

  const handleFieldCorrection = () => {
    if (!selectedSpan) return;

    const correction: FieldCorrection = {
      field_name: selectedSpan.field_name,
      original_value: selectedSpan.normalized_value || selectedSpan.text,
      corrected_value: editValue,
      correction_type: editValue !== (selectedSpan.normalized_value || selectedSpan.text) 
        ? 'value_change' 
        : 'addition'
    };

    setCorrections(prev => {
      const existing = prev.findIndex(c => c.field_name === correction.field_name);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = correction;
        return updated;
      } else {
        return [...prev, correction];
      }
    });

    setEditDialogOpen(false);
    setSelectedSpan(null);
  };

  const handleValidationSubmit = async (status: 'validated' | 'rejected') => {
    try {
      setSaving(true);
      
      await api.validation.submitValidation(extractionId!, {
        validation_status: status,
        corrections: corrections.length > 0 ? corrections : undefined,
        validator_notes: validatorNotes || undefined
      });

      // Show success and redirect
      alert(`Validation ${status} successfully!`);
      navigate('/validation');
      
    } catch (err) {
      setError(`Failed to submit validation: ${err}`);
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getExtractionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'demographics': '#FFE6E6',
      'genetics': '#E6F3FF',
      'phenotypes': '#E6FFE6',
      'treatments': '#FFF0E6',
      'outcomes': '#F0E6FF'
    };
    return colors[type] || '#F5F5F5';
  };

  const renderHighlightedText = (text: string) => {
    // Simple regex-based highlighting for demo
    return text.replace(
      /<span class='extraction-highlight'([^>]*)>([^<]*)<\/span>/g,
      (match, attrs, spanText) => {
        const fieldMatch = attrs.match(/data-field="([^"]*)"/) || [];
        const typeMatch = attrs.match(/data-type="([^"]*)"/) || [];
        const confidenceMatch = attrs.match(/data-confidence="([^"]*)"/) || [];
        
        const field = fieldMatch[1] || '';
        const type = typeMatch[1] || '';
        const confidence = parseFloat(confidenceMatch[1] || '0');
        
        return `<span 
          style="
            background-color: ${getExtractionTypeColor(type)};
            padding: 2px 4px;
            border-radius: 3px;
            cursor: pointer;
            border: 1px solid #ccc;
          "
          onclick="window.handleSpanClick('${field}', '${spanText}', ${confidence})"
          title="Field: ${field}, Confidence: ${confidence.toFixed(2)}"
        >${spanText}</span>`;
      }
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Typography>Loading validation data...</Typography>
      </Box>
    );
  }

  if (!validationData) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load validation data for extraction {extractionId}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Validation Interface
        </Typography>
        <Box>
          <Chip
            label={validationData.validation_status}
            color={validationData.validation_status === 'validated' ? 'success' : 'default'}
            sx={{ mr: 2 }}
          />
          <Typography variant="body2" color="textSecondary">
            Extraction ID: {validationData.extraction_id}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Left Panel - Text with Highlighting */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Original Text with Extractions
              </Typography>
              
              {/* Text Display */}
              <Box
                sx={{
                  border: '1px solid #ddd',
                  borderRadius: 1,
                  p: 2,
                  maxHeight: '600px',
                  overflow: 'auto',
                  backgroundColor: '#fafafa',
                  fontFamily: 'monospace',
                  lineHeight: 1.6
                }}
                dangerouslySetInnerHTML={{
                  __html: renderHighlightedText(validationData.highlighted_text)
                }}
              />

              {/* Legend */}
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Extraction Types:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {Object.entries({
                    'demographics': 'Demographics',
                    'genetics': 'Genetics',
                    'phenotypes': 'Phenotypes',
                    'treatments': 'Treatments',
                    'outcomes': 'Outcomes'
                  }).map(([type, label]) => (
                    <Chip
                      key={type}
                      label={label}
                      size="small"
                      sx={{ backgroundColor: getExtractionTypeColor(type) }}
                    />
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Panel - Extraction Details */}
        <Grid item xs={12} md={4}>
          {/* Confidence Summary */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Confidence Summary
              </Typography>
              {Object.entries(validationData.confidence_scores).map(([field, confidence]) => (
                <Box key={field} mb={1}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">{field}</Typography>
                    <Chip
                      label={`${(confidence * 100).toFixed(0)}%`}
                      size="small"
                      color={getConfidenceColor(confidence)}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={confidence * 100}
                    color={getConfidenceColor(confidence)}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>

          {/* Extracted Fields */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Extracted Fields
              </Typography>
              {validationData.spans.map((span, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                      <Typography variant="body2">{span.field_name}</Typography>
                      <Chip
                        label={`${(span.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color={getConfidenceColor(span.confidence)}
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        <strong>Extracted Text:</strong> {span.text}
                      </Typography>
                      {span.normalized_value && (
                        <Typography variant="body2" gutterBottom>
                          <strong>Normalized Value:</strong> {span.normalized_value}
                        </Typography>
                      )}
                      <Typography variant="body2" gutterBottom>
                        <strong>Type:</strong> {span.extraction_type}
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<Edit />}
                        onClick={() => handleSpanClick(span)}
                      >
                        Edit
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>

          {/* Corrections */}
          {corrections.length > 0 && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Corrections Made
                </Typography>
                {corrections.map((correction, index) => (
                  <Box key={index} mb={1} p={1} border="1px solid #ddd" borderRadius={1}>
                    <Typography variant="body2">
                      <strong>{correction.field_name}:</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {correction.original_value} → {correction.corrected_value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Validator Notes */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validator Notes
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={validatorNotes}
                onChange={(e) => setValidatorNotes(e.target.value)}
                placeholder="Add notes about the validation..."
                variant="outlined"
              />
            </CardContent>
          </Card>

          {/* Validation Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validation Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircle />}
                  onClick={() => handleValidationSubmit('validated')}
                  disabled={saving}
                  fullWidth
                >
                  Approve Extraction
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Cancel />}
                  onClick={() => handleValidationSubmit('rejected')}
                  disabled={saving}
                  fullWidth
                >
                  Reject Extraction
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  disabled={saving}
                  fullWidth
                >
                  Save Draft
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Edit Field: {selectedSpan?.field_name}
        </DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Typography variant="body2" color="textSecondary">
              Original Text: "{selectedSpan?.text}"
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Confidence: {((selectedSpan?.confidence || 0) * 100).toFixed(0)}%
            </Typography>
          </Box>
          <TextField
            autoFocus
            fullWidth
            label="Corrected Value"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            variant="outlined"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleFieldCorrection} variant="contained">
            Apply Correction
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ValidationInterface;
