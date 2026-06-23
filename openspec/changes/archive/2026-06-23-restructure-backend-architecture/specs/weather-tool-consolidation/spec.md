# weather-tool-consolidation

## Purpose

Merge the standalone `weather_agent.py` module (319 lines) into the canonical `tools/weather_tool.py`, eliminate the duplicate `WeatherTool` class, replace the hardcoded 150-line `city_coords` dictionary with LLM-based geocoding, and delete `weather_agent.py`.

## ADDED Requirements

### Requirement: Single WeatherTool class in tools/weather_tool.py

The system SHALL have exactly one `WeatherTool` class, located in `tools/weather_tool.py`, that accepts natural language weather queries and returns weather information with advice.

#### Scenario: Natural language weather query

- **WHEN** `WeatherTool._run("今天合肥热不热，需要穿外套吗")` is called
- **THEN** the tool extracts "合肥" as the city, resolves its coordinates via LLM, fetches weather from Open-Meteo, generates advice, and returns a formatted response

#### Scenario: English city name

- **WHEN** `WeatherTool._run("What's the weather in Shanghai?")` is called
- **THEN** the tool extracts "Shanghai", resolves coordinates, and returns weather data with advice in Chinese

### Requirement: LLM-based geocoding replaces hardcoded city_coords

The system SHALL use the active LLM to resolve city names to latitude/longitude coordinates instead of maintaining a hardcoded dictionary.

#### Scenario: City coordinate resolution

- **WHEN** the tool needs coordinates for "合肥"
- **THEN** the tool asks the LLM: "What are the latitude and longitude coordinates of 合肥, China? Return only JSON: {\"lat\": ..., \"lon\": ...}"
- **AND** the LLM returns `{"lat": 31.82, "lon": 117.23}` which is used for the Open-Meteo API call

#### Scenario: Coordinate validation

- **WHEN** the LLM returns coordinates
- **THEN** the tool validates that latitude is between -90 and 90 and longitude is between -180 and 180 before making the API call

#### Scenario: LLM geocoding failure

- **WHEN** the LLM returns invalid coordinates or fails to parse
- **THEN** the tool returns "无法识别城市坐标: {city}。请尝试使用更具体的城市名称。"

### Requirement: City extraction from natural language query

The system SHALL use the active LLM to extract city names from natural language queries, supporting both Chinese and English city names.

#### Scenario: Extract city from Chinese query

- **WHEN** the query is "北京今天会下雨吗"
- **THEN** the LLM extracts "北京" as the city

#### Scenario: No city found

- **WHEN** the query does not contain a recognizable city name (e.g., "今天天气怎么样")
- **THEN** the tool returns "抱歉，我无法识别您提到的城市。请告诉我具体是哪个城市。"

### Requirement: Weather advice generation via LLM

The system SHALL use the active LLM to generate practical life advice (dressing, travel, health) based on raw weather data and the user's implied focus areas.

#### Scenario: Temperature-focused advice

- **WHEN** the user asks "冷不冷" and the temperature is 5°C
- **THEN** the LLM generates advice recommending warm clothing, with specific suggestions about coats or layers

#### Scenario: Rain-focused advice

- **WHEN** the user asks about rain and the forecast shows precipitation
- **THEN** the LLM generates advice about bringing an umbrella and avoiding outdoor activities

### Requirement: weather_agent.py is deleted

After consolidation, the file `backend/weather_agent.py` SHALL be removed from the repository.

#### Scenario: Import weather_agent fails

- **WHEN** any code attempts `from weather_agent import ...`
- **THEN** the import fails with `ModuleNotFoundError`, confirming the file no longer exists

### Requirement: weather_tool.py is self-contained

The consolidated `tools/weather_tool.py` SHALL not import from any file outside `tools/`, `provider_manager`, and standard library / third-party packages.

#### Scenario: weather_tool.py has no backend-internal imports

- **WHEN** reviewing `tools/weather_tool.py` imports
- **THEN** all imports are from `langchain.tools`, `provider_manager`, `requests`, `json`, `logging`, or standard library — no imports from `main`, `agent`, `model_config`, or any service/router module
