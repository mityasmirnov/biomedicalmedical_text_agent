import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText } from '@mui/material';

interface Activity {
  id: string;
  description: string;
  timestamp: string;
}

interface RecentActivitiesCardProps {
  activities: Activity[];
}

const RecentActivitiesCard: React.FC<RecentActivitiesCardProps> = ({ activities }) => (
  <Card sx={{ minWidth: 180, boxShadow: 2 }}>
    <CardContent>
      <Typography variant="h6" mb={2}>Recent Activities</Typography>
      <List>
        {activities.map(activity => (
          <ListItem key={activity.id}>
            <ListItemText
              primary={activity.description}
              secondary={activity.timestamp}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
  </Card>
);

export default RecentActivitiesCard;
