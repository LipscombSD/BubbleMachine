import { create } from 'zustand';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/',
});

export const useAuthStore = create((set, get) => ({
  accessToken: null,
  refreshToken: null,
  user: null,
  isAuthenticated: false,
  isLoading: true, // Add loading state

  initialize: async () => {
    set({ isLoading: true });
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    if (accessToken && refreshToken) {
      set({ accessToken, refreshToken, isAuthenticated: true });
    }
    set({ isLoading: false });
  },

  login: async (email, password) => {
    try {
      const response = await api.post('users/login/', { email, password });
      const { access_token, refresh_token } = response.data.data;
      set({ accessToken: access_token, refreshToken: refresh_token, isAuthenticated: true });
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    }
  },

  register: async (userData) => {
    try {
      const response = await api.post('users/register/', userData);
      const { access_token, refresh_token, user } = response.data.data;
      set({ accessToken: access_token, refreshToken: refresh_token, user, isAuthenticated: true });
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
    } catch (error) {
      console.error('Registration failed', error);
      throw error;
    }
  },

  logout: () => {
    set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false });
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },

  refreshToken: async () => {
    try {
      const refreshToken = get().refreshToken;
      const response = await api.post('users/login/refresh/', { refresh_token: refreshToken });
      const { access_token, refresh_token } = response.data.data;
      set({ accessToken: access_token, refreshToken: refresh_token });
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      return access_token;
    } catch (error) {
      console.error('Token refresh failed', error);
      get().logout();
      throw error;
    }
  },
}));