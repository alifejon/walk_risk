import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ClueList } from '../components/ClueList';
import { HypothesisForm } from '../components/HypothesisForm';
import { ResultPanel } from '../components/ResultPanel';
import { PriceChart } from '../components/PriceChart';
import { puzzlesApi } from '../api/puzzles';
import type { Puzzle, Clue } from '../types';

type GamePhase = 'loading' | 'investigation' | 'hypothesis' | 'result';

interface GameResult {
  accuracy: number;
  feedback: string;
  matchedKeywords: string[];
  userHypothesis: string;
  correctAnswer?: string;
}

// API 응답을 프론트엔드 형식으로 변환
const CLUE_TYPE_MAP: Record<string, Clue['type']> = {
  news: 'news',
  financials: 'financial',
  chart: 'chart',
  analyst: 'analyst',
  insider: 'insider',
  technical: 'chart',
  fundamental: 'financial',
};

const CLUE_ICON_MAP: Record<string, string> = {
  news: '📰',
  financials: '📊',
  financial: '📊',
  chart: '📈',
  analyst: '🔬',
  insider: '🔍',
  technical: '📈',
  fundamental: '📊',
};

interface ApiClue {
  clue_id: string;
  source: string;
  title: string;
  description: string;
  cost: number;
  is_discovered: boolean;
  content?: string;
  reliability?: number;
}

interface ApiPuzzle {
  puzzle_id: string;
  title: string;
  description: string;
  difficulty: string;
  type?: string;
  target_symbol: string;
  event_data?: {
    price_change: number;
    volume?: number;
    date: string;
    market_context?: string;
  };
  available_clues: ApiClue[];
  discovered_clues: ApiClue[];
}

function transformClue(apiClue: ApiClue): Clue {
  return {
    id: apiClue.clue_id,
    title: apiClue.title,
    type: CLUE_TYPE_MAP[apiClue.source] || 'news',
    icon: CLUE_ICON_MAP[apiClue.source] || '📋',
    reliability: apiClue.reliability ?? 0.7,
    content: apiClue.content || apiClue.description,
    discovered: apiClue.is_discovered,
  };
}

function transformPuzzle(apiPuzzle: ApiPuzzle): Puzzle {
  const allClues = [
    ...apiPuzzle.available_clues.map(transformClue),
    ...apiPuzzle.discovered_clues.map(transformClue),
  ];

  return {
    id: apiPuzzle.puzzle_id,
    title: apiPuzzle.title,
    description: apiPuzzle.description,
    difficulty: apiPuzzle.difficulty,
    symbol: apiPuzzle.target_symbol,
    clues: allClues,
    event_data: apiPuzzle.event_data ? {
      price_change: apiPuzzle.event_data.price_change,
      volume_ratio: (apiPuzzle.event_data.volume || 0) / 5000000, // Normalize
      date: apiPuzzle.event_data.date,
    } : undefined,
  };
}

export function PuzzlePage() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<GamePhase>('loading');
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [selectedClueId, setSelectedClueId] = useState<string | null>(null);
  const [revealedClueIds, setRevealedClueIds] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<GameResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPuzzle();
  }, []);

  const loadPuzzle = async () => {
    try {
      setPhase('loading');
      setError(null);
      const response = await puzzlesApi.getAvailablePuzzles({ limit: 1 });
      if (response.puzzles.length > 0) {
        // API returns puzzle_id, not id
        const puzzleId = (response.puzzles[0] as unknown as { puzzle_id: string }).puzzle_id;
        const apiPuzzle = await puzzlesApi.getPuzzleDetails(puzzleId) as unknown as ApiPuzzle;
        const transformedPuzzle = transformPuzzle(apiPuzzle);
        setPuzzle(transformedPuzzle);
        setPhase('investigation');
      } else {
        setError('사용 가능한 퍼즐이 없습니다');
      }
    } catch (err) {
      setError('퍼즐을 불러오는데 실패했습니다');
      console.error(err);
    }
  };

  const handleClueSelect = async (clue: Clue) => {
    setSelectedClueId(clue.id);
    setRevealedClueIds((prev) => new Set([...prev, clue.id]));

    if (puzzle) {
      try {
        await puzzlesApi.investigateClue(puzzle.id, clue.id);
      } catch (err) {
        console.error('Failed to record clue investigation:', err);
      }
    }
  };

  const handleSubmitHypothesis = async (hypothesis: string) => {
    if (!puzzle) return;

    try {
      const response = await puzzlesApi.submitHypothesis(
        puzzle.id,
        hypothesis,
        70, // default confidence
        Array.from(revealedClueIds),
        hypothesis
      );

      setResult({
        accuracy: response.accuracy,
        feedback: response.feedback,
        matchedKeywords: response.evidence_used || [],
        userHypothesis: hypothesis,
        correctAnswer: response.correct_answer,
      });
      setPhase('result');
    } catch (err) {
      console.error('Failed to submit hypothesis:', err);
      setError('가설 제출에 실패했습니다');
    }
  };

  const handleRestart = () => {
    setPhase('loading');
    setSelectedClueId(null);
    setRevealedClueIds(new Set());
    setResult(null);
    loadPuzzle();
  };

  if (phase === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60">퍼즐 로딩 중...</p>
        </motion.div>
      </div>
    );
  }

  if (error || !puzzle) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center glass-card p-8"
        >
          <p className="text-neon-red mb-4">{error || '퍼즐을 찾을 수 없습니다'}</p>
          <div className="flex gap-4 justify-center">
            <motion.button
              onClick={loadPuzzle}
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
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-neon-cyan neon-text mb-2">
            리스크 퍼즐
          </h1>
          <p className="text-white/60">시장의 미스터리를 풀어보세요</p>
        </motion.header>

        {/* Puzzle Info Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 mb-8"
        >
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                {puzzle.title}
              </h2>
              <p className="text-white/70">{puzzle.description}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-white/50">종목</div>
              <div className="text-lg font-bold text-neon-pink">{puzzle.symbol}</div>
            </div>
          </div>

          {/* Event Data */}
          {puzzle.event_data && (
            <div className="mt-4 flex gap-6">
              <div className="flex items-center gap-2">
                <span className="text-white/50">변동률:</span>
                <span className={`font-bold ${puzzle.event_data.price_change < 0 ? 'text-neon-red' : 'text-neon-green'}`}>
                  {puzzle.event_data.price_change > 0 ? '+' : ''}
                  {puzzle.event_data.price_change}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/50">거래량:</span>
                <span className="font-bold text-neon-yellow">
                  {puzzle.event_data.volume_ratio.toFixed(1)}x
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/50">발생일:</span>
                <span className="text-neon-cyan font-semibold">{puzzle.event_data.date}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/50">난이도:</span>
                <span className="text-white/80">{puzzle.difficulty}</span>
              </div>
            </div>
          )}
        </motion.div>

        {/* Price Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <PriceChart
            symbol={puzzle.symbol}
            eventDate={puzzle.event_data?.date}
            priceChange={puzzle.event_data?.price_change}
          />
        </motion.div>

        {/* Main Content */}
        <AnimatePresence mode="wait">
          {phase === 'investigation' && (
            <motion.div
              key="investigation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ClueList
                clues={puzzle.clues}
                selectedClueId={selectedClueId}
                revealedClueIds={revealedClueIds}
                onClueSelect={handleClueSelect}
                symbol={puzzle.symbol}
                eventDate={puzzle.event_data?.date}
              />

              {/* Submit Button */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-8 text-center"
              >
                <motion.button
                  onClick={() => setPhase('hypothesis')}
                  disabled={revealedClueIds.size === 0}
                  className={`px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300
                    ${revealedClueIds.size > 0
                      ? 'bg-gradient-to-r from-neon-cyan to-neon-pink text-game-bg shadow-neon hover:shadow-[0_0_40px_#00F5FF]'
                      : 'bg-white/10 text-white/30 cursor-not-allowed'
                    }`}
                  whileHover={revealedClueIds.size > 0 ? { scale: 1.05 } : {}}
                  whileTap={revealedClueIds.size > 0 ? { scale: 0.95 } : {}}
                >
                  {revealedClueIds.size === 0
                    ? '단서를 먼저 조사하세요'
                    : `가설 제출하기 (${revealedClueIds.size}개 단서 수집)`}
                </motion.button>
              </motion.div>
            </motion.div>
          )}

          {phase === 'hypothesis' && (
            <motion.div
              key="hypothesis"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <HypothesisForm
                onSubmit={handleSubmitHypothesis}
                onBack={() => setPhase('investigation')}
              />
            </motion.div>
          )}

          {phase === 'result' && result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <ResultPanel
                accuracy={result.accuracy}
                feedback={result.feedback}
                matchedKeywords={result.matchedKeywords}
                correctAnswer={result.correctAnswer || ''}
                userHypothesis={result.userHypothesis}
                onRestart={handleRestart}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-12 text-center text-white/30 text-sm"
        >
          <button
            onClick={() => navigate('/dashboard')}
            className="hover:text-white/60 transition-colors"
          >
            ← 대시보드로 돌아가기
          </button>
        </motion.footer>
      </div>
    </div>
  );
}

export default PuzzlePage;
