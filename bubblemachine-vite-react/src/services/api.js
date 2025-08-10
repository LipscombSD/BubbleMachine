import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1/',
  withCredentials: false, // keep false for pure Bearer JWT (no cookies)
});

// Attach access token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- 401 refresh handling ---
let isRefreshing = false;
let waitQueue = [];

function queueRequest(cb) {
  return new Promise((resolve, reject) => {
    waitQueue.push({ resolve, reject, cb });
  });
}
function flushQueue(error, newToken) {
  waitQueue.forEach(({ resolve, reject, cb }) => {
    if (error) return reject(error);
    try {
      resolve(cb(newToken));
    } catch (e) {
      reject(e);
    }
  });
  waitQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Network error or server down
    if (!error.response) return Promise.reject(error);

    const { status } = error.response;
    const original = error.config;

    // Only refresh once per request
    if (status === 401 && !original._retry) {
      original._retry = true;

      // If a refresh is already in progress, wait for it
      if (isRefreshing) {
        return queueRequest((newToken) => {
          original.headers.Authorization = `Bearer ${newToken}`;
          return api(original);
        });
      }

      // Start refresh
      isRefreshing = true;
      try {
        const store = useAuthStore.getState();
        const newToken = await store.refreshToken(); // your store method
        flushQueue(null, newToken);
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (refreshErr) {
        flushQueue(refreshErr, null);
        // optional: log the user out on refresh failure
        try { useAuthStore.getState().logout?.(); } catch {}
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
