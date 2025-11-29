import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Change for production

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor if needed later (sending initData)

export const getUser = async (telegram_id: number) => {
  try {
    const response = await api.get(`/users/${telegram_id}`);
    return response.data;
  } catch (error) {
    // If 404, register
    const response = await api.post(`/users/`, { telegram_id });
    return response.data;
  }
};

export const spinWheel = async (telegram_id: number) => {
  const response = await api.post(`/game/spin?telegram_id=${telegram_id}`);
  return response.data;
};

export const getTasks = async () => {
  const response = await api.get(`/tasks/`);
  return response.data;
};

export const buySpins = async (telegram_id: number, amount: number = 1) => {
  const response = await api.post(`/game/buy_spins?telegram_id=${telegram_id}&amount=${amount}`);
  return response.data;
};

// Admin
export const getAdminStats = async (telegram_id: number) => {
    const response = await api.get('/admin/stats', {
        headers: { 'X-Telegram-ID': telegram_id }
    });
    return response.data;
};

export const createAdminTask = async (telegram_id: number, task: any) => {
    const response = await api.post('/admin/tasks', task, {
        headers: { 'X-Telegram-ID': telegram_id }
    });
    return response.data;
};

export const addAdminSpins = async (admin_id: number, user_id: number, amount: number) => {
    const response = await api.post(`/admin/users/${user_id}/spins`, { amount }, {
        headers: { 'X-Telegram-ID': admin_id }
    });
    return response.data;
};
