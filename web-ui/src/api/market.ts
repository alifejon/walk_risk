import apiClient from './client';

export interface HistoricalDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HistoricalData {
  symbol: string;
  period: string;
  interval: string;
  data: HistoricalDataPoint[];
}

export const marketApi = {
  async getHistoricalData(symbol: string, period: string = '1mo'): Promise<HistoricalData> {
    const response = await apiClient.get<HistoricalData>(`/v1/market/historical/${symbol}`, {
      params: { period },
    });
    return response.data;
  },

  async getQuote(symbol: string): Promise<{
    symbol: string;
    price: number;
    change: number;
    change_percent: number;
    volume: number;
    market_cap: number;
  }> {
    const response = await apiClient.get(`/v1/market/quote/${symbol}`);
    return response.data;
  },
};

export default marketApi;
