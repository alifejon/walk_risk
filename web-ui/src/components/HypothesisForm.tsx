import { useState } from 'react';
import { motion } from 'framer-motion';

interface HypothesisFormProps {
  onSubmit: (hypothesis: string) => void;
  onBack: () => void;
}

export function HypothesisForm({ onSubmit, onBack }: HypothesisFormProps) {
  const [hypothesis, setHypothesis] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hypothesis.trim().length > 0) {
      onSubmit(hypothesis.trim());
    }
  };

  const minLength = 20;
  const isValid = hypothesis.trim().length >= minLength;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-8"
    >
      <div className="text-center mb-6">
        <span className="text-4xl mb-4 block">💡</span>
        <h2 className="text-2xl font-bold text-neon-cyan neon-text">
          당신의 가설을 입력하세요
        </h2>
        <p className="text-white/60 mt-2">
          수집한 단서들을 바탕으로 주가 변동의 원인을 분석해 보세요
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <textarea
            value={hypothesis}
            onChange={(e) => setHypothesis(e.target.value)}
            placeholder="예: 반도체 시장 전망 하향과 실적 부진이 주가 하락의 주요 원인이며, 기술적으로 과매도 구간에 진입했으므로 단기 반등 가능성이 있다..."
            className="w-full h-40 p-4 bg-game-bg/50 border-2 border-neon-cyan/30 rounded-xl
                       text-white placeholder-white/30 resize-none
                       focus:outline-none focus:border-neon-cyan focus:shadow-neon
                       transition-all duration-300"
          />
          <div className="flex justify-between mt-2 text-sm">
            <span className={`${isValid ? 'text-neon-green' : 'text-white/40'}`}>
              {hypothesis.length}자 / 최소 {minLength}자
            </span>
            <span className="text-white/40">
              구체적으로 작성할수록 높은 점수를 받을 수 있습니다
            </span>
          </div>
        </div>

        {/* Hint Box */}
        <div className="bg-neon-purple/10 border border-neon-purple/30 rounded-lg p-4">
          <p className="text-sm text-white/70">
            <span className="text-neon-purple font-bold">💎 힌트:</span>{' '}
            좋은 가설에는 다음 요소가 포함됩니다:
          </p>
          <ul className="mt-2 text-sm text-white/60 space-y-1 ml-4">
            <li>• 주가 변동의 <span className="text-neon-cyan">원인</span> (왜 떨어졌는가?)</li>
            <li>• 시장 상황에 대한 <span className="text-neon-cyan">분석</span> (어떤 환경인가?)</li>
            <li>• 향후 <span className="text-neon-cyan">전망</span> (앞으로 어떻게 될까?)</li>
          </ul>
        </div>

        <div className="flex gap-4">
          <motion.button
            type="button"
            onClick={onBack}
            className="flex-1 py-3 px-6 border-2 border-white/30 rounded-xl
                       text-white/70 font-medium
                       hover:border-white/50 hover:text-white
                       transition-all duration-300"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            ← 단서 더 보기
          </motion.button>

          <motion.button
            type="submit"
            disabled={!isValid}
            className={`flex-1 py-3 px-6 rounded-xl font-bold
                        transition-all duration-300
                        ${isValid
                          ? 'bg-gradient-to-r from-neon-cyan to-neon-green text-game-bg shadow-neon hover:shadow-[0_0_30px_#00F5FF]'
                          : 'bg-white/10 text-white/30 cursor-not-allowed'
                        }`}
            whileHover={isValid ? { scale: 1.02 } : {}}
            whileTap={isValid ? { scale: 0.98 } : {}}
          >
            가설 제출하기 🎯
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
}
