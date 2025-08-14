import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Chip } from '@mui/material';

interface Alert {
  id: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

interface AlertsCardProps {
  alerts: Alert[];
}

const AlertsCard: React.FC<AlertsCardProps> = ({ alerts }) => (
  <Card sx={{ minWidth: 180, boxShadow: 2 }}>
    <CardContent>
      <Typography variant="h6" mb={2}>Alerts</Typography>
      <List>
        {alerts.map(alert => (
          <ListItem key={alert.id}>
            <Chip label={alert.severity} color={alert.severity} size="small" sx={{ mr: 1 }} />
            <ListItemText
              primary={alert.message}
              secondary={alert.timestamp}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
  </Card>
);

export default AlertsCard;
