from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
import httpx
import os

router = APIRouter(tags=["weather"])


def _wind_degrees_to_direction(degrees: float) -> str:
    """Convert wind degrees to cardinal direction"""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    try:
        index = int((degrees + 22.5) // 45 % 8)
        return directions[index]
    except (TypeError, ValueError):
        return "unknown"


def _pressure_to_mm(pressure: float) -> float:
    """Convert pressure from hPa to mmHg"""
    try:
        return round(pressure / 1.333, 1)
    except (TypeError, ZeroDivisionError):
        return 0


@router.get("/weather", response_class=PlainTextResponse)
async def get_weather_info(
    city: str = Query("Moscow", description="City name"),
    wind: bool = Query(False, description="Include wind info"),
    humidity: bool = Query(False, description="Include humidity"),
    pressure: bool = Query(False, description="Include pressure"),
    precipitation: bool = Query(True, description="Include precipitation (rain/snow)")
):
    """
    Get current weather for a city.
    
    StreamElements: add this text in "Response type" field:
    ${customapi.https://example.com/weather?city=$(1:)}
    
    If you want additional info like wind, humidity, pressure or precipitation, just add one or all of them as parameters:\n
    ${customapi.https://example.com/weather?city=$(1:)&wind=true&humidity=true&pressure=true&precipitation=true}\n

    Chat example: !weather Moscow
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "API key not configured"
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "en"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            
            if response.status_code == 404:
                return f"City '{city}' not found"
            
            if response.status_code != 200:
                return "Service temporarily unavailable"
            
            data = response.json()
            
            # Parse basic weather data
            name = data["name"]
            description = data["weather"][0]["description"]
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            
            # Build response based on parameters
            parts = [f"{name}: {temp}°C (feels like {feels_like}°C), {description}"] # default
            
            if wind:
                wind_speed = data["wind"]["speed"]
                wind_deg = data["wind"].get("deg", 0)
                wind_direction = _wind_degrees_to_direction(wind_deg)
                parts.append(f"Wind: {wind_speed} m/s {wind_direction}")
            
            if humidity:
                humidity_val = data["main"]["humidity"]
                parts.append(f"Humidity: {humidity_val}%")
            
            if pressure:
                pressure_val = data["main"]["pressure"]
                pressure_mm = _pressure_to_mm(pressure_val)
                parts.append(f"Pressure: {pressure_mm} mmHg")
            
            if precipitation:
                # Check for rain
                if "rain" in data:
                    rain_1h = data["rain"].get("1h", 0)
                    if rain_1h > 0:
                        parts.append(f"Rain: {rain_1h} mm/h")
                
                # Check for snow
                if "snow" in data:
                    snow_1h = data["snow"].get("1h", 0)
                    if snow_1h > 0:
                        parts.append(f"Snow: {snow_1h} mm/h")
            
            return " | ".join(parts)
            
    except KeyError:
        return "Error parsing weather data"
    except httpx.TimeoutException:
        return "Service temporarily unavailable"
    except Exception:
        return "Service temporarily unavailable"