import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export const useDashboardData = () => {
  const { 
    data: overview, 
    isLoading: isOverviewLoading, 
    error: overviewError, 
    refetch: refetchOverview 
  } = useQuery({
    queryKey: ['dashboardOverview'],
    queryFn: () => api.dashboard.getSystemStatus()
  });

  const { 
    data: statistics, 
    isLoading: isStatisticsLoading, 
    error: statisticsError, 
    refetch: refetchStatistics 
  } = useQuery({
    queryKey: ['dashboardStatistics'],
    queryFn: () => api.dashboard.getRecentResults()
  });

  const { 
    data: systemStatus, 
    isLoading: isSystemStatusLoading, 
    error: systemStatusError, 
    refetch: refetchSystemStatus 
  } = useQuery({
    queryKey: ['dashboardSystemStatus'],
    queryFn: () => api.dashboard.getSystemStatus()
  });

  const { 
    data: recentActivities, 
    isLoading: isRecentActivitiesLoading, 
    error: recentActivitiesError, 
    refetch: refetchRecentActivities 
  } = useQuery({
    queryKey: ['dashboardRecentActivities'],
    queryFn: () => api.dashboard.getProcessingQueue()
  });

  const { 
    data: alerts, 
    isLoading: isAlertsLoading, 
    error: alertsError, 
    refetch: refetchAlerts 
  } = useQuery({
    queryKey: ['dashboardAlerts'],
    queryFn: () => api.dashboard.getSystemStatus()
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
