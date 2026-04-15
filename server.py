from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("wger Workout Manager")

BASE_URL = "https://wger.de/api/v2"
API_TOKEN = os.environ.get("WGER_API_TOKEN", "")


def get_headers() -> dict:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"
    return headers


# ─── Exercise Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def list_exercises(
    language: Optional[str] = None,
    category: Optional[int] = None,
    muscles: Optional[int] = None,
    equipment: Optional[int] = None,
    offset: int = 0,
    limit: int = 20
) -> dict:
    """List exercises from the wger exercise database. Filter by language code (e.g. 'english'), category ID, muscle ID, or equipment ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if language:
        params["language"] = language
    if category is not None:
        params["category"] = category
    if muscles is not None:
        params["muscles"] = muscles
    if equipment is not None:
        params["equipment"] = equipment
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercise/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_exercise(exercise_id: int) -> dict:
    """Get details of a specific exercise by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercise/{exercise_id}/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_exercises(term: str, language: str = "english", format: str = "json") -> dict:
    """Search for exercises by name. Returns a list of matching exercises."""
    params = {"term": term, "language": language, "format": format}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercise/search/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_exercise_categories() -> dict:
    """List all exercise categories (e.g. Abs, Arms, Back, Chest, Legs, Shoulders)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercisecategory/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_muscles() -> dict:
    """List all muscles in the wger database."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/muscle/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_equipment() -> dict:
    """List all equipment types (e.g. Barbell, Dumbbell, Kettlebell, etc.)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/equipment/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_exercise_info(offset: int = 0, limit: int = 20) -> dict:
    """List exercises with full information including muscles, equipment, images, and translations."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exerciseinfo/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_exercise_info(exercise_id: int) -> dict:
    """Get full exercise info (muscles, equipment, images, translations) for a specific exercise ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exerciseinfo/{exercise_id}/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


# ─── Workout / Routine Tools ──────────────────────────────────────────────────

@mcp.tool()
async def list_workouts(offset: int = 0, limit: int = 20) -> dict:
    """List all workouts for the authenticated user."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workout/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_workout(workout_id: int) -> dict:
    """Get details of a specific workout by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workout/{workout_id}/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_workout(description: Optional[str] = None) -> dict:
    """Create a new workout for the authenticated user. Optionally provide a description."""
    payload = {}
    if description:
        payload["description"] = description
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/workout/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_workout(workout_id: int) -> dict:
    """Delete a specific workout by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/workout/{workout_id}/", headers=get_headers())
        if response.status_code == 204:
            return {"success": True, "message": f"Workout {workout_id} deleted successfully."}
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_workout_canonical(workout_id: int) -> dict:
    """Get the canonical (full structured) representation of a workout including all days, sets, and exercises."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workout/{workout_id}/canonical_representation/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


# ─── Training Day Tools ───────────────────────────────────────────────────────

@mcp.tool()
async def list_days(training: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List all training days, optionally filtered by workout ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if training is not None:
        params["training"] = training
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/day/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_day(workout_id: int, name: str, day_of_week: Optional[list] = None) -> dict:
    """Create a new training day in a workout. day_of_week is a list of integers (1=Monday...7=Sunday)."""
    payload = {"training": workout_id, "name": name}
    if day_of_week:
        payload["day"] = day_of_week
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/day/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Exercise Set Tools ───────────────────────────────────────────────────────

@mcp.tool()
async def list_sets(exercise_day: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List all exercise sets, optionally filtered by day ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if exercise_day is not None:
        params["exerciseday"] = exercise_day
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/set/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_set(exercise_day_id: int, sets: int = 3) -> dict:
    """Create a new exercise set container in a training day."""
    payload = {"exerciseday": exercise_day_id, "sets": sets}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/set/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Setting (Exercise within Set) Tools ─────────────────────────────────────

@mcp.tool()
async def list_settings(set_id: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List all settings (exercises within sets), optionally filtered by set ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if set_id is not None:
        params["set"] = set_id
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/setting/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_setting(
    set_id: int,
    exercise_id: int,
    reps: Optional[int] = None,
    weight: Optional[float] = None,
    rir: Optional[int] = None,
    weight_unit: Optional[int] = None
) -> dict:
    """Add an exercise to a set with optional reps, weight, RIR (reps in reserve), and weight unit ID."""
    payload = {"set": set_id, "exercise": exercise_id}
    if reps is not None:
        payload["reps"] = reps
    if weight is not None:
        payload["weight"] = weight
    if rir is not None:
        payload["rir"] = rir
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/setting/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Workout Log Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def list_workout_logs(
    workout: Optional[int] = None,
    exercise: Optional[int] = None,
    offset: int = 0,
    limit: int = 20
) -> dict:
    """List workout log entries. Optionally filter by workout ID or exercise ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if workout is not None:
        params["workout"] = workout
    if exercise is not None:
        params["exercise"] = exercise
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workoutsession/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_workout_session(
    workout_id: int,
    date: str,
    notes: Optional[str] = None,
    impression: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None
) -> dict:
    """Log a workout session. Date in YYYY-MM-DD format. Impression: '1' (General), '2' (Burned out), '3' (Good)."""
    payload = {"workout": workout_id, "date": date}
    if notes:
        payload["notes"] = notes
    if impression:
        payload["impression"] = impression
    if time_start:
        payload["time_start"] = time_start
    if time_end:
        payload["time_end"] = time_end
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/workoutsession/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_logs(
    exercise: Optional[int] = None,
    workout: Optional[int] = None,
    offset: int = 0,
    limit: int = 20
) -> dict:
    """List individual exercise log entries (sets/reps/weights logged). Optionally filter by exercise or workout."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if exercise is not None:
        params["exercise"] = exercise
    if workout is not None:
        params["workout"] = workout
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/log/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_log(
    workout_session_id: int,
    exercise_id: int,
    reps: int,
    weight: float,
    date: str,
    weight_unit: Optional[int] = None,
    rir: Optional[int] = None
) -> dict:
    """Log a specific exercise set (reps and weight) for a workout session. Date in YYYY-MM-DD format."""
    payload = {
        "workout": workout_session_id,
        "exercise": exercise_id,
        "reps": reps,
        "weight": weight,
        "date": date
    }
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    if rir is not None:
        payload["rir"] = rir
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/log/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Body Weight Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def list_body_weight(offset: int = 0, limit: int = 20) -> dict:
    """List body weight entries for the authenticated user."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weightentry/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_body_weight(date: str, weight: float) -> dict:
    """Log a body weight entry. Date in YYYY-MM-DD format, weight in kg."""
    payload = {"date": date, "weight": weight}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/weightentry/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_body_weight(entry_id: int) -> dict:
    """Delete a specific body weight entry by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/weightentry/{entry_id}/", headers=get_headers())
        if response.status_code == 204:
            return {"success": True, "message": f"Weight entry {entry_id} deleted."}
        response.raise_for_status()
        return response.json()


# ─── Nutrition Tools ──────────────────────────────────────────────────────────

@mcp.tool()
async def list_nutrition_plans(offset: int = 0, limit: int = 20) -> dict:
    """List all nutrition plans for the authenticated user."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_nutrition_plan(plan_id: int) -> dict:
    """Get details of a specific nutrition plan by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/{plan_id}/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_nutrition_plan_nutritional_values(plan_id: int) -> dict:
    """Get the computed nutritional values (calories, protein, carbs, fat) for a nutrition plan."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/{plan_id}/nutritional_values/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_nutrition_plan(description: Optional[str] = None, only_logging: bool = False) -> dict:
    """Create a new nutrition plan. Optionally set a description and whether it's only for logging."""
    payload = {"only_logging": only_logging}
    if description:
        payload["description"] = description
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nutritionplan/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meals(plan: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List all meals, optionally filtered by nutrition plan ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if plan is not None:
        params["plan"] = plan
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/meal/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal(plan_id: int, name: Optional[str] = None, time: Optional[str] = None) -> dict:
    """Create a new meal in a nutrition plan. Time format: HH:MM:SS."""
    payload = {"plan": plan_id}
    if name:
        payload["name"] = name
    if time:
        payload["time"] = time
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/meal/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meal_items(meal: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List all meal items (food + amount), optionally filtered by meal ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if meal is not None:
        params["meal"] = meal
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/mealitem/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal_item(
    meal_id: int,
    ingredient_id: int,
    amount: float,
    weight_unit: Optional[int] = None
) -> dict:
    """Add a food ingredient to a meal with a specified amount (in grams by default)."""
    payload = {"meal": meal_id, "ingredient": ingredient_id, "amount": amount}
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/mealitem/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Ingredient / Food Tools ──────────────────────────────────────────────────

@mcp.tool()
async def search_ingredients(name: str, language: Optional[str] = None, offset: int = 0, limit: int = 20) -> dict:
    """Search for food ingredients/items by name in the wger food database."""
    params = {"name": name, "offset": offset, "limit": limit, "format": "json"}
    if language:
        params["language"] = language
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ingredient/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_ingredient(ingredient_id: int) -> dict:
    """Get detailed nutritional information for a specific food ingredient by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ingredient/{ingredient_id}/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


# ─── Measurement Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def list_measurement_categories() -> dict:
    """List all measurement categories (e.g. chest, waist, arms) for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/measurement-category/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_measurement_category(name: str, unit: str) -> dict:
    """Create a new measurement category (e.g. 'Chest' in 'cm')."""
    payload = {"name": name, "unit": unit}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/measurement-category/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_measurements(category: Optional[int] = None, offset: int = 0, limit: int = 20) -> dict:
    """List measurement entries, optionally filtered by category ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if category is not None:
        params["category"] = category
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/measurement/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_measurement(category_id: int, date: str, value: float) -> dict:
    """Log a new measurement entry. Date in YYYY-MM-DD format."""
    payload = {"category": category_id, "date": date, "value": value}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/measurement/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── Nutrition Diary Tools ────────────────────────────────────────────────────

@mcp.tool()
async def list_nutrition_diary(
    plan: Optional[int] = None,
    ingredient: Optional[int] = None,
    offset: int = 0,
    limit: int = 20
) -> dict:
    """List nutrition diary entries. Optionally filter by plan ID or ingredient ID."""
    params = {"offset": offset, "limit": limit, "format": "json"}
    if plan is not None:
        params["plan"] = plan
    if ingredient is not None:
        params["ingredient"] = ingredient
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritiondiary/", headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_nutrition_diary(
    plan_id: int,
    ingredient_id: int,
    amount: float,
    datetime_str: Optional[str] = None,
    weight_unit: Optional[int] = None
) -> dict:
    """Log food intake to the nutrition diary. datetime_str in ISO format (YYYY-MM-DDTHH:MM:SS)."""
    payload = {"plan": plan_id, "ingredient": ingredient_id, "amount": amount}
    if datetime_str:
        payload["datetime"] = datetime_str
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nutritiondiary/", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


# ─── User Profile Tools ───────────────────────────────────────────────────────

@mcp.tool()
async def get_user_profile() -> dict:
    """Get the profile information for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/userprofile/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_gym_user_config() -> dict:
    """Get the gym/user configuration for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/gym/userconfig/", headers=get_headers(), params={"format": "json"})
        response.raise_for_status()
        return response.json()




async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

mcp_app = mcp.http_app(transport="streamable-http")

class _FixAcceptHeader:
    """Ensure Accept header includes both types FastMCP requires."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"").decode()
            if "text/event-stream" not in accept:
                new_headers = [(k, v) for k, v in scope["headers"] if k != b"accept"]
                new_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = dict(scope, headers=new_headers)
        await self.app(scope, receive, send)

app = _FixAcceptHeader(Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", mcp_app),
    ],
    lifespan=mcp_app.lifespan,
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
