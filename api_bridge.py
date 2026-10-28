"""
QuantPulse AI - Backend API Bridge
Connects Machine Learning / Time Series Models to the Frontend Interface
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import math

class StockAPIHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Endpoint 1: Health check
        if path == '/api/status':
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "ONLINE",
                "engine": "Bayesian MCMC Stan / Prophet",
                "latency_ms": 14.2
            }).encode('utf-8'))
            return

        # Endpoint 2: Get Prediction & Trends for a Ticker
        # e.g. GET /api/predict?ticker=NVDA&horizon=1M
        if path == '/api/predict':
            ticker = query.get('ticker', ['NVDA'])[0].upper()
            horizon = query.get('horizon', ['1M'])[0]
            
            response_data = self.generate_prediction(ticker, horizon)
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        # Endpoint 3: Get News Sentiment Score & Feed
        # e.g. GET /api/sentiment?ticker=NVDA
        if path == '/api/sentiment':
            ticker = query.get('ticker', ['NVDA'])[0].upper()
            sentiment_data = self.generate_sentiment(ticker)
            self._set_headers(200)
            self.wfile.write(json.dumps(sentiment_data).encode('utf-8'))
            return

        # Fallback 404
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": f"Endpoint '{path}' not found."}).encode('utf-8'))

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        # Endpoint: Custom Data Ingestion & Trend Prediction
        # Accepts custom prices / CSV rows and outputs trend predictions & cones
        if path == '/api/custom-predict':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                prices = payload.get('prices', [])
                dates = payload.get('dates', [])
                ticker = payload.get('ticker', 'CUSTOM')

                if len(prices) < 3:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Provide at least 3 historical price points."}).encode('utf-8'))
                    return

                result = self.compute_custom_trend(ticker, dates, prices)
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": f"Endpoint '{path}' not found."}).encode('utf-8'))

    # --------------------------------------------------------------------------
    # MODEL INFERENCE FUNCTIONS (Replace or connect with your ML functions here)
    # --------------------------------------------------------------------------
    def generate_prediction(self, ticker, horizon):
        """Generates trend forecast, uncertainty cones, changepoints, and metrics."""
        base_quotes = {
            'NVDA': {'price': 128.40, 'change': '+3.42%', 'isPos': True, 'vol': '48.2M', 'vwap': '$126.92'},
            'TSLA': {'price': 254.30, 'change': '+4.12%', 'isPos': True, 'vol': '62.4M', 'vwap': '$251.10'},
            'SPY':  {'price': 545.20, 'change': '+0.34%', 'isPos': True, 'vol': '54.1M', 'vwap': '$544.15'},
            'AAPL': {'price': 214.15, 'change': '-0.38%', 'isPos': False, 'vol': '41.8M', 'vwap': '$215.30'},
            'SENSEX': {'price': 80450.20, 'change': '+0.72%', 'isPos': True, 'vol': '18.4M', 'vwap': '80,210.00'}
        }
        quote = base_quotes.get(ticker, {'price': 100.0, 'change': '+1.0%', 'isPos': True, 'vol': '10M', 'vwap': '$99.50'})
        price = quote['price']

        # Horizon scaling factor for variance cone
        horizon_factors = {'1D': 0.2, '5D': 0.5, '1M': 1.0, '3M': 1.8, '1Y': 2.5}
        h_mult = horizon_factors.get(horizon, 1.0)

        # 6 forecast steps
        forecast = [round(price * (1 + 0.018 * i), 2) for i in range(1, 7)]
        upper_bound = [round(f + (price * 0.04 * math.sqrt(i) * h_mult), 2) for i, f in enumerate(forecast, 1)]
        lower_bound = [round(f - (price * 0.035 * math.sqrt(i) * h_mult), 2) for i, f in enumerate(forecast, 1)]

        return {
            "ticker": ticker,
            "horizon": horizon,
            "current_price": price,
            "change_pct": quote['change'],
            "is_positive": quote['isPos'],
            "volume": quote['vol'],
            "vwap": quote['vwap'],
            "changepoints_detected": 24,
            "model_fit_r2": 0.942,
            "expected_return": "+14.2%",
            "alpha_signal": "STRONG BUY",
            "forecast_dates": ["T+1", "T+5", "T+10", "T+15", "T+20", "T+30"],
            "forecast_prices": forecast,
            "upper_95_bound": upper_bound,
            "lower_95_bound": lower_bound
        }

    def generate_sentiment(self, ticker):
        """Generates NLP polarity extraction and live feed items."""
        return {
            "ticker": ticker,
            "composite_sentiment_score": 0.76, # -1.00 (Extreme Fear) to +1.00 (Greed)
            "sentiment_label": "+78% BULLISH",
            "meter_position_pct": 88, # 0% to 100% on the gauge
            "news_items": [
                {
                    "headline": f"{ticker} deployment schedules accelerate with hyper-scale cloud infrastructure.",
                    "source": "BLOOMBERG",
                    "time": "2m ago",
                    "ticker": ticker,
                    "sentiment": "+0.88 Bullish"
                },
                {
                    "headline": "Macro liquidity tailwinds support continued institutional accumulation.",
                    "source": "REUTERS",
                    "time": "7m ago",
                    "ticker": ticker,
                    "sentiment": "+0.62 Bullish"
                }
            ]
        }

    def compute_custom_trend(self, ticker, dates, prices):
        """Statistical trend computation for custom entered data."""
        n = len(prices)
        sum_x = sum(range(n))
        sum_y = sum(prices)
        sum_xy = sum(i * p for i, p in enumerate(prices))
        sum_x2 = sum(i * i for i in range(n))
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if n > 1 else 0

        mean = sum_y / n
        variance = sum((p - mean) ** 2 for p in prices) / n
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        last_p = prices[-1]
        future_forecast = [round(last_p + slope * i * 1.5, 2) for i in range(1, 7)]
        upper_bound = [round(f + std_dev * 0.8 * math.sqrt(i), 2) for i, f in enumerate(future_forecast, 1)]
        lower_bound = [round(f - std_dev * 0.8 * math.sqrt(i), 2) for i, f in enumerate(future_forecast, 1)]

        return {
            "ticker": ticker,
            "historical_dates": dates,
            "historical_prices": prices,
            "forecast_prices": future_forecast,
            "upper_95_bound": upper_bound,
            "lower_95_bound": lower_bound,
            "slope": round(slope, 4),
            "expected_return": f"{round(((future_forecast[-1] - last_p) / last_p) * 100, 1)}%",
            "alpha_signal": "BUY" if slope > 0 else "HOLD / TRIM"
        }

def run_server(port=8001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, StockAPIHandler)
    print("=" * 60)
    print(f"🚀 QuantPulse AI Backend API Bridge Running on port {port}")
    print(f"👉 API Endpoints Available:")
    print(f"   - GET  http://localhost:{port}/api/status")
    print(f"   - GET  http://localhost:{port}/api/predict?ticker=NVDA&horizon=1M")
    print(f"   - GET  http://localhost:{port}/api/sentiment?ticker=NVDA")
    print(f"   - POST http://localhost:{port}/api/custom-predict")
    print("=" * 60)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server(8001)
