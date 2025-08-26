import React from 'react';
import { Box, Typography } from '@mui/material';

interface Notification {
  id?: string;
  title?: string;
  message?: string;
}

export default function NotificationPanel({ open, onClose, notifications }: { open: boolean; onClose: () => void; notifications: Notification[] }) {
  if (!open) return null;
  return (
    <Box sx={{ p: 2, border: '1px solid #eee', borderRadius: 1, position: 'fixed', right: 16, top: 72, width: 320, bgcolor: 'background.paper' }}>
      <Typography variant="subtitle1" gutterBottom>Notifications</Typography>
      {notifications?.length ? notifications.map((n, i) => (
        <Box key={n.id || i} sx={{ mb: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{n.title || 'Notification'}</Typography>
          <Typography variant="body2" color="text.secondary">{n.message || '—'}</Typography>
        </Box>
      )) : (
        <Typography variant="body2" color="text.secondary">No notifications yet.</Typography>
      )}
    </Box>
  );
}
