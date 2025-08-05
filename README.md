# MAG7 Stock Returns Dashboard

A full-stack application for visualizing daily returns of the MAG7 stocks (Microsoft, Apple, Google, Amazon, Nvidia, Meta, Tesla) using real-time data from Yahoo Finance.

## Features

- Interactive grid layout showing individual stock performance
- Line charts with zoom and tooltip functionality
- Date range picker for custom time periods
- Summary statistics (min, max, mean returns)
- Performance comparison table
- In-memory caching for API optimization
- Responsive design for all devices

## Tech Stack

### Backend
- Python 3.11+
- FastAPI (lightweight version)
- yfinance
- In-memory caching with TTL

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
- `GET /returns?start=YYYY-MM-DD&end=YYYY-MM-DD` - Fetch stock returns for date range

## Project Structure

```
acadia/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── services/
│   │   ├── stock_data.py   # Yahoo Finance integration
│   │   └── cache.py        # Caching implementation
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

TODO:
[ ] use fast api - there's been trouble using yfinance within uvicorn, what the same yf functionality works in a native python server
[ ] use pydantic
[ ] use pandas
[ ] fix chart error where first and last days are not being graphed
[ ] testing
