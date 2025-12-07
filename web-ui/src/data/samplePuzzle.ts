export interface Clue {
  id: string;
  type: 'news' | 'financial' | 'chart' | 'analyst' | 'insider';
  title: string;
  content: string;
  reliability: number; // 0-1
  icon: string;
}

export interface Puzzle {
  id: string;
  title: string;
  symbol: string;
  description: string;
  eventData: {
    priceChange: number;
    volumeRatio: number;
    date: string;
  };
  clues: Clue[];
  correctAnswer: string;
  keywords: string[];
}

export const samplePuzzle: Puzzle = {
  id: 'puzzle-001',
  title: '삼성전자 급락의 비밀',
  symbol: '005930.KS',
  description: '삼성전자 주가가 하루 만에 8.5% 급락했습니다. 거래량은 평소의 3배에 달합니다. 무슨 일이 일어난 걸까요?',
  eventData: {
    priceChange: -8.5,
    volumeRatio: 3.2,
    date: '2024-03-15',
  },
  clues: [
    {
      id: 'clue-news',
      type: 'news',
      title: '뉴스',
      icon: '📰',
      content: `[속보] 글로벌 반도체 시장 전망 하향 조정

블룸버그 통신에 따르면, 주요 투자은행들이 2024년 글로벌 반도체 시장 성장률 전망을 기존 15%에서 8%로 하향 조정했습니다.

특히 메모리 반도체 부문에서 공급 과잉 우려가 커지고 있으며, 이는 삼성전자와 SK하이닉스 등 한국 반도체 기업들의 실적에 부정적 영향을 미칠 것으로 예상됩니다.

한편, 미중 무역갈등 재점화 가능성도 시장 불안 요인으로 작용하고 있습니다.`,
      reliability: 0.85,
    },
    {
      id: 'clue-financial',
      type: 'financial',
      title: '재무',
      icon: '📊',
      content: `삼성전자 최근 분기 실적 (전년 동기 대비)

• 매출: 67.8조원 (-12.3%)
• 영업이익: 6.5조원 (-35.2%)
• 순이익: 5.1조원 (-28.7%)

세부 사업부별:
• 반도체(DS): 매출 21.3조원 (-22.1%), 영업이익 1.2조원 (-68.5%)
• 디스플레이(SDC): 매출 7.8조원 (-8.3%), 영업이익 0.8조원 (-15.2%)
• 모바일(MX): 매출 29.7조원 (+3.2%), 영업이익 3.1조원 (+5.7%)

* 반도체 부문 적자 전환 우려 제기됨`,
      reliability: 0.95,
    },
    {
      id: 'clue-chart',
      type: 'chart',
      title: '차트',
      icon: '📈',
      content: `기술적 분석 요약:

• 50일 이동평균선 하향 돌파 (약세 신호)
• RSI: 23.5 (과매도 구간 진입)
• MACD: 데드크로스 발생 (3일 전)
• 볼린저 밴드: 하단 이탈

거래량 분석:
• 당일 거래량: 평균 대비 320% 증가
• 외국인 순매도: 8,500억원 (연중 최대)
• 기관 순매도: 3,200억원

지지선: 68,000원 / 저항선: 75,000원
현재가: 69,500원`,
      reliability: 0.75,
    },
    {
      id: 'clue-analyst',
      type: 'analyst',
      title: '애널리스트',
      icon: '🔬',
      content: `주요 증권사 리포트 요약:

[골드만삭스] 목표가 하향: 95,000원 → 78,000원
"메모리 반도체 사이클 바닥 시점이 예상보다 늦어질 것"

[JP모건] 투자의견: 비중확대 → 중립
"단기적 실적 부진 불가피, 하반기 회복 기대"

[삼성증권] 목표가 유지: 85,000원
"과도한 하락, 장기 투자 관점에서 매수 기회"

[대신증권] 신규 리포트
"AI 반도체 수요 증가가 2024년 하반기부터 본격화될 것"

컨센서스 변화: 목표가 평균 88,000원 → 82,000원`,
      reliability: 0.80,
    },
    {
      id: 'clue-insider',
      type: 'insider',
      title: '내부자',
      icon: '🔍',
      content: `내부자 거래 동향 (최근 3개월):

임원 주식 거래:
• 이재용 회장: 변동 없음 (지분 0.70% 유지)
• CFO 박학규: 2,000주 매도 (3월 10일)
• 반도체 부문장: 1,500주 매도 (3월 8일)

특이사항:
• 최근 3개월간 임원 6명 중 4명이 보유 주식 일부 매도
• 자사주 매입 계획 발표 없음
• 배당 정책 변경 가능성 언급 (IR 미팅)

업계 루머:
"삼성전자가 반도체 신규 투자 계획을 일부 연기할 수 있다는
내부 논의가 있다"는 소문이 업계에 돌고 있음 (미확인)`,
      reliability: 0.60,
    },
  ],
  correctAnswer: '글로벌 반도체 시장 전망 하향과 메모리 반도체 공급 과잉 우려로 인한 조정. 기술적으로는 과매도 구간에 진입했으며, 장기적으로는 AI 반도체 수요 증가에 따른 회복 가능성이 있음.',
  keywords: ['반도체', '공급과잉', '과매도', 'AI', '회복'],
};

// 사용자 가설과 정답 비교 함수
export function evaluateHypothesis(userHypothesis: string, puzzle: Puzzle): {
  accuracy: number;
  feedback: string;
  matchedKeywords: string[];
} {
  const lowerHypothesis = userHypothesis.toLowerCase();
  const matchedKeywords = puzzle.keywords.filter(keyword =>
    lowerHypothesis.includes(keyword.toLowerCase())
  );

  const keywordScore = matchedKeywords.length / puzzle.keywords.length;

  // 길이 보너스 (적절한 길이의 분석에 가산점)
  const lengthBonus = Math.min(userHypothesis.length / 100, 0.2);

  // 최종 점수 계산
  const accuracy = Math.min((keywordScore * 0.8 + lengthBonus) * 100, 100);

  let feedback: string;
  if (accuracy >= 80) {
    feedback = '훌륭한 분석입니다! 핵심 요인들을 정확히 파악했습니다. 실제 투자에서도 이런 종합적인 시각이 중요합니다.';
  } else if (accuracy >= 60) {
    feedback = '좋은 분석입니다. 주요 요인은 파악했지만, AI 반도체 수요나 기술적 과매도 신호 등 추가 고려 요소가 있습니다.';
  } else if (accuracy >= 40) {
    feedback = '방향은 맞지만 더 깊은 분석이 필요합니다. 뉴스와 재무 데이터를 종합적으로 살펴보세요.';
  } else {
    feedback = '다시 단서들을 살펴보세요. 반도체 시장 전망과 기업 실적 변화에 주목해 보세요.';
  }

  return {
    accuracy: Math.round(accuracy),
    feedback,
    matchedKeywords,
  };
}
