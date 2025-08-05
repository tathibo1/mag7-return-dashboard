import { describe, it, expect } from 'vitest'
import { render, screen } from '../utils'
import SummaryTable from '../../components/SummaryTable'
import { createMockStockStats } from '../utils'

describe('SummaryTable', () => {
  const mockSummary = {
    AAPL: createMockStockStats({ min: -0.02, max: 0.08, mean: 0.03 }),
    MSFT: createMockStockStats({ min: -0.01, max: 0.06, mean: 0.025 }),
    GOOGL: createMockStockStats({ min: -0.015, max: 0.07, mean: 0.028 }),
  }

  it('should render table with correct title', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    expect(screen.getByText('Performance Summary')).toBeInTheDocument()
  })

  it('should render table headers', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    expect(screen.getByText('Symbol')).toBeInTheDocument()
    expect(screen.getByText('Min Return')).toBeInTheDocument()
    expect(screen.getByText('Mean Return')).toBeInTheDocument()
    expect(screen.getByText('Max Return')).toBeInTheDocument()
  })

  it('should render all stock symbols in alphabetical order', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('GOOGL')).toBeInTheDocument()
    expect(screen.getByText('MSFT')).toBeInTheDocument()
    
    // Check order by finding the rows
    const rows = screen.getAllByRole('row')
    // Skip header row (index 0)
    expect(rows[1]).toHaveTextContent('AAPL')
    expect(rows[2]).toHaveTextContent('GOOGL')
    expect(rows[3]).toHaveTextContent('MSFT')
  })

  it('should format percentages correctly with 3 decimal places', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    // AAPL row: min: -0.02 = -2.000%, max: 0.08 = 8.000%, mean: 0.03 = 3.000%
    expect(screen.getByText('-2.000%')).toBeInTheDocument()
    expect(screen.getByText('8.000%')).toBeInTheDocument()
    expect(screen.getByText('3.000%')).toBeInTheDocument()
    
    // MSFT row: min: -0.01 = -1.000%, max: 0.06 = 6.000%, mean: 0.025 = 2.500%
    expect(screen.getByText('-1.000%')).toBeInTheDocument()
    expect(screen.getByText('6.000%')).toBeInTheDocument()
    expect(screen.getByText('2.500%')).toBeInTheDocument()
  })

  it('should apply correct styling to different return types', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    // Min returns should have red styling
    const minReturnCell = screen.getByText('-2.000%')
    expect(minReturnCell).toHaveClass('text-red-400')
    
    // Max returns should have green styling
    const maxReturnCell = screen.getByText('8.000%')
    expect(maxReturnCell).toHaveClass('text-green-400')
    
    // Mean returns should have gray styling
    const meanReturnCell = screen.getByText('3.000%')
    expect(meanReturnCell).toHaveClass('text-gray-300')
  })

  it('should have correct table structure and styling', () => {
    const { container } = render(<SummaryTable summary={mockSummary} />)
    
    // Main container styling
    const mainContainer = container.firstChild as HTMLElement
    expect(mainContainer).toHaveClass('bg-gray-900')
    expect(mainContainer).toHaveClass('rounded-lg')
    expect(mainContainer).toHaveClass('shadow-xl')
    expect(mainContainer).toHaveClass('p-6')
    expect(mainContainer).toHaveClass('mt-6')
    
    // Table should be present
    const table = screen.getByRole('table')
    expect(table).toHaveClass('min-w-full')
    expect(table).toHaveClass('divide-y')
    expect(table).toHaveClass('divide-gray-700')
  })

  it('should have proper table headers styling', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    const headers = screen.getAllByRole('columnheader')
    headers.forEach(header => {
      expect(header).toHaveClass('px-6')
      expect(header).toHaveClass('py-3')
      expect(header).toHaveClass('text-xs')
      expect(header).toHaveClass('font-medium')
      expect(header).toHaveClass('text-gray-300')
      expect(header).toHaveClass('uppercase')
      expect(header).toHaveClass('tracking-wider')
    })
    
    // Symbol header should be left-aligned
    const symbolHeader = screen.getByText('Symbol')
    expect(symbolHeader).toHaveClass('text-left')
    
    // Other headers should be right-aligned
    const returnHeaders = headers.slice(1)
    returnHeaders.forEach(header => {
      expect(header).toHaveClass('text-right')
    })
  })

  it('should have proper row styling', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    const rows = screen.getAllByRole('row')
    // Skip header row
    const dataRows = rows.slice(1)
    
    dataRows.forEach(row => {
      expect(row).toHaveClass('hover:bg-gray-800')
    })
  })

  it('should handle empty summary object', () => {
    render(<SummaryTable summary={{}} />)
    
    expect(screen.getByText('Performance Summary')).toBeInTheDocument()
    expect(screen.getByText('Symbol')).toBeInTheDocument()
    
    // Should only have header row
    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(1) // Only header row
  })

  it('should handle single stock summary', () => {
    const singleStock = {
      AAPL: createMockStockStats({ min: -0.01, max: 0.05, mean: 0.02 }),
    }
    
    render(<SummaryTable summary={singleStock} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('-1.000%')).toBeInTheDocument()
    expect(screen.getByText('5.000%')).toBeInTheDocument()
    expect(screen.getByText('2.000%')).toBeInTheDocument()
    
    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2) // Header + 1 data row
  })


  it('should handle very small decimal values', () => {
    const smallValues = {
      AAPL: createMockStockStats({ 
        min: -0.000123, 
        max: 0.000456, 
        mean: 0.000189 
      }),
    }
    
    render(<SummaryTable summary={smallValues} />)
    
    expect(screen.getByText('-0.012%')).toBeInTheDocument() // -0.000123 * 100 = -0.012%
    expect(screen.getByText('0.046%')).toBeInTheDocument()  // 0.000456 * 100 = 0.046%
    expect(screen.getByText('0.019%')).toBeInTheDocument()  // 0.000189 * 100 = 0.019%
  })

  it('should handle large values correctly', () => {
    const largeValues = {
      AAPL: createMockStockStats({ 
        min: -1.234567, 
        max: 2.345678, 
        mean: 0.555555 
      }),
    }
    
    render(<SummaryTable summary={largeValues} />)
    
    expect(screen.getByText('-123.457%')).toBeInTheDocument() // -1.234567 * 100 = -123.457%
    expect(screen.getByText('234.568%')).toBeInTheDocument()  // 2.345678 * 100 = 234.568%
    expect(screen.getByText('55.556%')).toBeInTheDocument()   // 0.555555 * 100 = 55.556%
  })


  it('should be responsive with horizontal scroll', () => {
    const { container } = render(<SummaryTable summary={mockSummary} />)
    
    const scrollContainer = container.querySelector('.overflow-x-auto')
    expect(scrollContainer).toBeInTheDocument()
  })

  it('should have proper accessibility structure', () => {
    render(<SummaryTable summary={mockSummary} />)
    
    // Should have proper table structure
    const table = screen.getByRole('table')
    expect(table).toBeInTheDocument()
    
    // Should have thead and tbody
    const thead = table.querySelector('thead')
    const tbody = table.querySelector('tbody')
    expect(thead).toBeInTheDocument()
    expect(tbody).toBeInTheDocument()
    
    // Headers should be in thead
    const headers = screen.getAllByRole('columnheader')
    headers.forEach(header => {
      expect(thead).toContainElement(header)
    })
  })

  it('should handle mixed positive and negative values', () => {
    const mixedValues = {
      AAPL: createMockStockStats({ min: -0.05, max: 0.03, mean: -0.01 }),
      MSFT: createMockStockStats({ min: 0.01, max: 0.08, mean: 0.045 }),
    }
    
    render(<SummaryTable summary={mixedValues} />)
    
    // Negative values
    expect(screen.getByText('-5.000%')).toBeInTheDocument()
    expect(screen.getByText('-1.000%')).toBeInTheDocument()
    
    // Positive values
    expect(screen.getByText('3.000%')).toBeInTheDocument()
    expect(screen.getByText('8.000%')).toBeInTheDocument()
    expect(screen.getByText('4.500%')).toBeInTheDocument()
  })
})