import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient } from '../api/client';

interface AuthContextType {
  user: any;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem('token').then((t) => {
      if (t) {
        setToken(t);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${t}`;
      }
      setLoading(false);
    });
  }, []);

  const login = async (username: string, password: string) => {
    const res = await apiClient.post('/api/auth/login', { username, password });
    const { access_token } = res.data;
    setToken(access_token);
    await AsyncStorage.setItem('token', access_token);
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    const me = await apiClient.get('/api/auth/me');
    setUser(me.data);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    AsyncStorage.removeItem('token');
    delete apiClient.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
