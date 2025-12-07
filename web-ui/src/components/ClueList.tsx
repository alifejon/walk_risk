import { motion, AnimatePresence } from 'framer-motion';
import { ClueCard } from './ClueCard';
import { ClueDetailPanel } from './ClueDetailPanel';
import type { Clue } from '../types';

interface ClueListProps {
  clues: Clue[];
  selectedClueId: string | null;
  revealedClueIds: Set<string>;
  onClueSelect: (clue: Clue) => void;
  symbol?: string;
  eventDate?: string;
}

export function ClueList({ clues, selectedClueId, revealedClueIds, onClueSelect, symbol = '', eventDate = '' }: ClueListProps) {
  const selectedClue = clues.find(c => c.id === selectedClueId);

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">🔍</span> 단서 조사
        </h3>
        <span className="text-sm text-white/50">
          단서를 클릭하여 조사하세요
        </span>
      </div>

      {/* Clue Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {clues.map((clue, index) => (
          <motion.div
            key={clue.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <ClueCard
              clue={clue}
              isSelected={selectedClueId === clue.id}
              isRevealed={revealedClueIds.has(clue.id)}
              onClick={() => onClueSelect(clue)}
            />
          </motion.div>
        ))}
      </div>

      {/* Clue Content Display */}
      <AnimatePresence mode="wait">
        {selectedClue && (
          <ClueDetailPanel
            key={selectedClue.id}
            clue={selectedClue}
            symbol={symbol}
            eventDate={eventDate}
          />
        )}
      </AnimatePresence>

      {/* Progress Indicator */}
      <div className="flex items-center justify-center gap-2 text-white/60">
        <span>조사 진행률:</span>
        <div className="w-32 h-2 bg-game-bg rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-neon-cyan to-neon-green"
            initial={{ width: 0 }}
            animate={{ width: `${(revealedClueIds.size / clues.length) * 100}%` }}
          />
        </div>
        <span className="text-neon-cyan">
          {revealedClueIds.size}/{clues.length}
        </span>
      </div>
    </div>
  );
}
