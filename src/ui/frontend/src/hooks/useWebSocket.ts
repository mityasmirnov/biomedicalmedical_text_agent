import useWebSocket, { ReadyState } from 'use-websocket';
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

const WEBSOCKET_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';

export const useWebSocketConnection = () => {
  const { token } = useAuth();
  const [socketUrl, setSocketUrl] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      setSocketUrl(`${WEBSOCKET_URL}?token=${token}`);
    }
  }, [token]);

  const {
    sendMessage,
    lastMessage,
    readyState,
  } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true,
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
