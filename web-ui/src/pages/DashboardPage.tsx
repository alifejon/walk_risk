import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { playersApi } from '../api/players';
import { puzzlesApi } from '../api/puzzles';

interface PlayerStats {
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
}

interface PuzzleStats {
  total_attempts: number;
  total_solved: number;
  success_rate: number;
  current_streak: number;
  best_streak: number;
  average_accuracy: number;
  by_difficulty: Record<string, { attempted: number; solved: number }>;
}

const MENTOR_INFO: Record<string, { name: string; color: string }> = {
  buffett: { name: '워렌 버핏', color: 'from-blue-500 to-blue-700' },
  lynch: { name: '피터 린치', color: 'from-green-500 to-green-700' },
  graham: { name: '벤자민 그레이엄', color: 'from-gray-500 to-gray-700' },
  dalio: { name: '레이 달리오', color: 'from-purple-500 to-purple-700' },
  wood: { name: '캐시 우드', color: 'from-pink-500 to-pink-700' },
};

export function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout, fetchUser } = useAuthStore();
  const [playerStats, setPlayerStats] = useState<PlayerStats | null>(null);
  const [puzzleStats, setPuzzleStats] = useState<PuzzleStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      await fetchUser();
      const [pStats, puzzStats] = await Promise.all([
        playersApi.getStats(),
        puzzlesApi.getStats(),
      ]);
      setPlayerStats(pStats);
      setPuzzleStats(puzzStats);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const mentorInfo = user?.preferred_mentor ? MENTOR_INFO[user.preferred_mentor] : null;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60">대시보드 로딩 중...</p>
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
              언락: 리스크 마스터
            </h1>
            <p className="text-white/60">투자의 미스터리를 풀어보세요</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-white/70">{user?.username}</span>
            <motion.button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg bg-white/10 text-white/70 hover:bg-white/20 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              로그아웃
            </motion.button>
          </div>
        </motion.header>

        {/* Player Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 mb-6"
        >
          <div className="flex items-center gap-6">
            {/* Avatar */}
            <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${mentorInfo?.color || 'from-neon-cyan to-neon-pink'} flex items-center justify-center text-white text-3xl font-bold`}>
              {user?.username?.[0]?.toUpperCase() || '?'}
            </div>

            {/* Info */}
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white">{user?.username}</h2>
              <div className="flex items-center gap-4 mt-1">
                <span className="text-neon-cyan">
                  Lv.{playerStats?.player_info?.level || user?.level || 1}
                </span>
                <span className="text-white/50">|</span>
                <span className="text-neon-pink">
                  {playerStats?.player_info?.current_class || user?.current_class || 'Risk Novice'}
                </span>
                {mentorInfo && (
                  <>
                    <span className="text-white/50">|</span>
                    <span className="text-white/70">멘토: {mentorInfo.name}</span>
                  </>
                )}
              </div>

              {/* XP Bar */}
              <div className="mt-3">
                <div className="flex justify-between text-sm text-white/50 mb-1">
                  <span>경험치</span>
                  <span>{playerStats?.player_info?.experience || user?.experience || 0} XP</span>
                </div>
                <div className="h-2 bg-game-card rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${((playerStats?.player_info?.experience || user?.experience || 0) % 100)}%` }}
                    className="h-full bg-gradient-to-r from-neon-cyan to-neon-pink"
                    transition={{ duration: 1, ease: 'easeOut' }}
                  />
                </div>
              </div>
            </div>

            {/* Energy */}
            <div className="text-center">
              <div className="text-sm text-white/50 mb-1">에너지</div>
              <div className="text-3xl font-bold text-neon-yellow">
                {user?.energy || 100}
              </div>
              <div className="text-xs text-white/30">/ {user?.max_energy || 100}</div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Puzzle Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">🧩</span> 퍼즐 현황
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/50">해결한 퍼즐</span>
                <span className="text-neon-cyan font-bold">{puzzleStats?.total_solved || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">성공률</span>
                <span className="text-neon-green font-bold">{(puzzleStats?.success_rate || 0).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">연속 성공</span>
                <span className="text-neon-yellow font-bold">{puzzleStats?.current_streak || 0}</span>
              </div>
            </div>
          </motion.div>

          {/* Portfolio Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">💰</span> 포트폴리오
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/50">총 자산</span>
                <span className="text-neon-cyan font-bold">
                  ${(playerStats?.portfolio_stats?.total_value || 0).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">포트폴리오 수</span>
                <span className="text-white font-bold">{playerStats?.portfolio_stats?.total_portfolios || 1}</span>
              </div>
            </div>
          </motion.div>

          {/* Learning Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">📊</span> 학습 현황
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/50">평균 정확도</span>
                <span className="text-neon-pink font-bold">
                  {(puzzleStats?.average_accuracy || 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">최고 연속 기록</span>
                <span className="text-neon-yellow font-bold">{puzzleStats?.best_streak || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">총 시도</span>
                <span className="text-white font-bold">{puzzleStats?.total_attempts || 0}</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          {/* Start Puzzle */}
          <Link to="/puzzle">
            <motion.div
              className="glass-card p-8 cursor-pointer border-2 border-transparent hover:border-neon-cyan transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-neon-cyan to-neon-pink flex items-center justify-center text-3xl">
                  🔍
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">리스크 퍼즐 시작</h3>
                  <p className="text-white/60">시장의 미스터리를 분석하고 해결하세요</p>
                </div>
              </div>
            </motion.div>
          </Link>

          {/* Portfolio */}
          <Link to="/portfolio">
            <motion.div
              className="glass-card p-8 cursor-pointer border-2 border-transparent hover:border-neon-pink transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-neon-pink to-neon-yellow flex items-center justify-center text-3xl">
                  📈
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">포트폴리오 관리</h3>
                  <p className="text-white/60">투자 현황을 확인하고 거래하세요</p>
                </div>
              </div>
            </motion.div>
          </Link>
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-12 text-center text-white/30 text-sm"
        >
          언락: 리스크 마스터 | Walk Risk MVP
        </motion.footer>
      </div>
    </div>
  );
}

export default DashboardPage;
