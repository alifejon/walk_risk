import apiClient from './client';
import type { Portfolio, Trade, OrderRequest, Holding } from '../types';

export const portfolioApi = {
  async getPortfolio(): Promise<Portfolio> {
    const response = await apiClient.get<Portfolio>('/v1/portfolio/');
    return response.data;
  },

  async placeOrder(order: OrderRequest): Promise<{
    order_id: string;
    status: string;
    execution_price: number;
    execution_time: string;
    portfolio_update: {
      new_cash_balance: number;
      new_total_value: number;
    };
  }> {
    const response = await apiClient.post('/v1/portfolio/orders', order);
    return response.data;
  },

  async getPerformance(): Promise<{
    performance: {
      total_return: number;
      realized_pnl: number;
      unrealized_pnl: number;
      initial_value: number;
      current_value: number;
    };
    trading_stats: {
      total_trades: number;
      buy_trades: number;
      sell_trades: number;
      avg_trade_size: number;
    };
    allocation: {
      cash_ratio: number;
      equity_ratio: number;
      sector_allocation: Record<string, number>;
    };
    risk_metrics: {
      diversification_score: number;
      concentration_risk: number;
      position_count: number;
      cash_ratio: number;
    };
  }> {
    const response = await apiClient.get('/v1/portfolio/performance');
    return response.data;
  },

  async getHistory(params?: {
    limit?: number;
    offset?: number;
    symbol?: string;
    side?: string;
  }): Promise<{
    trades: Trade[];
    total: number;
    has_more: boolean;
  }> {
    const response = await apiClient.get('/v1/portfolio/history', { params });
    return response.data;
  },

  async getPositions(): Promise<{
    positions: Array<Holding & { profit_loss: number; profit_loss_percent: number; days_held: number }>;
    summary: {
      total_positions: number;
      total_market_value: number;
      total_unrealized_pnl: number;
      best_performer: Holding | null;
      worst_performer: Holding | null;
    };
  }> {
    const response = await apiClient.get('/v1/portfolio/positions');
    return response.data;
  },

  async getAllocation(): Promise<{
    asset_allocation: {
      cash: number;
      stocks: number;
    };
    sector_allocation: Record<string, number>;
    recommendations: string[];
  }> {
    const response = await apiClient.get('/v1/portfolio/allocation');
    return response.data;
  },

  async suggestRebalancing(targetAllocation: Record<string, number>): Promise<{
    rebalancing_needed: boolean;
    current_allocation: Record<string, number>;
    target_allocation: Record<string, number>;
    suggested_trades: Array<{
      action: 'buy' | 'sell';
      symbol: string;
      quantity: number;
      reason: string;
    }>;
    estimated_cost: number;
  }> {
    const response = await apiClient.post('/v1/portfolio/rebalance', {
      target_allocation: targetAllocation,
    });
    return response.data;
  },
};

export default portfolioApi;
