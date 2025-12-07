import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const MENTORS = [
  {
    id: 'buffett',
    name: '워렌 버핏',
    style: '가치 투자',
    description: '장기적 가치에 집중하는 현명한 투자',
    color: 'from-blue-500 to-blue-700',
  },
  {
    id: 'lynch',
    name: '피터 린치',
    style: '성장 투자',
    description: '일상에서 투자 기회를 발견하는 방법',
    color: 'from-green-500 to-green-700',
  },
  {
    id: 'graham',
    name: '벤자민 그레이엄',
    style: '안전 마진',
    description: '철저한 분석과 보수적 접근',
    color: 'from-gray-500 to-gray-700',
  },
  {
    id: 'dalio',
    name: '레이 달리오',
    style: '원칙 기반',
    description: '시스템과 원칙으로 리스크 관리',
    color: 'from-purple-500 to-purple-700',
  },
  {
    id: 'wood',
    name: '캐시 우드',
    style: '혁신 투자',
    description: '미래 기술과 파괴적 혁신에 투자',
    color: 'from-pink-500 to-pink-700',
  },
];

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();

  const [step, setStep] = useState(1);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [selectedMentor, setSelectedMentor] = useState('buffett');
  const [localError, setLocalError] = useState('');

  const handleNextStep = () => {
    setLocalError('');

    if (!username.trim()) {
      setLocalError('사용자 이름을 입력해주세요');
      return;
    }
    if (!email.trim()) {
      setLocalError('이메일을 입력해주세요');
      return;
    }
    if (password.length < 8) {
      setLocalError('비밀번호는 8자 이상이어야 합니다');
      return;
    }
    if (password !== confirmPassword) {
      setLocalError('비밀번호가 일치하지 않습니다');
      return;
    }

    setStep(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(username, email, password, selectedMentor);
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

        {/* Progress Indicator */}
        <div className="flex justify-center mb-6 gap-2">
          <div className={`w-3 h-3 rounded-full ${step >= 1 ? 'bg-neon-cyan' : 'bg-white/20'}`} />
          <div className={`w-3 h-3 rounded-full ${step >= 2 ? 'bg-neon-cyan' : 'bg-white/20'}`} />
        </div>

        {/* Registration Form */}
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold text-white text-center mb-6">
            {step === 1 ? '회원가입' : '멘토 선택'}
          </h2>

          {(error || localError) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-lg bg-neon-red/20 border border-neon-red/50 text-neon-red text-sm"
            >
              {error || localError}
              <button
                onClick={() => {
                  clearError();
                  setLocalError('');
                }}
                className="float-right text-white/50 hover:text-white"
              >
                ✕
              </button>
            </motion.div>
          )}

          {step === 1 ? (
            <form onSubmit={(e) => { e.preventDefault(); handleNextStep(); }} className="space-y-4">
              <div>
                <label className="block text-white/70 text-sm mb-2">사용자 이름</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-game-card border border-white/20 text-white
                           focus:border-neon-cyan focus:outline-none focus:ring-1 focus:ring-neon-cyan
                           transition-colors"
                  placeholder="username"
                  required
                />
              </div>

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
                  minLength={8}
                />
              </div>

              <div>
                <label className="block text-white/70 text-sm mb-2">비밀번호 확인</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-game-card border border-white/20 text-white
                           focus:border-neon-cyan focus:outline-none focus:ring-1 focus:ring-neon-cyan
                           transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>

              <motion.button
                type="submit"
                className="w-full py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-neon-cyan to-neon-pink text-game-bg hover:shadow-neon transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                다음
              </motion.button>
            </form>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <p className="text-white/60 text-sm text-center mb-4">
                당신의 투자 여정을 함께할 멘토를 선택하세요
              </p>

              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {MENTORS.map((mentor) => (
                  <motion.div
                    key={mentor.id}
                    onClick={() => setSelectedMentor(mentor.id)}
                    className={`p-4 rounded-lg cursor-pointer border-2 transition-all ${
                      selectedMentor === mentor.id
                        ? 'border-neon-cyan bg-neon-cyan/10'
                        : 'border-white/10 bg-game-card hover:border-white/30'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${mentor.color} flex items-center justify-center text-white font-bold text-lg`}>
                        {mentor.name[0]}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-white font-semibold">{mentor.name}</h3>
                        <p className="text-neon-cyan text-sm">{mentor.style}</p>
                        <p className="text-white/50 text-xs">{mentor.description}</p>
                      </div>
                      {selectedMentor === mentor.id && (
                        <div className="text-neon-cyan text-xl">✓</div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="flex gap-3 pt-4">
                <motion.button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-4 rounded-xl font-bold text-lg bg-white/10 text-white hover:bg-white/20 transition-all duration-300"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  이전
                </motion.button>
                <motion.button
                  type="submit"
                  disabled={isLoading}
                  className={`flex-1 py-4 rounded-xl font-bold text-lg transition-all duration-300
                    ${isLoading
                      ? 'bg-white/20 text-white/50 cursor-wait'
                      : 'bg-gradient-to-r from-neon-cyan to-neon-pink text-game-bg hover:shadow-neon'
                    }`}
                  whileHover={!isLoading ? { scale: 1.02 } : {}}
                  whileTap={!isLoading ? { scale: 0.98 } : {}}
                >
                  {isLoading ? '가입 중...' : '시작하기'}
                </motion.button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center">
            <p className="text-white/50">
              이미 계정이 있으신가요?{' '}
              <Link to="/login" className="text-neon-cyan hover:underline">
                로그인
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default RegisterPage;
