import { describe, it, expect } from 'vitest'
import { render, screen } from '../utils'
import StockGrid from '../../components/StockGrid'
import { createMockReturnsResponse } from '../utils'

describe('StockGrid', () => {
  it('should display loading state', () => {
    render(<StockGrid data={null} loading={true} error={null} />)
    
    expect(screen.getByText('Loading stock data...')).toBeInTheDocument()
  })

  it('should display error state', () => {
    const errorMessage = 'Failed to fetch data'
    render(<StockGrid data={null} loading={false} error={errorMessage} />)
    
    expect(screen.getByText(`Error: ${errorMessage}`)).toBeInTheDocument()
  })

  it('should display no data message when data is null', () => {
    render(<StockGrid data={null} loading={false} error={null} />)
    
    expect(screen.getByText('No data to display')).toBeInTheDocument()
  })

  it('should render stock cards when data is provided', () => {
    const mockData = createMockReturnsResponse()
    render(<StockGrid data={mockData} loading={false} error={null} />)
    
    // Should render cards for AAPL and MSFT (from mock data)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('MSFT')).toBeInTheDocument()
  })

  it('should have correct layout styling', () => {
    const mockData = createMockReturnsResponse()
    const { container } = render(<StockGrid data={mockData} loading={false} error={null} />)
    
    const gridContainer = container.firstChild as HTMLElement
    expect(gridContainer).toHaveClass('flex')
    expect(gridContainer).toHaveClass('flex-col')
    expect(gridContainer).toHaveClass('gap-4')
  })

  it('should handle empty data object', () => {
    const emptyData = createMockReturnsResponse({
      data: {},
      summary: {},
    })
    
    render(<StockGrid data={emptyData} loading={false} error={null} />)
    
    // Should not crash, though no stock cards will be rendered
    const stockCards = screen.queryAllByText(/AAPL|MSFT|GOOGL|AMZN|NVDA|META|TSLA/)
    expect(stockCards).toHaveLength(0)
  })
})