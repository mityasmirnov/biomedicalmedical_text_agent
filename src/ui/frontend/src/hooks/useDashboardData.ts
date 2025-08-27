import { useQuery } from '@tanstack/react-query';
import { dashboardAPI } from '../services/api';

export const useDashboardData = () => {
  const { 
    data: overview, 
    isLoading: isOverviewLoading, 
    error: overviewError, 
    refetch: refetchOverview 
  } = useQuery({
    queryKey: ['dashboardOverview'],
    queryFn: dashboardAPI.getOverview
  });

  const { 
    data: statistics, 
    isLoading: isStatisticsLoading, 
    error: statisticsError, 
    refetch: refetchStatistics 
  } = useQuery({
    queryKey: ['dashboardStatistics'],
    queryFn: dashboardAPI.getStatistics
  });

  const { 
    data: systemStatus, 
    isLoading: isSystemStatusLoading, 
    error: systemStatusError, 
    refetch: refetchSystemStatus 
  } = useQuery({
    queryKey: ['dashboardSystemStatus'],
    queryFn: dashboardAPI.getSystemStatus
  });

  const { 
    data: recentActivities, 
    isLoading: isRecentActivitiesLoading, 
    error: recentActivitiesError, 
    refetch: refetchRecentActivities 
  } = useQuery({
    queryKey: ['dashboardRecentActivities'],
    queryFn: dashboardAPI.getRecentActivities
  });

  const { 
    data: alerts, 
    isLoading: isAlertsLoading, 
    error: alertsError, 
    refetch: refetchAlerts 
  } = useQuery({
    queryKey: ['dashboardAlerts'],
    queryFn: dashboardAPI.getAlerts
  });

  const refetchAll = () => {
    refetchOverview();
    refetchStatistics();
    refetchSystemStatus();
    refetchRecentActivities();
    refetchAlerts();
  };

  return {
    overview: overview?.data || overview, // Handle both Axios response and direct data
    statistics: statistics?.data || statistics, // Handle both Axios response and direct data
    systemStatus: systemStatus?.data || systemStatus, // Handle both Axios response and direct data
    recentActivities: recentActivities?.data || recentActivities, // Handle both Axios response and direct data
    alerts: alerts?.data || alerts, // Handle both Axios response and direct data
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
