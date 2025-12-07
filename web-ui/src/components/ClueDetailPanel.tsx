import { motion } from 'framer-motion';
import type { Clue } from '../types';

interface ClueDetailPanelProps {
  clue: Clue;
  symbol: string;
  eventDate: string;
}

// 삼성전자 퍼즐용 상세 단서 콘텐츠
const CLUE_CONTENTS: Record<string, {
  title: string;
  sections: Array<{
    heading: string;
    content: string;
    highlight?: 'positive' | 'negative' | 'neutral';
  }>;
}> = {
  news: {
    title: '관련 뉴스 기사',
    sections: [
      {
        heading: '[속보] 글로벌 반도체 시장 전망 하향 조정',
        content: `블룸버그 통신에 따르면, 주요 투자은행들이 2024년 글로벌 반도체 시장 성장률 전망을 기존 15%에서 8%로 하향 조정했습니다.

특히 메모리 반도체 부문에서 공급 과잉 우려가 커지고 있으며, 이는 삼성전자와 SK하이닉스 등 한국 반도체 기업들의 실적에 부정적 영향을 미칠 것으로 예상됩니다.`,
        highlight: 'negative',
      },
      {
        heading: '[단독] 삼성전자, AI 반도체 신규 투자 연기 검토',
        content: `업계 소식통에 따르면 삼성전자가 당초 계획했던 AI 반도체 생산라인 증설을 6개월 이상 연기하는 방안을 내부적으로 검토 중인 것으로 알려졌습니다.

이는 글로벌 수요 둔화와 미중 무역갈등에 따른 불확실성 때문으로 분석됩니다.`,
        highlight: 'negative',
      },
    ],
  },
  financial: {
    title: '재무제표 분석',
    sections: [
      {
        heading: '최근 분기 실적 (전년 동기 대비)',
        content: `• 매출: 67.8조원 (-12.3%)
• 영업이익: 6.5조원 (-35.2%)
• 순이익: 5.1조원 (-28.7%)

세부 사업부별:
• 반도체(DS): 매출 21.3조원 (-22.1%), 영업이익 1.2조원 (-68.5%)
• 디스플레이(SDC): 매출 7.8조원 (-8.3%), 영업이익 0.8조원 (-15.2%)
• 모바일(MX): 매출 29.7조원 (+3.2%), 영업이익 3.1조원 (+5.7%)`,
        highlight: 'negative',
      },
      {
        heading: '주요 재무 지표',
        content: `• PER: 12.5배 (업종 평균 15.2배)
• PBR: 1.1배 (역사적 저점 수준)
• ROE: 8.2% (전년 12.5%)
• 부채비율: 35% (안정적)
• 현금성자산: 105조원`,
        highlight: 'neutral',
      },
    ],
  },
  chart: {
    title: '기술적 분석',
    sections: [
      {
        heading: '주요 기술 지표',
        content: `• 50일 이동평균선 하향 돌파 (약세 신호)
• RSI: 23.5 (과매도 구간 진입)
• MACD: 데드크로스 발생 (3일 전)
• 볼린저 밴드: 하단 이탈
• 스토캐스틱: 15.2 (과매도)`,
        highlight: 'negative',
      },
      {
        heading: '거래량 분석',
        content: `• 당일 거래량: 평균 대비 320% 증가
• 외국인 순매도: 8,500억원 (연중 최대)
• 기관 순매도: 3,200억원
• 개인 순매수: 1,100억원

지지선: 68,000원 / 저항선: 75,000원
현재가: 69,500원`,
        highlight: 'negative',
      },
    ],
  },
  analyst: {
    title: '애널리스트 리포트',
    sections: [
      {
        heading: '주요 증권사 의견',
        content: `[골드만삭스] 목표가 하향: 95,000원 → 78,000원
"메모리 반도체 사이클 바닥 시점이 예상보다 늦어질 것"

[JP모건] 투자의견: 비중확대 → 중립
"단기적 실적 부진 불가피, 하반기 회복 기대"

[삼성증권] 목표가 유지: 85,000원
"과도한 하락, 장기 투자 관점에서 매수 기회"`,
        highlight: 'neutral',
      },
      {
        heading: '컨센서스 변화',
        content: `• 목표가 평균: 88,000원 → 82,000원 (-6.8%)
• 투자의견: 매수 70% → 55%
• 실적 전망: 하반기 반등 예상 유지
• AI 반도체 수요 증가 전망은 긍정적`,
        highlight: 'positive',
      },
    ],
  },
  insider: {
    title: '내부자 거래 동향',
    sections: [
      {
        heading: '임원 주식 거래 (최근 3개월)',
        content: `• 이재용 회장: 변동 없음 (지분 0.70% 유지)
• CFO 박학규: 2,000주 매도 (3월 10일)
• 반도체 부문장: 1,500주 매도 (3월 8일)

특이사항:
• 최근 3개월간 임원 6명 중 4명이 보유 주식 일부 매도
• 자사주 매입 계획 발표 없음`,
        highlight: 'negative',
      },
      {
        heading: '업계 루머 (미확인)',
        content: `"삼성전자가 반도체 신규 투자 계획을 일부 연기할 수 있다는 내부 논의가 있다"는 소문이 업계에 돌고 있음.

⚠️ 이 정보는 미확인 루머이며 신뢰도가 낮습니다.`,
        highlight: 'neutral',
      },
    ],
  },
};

export function ClueDetailPanel({ clue, symbol, eventDate }: ClueDetailPanelProps) {
  const content = CLUE_CONTENTS[clue.type] || {
    title: clue.title,
    sections: [{ heading: '조사 결과', content: clue.content || '상세 정보 없음', highlight: 'neutral' as const }],
  };

  const highlightColors = {
    positive: 'border-l-neon-green bg-neon-green/5',
    negative: 'border-l-neon-red bg-neon-red/5',
    neutral: 'border-l-white/30 bg-white/5',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="glass-card p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{clue.icon}</span>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-neon-cyan">{content.title}</h3>
          <p className="text-sm text-white/50">{symbol} | {eventDate}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-white/60">신뢰도:</span>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full ${
                  i <= clue.reliability * 5 ? 'bg-neon-green' : 'bg-white/20'
                }`}
              />
            ))}
          </div>
          <span className="text-sm text-neon-green">
            {Math.round(clue.reliability * 100)}%
          </span>
        </div>
      </div>

      {/* Content Sections */}
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {content.sections.map((section, idx) => (
          <div
            key={idx}
            className={`border-l-4 pl-4 py-2 rounded-r ${highlightColors[section.highlight || 'neutral']}`}
          >
            <h4 className="font-semibold text-white mb-2">{section.heading}</h4>
            <pre className="text-sm text-white/80 whitespace-pre-wrap font-sans leading-relaxed">
              {section.content}
            </pre>
          </div>
        ))}
      </div>

      {/* Tip */}
      <div className="mt-4 p-3 bg-neon-purple/10 border border-neon-purple/30 rounded-lg">
        <p className="text-sm text-white/70">
          <span className="text-neon-purple font-semibold">💡 팁:</span>{' '}
          {clue.type === 'news' && '뉴스의 시점과 시장 반응 시차를 고려하세요.'}
          {clue.type === 'financial' && '단기 실적과 장기 성장성을 구분해서 분석하세요.'}
          {clue.type === 'chart' && 'RSI 과매도는 반등 가능성을 시사할 수 있습니다.'}
          {clue.type === 'analyst' && '목표가 하향은 이미 주가에 반영되었을 수 있습니다.'}
          {clue.type === 'insider' && '내부자 매도가 항상 부정적인 신호는 아닙니다.'}
        </p>
      </div>
    </motion.div>
  );
}

export default ClueDetailPanel;
