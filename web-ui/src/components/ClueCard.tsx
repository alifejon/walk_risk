import { motion } from 'framer-motion';
import type { Clue } from '../types';

interface ClueCardProps {
  clue: Clue;
  isSelected: boolean;
  isRevealed: boolean;
  onClick: () => void;
}

const typeColors: Record<Clue['type'], string> = {
  news: 'border-neon-cyan',
  financial: 'border-neon-green',
  chart: 'border-neon-yellow',
  analyst: 'border-neon-pink',
  insider: 'border-neon-purple',
};

const typeGlows: Record<Clue['type'], string> = {
  news: 'shadow-neon',
  financial: 'shadow-neon-green',
  chart: 'hover:shadow-[0_0_15px_#FFE66D]',
  analyst: 'shadow-neon-pink',
  insider: 'hover:shadow-[0_0_15px_#9D00FF]',
};

export function ClueCard({ clue, isSelected, isRevealed, onClick }: ClueCardProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`
        relative p-4 rounded-xl border-2 transition-all duration-300
        ${typeColors[clue.type]}
        ${isSelected ? typeGlows[clue.type] : 'border-opacity-50'}
        ${isRevealed ? 'bg-game-card' : 'bg-game-card/50'}
        hover:scale-105 hover:border-opacity-100
        focus:outline-none focus:ring-2 focus:ring-neon-cyan/50
      `}
      whileHover={{ y: -5 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="flex flex-col items-center gap-2">
        <span className="text-3xl">{clue.icon}</span>
        <span className="text-sm font-medium text-white/90">{clue.title}</span>
        {isRevealed && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute -top-2 -right-2 w-5 h-5 bg-neon-green rounded-full flex items-center justify-center"
          >
            <span className="text-xs">✓</span>
          </motion.div>
        )}
      </div>

      {/* Reliability indicator */}
      <div className="mt-2 w-full h-1 bg-game-bg rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-neon-cyan to-neon-green"
          initial={{ width: 0 }}
          animate={{ width: `${clue.reliability * 100}%` }}
          transition={{ delay: 0.2, duration: 0.5 }}
        />
      </div>
    </motion.button>
  );
}
