import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface ResultPanelProps {
  accuracy: number;
  feedback: string;
  matchedKeywords: string[];
  correctAnswer: string;
  userHypothesis: string;
  onRestart: () => void;
}

export function ResultPanel({
  accuracy,
  feedback,
  matchedKeywords,
  correctAnswer,
  userHypothesis,
  onRestart,
}: ResultPanelProps) {
  const [displayedAccuracy, setDisplayedAccuracy] = useState(0);

  // Animate accuracy counter
  useEffect(() => {
    const duration = 1500;
    const steps = 60;
    const increment = accuracy / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= accuracy) {
        setDisplayedAccuracy(accuracy);
        clearInterval(timer);
      } else {
        setDisplayedAccuracy(Math.round(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [accuracy]);

  const getGrade = (score: number) => {
    if (score >= 80) return { label: '훌륭함', color: 'text-neon-green', emoji: '🌟' };
    if (score >= 60) return { label: '좋음', color: 'text-neon-cyan', emoji: '👍' };
    if (score >= 40) return { label: '보통', color: 'text-neon-yellow', emoji: '💪' };
    return { label: '노력 필요', color: 'text-neon-red', emoji: '📚' };
  };

  const grade = getGrade(accuracy);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-8 space-y-6"
    >
      {/* Accuracy Display */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className="inline-block"
        >
          <div className="relative w-40 h-40 mx-auto">
            {/* Background circle */}
            <svg className="w-full h-full -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="#1A1A2E"
                strokeWidth="12"
                fill="none"
              />
              <motion.circle
                cx="80"
                cy="80"
                r="70"
                stroke="url(#gradient)"
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: accuracy / 100 }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
                style={{ strokeDasharray: '440', strokeDashoffset: '0' }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00F5FF" />
                  <stop offset="100%" stopColor="#39FF14" />
                </linearGradient>
              </defs>
            </svg>
            {/* Center text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-white">{displayedAccuracy}%</span>
              <span className={`text-sm ${grade.color}`}>{grade.label}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-4"
        >
          <span className="text-5xl">{grade.emoji}</span>
        </motion.div>
      </div>

      {/* Feedback */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-game-bg/50 rounded-xl p-4"
      >
        <h3 className="text-lg font-bold text-neon-cyan mb-2">📝 피드백</h3>
        <p className="text-white/80">{feedback}</p>
      </motion.div>

      {/* Matched Keywords */}
      {matchedKeywords.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <h3 className="text-sm font-bold text-white/60 mb-2">✓ 맞춘 키워드</h3>
          <div className="flex flex-wrap gap-2">
            {matchedKeywords.map((keyword) => (
              <span
                key={keyword}
                className="px-3 py-1 bg-neon-green/20 text-neon-green rounded-full text-sm border border-neon-green/30"
              >
                {keyword}
              </span>
            ))}
          </div>
        </motion.div>
      )}

      {/* Your Hypothesis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="bg-game-bg/30 rounded-xl p-4"
      >
        <h3 className="text-sm font-bold text-white/60 mb-2">📋 당신의 가설</h3>
        <p className="text-white/70 text-sm">{userHypothesis}</p>
      </motion.div>

      {/* Correct Answer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.1 }}
        className="bg-neon-cyan/10 border border-neon-cyan/30 rounded-xl p-4"
      >
        <h3 className="text-sm font-bold text-neon-cyan mb-2">💡 모범 답안</h3>
        <p className="text-white/80 text-sm">{correctAnswer}</p>
      </motion.div>

      {/* Restart Button */}
      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.3 }}
        onClick={onRestart}
        className="w-full py-4 bg-gradient-to-r from-neon-pink to-neon-purple
                   text-white font-bold rounded-xl
                   hover:shadow-neon-pink transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        🔄 다시 도전하기
      </motion.button>
    </motion.div>
  );
}
