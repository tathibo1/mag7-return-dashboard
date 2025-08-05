import { ReturnsResponse, TickerReturn } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const MAG7_SYMBOLS = ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA"];

// Generate business days only (Monday-Friday)
function generateBusinessDays(startDate: string, endDate: string): string[] {
  const dates: string[] = [];
  // Parse dates in local timezone to avoid timezone shifting
  const start = new Date(startDate + 'T00:00:00');
  const end = new Date(endDate + 'T00:00:00');
  
  for (const current = new Date(start); current <= end; current.setDate(current.getDate() + 1)) {
    const dayOfWeek = current.getDay();
    // Skip weekends (0 = Sunday, 6 = Saturday)
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      dates.push(current.toISOString().split('T')[0]);
    }
  }
  
  return dates;
}

export const api = {
  async fetchTickerReturn(ticker: string, date: string): Promise<TickerReturn> {
    try {
      const params = new URLSearchParams({
        ticker,
        date
      });
      
      const response = await fetch(`${API_BASE_URL}/ticker-return?${params}`);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Network error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching return for ${ticker} on ${date}:`, error);
      throw error;
    }
  },

  async fetchReturns(startDate: string, endDate: string): Promise<ReturnsResponse> {
    try {
      const businessDays = generateBusinessDays(startDate, endDate);
      
      // Create all ticker+date combinations for business days only
      const requests: Promise<TickerReturn>[] = [];
      for (const ticker of MAG7_SYMBOLS) {
        for (const date of businessDays) {
          requests.push(this.fetchTickerReturn(ticker, date));
        }
      }
      
      // Fetch all in parallel
      const results = await Promise.all(requests);
      
      // Transform to old format for compatibility
      const data: Record<string, any[]> = {};
      const summary: Record<string, any> = {};
      
      // Initialize data structure
      MAG7_SYMBOLS.forEach(ticker => {
        data[ticker] = [];
        const returns: number[] = [];
        
        // Collect returns for this ticker
        results
          .filter(r => r.ticker === ticker && r.return !== null)
          .forEach(r => {
            if (r.return !== null) {
              data[ticker].push({
                date: r.date,
                return: r.return
              });
              returns.push(r.return);
            }
          });
        
        // Calculate summary stats
        if (returns.length > 0) {
          summary[ticker] = {
            min: Math.min(...returns),
            max: Math.max(...returns),
            mean: returns.reduce((a, b) => a + b, 0) / returns.length
          };
        } else {
          summary[ticker] = { min: 0, max: 0, mean: 0 };
        }
      });
      
      return { data, summary };
    } catch (error) {
      console.error('Error fetching returns:', error);
      throw error;
    }
  }
};