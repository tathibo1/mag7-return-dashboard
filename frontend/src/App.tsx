import React, { useState, useEffect } from 'react';
import DatePicker from './components/DatePicker';
import StockGrid from './components/StockGrid';
import SummaryTable from './components/SummaryTable';
import { api } from './services/api';
import { ReturnsResponse } from './types';
import { format, subMonths, subDays } from 'date-fns';

function getPreviousBusinessDay(): Date {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
  
  // If today is Monday (1), go back 3 days to Friday
  // If today is Sunday (0), go back 2 days to Friday
  // Otherwise, go back 1 day
  let daysToSubtract = 1;
  if (dayOfWeek === 1) { // Monday
    daysToSubtract = 3;
  } else if (dayOfWeek === 0) { // Sunday
    daysToSubtract = 2;
  }
  
  return subDays(today, daysToSubtract);
}

function subtractBusinessDays(date: Date, businessDays: number): Date {
  let currentDate = new Date(date);
  let daysSubtracted = 0;
  
  while (daysSubtracted < businessDays) {
    currentDate = subDays(currentDate, 1);
    const dayOfWeek = currentDate.getDay();
    // Count only weekdays (Monday=1 to Friday=5)
    if (dayOfWeek >= 1 && dayOfWeek <= 5) {
      daysSubtracted++;
    }
  }
  
  return currentDate;
}

function App() {
  const defaultEndDate = getPreviousBusinessDay();
  const [startDate, setStartDate] = useState<Date>(subtractBusinessDays(defaultEndDate, 4));
  const [endDate, setEndDate] = useState<Date>(defaultEndDate);
  const [data, setData] = useState<ReturnsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const startStr = format(startDate, 'yyyy-MM-dd');
      const endStr = format(endDate, 'yyyy-MM-dd');
      
      const response = await api.fetchReturns(startStr, endStr);
      setData(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          MAG7 Stock Returns Dashboard
        </h1>
        
        <DatePicker
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onFetchData={fetchData}
        />
        
        <StockGrid data={data} loading={loading} error={error} />
        
        {data && data.summary && Object.keys(data.summary).length > 0 && (
          <SummaryTable summary={data.summary} />
        )}
      </div>
    </div>
  );
}

export default App;