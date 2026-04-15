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

def get_headers(api_key: Optional[str] = None) -> dict:
    token = api_key or os.environ.get("WGER_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@mcp.tool()
async def list_exercises(
    language: Optional[str] = None,
    category: Optional[int] = None,
    equipment: Optional[int] = None,
    muscles: Optional[int] = None,
    muscles_secondary: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List exercises from the wger exercise database with optional filters."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if language:
        params["language"] = language
    if category is not None:
        params["category"] = category
    if equipment is not None:
        params["equipment"] = equipment
    if muscles is not None:
        params["muscles"] = muscles
    if muscles_secondary is not None:
        params["muscles_secondary"] = muscles_secondary

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/exercise/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_exercise(exercise_id: int, api_key: Optional[str] = None) -> dict:
    """Get details of a specific exercise by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/exercise/{exercise_id}/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_exercise_categories(api_key: Optional[str] = None) -> dict:
    """List all exercise categories (e.g. Chest, Back, Legs)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/exercisecategory/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_equipment(api_key: Optional[str] = None) -> dict:
    """List all available gym equipment types."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/equipment/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_muscles(api_key: Optional[str] = None) -> dict:
    """List all muscles available in the exercise database."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/muscle/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_workouts(limit: int = 20, offset: int = 0, api_key: Optional[str] = None) -> dict:
    """List all workouts for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workout/",
            headers=get_headers(api_key),
            params={"format": "json", "limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_workout(workout_id: int, api_key: Optional[str] = None) -> dict:
    """Get details of a specific workout by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workout/{workout_id}/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_workout(description: str = "", api_key: Optional[str] = None) -> dict:
    """Create a new workout for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workout/",
            headers=get_headers(api_key),
            json={"description": description}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_workout(workout_id: int, api_key: Optional[str] = None) -> dict:
    """Delete a specific workout by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/workout/{workout_id}/",
            headers=get_headers(api_key)
        )
        response.raise_for_status()
        return {"status": "deleted", "workout_id": workout_id}


@mcp.tool()
async def list_training_days(
    training: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List training days, optionally filtered by workout ID."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if training is not None:
        params["training"] = training

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/day/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_training_day(
    workout_id: int,
    description: str = "",
    day: Optional[list] = None,
    api_key: Optional[str] = None
) -> dict:
    """Create a training day within a workout. day is a list of weekday numbers (1=Monday...7=Sunday)."""
    payload = {"training": workout_id, "description": description}
    if day:
        payload["day"] = day
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/day/",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_slots(
    day: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List exercise slots, optionally filtered by training day ID."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if day is not None:
        params["day"] = day

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/slot/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_slot(day_id: int, order: int = 1, api_key: Optional[str] = None) -> dict:
    """Create an exercise slot in a training day."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/slot/",
            headers=get_headers(api_key),
            json={"day": day_id, "order": order}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_slot_entries(
    slot: Optional[int] = None,
    exercise: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List slot entries (exercises assigned to slots)."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if slot is not None:
        params["slot"] = slot
    if exercise is not None:
        params["exercise"] = exercise

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/slot-entry/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_slot_entry(
    slot_id: int,
    exercise_id: int,
    order: int = 1,
    api_key: Optional[str] = None
) -> dict:
    """Add an exercise to a slot."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/slot-entry/",
            headers=get_headers(api_key),
            json={"slot": slot_id, "exercise": exercise_id, "order": order}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_workout_logs(
    workout: Optional[int] = None,
    exercise: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List workout log entries for the authenticated user."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if workout is not None:
        params["workout"] = workout
    if exercise is not None:
        params["exercise"] = exercise

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workoutsession/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_workout_log(
    workout_id: int,
    date: str,
    notes: str = "",
    impression: str = "3",
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """Create a workout session log. impression: 1=General, 2=Burned Out, 3=Good, 4=Excellent. date format: YYYY-MM-DD. time format: HH:MM:SS."""
    payload = {
        "workout": workout_id,
        "date": date,
        "notes": notes,
        "impression": impression
    }
    if time_start:
        payload["time_start"] = time_start
    if time_end:
        payload["time_end"] = time_end

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/workoutsession/",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_exercise_logs(
    workout: Optional[int] = None,
    exercise: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List exercise log entries (individual sets logged during workouts)."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if workout is not None:
        params["workout"] = workout
    if exercise is not None:
        params["exercise"] = exercise

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/log/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_exercise_log(
    workout_id: int,
    exercise_id: int,
    reps: int,
    weight: float,
    date: str,
    weight_unit: int = 1,
    repetition_unit: int = 1,
    api_key: Optional[str] = None
) -> dict:
    """Log a set for an exercise. weight_unit: 1=kg, 2=lb. repetition_unit: 1=Repetitions. date format: YYYY-MM-DD."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/log/",
            headers=get_headers(api_key),
            json={
                "workout": workout_id,
                "exercise": exercise_id,
                "reps": reps,
                "weight": str(weight),
                "date": date,
                "weight_unit": weight_unit,
                "repetition_unit": repetition_unit
            }
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_nutrition_plans(limit: int = 20, offset: int = 0, api_key: Optional[str] = None) -> dict:
    """List all nutrition plans for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/nutritionplan/",
            headers=get_headers(api_key),
            params={"format": "json", "limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_nutrition_plan(plan_id: int, api_key: Optional[str] = None) -> dict:
    """Get details of a specific nutrition plan including nutritional values."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/nutritionplan/{plan_id}/nutritional_values/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_nutrition_plan(
    description: str = "",
    only_logging: bool = False,
    goal_energy: Optional[float] = None,
    goal_protein: Optional[float] = None,
    goal_carbohydrates: Optional[float] = None,
    goal_fat: Optional[float] = None,
    api_key: Optional[str] = None
) -> dict:
    """Create a new nutrition plan."""
    payload = {"description": description, "only_logging": only_logging}
    if goal_energy is not None:
        payload["goal_energy"] = goal_energy
    if goal_protein is not None:
        payload["goal_protein"] = goal_protein
    if goal_carbohydrates is not None:
        payload["goal_carbohydrates"] = goal_carbohydrates
    if goal_fat is not None:
        payload["goal_fat"] = goal_fat

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/nutritionplan/",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meals(
    plan: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List meals, optionally filtered by nutrition plan ID."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if plan is not None:
        params["plan"] = plan

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/meal/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal(
    plan_id: int,
    name: str = "",
    time: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """Create a meal in a nutrition plan. time format: HH:MM:SS."""
    payload = {"plan": plan_id, "name": name}
    if time:
        payload["time"] = time

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/meal/",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meal_items(
    meal: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List food items in meals."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if meal is not None:
        params["meal"] = meal

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/mealitem/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal_item(
    meal_id: int,
    ingredient_id: int,
    amount: float,
    weight_unit: Optional[int] = None,
    api_key: Optional[str] = None
) -> dict:
    """Add a food ingredient to a meal. amount is in grams by default."""
    payload = {"meal": meal_id, "ingredient": ingredient_id, "amount": str(amount)}
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mealitem/",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_ingredients(
    name: str,
    language: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """Search for food ingredients/nutrients in the wger database."""
    params = {"format": "json", "name": name, "limit": limit, "offset": offset}
    if language:
        params["language"] = language

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/ingredient/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_ingredient(ingredient_id: int, api_key: Optional[str] = None) -> dict:
    """Get nutritional details of a specific ingredient/food item."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/ingredient/{ingredient_id}/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_body_weight(
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List body weight entries for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weightentry/",
            headers=get_headers(api_key),
            params={"format": "json", "limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_body_weight_entry(
    date: str,
    weight: float,
    api_key: Optional[str] = None
) -> dict:
    """Log a body weight entry. date format: YYYY-MM-DD. weight in kg."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/weightentry/",
            headers=get_headers(api_key),
            json={"date": date, "weight": str(weight)}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_measurement_categories(api_key: Optional[str] = None) -> dict:
    """List all custom measurement categories for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/measurement-category/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_measurement_category(name: str, unit: str, api_key: Optional[str] = None) -> dict:
    """Create a custom measurement category (e.g. 'Bicep' with unit 'cm')."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/measurement-category/",
            headers=get_headers(api_key),
            json={"name": name, "unit": unit}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_measurements(
    category: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None
) -> dict:
    """List measurement entries, optionally filtered by category ID."""
    params = {"format": "json", "limit": limit, "offset": offset}
    if category is not None:
        params["category"] = category

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/measurement/",
            headers=get_headers(api_key),
            params=params
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_measurement(
    category_id: int,
    date: str,
    value: float,
    notes: str = "",
    api_key: Optional[str] = None
) -> dict:
    """Log a measurement entry for a given category. date format: YYYY-MM-DD."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/measurement/",
            headers=get_headers(api_key),
            json={"category": category_id, "date": date, "value": str(value), "notes": notes}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_user_profile(api_key: Optional[str] = None) -> dict:
    """Get the profile information of the currently authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/userprofile/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_api_info(api_key: Optional[str] = None) -> dict:
    """Get general API information and available endpoints."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/",
            headers=get_headers(api_key),
            params={"format": "json"}
        )
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
