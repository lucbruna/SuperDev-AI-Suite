import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  created_at: string;
}

interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  plan: string;
  settings: Record<string, any>;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  org: Organization | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; username: string; full_name?: string }) => Promise<void>;
  logout: () => Promise<void>;
  setOrg: (org: Organization) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [org, setOrg] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchUser = async () => {
    try {
      const response = await api.get('/users/me');
      setUser(response.data);
      
      if (response.data.organization_id) {
        const orgResponse = await api.get(`/organizations/${response.data.organization_id}`);
        setOrg(orgResponse.data);
      }
    } catch (error) {
      setUser(null);
      setOrg(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = response.data;
    
    localStorage.setItem('access_token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setUser(userData);
  };

  const register = async (data: { email: string; password: string; username: string; full_name?: string }) => {
    const response = await api.post('/auth/register', data);
    const { access_token, user: userData } = response.data;
    
    localStorage.setItem('access_token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setUser(userData);
  };

  const logout = async () => {
    localStorage.removeItem('access_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    setOrg(null);
    navigate('/login');
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider value={{ user, org, loading, login, register, logout, setOrg, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Initialize auth from localStorage
const token = localStorage.getItem('access_token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}