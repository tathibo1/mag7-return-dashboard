export interface TickerReturn {
  ticker: string;
  date: string;
  return: number | null;
  price?: number;
  previous_price?: number;
  error?: string;
}

export interface ReturnData {
  date: string;
  return: number;
}

export interface StockStats {
  min: number;
  max: number;
  mean: number;
}

export interface ReturnsResponse {
  data: Record<string, ReturnData[]>;
  summary: Record<string, StockStats>;
}