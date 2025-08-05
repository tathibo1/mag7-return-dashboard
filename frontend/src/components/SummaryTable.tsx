import React from 'react';
import { StockStats } from '../types';

interface SummaryTableProps {
  summary: Record<string, StockStats>;
}

const SummaryTable: React.FC<SummaryTableProps> = ({ summary }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(3)}%`;
  
  const symbols = Object.keys(summary).sort();

  return (
    <div className="bg-gray-900 rounded-lg shadow-xl p-6 mt-6 border border-gray-800">
      <h2 className="text-2xl font-bold mb-4 text-gray-100">Performance Summary</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                Min Return
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                Mean Return
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                Max Return
              </th>
            </tr>
          </thead>
          <tbody className="bg-gray-900 divide-y divide-gray-800">
            {symbols.map((symbol) => (
              <tr key={symbol} className="hover:bg-gray-800">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">
                  {symbol}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-400">
                  {formatPercent(summary[symbol].min)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-300">
                  {formatPercent(summary[symbol].mean)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-400">
                  {formatPercent(summary[symbol].max)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SummaryTable;