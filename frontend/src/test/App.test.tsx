import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from './utils'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { mockFetch, mockFetchError, createMockReturnsResponse } from './utils'

// Mock the api module
vi.mock('../services/api', () => ({
  api: {
    fetchReturns: vi.fn(),
  },
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render main heading', () => {
    render(<App />)
    
    expect(screen.getByText('MAG7 Returns')).toBeInTheDocument()
  })

  it('should render StockGrid component', () => {
    render(<App />)
    
    // Should start with loading state
    expect(screen.getByText('Loading stock data...')).toBeInTheDocument()
  })

  it('should display error when fetch fails', async () => {
    const { api } = await import('../services/api')
    const errorMessage = 'Network error'
    
    ;(api.fetchReturns as any).mockRejectedValue(new Error(errorMessage))
    
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText(`Error: ${errorMessage}`)).toBeInTheDocument()
    })
  })

  it('should handle API error with response data', async () => {
    const { api } = await import('../services/api')
    const error = {
      response: {
        data: {
          detail: 'Invalid date range'
        }
      }
    }
    
    ;(api.fetchReturns as any).mockRejectedValue(error)
    
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Error: Invalid date range')).toBeInTheDocument()
    })
  })

  it('should have correct page structure and styling', () => {
    const { container } = render(<App />)
    
    const mainContainer = container.firstChild as HTMLElement
    expect(mainContainer).toHaveClass('min-h-screen')
    expect(mainContainer).toHaveClass('bg-gray-900')
    
    const contentContainer = mainContainer.firstChild as HTMLElement
    expect(contentContainer).toHaveClass('container')
    expect(contentContainer).toHaveClass('mx-auto')
    expect(contentContainer).toHaveClass('px-4')
    expect(contentContainer).toHaveClass('py-8')
  })

  it('should have properly styled heading', () => {
    render(<App />)
    
    const heading = screen.getByText('MAG7 Returns')
    expect(heading).toHaveClass('text-4xl')
    expect(heading).toHaveClass('font-bold')
    expect(heading).toHaveClass('text-center')
    expect(heading).toHaveClass('mb-8')
    expect(heading).toHaveClass('text-gray-100')
  })
})