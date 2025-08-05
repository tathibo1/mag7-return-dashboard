import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { ReturnData, StockStats } from '../types';

interface StockCardProps {
  symbol: string;
  data: ReturnData[];
  stats: StockStats;
}

const StockCard: React.FC<StockCardProps> = ({ symbol, data, stats }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  
  const chartData = data.map(item => ({
    ...item,
    returnPercent: item.return * 100
  }));

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 hover:shadow-2xl transition-shadow border border-gray-700">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-100 pb-2">{symbol}</h3>
        <div className="flex space-x-3 text-xs">
          <div className="text-gray-400">Max: <span className="font-semibold text-green-400">{formatPercent(stats.max)}</span></div>
          <div className="text-gray-400">Mean: <span className="font-semibold text-gray-300">{formatPercent(stats.mean)}</span></div>
          <div className="text-gray-400">Min: <span className="font-semibold text-red-400">{formatPercent(stats.min)}</span></div>
        </div>
      </div>
      
      <div className="h-56 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(3)}%`, 'Return']}
              labelStyle={{ color: '#E5E7EB' }}
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.375rem' }}
            />
            <ReferenceLine y={0} stroke="#6B7280" strokeDasharray="3 3" />
            <Line 
              type="monotone" 
              dataKey="returnPercent" 
              stroke="#60A5FA" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#60A5FA' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default StockCard;