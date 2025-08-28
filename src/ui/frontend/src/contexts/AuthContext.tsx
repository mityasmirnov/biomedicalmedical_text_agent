import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { api } from '../services/api';

// Types
interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  clearError: () => void;
  refreshToken: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

// Action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

// Mock admin user for automatic authentication
const MOCK_ADMIN_USER: User = {
  id: "admin-1",
  email: "admin@biomedical-agent.com",
  name: "System Administrator",
  role: "admin",
  permissions: ["read", "write", "admin", "delete"]
};

const MOCK_ADMIN_TOKEN = "mock-admin-token-12345";

// Initial state - automatically authenticated as admin
const initialState: AuthState = {
  user: MOCK_ADMIN_USER,
  token: MOCK_ADMIN_TOKEN,
  isAuthenticated: true,
  isLoading: false,
  error: null,
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: MOCK_ADMIN_USER, // Always return to admin state
        token: MOCK_ADMIN_TOKEN,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextType>(initialState as AuthContextType);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state on mount - automatically authenticate as admin
  useEffect(() => {
    const initializeAuth = async () => {
      // Automatically authenticate as admin
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: MOCK_ADMIN_USER,
          token: MOCK_ADMIN_TOKEN,
        },
      });
    };

    initializeAuth();
  }, []);

  // Login function - always succeeds with admin
  const login = async (email: string, password: string): Promise<void> => {
    // Mock successful login
    dispatch({
      type: 'AUTH_SUCCESS',
      payload: {
        user: MOCK_ADMIN_USER,
        token: MOCK_ADMIN_TOKEN,
      },
    });
  };

  // Logout function - always returns to admin state
  const logout = async (): Promise<void> => {
    // Always return to admin state
    dispatch({
      type: 'AUTH_SUCCESS',
      payload: {
        user: MOCK_ADMIN_USER,
        token: MOCK_ADMIN_TOKEN,
      },
    });
  };

  // Register function - always succeeds with admin
  const register = async (userData: RegisterData): Promise<void> => {
    // Mock successful registration
    dispatch({
      type: 'AUTH_SUCCESS',
      payload: {
        user: MOCK_ADMIN_USER,
        token: MOCK_ADMIN_TOKEN,
      },
    });
  };

  // Clear error function
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Refresh token function - always returns admin token
  const refreshToken = async (): Promise<void> => {
    // Always return admin token
    dispatch({
      type: 'AUTH_SUCCESS',
      payload: {
        user: MOCK_ADMIN_USER,
        token: MOCK_ADMIN_TOKEN,
      },
    });
  };

  // Context value
  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    register,
    clearError,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

// HOC for components that require authentication
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  return (props: P) => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
      return <div>Please log in to access this page.</div>;
    }

    return <Component {...props} />;
  };
};

export default AuthContext;

