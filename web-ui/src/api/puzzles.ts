import apiClient from './client';
import type { Puzzle, PuzzleHint, PuzzleStats, HypothesisResult } from '../types';

export const puzzlesApi = {
  async getAvailablePuzzles(params?: {
    difficulty?: string;
    puzzle_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ puzzles: Puzzle[] }> {
    const response = await apiClient.get('/v1/puzzles/', { params });
    return response.data;
  },

  async getPuzzleDetails(puzzleId: string): Promise<Puzzle> {
    const response = await apiClient.get<Puzzle>(`/v1/puzzles/${puzzleId}`);
    return response.data;
  },

  async investigateClue(
    puzzleId: string,
    clueId: string,
    investigationType: string = 'detailed'
  ): Promise<{
    clue: {
      clue_id: string;
      content: string;
      reliability: number;
    };
    discovered_info: string;
    energy_cost: number;
  }> {
    const response = await apiClient.post(`/v1/puzzles/${puzzleId}/investigate`, {
      clue_id: clueId,
      investigation_type: investigationType,
    });
    return response.data;
  },

  async submitHypothesis(
    puzzleId: string,
    hypothesis: string,
    confidence: number,
    evidence: string[],
    predictedOutcome: string
  ): Promise<HypothesisResult> {
    const response = await apiClient.post<HypothesisResult>(
      `/v1/puzzles/${puzzleId}/hypothesis`,
      {
        hypothesis,
        confidence,
        evidence,
        predicted_outcome: predictedOutcome,
      }
    );
    return response.data;
  },

  async getHints(puzzleId: string): Promise<{ puzzle_id: string; hints: PuzzleHint[]; player_xp: number }> {
    const response = await apiClient.get(`/v1/puzzles/${puzzleId}/hints`);
    return response.data;
  },

  async getStats(): Promise<PuzzleStats> {
    const response = await apiClient.get<PuzzleStats>('/v1/puzzles/stats/summary');
    return response.data;
  },

  async createDailyPuzzles(): Promise<{ created: number; puzzles: Puzzle[] }> {
    const response = await apiClient.post('/v1/puzzles/daily');
    return response.data;
  },
};

export default puzzlesApi;
