from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
import httpx
import os

router = APIRouter(tags=["lastfm"])

@router.get("/lastfm", response_class=PlainTextResponse)
async def get_lastfm_info(user: str = Query("dj", description="Last.fm username")):
    """
    Get user's currently playing track from Last.fm.
    
    StreamElements: add this text in "Response type" field:\n
    ${customapi.https://tbc-rksp.onrender.com/lastfm?user=your_username}
    
    Chat example: !track
    """
    api_key = os.getenv("LASTFM_API_KEY")
    
    if not api_key:
        return "API key not configured"
    
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": user,
        "api_key": api_key,
        "format": "json",
        "limit": 1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            data = response.json()
            
            if "error" in data:
                return f"User '{user}' not found"
            
            tracks = data.get("recenttracks", {}).get("track", [])
            if not tracks:
                return f"User hasn't played anything yet"
            
            track = tracks[0] if isinstance(tracks, list) else tracks
            artist = track["artist"]["#text"]
            song = track["name"]
            
            # Проверяем, что сейчас что-нибудь играет
            now_playing = "@attr" in track and "nowplaying" in track["@attr"]
            
            if now_playing:
                return f"{artist} - {song}"
            else:
                return f"Nothing is playing right now"
    
    except httpx.TimeoutException:
        return "Service temporarily unavailable"
    except Exception:
        return "Service temporarily unavailable"