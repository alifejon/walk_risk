import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch {
      // Error is handled in store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-neon-cyan neon-text mb-2">
            언락: 리스크 마스터
          </h1>
          <p className="text-white/60">투자의 미스터리를 풀어보세요</p>
        </div>

        {/* Login Form */}
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold text-white text-center mb-6">로그인</h2>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-lg bg-neon-red/20 border border-neon-red/50 text-neon-red text-sm"
            >
              {error}
              <button
                onClick={clearError}
                className="float-right text-white/50 hover:text-white"
              >
                ✕
              </button>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white/70 text-sm mb-2">이메일</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-game-card border border-white/20 text-white
                         focus:border-neon-cyan focus:outline-none focus:ring-1 focus:ring-neon-cyan
                         transition-colors"
                placeholder="email@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-white/70 text-sm mb-2">비밀번호</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-game-card border border-white/20 text-white
                         focus:border-neon-cyan focus:outline-none focus:ring-1 focus:ring-neon-cyan
                         transition-colors"
                placeholder="••••••••"
                required
              />
            </div>

            <motion.button
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300
                ${isLoading
                  ? 'bg-white/20 text-white/50 cursor-wait'
                  : 'bg-gradient-to-r from-neon-cyan to-neon-pink text-game-bg hover:shadow-neon'
                }`}
              whileHover={!isLoading ? { scale: 1.02 } : {}}
              whileTap={!isLoading ? { scale: 0.98 } : {}}
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </motion.button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-white/50">
              계정이 없으신가요?{' '}
              <Link to="/register" className="text-neon-cyan hover:underline">
                회원가입
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default LoginPage;
