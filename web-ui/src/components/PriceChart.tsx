import { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ComposedChart,
  Area,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
  ReferenceDot,
} from 'recharts';

interface PriceChartProps {
  symbol: string;
  eventDate?: string;
  priceChange?: number;
}

interface ChartDataPoint {
  date: string;
  fullDate: string;
  close: number;
  volume: number;
  ma5: number | null;
  ma20: number | null;
  isUp: boolean;
  isEvent?: boolean;
  isVisible?: boolean;
}

// 이동평균 계산
function calculateMA(data: number[], period: number): (number | null)[] {
  const result: (number | null)[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }
  }
  return result;
}

// 퍼즐 이벤트 날짜 기준으로 시뮬레이션 데이터 생성
function generatePuzzleChartData(
  eventDate: string,
  priceChange: number,
  basePrice: number = 75000
): ChartDataPoint[] {
  const allData: { date: string; fullDate: string; close: number; volume: number; isEvent: boolean; isVisible: boolean }[] = [];
  const eventDateObj = new Date(eventDate);
  const baseVolume = 5000000;

  // 이동평균 계산을 위해 더 긴 기간 데이터 생성 (-60일 ~ +10일)
  // 화면에는 -20일 ~ +7일만 표시
  const dataStartDay = -60;
  const dataEndDay = 10;
  const visibleStartDay = -20;
  const visibleEndDay = 7;

  for (let i = dataStartDay; i <= dataEndDay; i++) {
    const date = new Date(eventDateObj);
    date.setDate(date.getDate() + i);

    if (date.getDay() === 0 || date.getDay() === 6) continue;

    const isEvent = i === 0;
    const isVisible = i >= visibleStartDay && i <= visibleEndDay;
    let close: number, volume: number;

    if (i < -30) {
      // 먼 과거: 기준가 근처에서 완만한 상승 추세
      const trend = 0.0008 * (i + 60);
      const noise = (Math.random() - 0.5) * 0.012;
      close = basePrice * (0.95 + trend + noise);
      volume = baseVolume * (0.5 + Math.random() * 0.4);
    } else if (i < -10) {
      // 중간 과거: 상승 추세
      const trend = 0.001 * (i + 30);
      const noise = (Math.random() - 0.5) * 0.015;
      close = basePrice * (0.98 + trend + noise);
      volume = baseVolume * (0.6 + Math.random() * 0.5);
    } else if (i < 0) {
      // 이벤트 직전: 고점 형성 후 하락 전조
      const trend = i > -5 ? -0.003 * (i + 5) : 0.002 * Math.abs(i + 10);
      const noise = (Math.random() - 0.5) * 0.015;
      close = basePrice * (1.02 + trend + noise);
      volume = baseVolume * (0.7 + Math.random() * 0.6);
    } else if (i === 0) {
      // 이벤트 당일: 급락
      close = basePrice * (1 + priceChange / 100);
      volume = baseVolume * 3.2;
    } else {
      // 이벤트 이후: 약간 회복
      const recovery = Math.min(i * 0.3, Math.abs(priceChange) * 0.2);
      const adjustedChange = priceChange + recovery;
      const noise = (Math.random() - 0.5) * 0.01;
      close = basePrice * (1 + adjustedChange / 100 + noise);
      volume = baseVolume * (0.9 + Math.random() * 0.8);
    }

    const dateStr = date.toISOString().split('T')[0];
    allData.push({
      date: dateStr.slice(5),
      fullDate: dateStr,
      close: Math.round(close),
      volume: Math.round(volume),
      isEvent,
      isVisible,
    });
  }

  // 전체 데이터로 이동평균 계산
  const closes = allData.map(d => d.close);
  const ma5Values = calculateMA(closes, 5);
  const ma20Values = calculateMA(closes, 20);

  // 이동평균 값을 포함한 전체 데이터 생성
  const fullData = allData.map((d, i) => ({
    date: d.date,
    fullDate: d.fullDate,
    close: d.close,
    volume: d.volume,
    ma5: ma5Values[i] ? Math.round(ma5Values[i]!) : null,
    ma20: ma20Values[i] ? Math.round(ma20Values[i]!) : null,
    isUp: i > 0 ? d.close >= allData[i - 1].close : true,
    isEvent: d.isEvent,
    isVisible: d.isVisible,
  }));

  // 화면에 표시할 데이터만 필터링
  return fullData.filter(d => d.isVisible);
}

export function PriceChart({ symbol, eventDate, priceChange }: PriceChartProps) {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (eventDate && priceChange !== undefined) {
      const simulatedData = generatePuzzleChartData(eventDate, priceChange);
      setData(simulatedData);
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  }, [symbol, eventDate, priceChange]);

  const { minPrice, maxPrice, maxVolume, eventIndex, eventData } = useMemo(() => {
    if (data.length === 0) return { minPrice: 0, maxPrice: 0, maxVolume: 0, eventIndex: -1, eventData: null };

    const closes = data.map(d => d.close);
    const volumes = data.map(d => d.volume);
    const evtIdx = data.findIndex(d => d.isEvent);

    const min = Math.min(...closes);
    const max = Math.max(...closes);
    const padding = (max - min) * 0.15;

    return {
      minPrice: min - padding,
      maxPrice: max + padding,
      maxVolume: Math.max(...volumes) * 1.3,
      eventIndex: evtIdx,
      eventData: evtIdx >= 0 ? data[evtIdx] : null,
    };
  }, [data]);

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center bg-[#131722] rounded-lg">
        <div className="w-8 h-8 border-2 border-neon-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-[#131722] rounded-lg text-white/50">
        차트 데이터 없음
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-[#131722] rounded-lg overflow-hidden"
    >
      {/* Chart Header */}
      <div className="px-4 py-3 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-4">
          <span className="text-white font-semibold">{symbol}</span>
          <div className="flex items-center gap-3 text-xs">
            <span className="text-white/50">일</span>
            <span className="text-white/30">|</span>
            <div className="flex items-center gap-1">
              <span className="text-[#FF9800]">이동평균</span>
              <span className="text-[#2196F3]">5</span>
              <span className="text-[#E91E63]">20</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          {eventData && (
            <span className={`font-bold ${priceChange && priceChange < 0 ? 'text-[#EF5350]' : 'text-[#26A69A]'}`}>
              {priceChange && priceChange > 0 ? '+' : ''}{priceChange}% ({eventDate})
            </span>
          )}
        </div>
      </div>

      {/* OHLC Info Bar */}
      {eventData && (
        <div className="px-4 py-2 flex items-center gap-4 text-xs bg-[#1E222D] border-b border-white/5">
          <div className="flex items-center gap-1">
            <span className="text-white/40">시작</span>
            <span className="text-white">{(data[0]?.close || 0).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-white/40">고가</span>
            <span className="text-[#26A69A]">{Math.max(...data.map(d => d.close)).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-white/40">저가</span>
            <span className="text-[#EF5350]">{Math.min(...data.map(d => d.close)).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-white/40">종가</span>
            <span className={eventData.isUp ? 'text-[#26A69A]' : 'text-[#EF5350]'}>
              {eventData.close.toLocaleString()}
            </span>
          </div>
          <div className="flex items-center gap-1 ml-auto">
            <span className="text-white/40">거래량</span>
            <span className="text-[#FFB74D]">{(eventData.volume / 10000).toFixed(0)}만</span>
          </div>
        </div>
      )}

      {/* Price Chart */}
      <div className="h-56 px-1">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 60, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="priceAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#EF5350" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#EF5350" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[minPrice, maxPrice]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
              tickFormatter={(value) => value.toLocaleString()}
              orientation="right"
              width={55}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E222D',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '4px',
                color: '#fff',
                fontSize: '11px',
              }}
              formatter={(value: number, name: string) => {
                const labels: Record<string, string> = {
                  close: '종가',
                  ma5: 'MA5',
                  ma20: 'MA20',
                };
                return [value.toLocaleString(), labels[name] || name];
              }}
              labelFormatter={(label) => label}
            />

            {/* Event Reference Line */}
            {eventIndex >= 0 && (
              <ReferenceLine
                x={data[eventIndex]?.date}
                stroke="#EF5350"
                strokeDasharray="3 3"
                strokeWidth={1}
              />
            )}

            {/* Price Area */}
            <Area
              type="monotone"
              dataKey="close"
              stroke="#EF5350"
              strokeWidth={1.5}
              fill="url(#priceAreaGradient)"
              dot={false}
            />

            {/* MA Lines */}
            <Line
              type="monotone"
              dataKey="ma5"
              stroke="#2196F3"
              strokeWidth={1}
              dot={false}
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="ma20"
              stroke="#E91E63"
              strokeWidth={1}
              dot={false}
              connectNulls={false}
            />

            {/* Event Point Marker */}
            {eventIndex >= 0 && eventData && (
              <ReferenceDot
                x={eventData.date}
                y={eventData.close}
                r={6}
                fill="#EF5350"
                stroke="#fff"
                strokeWidth={2}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Event Annotation */}
      {eventData && priceChange && (
        <div className="px-4 py-1 text-center">
          <span className="text-xs px-2 py-1 bg-[#EF5350]/20 text-[#EF5350] rounded">
            ₩{eventData.close.toLocaleString()} ({priceChange > 0 ? '+' : ''}{priceChange}%, {eventDate})
          </span>
        </div>
      )}

      {/* Volume Label */}
      <div className="px-4 py-1 flex items-center gap-2 border-t border-white/5">
        <span className="text-[10px] text-white/40">거래량 (20)</span>
      </div>

      {/* Volume Chart */}
      <div className="h-24 px-1">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 5, right: 60, left: 10, bottom: 5 }}>
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9 }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, maxVolume]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 9 }}
              tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
              orientation="right"
              width={55}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E222D',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '4px',
                color: '#fff',
                fontSize: '11px',
              }}
              formatter={(value: number) => [`${(value / 10000).toFixed(0)}만주`, '거래량']}
            />
            <Bar dataKey="volume" radius={[1, 1, 0, 0]} isAnimationActive={false}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    entry.isEvent
                      ? '#EF5350'
                      : entry.isUp
                      ? 'rgba(38, 166, 154, 0.7)'
                      : 'rgba(239, 83, 80, 0.7)'
                  }
                />
              ))}
            </Bar>
            {/* Volume MA Line */}
            <Line
              type="monotone"
              dataKey={(d: ChartDataPoint) => d.volume * 0.8}
              stroke="#FFB74D"
              strokeWidth={1}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom Info */}
      <div className="px-4 py-3 bg-[#1E222D] border-t border-white/5">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-white/40 block">이벤트</span>
              <span className="text-white font-medium">{eventDate}</span>
            </div>
            <div>
              <span className="text-white/40 block">등락률</span>
              <span className={`font-bold ${priceChange && priceChange < 0 ? 'text-[#EF5350]' : 'text-[#26A69A]'}`}>
                {priceChange && priceChange > 0 ? '+' : ''}{priceChange}%
              </span>
            </div>
            <div>
              <span className="text-white/40 block">거래량</span>
              <span className="text-[#FFB74D] font-medium">3.2x 증가</span>
            </div>
            <div>
              <span className="text-white/40 block">외국인</span>
              <span className="text-[#EF5350] font-medium">-8,500억</span>
            </div>
          </div>
          <div className="text-white/30 text-[10px]">
            TradingView 스타일
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default PriceChart;
