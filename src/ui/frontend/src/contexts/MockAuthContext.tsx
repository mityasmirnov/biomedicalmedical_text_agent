import React, { createContext, useContext, ReactNode } from 'react';

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
  register: (userData: any) => Promise<void>;
  clearError: () => void;
  refreshToken: () => Promise<void>;
}

const mockUser: User = {
  id: '1',
  email: 'admin@example.com',
  name: 'Admin User',
  role: 'admin',
  permissions: ['*']
};

const MockAuthContext = createContext<AuthContextType>({
  user: mockUser,
  token: 'mock-token',
  isAuthenticated: true,
  isLoading: false,
  error: null,
  login: async () => {},
  logout: async () => {},
  register: async () => {},
  clearError: () => {},
  refreshToken: async () => {}
});

export const MockAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <MockAuthContext.Provider
      value={{
        user: mockUser,
        token: 'mock-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        login: async () => {},
        logout: async () => {},
        register: async () => {},
        clearError: () => {},
        refreshToken: async () => {}
      }}
    >
      {children}
    </MockAuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  return useContext(MockAuthContext);
};

export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  return (props: P) => {
    return <Component {...props} />;
  };
};

export default MockAuthContext;
