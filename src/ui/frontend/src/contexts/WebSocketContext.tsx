import React, { createContext, useContext, useEffect, useReducer, useCallback } from 'react';
import useWebSocketLib, { ReadyState } from 'react-use-websocket';
import { useAuth } from './AuthContext';

// Types
interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  read: boolean;
  data?: any;
}

interface WebSocketState {
  isConnected: boolean;
  connectionStatus: string;
  notifications: Notification[];
  unreadCount: number;
  subscriptions: Set<string>;
  lastMessage: any;
  error: string | null;
}

interface WebSocketContextType extends WebSocketState {
  subscribe: (topic: string) => void;
  unsubscribe: (topic: string) => void;
  sendMessage: (message: any) => void;
  markNotificationAsRead: (notificationId: string) => void;
  markAllNotificationsAsRead: () => void;
  clearNotifications: () => void;
  clearError: () => void;
}

// Action types
type WebSocketAction =
  | { type: 'CONNECTION_OPENED' }
  | { type: 'CONNECTION_CLOSED' }
  | { type: 'CONNECTION_ERROR'; payload: string }
  | { type: 'MESSAGE_RECEIVED'; payload: any }
  | { type: 'NOTIFICATION_ADDED'; payload: Notification }
  | { type: 'NOTIFICATION_READ'; payload: string }
  | { type: 'ALL_NOTIFICATIONS_READ' }
  | { type: 'NOTIFICATIONS_CLEARED' }
  | { type: 'SUBSCRIPTION_ADDED'; payload: string }
  | { type: 'SUBSCRIPTION_REMOVED'; payload: string }
  | { type: 'CLEAR_ERROR' };

// Initial state
const initialState: WebSocketState = {
  isConnected: false,
  connectionStatus: 'Disconnected',
  notifications: [],
  unreadCount: 0,
  subscriptions: new Set(),
  lastMessage: null,
  error: null,
};

// Reducer
const webSocketReducer = (state: WebSocketState, action: WebSocketAction): WebSocketState => {
  switch (action.type) {
    case 'CONNECTION_OPENED':
      return {
        ...state,
        isConnected: true,
        connectionStatus: 'Connected',
        error: null,
      };
    
    case 'CONNECTION_CLOSED':
      return {
        ...state,
        isConnected: false,
        connectionStatus: 'Disconnected',
      };
    
    case 'CONNECTION_ERROR':
      return {
        ...state,
        isConnected: false,
        connectionStatus: 'Error',
        error: action.payload,
      };
    
    case 'MESSAGE_RECEIVED':
      return {
        ...state,
        lastMessage: action.payload,
      };
    
    case 'NOTIFICATION_ADDED':
      const newNotification = action.payload;
      return {
        ...state,
        notifications: [newNotification, ...state.notifications],
        unreadCount: state.unreadCount + (newNotification.read ? 0 : 1),
      };
    
    case 'NOTIFICATION_READ':
      const updatedNotifications = state.notifications.map(notification =>
        notification.id === action.payload
          ? { ...notification, read: true }
          : notification
      );
      const unreadNotification = state.notifications.find(n => n.id === action.payload && !n.read);
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: unreadNotification ? state.unreadCount - 1 : state.unreadCount,
      };
    
    case 'ALL_NOTIFICATIONS_READ':
      return {
        ...state,
        notifications: state.notifications.map(notification => ({
          ...notification,
          read: true,
        })),
        unreadCount: 0,
      };
    
    case 'NOTIFICATIONS_CLEARED':
      return {
        ...state,
        notifications: [],
        unreadCount: 0,
      };
    
    case 'SUBSCRIPTION_ADDED':
      const newSubscriptions = new Set(state.subscriptions);
      newSubscriptions.add(action.payload);
      return {
        ...state,
        subscriptions: newSubscriptions,
      };
    
    case 'SUBSCRIPTION_REMOVED':
      const filteredSubscriptions = new Set(state.subscriptions);
      filteredSubscriptions.delete(action.payload);
      return {
        ...state,
        subscriptions: filteredSubscriptions,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
};

// Create context
const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// Provider component
export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(webSocketReducer, initialState);
  const { token, isAuthenticated } = useAuth();

  // WebSocket URL
  const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/v1/ws`;
  };

  // WebSocket hook
  const {
    sendMessage: wsSendMessage,
    lastMessage,
    readyState,
  } = useWebSocketLib(
    isAuthenticated ? getWebSocketUrl() : null,
    {
      onOpen: () => {
        console.log('WebSocket connection opened');
        dispatch({ type: 'CONNECTION_OPENED' });
      },
      onClose: () => {
        console.log('WebSocket connection closed');
        dispatch({ type: 'CONNECTION_CLOSED' });
      },
      onError: (event) => {
        console.error('WebSocket error:', event);
        dispatch({ 
          type: 'CONNECTION_ERROR', 
          payload: 'WebSocket connection error' 
        });
      },
      shouldReconnect: (closeEvent) => {
        // Reconnect if authenticated and not a manual close
        return isAuthenticated && closeEvent.code !== 1000;
      },
      reconnectAttempts: 5,
      reconnectInterval: 3000,
    },
    isAuthenticated
  );

  // Handle incoming messages
  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const message = JSON.parse(lastMessage.data);
        dispatch({ type: 'MESSAGE_RECEIVED', payload: message });

        // Handle different message types
        switch (message.type) {
          case 'notification':
          case 'system_alert':
          case 'extraction_progress':
          case 'validation_update':
            const notification: Notification = {
              id: message.id || Date.now().toString(),
              type: message.type,
              title: message.data?.title || message.type,
              message: message.data?.message || JSON.stringify(message.data),
              severity: getSeverityFromMessageType(message.type, message.data),
              timestamp: message.timestamp || new Date().toISOString(),
              read: false,
              data: message.data,
            };
            dispatch({ type: 'NOTIFICATION_ADDED', payload: notification });
            break;
          
          case 'subscription_confirmed':
            console.log('Subscription confirmed:', message.data?.topic);
            break;
          
          case 'unsubscription_confirmed':
            console.log('Unsubscription confirmed:', message.data?.topic);
            break;
          
          case 'heartbeat':
            // Handle heartbeat silently
            break;
          
          default:
            console.log('Unhandled WebSocket message:', message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  // Update connection status based on ready state
  useEffect(() => {
    const connectionStatus = getConnectionStatus(readyState);
    if (state.connectionStatus !== connectionStatus) {
      if (readyState === ReadyState.OPEN) {
        dispatch({ type: 'CONNECTION_OPENED' });
      } else if (readyState === ReadyState.CLOSED) {
        dispatch({ type: 'CONNECTION_CLOSED' });
      }
    }
  }, [readyState, state.connectionStatus]);

  // Subscribe to a topic
  const subscribe = useCallback((topic: string) => {
    if (readyState === ReadyState.OPEN) {
      wsSendMessage(JSON.stringify({
        type: 'subscribe',
        data: { topic }
      }));
      dispatch({ type: 'SUBSCRIPTION_ADDED', payload: topic });
    }
  }, [readyState, wsSendMessage]);

  // Unsubscribe from a topic
  const unsubscribe = useCallback((topic: string) => {
    if (readyState === ReadyState.OPEN) {
      wsSendMessage(JSON.stringify({
        type: 'unsubscribe',
        data: { topic }
      }));
      dispatch({ type: 'SUBSCRIPTION_REMOVED', payload: topic });
    }
  }, [readyState, wsSendMessage]);

  // Send a message
  const sendMessage = useCallback((message: any) => {
    if (readyState === ReadyState.OPEN) {
      wsSendMessage(JSON.stringify(message));
    }
  }, [readyState, wsSendMessage]);

  // Mark notification as read
  const markNotificationAsRead = useCallback((notificationId: string) => {
    dispatch({ type: 'NOTIFICATION_READ', payload: notificationId });
  }, []);

  // Mark all notifications as read
  const markAllNotificationsAsRead = useCallback(() => {
    dispatch({ type: 'ALL_NOTIFICATIONS_READ' });
  }, []);

  // Clear all notifications
  const clearNotifications = useCallback(() => {
    dispatch({ type: 'NOTIFICATIONS_CLEARED' });
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // Auto-subscribe to default topics when connected
  useEffect(() => {
    if (readyState === ReadyState.OPEN && isAuthenticated) {
      // Subscribe to default topics
      const defaultTopics = [
        'system_alerts',
        'extraction_progress',
        'validation_updates',
        'notifications'
      ];

      defaultTopics.forEach(topic => {
        if (!state.subscriptions.has(topic)) {
          subscribe(topic);
        }
      });
    }
  }, [readyState, isAuthenticated, subscribe, state.subscriptions]);

  // Context value
  const contextValue: WebSocketContextType = {
    ...state,
    isConnected: readyState === ReadyState.OPEN,
    connectionStatus: getConnectionStatus(readyState),
    subscribe,
    unsubscribe,
    sendMessage,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    clearNotifications,
    clearError,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Hook to use WebSocket context
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  
  return context;
};

// Helper functions
function getConnectionStatus(readyState: ReadyState): string {
  switch (readyState) {
    case ReadyState.CONNECTING:
      return 'Connecting';
    case ReadyState.OPEN:
      return 'Connected';
    case ReadyState.CLOSING:
      return 'Closing';
    case ReadyState.CLOSED:
      return 'Disconnected';
    default:
      return 'Unknown';
  }
}

function getSeverityFromMessageType(type: string, data: any): 'info' | 'warning' | 'error' | 'success' {
  switch (type) {
    case 'system_alert':
      return data?.severity || 'warning';
    case 'extraction_progress':
      if (data?.status === 'completed') return 'success';
      if (data?.status === 'failed') return 'error';
      return 'info';
    case 'validation_update':
      if (data?.status === 'validated') return 'success';
      if (data?.status === 'failed') return 'error';
      return 'info';
    default:
      return 'info';
  }
}

export default WebSocketContext;

