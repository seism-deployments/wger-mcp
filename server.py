from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
from fastmcp import FastMCP
import httpx
import os
import json
from typing import Optional

mcp = FastMCP("wger-workout-manager")

DEFAULT_BASE_URL = "https://wger.de"
API_PATH = "/api/v2"


def build_headers(auth_token: Optional[str] = None) -> dict:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Token {auth_token}"
    return headers


def build_api_url(base_url: str, endpoint: str) -> str:
    base = base_url.rstrip("/")
    ep = endpoint.lstrip("/")
    return f"{base}{API_PATH}/{ep}"


async def api_request(
    method: str,
    url: str,
    headers: dict,
    params: Optional[dict] = None,
    json_data: Optional[dict] = None,
) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        kwargs = {"headers": headers}
        if params:
            kwargs["params"] = {k: v for k, v in params.items() if v is not None}
        if json_data is not None:
            kwargs["json"] = json_data
        response = await client.request(method, url, **kwargs)
        if response.status_code == 204:
            return {"success": True, "status_code": 204}
        try:
            return {"status_code": response.status_code, "data": response.json()}
        except Exception:
            return {"status_code": response.status_code, "data": response.text}


@mcp.tool()
async def get_api_info(base_url: str, auth_token: Optional[str] = None) -> dict:
    """Retrieve general API information, available endpoints, and server version details from the wger instance."""
    headers = build_headers(auth_token)
    base = base_url.rstrip("/")
    api_root_url = f"{base}{API_PATH}/"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_root_url, headers=headers)
        try:
            api_root = response.json()
        except Exception:
            api_root = response.text

        result = {
            "status_code": response.status_code,
            "api_root": api_root,
            "base_url": base_url,
            "api_version": "v2",
        }

        # Try to get server info from status endpoint
        try:
            status_response = await client.get(
                f"{base}/api/v2/status/", headers=headers
            )
            if status_response.status_code == 200:
                result["server_status"] = status_response.json()
        except Exception:
            pass

        return result


@mcp.tool()
async def manage_workouts(
    base_url: str,
    auth_token: str,
    action: str,
    workout_id: Optional[int] = None,
    data: Optional[str] = None,
) -> dict:
    """Create, retrieve, update, or delete workout routines and training plans."""
    headers = build_headers(auth_token)
    json_data = json.loads(data) if data else None

    if action == "list":
        url = build_api_url(base_url, "workout/")
        return await api_request("GET", url, headers)

    elif action == "get":
        if not workout_id:
            return {"error": "workout_id is required for 'get' action"}
        url = build_api_url(base_url, f"workout/{workout_id}/")
        return await api_request("GET", url, headers)

    elif action == "create":
        url = build_api_url(base_url, "workout/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "update":
        if not workout_id:
            return {"error": "workout_id is required for 'update' action"}
        url = build_api_url(base_url, f"workout/{workout_id}/")
        return await api_request("PATCH", url, headers, json_data=json_data or {})

    elif action == "delete":
        if not workout_id:
            return {"error": "workout_id is required for 'delete' action"}
        url = build_api_url(base_url, f"workout/{workout_id}/")
        return await api_request("DELETE", url, headers)

    else:
        # Try to also list training days and exercises if listing
        return {"error": f"Unknown action '{action}'. Use: list, get, create, update, delete"}


@mcp.tool()
async def track_body_metrics(
    base_url: str,
    auth_token: str,
    metric_type: str,
    action: str,
    entry_id: Optional[int] = None,
    data: Optional[str] = None,
) -> dict:
    """Log and retrieve body weight entries and custom body measurements."""
    headers = build_headers(auth_token)
    json_data = json.loads(data) if data else None

    # Determine endpoint based on metric type
    if metric_type == "weight":
        base_endpoint = "weightentry"
    elif metric_type == "measurement":
        base_endpoint = "measurement"
    elif metric_type == "measurement_category":
        base_endpoint = "measurement-category"
    else:
        return {
            "error": f"Unknown metric_type '{metric_type}'. Use: weight, measurement, measurement_category"
        }

    if action == "list":
        url = build_api_url(base_url, f"{base_endpoint}/")
        params = {}
        if json_data:
            params.update(json_data)
        return await api_request("GET", url, headers, params=params if params else None)

    elif action == "get":
        if not entry_id:
            return {"error": "entry_id is required for 'get' action"}
        url = build_api_url(base_url, f"{base_endpoint}/{entry_id}/")
        return await api_request("GET", url, headers)

    elif action == "create":
        url = build_api_url(base_url, f"{base_endpoint}/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "update":
        if not entry_id:
            return {"error": "entry_id is required for 'update' action"}
        url = build_api_url(base_url, f"{base_endpoint}/{entry_id}/")
        return await api_request("PATCH", url, headers, json_data=json_data or {})

    elif action == "delete":
        if not entry_id:
            return {"error": "entry_id is required for 'delete' action"}
        url = build_api_url(base_url, f"{base_endpoint}/{entry_id}/")
        return await api_request("DELETE", url, headers)

    else:
        return {"error": f"Unknown action '{action}'. Use: list, get, create, update, delete"}


@mcp.tool()
async def manage_nutrition(
    base_url: str,
    auth_token: str,
    action: str,
    plan_id: Optional[int] = None,
    data: Optional[str] = None,
) -> dict:
    """Create and manage nutrition/diet plans, log meals and food items, and retrieve nutritional values."""
    headers = build_headers(auth_token)
    json_data = json.loads(data) if data else None

    if action == "list_plans":
        url = build_api_url(base_url, "nutritionplan/")
        return await api_request("GET", url, headers)

    elif action == "get_plan":
        if not plan_id:
            return {"error": "plan_id is required for 'get_plan' action"}
        url = build_api_url(base_url, f"nutritionplan/{plan_id}/")
        result = await api_request("GET", url, headers)
        # Also fetch nutritional values for the plan
        values_url = build_api_url(base_url, f"nutritionplan/{plan_id}/nutritional_values/")
        values_result = await api_request("GET", values_url, headers)
        return {"plan": result, "nutritional_values": values_result}

    elif action == "create_plan":
        url = build_api_url(base_url, "nutritionplan/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "delete_plan":
        if not plan_id:
            return {"error": "plan_id is required for 'delete_plan' action"}
        url = build_api_url(base_url, f"nutritionplan/{plan_id}/")
        return await api_request("DELETE", url, headers)

    elif action == "log_meal":
        # Log a nutrition diary entry
        url = build_api_url(base_url, "nutritiondiary/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "list_logs":
        url = build_api_url(base_url, "nutritiondiary/")
        params = {}
        if json_data:
            params.update(json_data)
        return await api_request("GET", url, headers, params=params if params else None)

    elif action == "get_nutritional_values":
        if not plan_id:
            return {"error": "plan_id is required for 'get_nutritional_values' action"}
        url = build_api_url(base_url, f"nutritionplan/{plan_id}/nutritional_values/")
        return await api_request("GET", url, headers)

    elif action == "list_meals":
        url = build_api_url(base_url, "meal/")
        return await api_request("GET", url, headers)

    elif action == "create_meal":
        url = build_api_url(base_url, "meal/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "list_meal_items":
        url = build_api_url(base_url, "mealitem/")
        params = {}
        if json_data:
            params.update(json_data)
        return await api_request("GET", url, headers, params=params if params else None)

    elif action == "create_meal_item":
        url = build_api_url(base_url, "mealitem/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "search_food":
        url = build_api_url(base_url, "ingredient/")
        params = {}
        if json_data:
            params.update(json_data)
        return await api_request("GET", url, headers, params=params if params else None)

    else:
        return {
            "error": f"Unknown action '{action}'. Use: list_plans, get_plan, create_plan, delete_plan, log_meal, list_logs, get_nutritional_values, list_meals, create_meal, list_meal_items, create_meal_item, search_food"
        }


@mcp.tool()
async def search_exercises(
    base_url: str,
    auth_token: Optional[str] = None,
    query: Optional[str] = None,
    language: Optional[str] = "english",
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
    exercise_id: Optional[int] = None,
) -> dict:
    """Search and retrieve exercises from the wger exercise wiki."""
    headers = build_headers(auth_token)

    # Language name to ID mapping (wger uses numeric IDs)
    language_map = {
        "english": 2,
        "german": 1,
        "bulgarian": 3,
        "spanish": 4,
        "russian": 5,
        "dutch": 6,
        "portuguese": 7,
        "arabic": 8,
        "turkish": 9,
        "swedish": 10,
        "norwegian": 11,
        "french": 14,
    }

    # Muscle group name to ID mapping
    muscle_map = {
        "chest": 4,
        "pectorals": 4,
        "back": 12,
        "lats": 12,
        "shoulders": 13,
        "deltoids": 13,
        "biceps": 1,
        "triceps": 5,
        "abs": 6,
        "abdominals": 6,
        "legs": 10,
        "quads": 10,
        "quadriceps": 10,
        "hamstrings": 11,
        "glutes": 8,
        "calves": 7,
        "forearms": 9,
        "traps": 14,
        "trapezius": 14,
    }

    # Equipment name to ID mapping
    equipment_map = {
        "barbell": 1,
        "sj barbell": 2,
        "dumbbell": 3,
        "gym mat": 4,
        "swiss ball": 5,
        "pull-up bar": 6,
        "bodyweight": 7,
        "body weight": 7,
        "cable": 8,
        "machine": 9,
        "bench": 10,
        "kettlebell": 11,
        "bands": 12,
        "resistance bands": 12,
        "plate": 13,
    }

    if exercise_id:
        url = build_api_url(base_url, f"exercise/{exercise_id}/")
        exercise_result = await api_request("GET", url, headers)

        # Also get exercise info (translations, images, etc.)
        info_url = build_api_url(base_url, f"exerciseinfo/{exercise_id}/")
        info_result = await api_request("GET", info_url, headers)
        return {"exercise": exercise_result, "exercise_info": info_result}

    if query:
        # Use the search endpoint
        search_url = build_api_url(base_url, "exercise/search/")
        lang_id = language_map.get(language.lower() if language else "english", 2)
        params = {"term": query, "language": language or "english", "format": "json"}
        return await api_request("GET", search_url, headers, params=params)

    # Use exerciseinfo for filtered listing
    url = build_api_url(base_url, "exerciseinfo/")
    params = {}

    if language:
        lang_id = language_map.get(language.lower(), 2)
        params["language"] = lang_id

    if muscle_group:
        muscle_id = muscle_map.get(muscle_group.lower())
        if muscle_id:
            params["muscles"] = muscle_id
        else:
            try:
                params["muscles"] = int(muscle_group)
            except ValueError:
                pass

    if equipment:
        equip_id = equipment_map.get(equipment.lower())
        if equip_id:
            params["equipment"] = equip_id
        else:
            try:
                params["equipment"] = int(equipment)
            except ValueError:
                pass

    return await api_request("GET", url, headers, params=params)


@mcp.tool()
async def log_workout_session(
    base_url: str,
    auth_token: str,
    action: str,
    log_id: Optional[int] = None,
    data: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Record and retrieve workout session logs including exercises performed, sets, reps, and weights."""
    headers = build_headers(auth_token)
    json_data = json.loads(data) if data else None

    if action == "list":
        url = build_api_url(base_url, "workoutsession/")
        params = {}
        if start_date:
            params["date__gte"] = start_date
        if end_date:
            params["date__lte"] = end_date
        return await api_request("GET", url, headers, params=params if params else None)

    elif action == "get":
        if not log_id:
            return {"error": "log_id is required for 'get' action"}
        url = build_api_url(base_url, f"workoutsession/{log_id}/")
        return await api_request("GET", url, headers)

    elif action == "create":
        url = build_api_url(base_url, "workoutsession/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "update":
        if not log_id:
            return {"error": "log_id is required for 'update' action"}
        url = build_api_url(base_url, f"workoutsession/{log_id}/")
        return await api_request("PATCH", url, headers, json_data=json_data or {})

    elif action == "delete":
        if not log_id:
            return {"error": "log_id is required for 'delete' action"}
        url = build_api_url(base_url, f"workoutsession/{log_id}/")
        return await api_request("DELETE", url, headers)

    elif action == "list_logs":
        # Exercise logs (individual sets/reps/weights)
        url = build_api_url(base_url, "workoutlog/")
        params = {}
        if start_date:
            params["date__gte"] = start_date
        if end_date:
            params["date__lte"] = end_date
        if json_data:
            params.update(json_data)
        return await api_request("GET", url, headers, params=params if params else None)

    elif action == "create_log":
        # Create an individual exercise log entry
        url = build_api_url(base_url, "workoutlog/")
        return await api_request("POST", url, headers, json_data=json_data or {})

    elif action == "get_log":
        if not log_id:
            return {"error": "log_id is required for 'get_log' action"}
        url = build_api_url(base_url, f"workoutlog/{log_id}/")
        return await api_request("GET", url, headers)

    elif action == "delete_log":
        if not log_id:
            return {"error": "log_id is required for 'delete_log' action"}
        url = build_api_url(base_url, f"workoutlog/{log_id}/")
        return await api_request("DELETE", url, headers)

    else:
        return {
            "error": f"Unknown action '{action}'. Use: list, get, create, update, delete, list_logs, create_log, get_log, delete_log"
        }


@mcp.tool()
async def manage_user_profile(
    base_url: str,
    auth_token: str,
    action: str,
    data: Optional[str] = None,
) -> dict:
    """Retrieve and update the authenticated user's profile settings including personal details, fitness goals, and preferences."""
    headers = build_headers(auth_token)
    json_data = json.loads(data) if data else None

    if action == "get_profile":
        results = {}
        # Get user profile
        url = build_api_url(base_url, "userprofile/")
        results["profile"] = await api_request("GET", url, headers)
        return results

    elif action == "update_profile":
        # Get profile first to find the ID
        url = build_api_url(base_url, "userprofile/")
        profile_result = await api_request("GET", url, headers)
        profile_data = profile_result.get("data", {})
        results_list = profile_data.get("results", [])

        if not results_list:
            return {"error": "Could not fetch user profile to update"}

        profile_id = results_list[0].get("id")
        if not profile_id:
            return {"error": "Could not determine profile ID"}

        update_url = build_api_url(base_url, f"userprofile/{profile_id}/")
        return await api_request("PATCH", update_url, headers, json_data=json_data or {})

    elif action == "list_users":
        url = build_api_url(base_url, "gym/userconfig/")
        return await api_request("GET", url, headers)

    elif action == "get_preferences":
        results = {}
        url = build_api_url(base_url, "userprofile/")
        results["profile"] = await api_request("GET", url, headers)
        # Also get language list
        lang_url = build_api_url(base_url, "language/")
        results["languages"] = await api_request("GET", lang_url, headers)
        return results

    elif action == "get_gym_info":
        url = build_api_url(base_url, "gym/gym/")
        return await api_request("GET", url, headers)

    else:
        return {
            "error": f"Unknown action '{action}'. Use: get_profile, update_profile, list_users, get_preferences, get_gym_info"
        }




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
