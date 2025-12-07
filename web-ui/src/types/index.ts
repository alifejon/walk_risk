// User & Auth Types
export interface User {
  id: string;
  username: string;
  email: string;
  level: number;
  experience: number;
  current_class: string;
  energy: number;
  max_energy: number;
  unlocked_skills: string[];
  unlocked_features: string[];
  preferred_mentor: string;
  settings: Record<string, unknown>;
  created_at: string;
  last_active: string | null;
}

export interface AuthResponse {
  user_id: string;
  username: string;
  email: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  preferred_mentor?: string;
}

// Puzzle Types
export interface Clue {
  id: string;
  title: string;
  type: 'news' | 'financial' | 'chart' | 'analyst' | 'insider';
  icon: string;
  reliability: number;
  content?: string;
  discovered?: boolean;
}

export interface Puzzle {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  symbol: string;
  type?: string;
  estimated_time?: number;
  reward_xp?: number;
  is_solved?: boolean;
  created_at?: string;
  clues: Clue[];
  event_data?: {
    price_change: number;
    volume_ratio: number;
    date: string;
  };
  correct_answer?: string;
}

export interface HypothesisResult {
  is_correct: boolean;
  accuracy: number;
  xp_earned: number;
  feedback: string;
  evidence_used?: string[];
  correct_answer: string;
}

export interface PuzzleHint {
  hint_id: string;
  level: number;
  text: string;
  cost: number;
  available: boolean;
  unlocked: boolean;
  mentor?: string;
}

export interface PuzzleStats {
  total_attempts: number;
  total_solved: number;
  success_rate: number;
  current_streak: number;
  best_streak: number;
  average_accuracy: number;
  by_difficulty: Record<string, { attempted: number; solved: number }>;
}

// Portfolio Types
export interface Holding {
  symbol: string;
  name?: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl?: number;
  weight?: number;
  sector?: string;
}

export interface Portfolio {
  portfolio_id: string;
  total_value: number;
  cash_balance: number;
  market_value?: number;
  total_return?: number;
  holdings: Holding[];
  recent_trades?: Trade[];
}

export interface Trade {
  trade_id: string;
  symbol: string;
  name?: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  total_value: number;
  executed_at: string;
  reason?: string;
}

export interface OrderRequest {
  symbol: string;
  order_type: 'market' | 'limit';
  side: 'buy' | 'sell';
  quantity: number;
  price?: number;
  reason?: string;
}

// Mentor Types
export interface MentorAdvice {
  mentor_id: string;
  mentor_name: string;
  advice: string;
  context?: Record<string, unknown>;
}

// Leaderboard Types
export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  score: number;
  level: number;
  current_class: string;
}

export interface Leaderboard {
  leaderboard: LeaderboardEntry[];
  my_rank: {
    rank: number | null;
    score: number;
  };
  period: string;
  metric: string;
}
