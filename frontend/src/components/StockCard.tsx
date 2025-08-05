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
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-bold mb-2 text-gray-800">{symbol}</h3>
      
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 10 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              tick={{ fontSize: 10 }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(3)}%`, 'Return']}
              labelStyle={{ color: '#333' }}
            />
            <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            <Line 
              type="monotone" 
              dataKey="returnPercent" 
              stroke="#2563eb" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="text-center">
          <p className="text-gray-500">Min</p>
          <p className="font-semibold text-red-600">{formatPercent(stats.min)}</p>
        </div>
        <div className="text-center">
          <p className="text-gray-500">Mean</p>
          <p className="font-semibold text-gray-700">{formatPercent(stats.mean)}</p>
        </div>
        <div className="text-center">
          <p className="text-gray-500">Max</p>
          <p className="font-semibold text-green-600">{formatPercent(stats.max)}</p>
        </div>
      </div>
    </div>
  );
};

export default StockCard;