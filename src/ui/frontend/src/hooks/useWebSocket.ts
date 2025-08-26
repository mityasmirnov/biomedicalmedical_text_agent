import useWebSocketLib, { ReadyState } from 'react-use-websocket';
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

const WEBSOCKET_URL = process.env.REACT_APP_WS_URL || 'ws://127.0.0.1:8000/api/v1/ws';

export const useWebSocketConnection = () => {
  const { token } = useAuth();
  const [socketUrl, setSocketUrl] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setSocketUrl(`${WEBSOCKET_URL}?token=${token}`);
    } else {
      setSocketUrl(WEBSOCKET_URL);
    }
  }, [token]);

  const {
    sendMessage,
    lastMessage,
    readyState,
  } = useWebSocketLib(socketUrl ?? '', {
    shouldReconnect: () => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  const sendJsonMessage = useCallback((jsonMessage: any) => {
    sendMessage(JSON.stringify(jsonMessage));
  }, [sendMessage]);

  return {
    sendJsonMessage,
    lastJsonMessage: lastMessage ? JSON.parse(lastMessage.data) : null,
    readyState,
    connectionStatus,
    isConnected: readyState === ReadyState.OPEN,
  };
};

// Minimal adapter used by Layout
export const useWebSocket = () => {
  // In this minimal setup, expose empty notifications
  return { notifications: [], unreadCount: 0 } as { notifications: any[]; unreadCount: number };
};
