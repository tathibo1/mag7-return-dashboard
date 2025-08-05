import React from 'react';
import ReactDatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

interface DatePickerProps {
  startDate: Date;
  endDate: Date;
  onStartDateChange: (date: Date) => void;
  onEndDateChange: (date: Date) => void;
  onFetchData: () => void;
}

const DatePicker: React.FC<DatePickerProps> = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onFetchData
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Select Date Range</h2>
      <div className="flex flex-col md:flex-row gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Start Date
          </label>
          <ReactDatePicker
            selected={startDate}
            onChange={onStartDateChange}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            maxDate={new Date()}
            dateFormat="yyyy-MM-dd"
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            End Date
          </label>
          <ReactDatePicker
            selected={endDate}
            onChange={onEndDateChange}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            maxDate={new Date()}
            dateFormat="yyyy-MM-dd"
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <button
          onClick={onFetchData}
          className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          Fetch Data
        </button>
      </div>
    </div>
  );
};

export default DatePicker;