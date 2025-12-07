import apiClient, { setTokens, clearTokens } from './client';
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types';

export const authApi = {
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/v1/auth/register', data);
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return response.data;
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/v1/auth/login', data);
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/v1/auth/logout');
    } finally {
      clearTokens();
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/v1/players/me');
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await apiClient.post('/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};

export default authApi;
