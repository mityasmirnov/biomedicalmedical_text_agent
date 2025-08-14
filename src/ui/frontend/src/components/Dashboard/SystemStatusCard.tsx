import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';

interface SystemStatusCardProps {
  status: string;
  details: string;
  health: 'healthy' | 'warning' | 'critical';
}

const healthColor = {
  healthy: 'success',
  warning: 'warning',
  critical: 'error',
};

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ status, details, health }) => (
  <Card sx={{ minWidth: 180, boxShadow: 2 }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={1}>
        <Chip label={status} color={healthColor[health]} />
        <Typography variant="h6" ml={1}>System Status</Typography>
      </Box>
      <Typography variant="body2" color="text.secondary">{details}</Typography>
    </CardContent>
  </Card>
);

export default SystemStatusCard;
