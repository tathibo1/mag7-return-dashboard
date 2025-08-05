from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
import logging

from services.stock_data import StockDataService
from services.cache import cache_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MAG7 Stock Returns API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/returns")
async def get_returns(
    start: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end: str = Query(..., description="End date in YYYY-MM-DD format")
):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if end_date > date.today():
        raise HTTPException(status_code=400, detail="End date cannot be in the future")
    
    cached_data = cache_instance.get(start, end)
    if cached_data:
        logger.info(f"Cache hit for {start} to {end}")
        return cached_data
    
    logger.info(f"Cache miss for {start} to {end}, fetching data...")
    
    try:
        # Try batch download first for better reliability
        data = StockDataService.fetch_returns_batch(start, end)
        cache_instance.set(start, end, data)
        return data
    except Exception as e:
        logger.error(f"Error fetching returns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")


if __name__ == "__main__":
    import socketserver
    import http.server
    import json
    from urllib.parse import urlparse, parse_qs
    
    class SimpleAPIHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)
            
            try:
                if path == "/health":
                    response = {"status": "healthy"}
                elif path == "/returns":
                    start = query.get('start', [None])[0]
                    end = query.get('end', [None])[0]
                    
                    if not start or not end:
                        response = {"detail": "start and end parameters are required"}
                        status = 400
                    else:
                        from services.stock_data import StockDataService
                        response = StockDataService.fetch_returns(start, end)
                        status = 200
                else:
                    response = {"detail": "Not found"}
                    status = 404
                
                self.send_response(status if 'status' in locals() else 200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"detail": f"Error fetching stock data: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
    
    print("API server starting on http://0.0.0.0:8000")
    with socketserver.TCPServer(("", 8000), SimpleAPIHandler) as httpd:
        httpd.serve_forever()