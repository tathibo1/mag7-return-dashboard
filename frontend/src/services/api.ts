import { ReturnsResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async fetchReturns(startDate: string, endDate: string): Promise<ReturnsResponse> {
    try {
      const params = new URLSearchParams({
        start: startDate,
        end: endDate
      });
      
      const response = await fetch(`${API_BASE_URL}/returns?${params}`);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Network error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching returns:', error);
      throw error;
    }
  }
};