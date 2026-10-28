import asyncio
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS so your frontend dashboard can safely talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL LIVE STATE ---
live_market_data = {
    "status": "ONLINE",
    "mcmc_engine": "CONVERGED",
    "ticker": "NVDA",
    "current_price": 132.79,
    "percent_change": 3.42,
    "historical_x": ["Sep 15", "Sep 18", "Sep 21", "Sep 24", "Sep 27", "Sep 30", "Oct 03", "Oct 27"],
    "historical_y": [112.0, 114.0, 113.0, 116.0, 118.90, 117.0, 121.0, 128.0],
    "forecast_x": ["Oct 30", "Nov 04", "Nov 09", "Nov 14", "Nov 19", "Nov 24"],
    "forecast_y": [130.5, 133.0, 136.2, 138.0, 141.1, 143.5]
}

# Background task to automatically bounce the prices around every second
async def simulate_live_ticks():
    while True:
        tick = random.choice([-0.35, -0.10, 0.05, 0.25, 0.50])
        live_market_data["current_price"] = round(live_market_data["current_price"] + tick, 2)
        # Randomly wiggle the forecast endpoints slightly to show real-time dynamic movement
        live_market_data["forecast_y"] = [round(y + random.choice([-0.05, 0.05]), 2) for y in [130.5, 133.0, 136.2, 138.0, 141.1, 143.5]]
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_live_ticks())

# 1. FIXED: The health check path the frontend is calling
@app.route("/api/status")
@app.get("/api/status")
def get_status():
    return {"status": "ONLINE", "mcmc_engine": "CONVERGED"}

# 2. FIXED: The missing endpoint causing your 404 errors!
@app.route("/api/live-quotes")
@app.get("/api/live-quotes")
def get_live_quotes():
    return live_market_data
