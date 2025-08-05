# MAG7 Stock Returns Dashboard

A full-stack application for visualizing daily returns of the MAG7 stocks (Microsoft, Apple, Google, Amazon, Nvidia, Meta, Tesla) using real-time data from Yahoo Finance.

## Features

- Interactive grid layout showing individual stock performance
- Line charts with zoom and tooltip functionality
- Date range picker for custom time periods
- Summary statistics (min, max, mean returns)
- Performance comparison table
- Granular ticker+date caching with LRU eviction
- Parallel data fetching for improved performance
- Responsive design for all devices

## Tech Stack

### Backend
- Python 3.11+
- FastAPI with Uvicorn ASGI server
- yfinance for real-time stock data
- cachetools for LRU+TTL caching
- Thread pool executor for parallel data fetching

### Frontend
- React 18
- TypeScript
- Vite for lightning-fast dev server
- Recharts for data visualization
- Tailwind CSS for styling

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Local Development

Simply run:
```bash
make dev
```

This single command will:
- Set up virtual environment and install all dependencies (if needed)
- Start both backend and frontend servers
- Open the app in your browser at http://localhost:3000

**Manual installation (if preferred):**
```bash
make install  # Install all dependencies first
make dev      # Then run the services
```

The frontend will be available at http://localhost:3000 and the backend API at http://localhost:8000

### Using Docker

1. Build and run with Docker Compose:
```bash
make build
make up
```

2. View logs:
```bash
make logs
```

3. Stop containers:
```bash
make down
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /ticker-return?ticker=SYMBOL&date=YYYY-MM-DD` - Fetch daily return for a specific stock
  - Returns: `{ ticker, date, return, price, previous_price }`
  - Cached per ticker+date combination
  - Handles non-trading days automatically

## Project Structure

```
acadia/
├── backend/
│   ├── app.py              # FastAPI application with Uvicorn
│   ├── services/
│   │   ├── stock_data.py   # Yahoo Finance integration with parallel fetching
│   │   └── cache.py        # TTL+LRU caching with cachetools
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   ├── index.html          # Entry point
│   ├── package.json
│   └── vite.config.ts      # Vite configuration
├── docker-compose.yml
└── Makefile                # Build automation
```

## Performance Features

- **Parallel Fetching**: All MAG7 stocks are fetched concurrently using a thread pool
- **Smart Caching**: Each ticker+date combination is cached individually (1-hour TTL, 1000 entry limit)
- **Business Day Filtering**: Frontend automatically skips weekends to reduce unnecessary API calls
- **Thread Pool Isolation**: Fixes yfinance HTTP session conflicts with uvicorn's async event loop

TODO:
[ ] use pydantic
[ ] use pandas
[ ] fix chart error where first and last days are not being graphed
[ ] testing
[ ] set default end date to today on fe
[ ] set default start date to end-30 days
