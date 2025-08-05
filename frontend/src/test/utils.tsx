import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { vi } from 'vitest'
import { ReturnsResponse, StockStats, ReturnData } from '../types'

// Custom render function that can be extended with providers if needed
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock data generators for tests
export const createMockReturnData = (overrides?: Partial<ReturnData>): ReturnData => ({
  date: '2024-01-02',
  return: 0.05,
  ...overrides,
})

export const createMockStockStats = (overrides?: Partial<StockStats>): StockStats => ({
  min: -0.02,
  max: 0.08,
  mean: 0.03,
  ...overrides,
})

export const createMockReturnsResponse = (overrides?: Partial<ReturnsResponse>): ReturnsResponse => ({
  data: {
    AAPL: [
      createMockReturnData({ date: '2024-01-01', return: 0.02 }),
      createMockReturnData({ date: '2024-01-02', return: 0.05 }),
      createMockReturnData({ date: '2024-01-03', return: -0.01 }),
    ],
    MSFT: [
      createMockReturnData({ date: '2024-01-01', return: 0.01 }),
      createMockReturnData({ date: '2024-01-02', return: 0.03 }),
      createMockReturnData({ date: '2024-01-03', return: 0.02 }),
    ],
  },
  summary: {
    AAPL: createMockStockStats({ min: -0.01, max: 0.05, mean: 0.02 }),
    MSFT: createMockStockStats({ min: 0.01, max: 0.03, mean: 0.02 }),
  },
  ...overrides,
})

// Helper to wait for async operations
export const waitFor = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms))

// Mock fetch helper
export const mockFetch = (response: any, ok = true) => {
  global.fetch = vi.fn().mockResolvedValue({
    ok,
    json: async () => response,
  })
}

// Mock fetch with error
export const mockFetchError = (error: string) => {
  global.fetch = vi.fn().mockRejectedValue(new Error(error))
}

// Date helpers for consistent test dates
export const TEST_DATES = {
  start: new Date('2024-01-01'),
  end: new Date('2024-01-31'),
  today: new Date('2024-01-31'),
} as const

// Format date for API calls (YYYY-MM-DD)
export const formatDateForAPI = (date: Date): string => {
  return date.toISOString().split('T')[0]
}