import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '../utils'
import userEvent from '@testing-library/user-event'
import DatePicker from '../../components/DatePicker'
import { TEST_DATES } from '../utils'

describe('DatePicker', () => {
  const mockOnStartDateChange = vi.fn()
  const mockOnEndDateChange = vi.fn()
  const mockOnFetchData = vi.fn()

  const defaultProps = {
    startDate: TEST_DATES.start,
    endDate: TEST_DATES.end,
    onStartDateChange: mockOnStartDateChange,
    onEndDateChange: mockOnEndDateChange,
    onFetchData: mockOnFetchData,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render start and end date inputs', () => {
    render(<DatePicker {...defaultProps} />)
    
    const inputs = screen.getAllByRole('textbox')
    expect(inputs).toHaveLength(2)
    
    // Check for labels (without colon since actual text is "Start Date")
    expect(screen.getByText('Start Date')).toBeInTheDocument()
    expect(screen.getByText('End Date')).toBeInTheDocument()
  })

  it('should render fetch button', () => {
    render(<DatePicker {...defaultProps} />)
    
    const fetchButton = screen.getByRole('button', { name: /fetch data/i })
    expect(fetchButton).toBeInTheDocument()
  })

  it('should call onFetchData when fetch button is clicked', async () => {
    const user = userEvent.setup()
    render(<DatePicker {...defaultProps} />)
    
    const fetchButton = screen.getByRole('button', { name: /fetch data/i })
    await user.click(fetchButton)
    
    expect(mockOnFetchData).toHaveBeenCalledTimes(1)
  })

  it('should call onStartDateChange when start date is changed', async () => {
    const user = userEvent.setup()
    render(<DatePicker {...defaultProps} />)
    
    const startDateInput = screen.getAllByRole('textbox')[0]
    await user.clear(startDateInput)
    await user.type(startDateInput, '2024-02-01')
    
    // The exact behavior depends on react-datepicker implementation
    // We're testing that the callback is set up correctly
    expect(mockOnStartDateChange).toHaveBeenCalled()
  })

  it('should call onEndDateChange when end date is changed', async () => {
    const user = userEvent.setup()
    render(<DatePicker {...defaultProps} />)
    
    const endDateInput = screen.getAllByRole('textbox')[1]
    await user.clear(endDateInput)
    await user.type(endDateInput, '2024-02-28')
    
    expect(mockOnEndDateChange).toHaveBeenCalled()
  })

  it('should have fetch button with correct styling', () => {
    render(<DatePicker {...defaultProps} />)
    
    const fetchButton = screen.getByRole('button', { name: /fetch data/i })
    expect(fetchButton).toHaveClass('bg-gray-800')
    expect(fetchButton).toHaveClass('text-white')
  })

  it('should render in dark theme styling', () => {
    render(<DatePicker {...defaultProps} />)
    
    const inputs = screen.getAllByRole('textbox')
    inputs.forEach(input => {
      expect(input).toHaveClass('bg-gray-800')
      expect(input).toHaveClass('text-gray-100')
    })
  })

  it('should handle rapid clicks on fetch button', async () => {
    const user = userEvent.setup()
    render(<DatePicker {...defaultProps} />)
    
    const fetchButton = screen.getByRole('button', { name: /fetch data/i })
    
    // Simulate rapid clicks
    await user.click(fetchButton)
    await user.click(fetchButton)
    await user.click(fetchButton)
    
    expect(mockOnFetchData).toHaveBeenCalledTimes(3)
  })
})