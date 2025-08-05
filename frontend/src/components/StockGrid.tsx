import React from 'react';
import StockCard from './StockCard';
import { ReturnsResponse } from '../types';

interface StockGridProps {
  data: ReturnsResponse | null;
  loading: boolean;
  error: string | null;
}

const StockGrid: React.FC<StockGridProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-300">Loading stock data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-400">Error: {error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-300">No data to display</div>
      </div>
    );
  }

  const symbols = Object.keys(data.data);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {symbols.map((symbol) => (
        <StockCard
          key={symbol}
          symbol={symbol}
          data={data.data[symbol]}
          stats={data.summary[symbol]}
        />
      ))}
    </div>
  );
};

export default StockGrid;