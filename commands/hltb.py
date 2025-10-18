from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
import urllib.parse
import re
from typing import Optional, Tuple
from howlongtobeatpy import HowLongToBeat

router = APIRouter(tags=["hltb"])


def _format_time(hours: float) -> str:
    """Format hours to readable string"""
    if hours <= 0:
        return "N/A"
    if hours < 1:
        return f"{int(hours * 60)}m"
    return f"{hours:.1f}h"


def _extract_year_from_query(game: str) -> Tuple[str, Optional[int]]:
    """
    Extract year from game query if specified with ** separator.
    Returns: (game_name, year or None)
    
    Examples:
        "doom**1993" -> ("doom", 1993)
        "battlefield 2142" -> ("battlefield 2142", None)
        "fifa 23" -> ("fifa 23", None)
    """
    # Check for ** separator (explicit year marker)
    if "**" in game:
        parts = game.split("**")
        if len(parts) == 2:
            game_name = parts[0].strip()
            try:
                year = int(parts[1].strip())
                # Validate year (games exist roughly from 1970 to current year + 5)
                if 1970 <= year <= 2030:
                    return (game_name, year)
            except ValueError:
                pass
    
    # No explicit year marker found
    return (game, None)


@router.get("/hltb", response_class=PlainTextResponse)
async def get_hltb_info(
    game: str = Query(..., description="Game name, optionally with \*\*YEAR for filtering (e.g., 'doom\*\*1993')"),
    show_url: bool = Query(False, description="Include HLTB URL in response")
):
    """
    Get game completion time from HowLongToBeat.
    
    StreamElements: add this text in "Response type" field:\n
    ${customapi.https://tbc-rksp.onrender.com/hltb?game=$(1:)&show_url=true}
    
    Chat example: !hltb Elden Ring\n 
    
    Use ** separator to specify release year:\n
    !hltb Doom**1993
    """
    try:
        game_query = urllib.parse.unquote_plus(game)
        
        # Extract year if specified with **
        game_name, filter_year = _extract_year_from_query(game_query)
        search_results = HowLongToBeat().search(game_name, similarity_case_sensitive=False)
        
        if not search_results:
            return f"Game '{game_name}' not found"
        
        # Filter by year if specified
        if filter_year:
            filtered = [g for g in search_results if g.release_world == filter_year]
            if not filtered:
                return f"Game '{game_name}' ({filter_year}) not found"
            game_data = filtered[0]
        else:
            # Get best match by similarity
            game_data = max(search_results, key=lambda x: x.similarity)
        
        # Parse game info
        title = game_data.game_name
        release_year = game_data.release_world if game_data.release_world else "Unknown"
        game_id = game_data.game_id
        
        # Parse completion times (already in hours)
        main_story = game_data.main_story if game_data.main_story else 0
        main_extra = game_data.main_extra if game_data.main_extra else 0
        completionist = game_data.completionist if game_data.completionist else 0
        
        # Build response
        parts = [f"{title} ({release_year}):"]
        
        time_parts = []
        if main_story > 0:
            time_parts.append(f"Main: {_format_time(main_story)}")
        if main_extra > 0:
            time_parts.append(f"Main+Extra: {_format_time(main_extra)}")
        if completionist > 0:
            time_parts.append(f"100%: {_format_time(completionist)}")
        
        if time_parts:
            parts.append(" | ".join(time_parts))
        else:
            return f"{title} ({release_year}): No completion time data available"
        
        if show_url and game_id:
            parts.append(f"https://howlongtobeat.com/game/{game_id}")
        
        return " | ".join(parts)
        
    except Exception:
        return "Service temporarily unavailable"