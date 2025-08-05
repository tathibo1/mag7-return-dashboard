import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api } from '../../services/api'
import { mockFetch, mockFetchError } from '../utils'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('fetchTickerReturn', () => {
    it('should fetch ticker return successfully', async () => {
      const mockResponse = {
        ticker: 'AAPL',
        date: '2024-01-02',
        return: 0.05,
        price: 150.0,
        previous_price: 142.86,
      }

      mockFetch(mockResponse)

      const result = await api.fetchTickerReturn('AAPL', '2024-01-02')

      expect(result).toEqual(mockResponse)
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/ticker-return?ticker=AAPL&date=2024-01-02'
      )
    })

    it('should handle network errors', async () => {
      mockFetchError('Network error')

      await expect(api.fetchTickerReturn('AAPL', '2024-01-02')).rejects.toThrow('Network error')
    })

    it('should handle HTTP errors with JSON response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      })

      await expect(api.fetchTickerReturn('AAPL', '2024-01-02')).rejects.toThrow('Not found')
    })


    it('should construct correct URL with parameters', async () => {
      const mockResponse = { ticker: 'MSFT', date: '2024-01-15', return: 0.03 }
      mockFetch(mockResponse)

      await api.fetchTickerReturn('MSFT', '2024-01-15')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/ticker-return?ticker=MSFT&date=2024-01-15'
      )
    })
  })

  describe('fetchReturns', () => {
    it('should fetch returns for date range successfully', async () => {
      const mockTickerResponse = {
        ticker: 'AAPL',
        date: '2024-01-01',
        return: 0.02,
      }

      mockFetch(mockTickerResponse)

      const result = await api.fetchReturns('2024-01-01', '2024-01-01')

      expect(result).toHaveProperty('data')
      expect(result).toHaveProperty('summary')
      expect(result.data).toHaveProperty('AAPL')
      expect(result.data).toHaveProperty('MSFT')
      expect(result.data).toHaveProperty('GOOGL')
      expect(result.data).toHaveProperty('AMZN')
      expect(result.data).toHaveProperty('NVDA')
      expect(result.data).toHaveProperty('META')
      expect(result.data).toHaveProperty('TSLA')
    })

    it('should generate business days correctly', async () => {
      const mockTickerResponse = { ticker: 'AAPL', date: '2024-01-01', return: 0.02 }
      mockFetch(mockTickerResponse)

      // Test Monday to Friday (should include all 5 days)
      await api.fetchReturns('2024-01-01', '2024-01-05')

      // Should make calls for 5 business days × 7 tickers = 35 calls
      expect(fetch).toHaveBeenCalledTimes(35)
    })

    it('should skip weekends in business days', async () => {
      const mockTickerResponse = { ticker: 'AAPL', date: '2024-01-01', return: 0.02 }
      mockFetch(mockTickerResponse)

      // Test range that includes a weekend (Jan 6-7, 2024 are Saturday-Sunday)
      await api.fetchReturns('2024-01-05', '2024-01-08')

      // Should make calls for 2 business days (Jan 5, 8) × 7 tickers = 14 calls
      expect(fetch).toHaveBeenCalledTimes(14)

      // Verify no weekend calls were made
      const calls = (fetch as any).mock.calls
      const weekendCalls = calls.filter((call: any[]) => 
        call[0].includes('2024-01-06') || call[0].includes('2024-01-07')
      )
      expect(weekendCalls).toHaveLength(0)
    })

    it('should calculate summary statistics correctly', async () => {
      // Mock responses with known values
      const responses = [
        { ticker: 'AAPL', date: '2024-01-01', return: 0.02 },
        { ticker: 'AAPL', date: '2024-01-02', return: 0.05 },
        { ticker: 'AAPL', date: '2024-01-03', return: -0.01 },
      ]

      let callCount = 0
      global.fetch = vi.fn()
        .mockImplementation(() => {
          const response = responses[callCount % responses.length]
          callCount++
          return Promise.resolve({
            ok: true,
            json: async () => response,
          })
        })

      const result = await api.fetchReturns('2024-01-01', '2024-01-03')

      expect(result.summary.AAPL).toEqual({
        min: -0.01,
        max: 0.05,
        mean: 0.02, // (0.02 + 0.05 + -0.01) / 3 = 0.02
      })
    })

    it('should handle mixed successful and failed responses', async () => {
      let callCount = 0
      global.fetch = vi.fn()
        .mockImplementation(() => {
          callCount++
          if (callCount % 2 === 0) {
            // Every other call fails
            return Promise.resolve({
              ok: true,
              json: async () => ({ ticker: 'AAPL', date: '2024-01-01', return: null }),
            })
          }
          return Promise.resolve({
            ok: true,
            json: async () => ({ ticker: 'AAPL', date: '2024-01-01', return: 0.02 }),
          })
        })

      const result = await api.fetchReturns('2024-01-01', '2024-01-01')

      // Should still return a valid structure
      expect(result).toHaveProperty('data')
      expect(result).toHaveProperty('summary')
    })

    it('should handle all null returns for a ticker', async () => {
      mockFetch({ ticker: 'AAPL', date: '2024-01-01', return: null })

      const result = await api.fetchReturns('2024-01-01', '2024-01-01')

      // Should return zero stats for tickers with no valid returns
      expect(result.summary.AAPL).toEqual({
        min: 0,
        max: 0,
        mean: 0,
      })
    })



    it('should handle network failures gracefully', async () => {
      mockFetchError('Network connection failed')

      await expect(api.fetchReturns('2024-01-01', '2024-01-01')).rejects.toThrow(
        'Network connection failed'
      )
    })
  })

})