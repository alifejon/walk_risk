import apiClient from './client';
import type { User, Leaderboard } from '../types';

export const playersApi = {
  async getCurrentPlayer(): Promise<User> {
    const response = await apiClient.get<User>('/v1/players/me');
    return response.data;
  },

  async updatePlayer(data: {
    preferred_mentor?: string;
    settings?: Record<string, unknown>;
  }): Promise<{ message: string; player: User }> {
    const response = await apiClient.put('/v1/players/me', data);
    return response.data;
  },

  async consumeEnergy(amount: number): Promise<{ energy: number; max_energy: number }> {
    const response = await apiClient.post('/v1/players/me/energy/consume', { amount });
    return response.data;
  },

  async restoreEnergy(amount?: number): Promise<{ energy: number; max_energy: number }> {
    const response = await apiClient.post('/v1/players/me/energy/restore',
      amount ? { amount } : {}
    );
    return response.data;
  },

  async updateProgress(data: {
    experience_gained?: number;
    skills_unlocked?: string[];
    features_unlocked?: string[];
  }): Promise<{
    level: number;
    experience: number;
    current_class: string;
    unlocked_skills: string[];
    unlocked_features: string[];
  }> {
    const response = await apiClient.post('/v1/players/me/progress', data);
    return response.data;
  },

  async getStats(): Promise<{
    player_info: {
      level: number;
      experience: number;
      current_class: string;
    };
    puzzle_stats: {
      total_attempts: number;
      solved: number;
      success_rate: number;
    };
    portfolio_stats: {
      total_portfolios: number;
      total_value: number;
    };
  }> {
    const response = await apiClient.get('/v1/players/stats');
    return response.data;
  },

  async getLeaderboard(params?: {
    period?: string;
    metric?: string;
    limit?: number;
    offset?: number;
  }): Promise<Leaderboard> {
    const response = await apiClient.get<Leaderboard>('/v1/players/leaderboard', { params });
    return response.data;
  },

  async searchPlayers(params: {
    username?: string;
    current_class?: string;
    min_level?: number;
    limit?: number;
  }): Promise<{
    results: Array<{
      user_id: string;
      username: string;
      level: number;
      current_class: string;
    }>;
    count: number;
  }> {
    const response = await apiClient.get('/v1/players/search', { params });
    return response.data;
  },

  async getPlayerProfile(playerId: string): Promise<{
    id: string;
    username: string;
    level: number;
    current_class: string;
    unlocked_skills: string[];
  }> {
    const response = await apiClient.get(`/v1/players/${playerId}`);
    return response.data;
  },

  async deleteAccount(): Promise<{ message: string; user_id: string }> {
    const response = await apiClient.delete('/v1/players/me');
    return response.data;
  },
};

export default playersApi;
