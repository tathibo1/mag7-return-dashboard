import { useState, useEffect } from 'react';
import DatePicker from './components/DatePicker';
import StockGrid from './components/StockGrid';
import SummaryTable from './components/SummaryTable';
import { api } from './services/api';
import { ReturnsResponse } from './types';
import { format, subDays } from 'date-fns';



function App() {
  const defaultEndDate = new Date();
  const [startDate, setStartDate] = useState<Date>(subDays(defaultEndDate, 30));
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
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-100">
          MAG7 Returns
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