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
    <div className="bg-transparent mb-6">
      <div className="flex flex-col md:flex-row gap-4 items-end justify-center">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
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
            className="px-3 py-2 border border-gray-700 bg-gray-800 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
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
            className="px-3 py-2 border border-gray-700 bg-gray-800 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        
        <button
          onClick={onFetchData}
          className="px-6 py-2 bg-gray-800 text-white font-medium rounded-md hover:bg-gray-700 transition-colors"
        >
          Fetch Data
        </button>
      </div>
    </div>
  );
};

export default DatePicker;