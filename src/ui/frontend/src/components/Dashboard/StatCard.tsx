import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color?: string;
  subtitle?: string;
  change?: number;
  changeLabel?: string;
  isPercentage?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle, change, changeLabel, isPercentage }) => (
  <Card sx={{ minWidth: 180, bgcolor: 'background.paper', boxShadow: 2 }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={1}>
        {icon}
        <Typography variant="h6" ml={1}>{title}</Typography>
      </Box>
      <Typography variant="h4" fontWeight={700}>{value}</Typography>
      {subtitle && <Typography variant="body2" color="text.secondary">{subtitle}</Typography>}
      {(change !== undefined && changeLabel) && (
        <Typography variant="body2" color={change >= 0 ? 'success.main' : 'error.main'}>
          {change >= 0 ? '+' : ''}{isPercentage ? `${change}%` : change} {changeLabel}
        </Typography>
      )}
    </CardContent>
  </Card>
);

export default StatCard;
