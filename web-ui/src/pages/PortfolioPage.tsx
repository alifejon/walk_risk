import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { portfolioApi } from '../api/portfolio';
import type { Portfolio, Trade } from '../types';

interface PerformanceData {
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
}

export function PortfolioPage() {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [portfolioData, performanceData, historyData] = await Promise.all([
        portfolioApi.getPortfolio(),
        portfolioApi.getPerformance(),
        portfolioApi.getHistory({ limit: 10 }),
      ]);
      setPortfolio(portfolioData);
      setPerformance(performanceData);
      setTrades(historyData.trades);
    } catch (err) {
      setError('포트폴리오 데이터를 불러오는데 실패했습니다');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60">포트폴리오 로딩 중...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center glass-card p-8"
        >
          <p className="text-neon-red mb-4">{error}</p>
          <div className="flex gap-4 justify-center">
            <motion.button
              onClick={loadData}
              className="px-6 py-3 rounded-lg bg-neon-cyan/20 border border-neon-cyan text-neon-cyan hover:bg-neon-cyan/30"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              다시 시도
            </motion.button>
            <motion.button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 rounded-lg bg-white/10 text-white hover:bg-white/20"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              대시보드로
            </motion.button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-center mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-neon-cyan neon-text">
              포트폴리오
            </h1>
            <p className="text-white/60">투자 현황을 확인하세요</p>
          </div>
          <motion.button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 rounded-lg bg-white/10 text-white/70 hover:bg-white/20 hover:text-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            ← 대시보드
          </motion.button>
        </motion.header>

        {/* Portfolio Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 mb-6"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-white/50 mb-1">총 자산</div>
              <div className="text-2xl font-bold text-neon-cyan">
                ${(portfolio?.total_value || 0).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-white/50 mb-1">현금</div>
              <div className="text-2xl font-bold text-neon-green">
                ${(portfolio?.cash_balance || 0).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-white/50 mb-1">총 수익률</div>
              <div className={`text-2xl font-bold ${(performance?.performance?.total_return || 0) >= 0 ? 'text-neon-green' : 'text-neon-red'}`}>
                {(performance?.performance?.total_return || 0) >= 0 ? '+' : ''}
                {((performance?.performance?.total_return || 0) * 100).toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-white/50 mb-1">미실현 손익</div>
              <div className={`text-2xl font-bold ${(performance?.performance?.unrealized_pnl || 0) >= 0 ? 'text-neon-green' : 'text-neon-red'}`}>
                ${(performance?.performance?.unrealized_pnl || 0).toLocaleString()}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Holdings & Stats Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Holdings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4">보유 종목</h3>
            {portfolio?.holdings && portfolio.holdings.length > 0 ? (
              <div className="space-y-3">
                {portfolio.holdings.map((holding, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-game-card rounded-lg">
                    <div>
                      <div className="font-semibold text-white">{holding.symbol}</div>
                      <div className="text-sm text-white/50">{holding.quantity}주 @ ${holding.average_cost.toFixed(2)}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-neon-cyan">
                        ${holding.market_value.toLocaleString()}
                      </div>
                      <div className={`text-sm ${(holding.market_value - holding.quantity * holding.average_cost) >= 0 ? 'text-neon-green' : 'text-neon-red'}`}>
                        {(holding.market_value - holding.quantity * holding.average_cost) >= 0 ? '+' : ''}
                        ${(holding.market_value - holding.quantity * holding.average_cost).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-white/50 py-8">
                보유 종목이 없습니다
              </div>
            )}
          </motion.div>

          {/* Risk Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4">리스크 지표</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white/50">분산 점수</span>
                  <span className="text-neon-cyan">{(performance?.risk_metrics?.diversification_score || 0).toFixed(1)}/10</span>
                </div>
                <div className="h-2 bg-game-card rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(performance?.risk_metrics?.diversification_score || 0) * 10}%` }}
                    className="h-full bg-gradient-to-r from-neon-cyan to-neon-pink"
                    transition={{ duration: 1 }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white/50">집중 리스크</span>
                  <span className="text-neon-yellow">{((performance?.risk_metrics?.concentration_risk || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-game-card rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(performance?.risk_metrics?.concentration_risk || 0) * 100}%` }}
                    className="h-full bg-gradient-to-r from-neon-yellow to-neon-red"
                    transition={{ duration: 1 }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="text-center p-3 bg-game-card rounded-lg">
                  <div className="text-2xl font-bold text-white">{performance?.risk_metrics?.position_count || 0}</div>
                  <div className="text-sm text-white/50">포지션 수</div>
                </div>
                <div className="text-center p-3 bg-game-card rounded-lg">
                  <div className="text-2xl font-bold text-white">{((performance?.risk_metrics?.cash_ratio || 0) * 100).toFixed(0)}%</div>
                  <div className="text-sm text-white/50">현금 비율</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Recent Trades */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">최근 거래</h3>
          {trades.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-white/50 text-sm border-b border-white/10">
                    <th className="pb-3">종목</th>
                    <th className="pb-3">유형</th>
                    <th className="pb-3">수량</th>
                    <th className="pb-3">가격</th>
                    <th className="pb-3">총액</th>
                    <th className="pb-3">일시</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade, idx) => (
                    <tr key={idx} className="border-b border-white/5">
                      <td className="py-3 font-semibold text-white">{trade.symbol}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-sm ${trade.side === 'buy' ? 'bg-neon-green/20 text-neon-green' : 'bg-neon-red/20 text-neon-red'}`}>
                          {trade.side === 'buy' ? '매수' : '매도'}
                        </span>
                      </td>
                      <td className="py-3 text-white">{trade.quantity}</td>
                      <td className="py-3 text-white">${trade.price.toFixed(2)}</td>
                      <td className="py-3 text-neon-cyan">${trade.total_value.toFixed(2)}</td>
                      <td className="py-3 text-white/50 text-sm">
                        {new Date(trade.executed_at).toLocaleDateString('ko-KR')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-white/50 py-8">
              거래 내역이 없습니다
            </div>
          )}
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center text-white/30 text-sm"
        >
          언락: 리스크 마스터 | Walk Risk MVP
        </motion.footer>
      </div>
    </div>
  );
}

export default PortfolioPage;
