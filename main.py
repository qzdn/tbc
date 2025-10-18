from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from commands import lastfm, weather, hltb
from dotenv import load_dotenv
import httpx
import uvicorn

load_dotenv()
app = FastAPI(title="Twitch bot commands")

app.include_router(lastfm.router)
app.include_router(weather.router)
app.include_router(hltb.router)

@app.get("/", response_class=PlainTextResponse)
async def root():
    return f"Check /docs for info"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)