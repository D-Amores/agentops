import httpx
from fastmcp import FastMCP

mcp = FastMCP("weather-server")


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the current weather for a given city name.

    Args:
        city: The name of the city, e.g. "Mexico City" or "Ramos Arizpe".
    """
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
        )
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Could not find location: {city}"

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        weather_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current": "temperature_2m"},
        )
        weather_data = weather_response.json()
        temp = weather_data["current"]["temperature_2m"]

        return f"The current temperature in {city} is {temp}°C."


if __name__ == "__main__":
    mcp.run(transport="stdio")
