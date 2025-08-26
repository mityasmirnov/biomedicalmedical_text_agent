import { useQuery } from 'react-query';
import { dashboardAPI } from '../services/api';

export const useDashboardData = () => {
  const { 
    data: overview, 
    isLoading: isOverviewLoading, 
    error: overviewError, 
    refetch: refetchOverview 
  } = useQuery('dashboardOverview', dashboardAPI.getOverview);

  const { 
    data: statistics, 
    isLoading: isStatisticsLoading, 
    error: statisticsError, 
    refetch: refetchStatistics 
  } = useQuery('dashboardStatistics', dashboardAPI.getStatistics);

  const { 
    data: systemStatus, 
    isLoading: isSystemStatusLoading, 
    error: systemStatusError, 
    refetch: refetchSystemStatus 
  } = useQuery('dashboardSystemStatus', dashboardAPI.getSystemStatus);

  const { 
    data: recentActivities, 
    isLoading: isRecentActivitiesLoading, 
    error: recentActivitiesError, 
    refetch: refetchRecentActivities 
  } = useQuery('dashboardRecentActivities', dashboardAPI.getRecentActivities);

  const { 
    data: alerts, 
    isLoading: isAlertsLoading, 
    error: alertsError, 
    refetch: refetchAlerts 
  } = useQuery('dashboardAlerts', dashboardAPI.getAlerts);

  const refetchAll = () => {
    refetchOverview();
    refetchStatistics();
    refetchSystemStatus();
    refetchRecentActivities();
    refetchAlerts();
  };

  return {
    overview: overview, // Remove .data since backend returns data directly
    statistics: statistics, // Remove .data since backend returns data directly
    systemStatus: systemStatus, // Remove .data since backend returns data directly
    recentActivities: recentActivities, // Remove .data since backend returns data directly
    alerts: alerts, // Remove .data since backend returns data directly
    isLoading: 
      isOverviewLoading || 
      isStatisticsLoading || 
      isSystemStatusLoading || 
      isRecentActivitiesLoading || 
      isAlertsLoading,
    error: 
      overviewError || 
      statisticsError || 
      systemStatusError || 
      recentActivitiesError || 
      alertsError,
    refetch: refetchAll,
  };
};
