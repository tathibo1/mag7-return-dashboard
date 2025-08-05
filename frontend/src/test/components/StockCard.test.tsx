import { describe, it, expect } from 'vitest'
import { render, screen } from '../utils'
import StockCard from '../../components/StockCard'
import { createMockReturnData, createMockStockStats } from '../utils'

describe('StockCard', () => {
  const mockData = [
    createMockReturnData({ date: '2024-01-01', return: 0.02 }),
    createMockReturnData({ date: '2024-01-02', return: 0.05 }),
    createMockReturnData({ date: '2024-01-03', return: -0.01 }),
  ]

  const mockStats = createMockStockStats({
    min: -0.01,
    max: 0.05,
    mean: 0.02,
  })

  it('should render stock symbol', () => {
    render(<StockCard symbol="AAPL" data={mockData} stats={mockStats} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
  })

  it('should display statistics correctly formatted', () => {
    render(<StockCard symbol="AAPL" data={mockData} stats={mockStats} />)
    
    expect(screen.getByText('Max:')).toBeInTheDocument()
    expect(screen.getByText('5.00%')).toBeInTheDocument() // max: 0.05 * 100 = 5.00%
    
    expect(screen.getByText('Mean:')).toBeInTheDocument()
    expect(screen.getByText('2.00%')).toBeInTheDocument() // mean: 0.02 * 100 = 2.00%
    
    expect(screen.getByText('Min:')).toBeInTheDocument()
    expect(screen.getByText('-1.00%')).toBeInTheDocument() // min: -0.01 * 100 = -1.00%
  })

  it('should handle empty data gracefully', () => {
    render(<StockCard symbol="AAPL" data={[]} stats={mockStats} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('Max:')).toBeInTheDocument()
  })

  it('should handle negative returns with correct formatting', () => {
    const negativeStats = createMockStockStats({
      min: -0.15,
      max: -0.05,
      mean: -0.10,
    })
    
    render(<StockCard symbol="AAPL" data={mockData} stats={negativeStats} />)
    
    expect(screen.getByText('-15.00%')).toBeInTheDocument() // min
    expect(screen.getByText('-5.00%')).toBeInTheDocument()  // max
    expect(screen.getByText('-10.00%')).toBeInTheDocument() // mean
  })
})