"""MCP Server"""
from mcp.server.fastmcp import FastMCP
import requests
import base64
from pathlib import Path
from typing import Optional

MCP = FastMCP("plant-diagnosis-mcp")

FASTAPI_URL = "http://localhost:8000"

# Server Healthcheck
@MCP.tool()
def health_check() -> dict:
    """
    Checks if the FastAPI backend is accessible and healthy.

    Returns:
        Dictionary with health status information
    """
    try:
        resp = requests.get(f"{FASTAPI_URL}/health", timeout=5)

        if resp.status_code == 200:
            return {
                "status": "healthy",
                "backend_url": FASTAPI_URL,
                "response": resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text
            }
        else:
            return {
                "status": "unhealthy",
                "status_code": resp.status_code,
                "details": resp.text
            }

    except requests.exceptions.ConnectionError:
        return {
            "status": "unreachable",
            "details": f"Cannot connect to FastAPI server at {FASTAPI_URL}"
        }
    except Exception as e:
        return {"status": "error", "details": str(e)}

# Analyzing Plant Disease and Cure
@MCP.tool()
def analyze_plant(plant: str, image_path: str) -> dict:
    """
    Analyzes a plant image for diseases using the FastAPI backend.

    Args:
        plant: Type of plant - must be one of: 'potato', 'tomato', 'pepper'
        image_path: Local filesystem path to the plant image

    Returns:
        Dictionary containing diagnosis results with disease classification,
        confidence scores, and treatment recommendations
    """
    # Validate plant type
    valid_plants = ["potato", "tomato", "pepper"]
    if plant.lower() not in valid_plants:
        return {
            "error": "Invalid plant type",
            "details": f"Plant must be one of: {', '.join(valid_plants)}"
        }

    # Validate file exists
    image_file = Path(image_path)
    if not image_file.exists():
        return {
            "error": "File not found",
            "details": f"Image file does not exist: {image_path}"
        }

    # Determine MIME type
    mime_type = "image/jpeg"
    if image_file.suffix.lower() in ['.png']:
        mime_type = "image/png"
    elif image_file.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"

    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_file.name, f, mime_type)}
            params = {"plant": plant.lower()}

            resp = requests.post(
                f"{FASTAPI_URL}/analyze",
                params=params,
                files=files,
                timeout=30
            )

        if resp.status_code != 200:
            return {
                "error": "FastAPI error",
                "status_code": resp.status_code,
                "details": resp.text
            }

        return resp.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "details": "FastAPI server did not respond within 30 seconds"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed", "details": f"Could not connect to FastAPI server at {FASTAPI_URL}"}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}


# Playing Audio
@MCP.tool()
def play_audio(audio_url: str) -> dict:
    """
    Retrieves an audio file from the FastAPI server and returns it as base64.

    Args:
        audio_url: The URL path to the audio file (e.g., '/audio/result.mp3')

    Returns:
        Dictionary with base64 encoded audio data and metadata, or error information
    """
    # Ensure URL starts with /
    if not audio_url.startswith('/'):
        audio_url = '/' + audio_url

    full_url = f"{FASTAPI_URL}{audio_url}"

    try:
        resp = requests.get(full_url, timeout=30)

        if resp.status_code != 200:
            return {
                "error": "Failed to download audio",
                "status_code": resp.status_code,
                "details": resp.text
            }

        audio_base64 = base64.b64encode(resp.content).decode("utf-8")

        # Determine audio format from URL or content-type
        audio_format = "mp3"  # default
        if audio_url.endswith('.wav'):
            audio_format = "wav"
        elif audio_url.endswith('.ogg'):
            audio_format = "ogg"

        return {
            "success": True,
            "audio_data": audio_base64,
            "format": audio_format,
            "size_bytes": len(resp.content)
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed", "details": f"Could not connect to {FASTAPI_URL}"}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}


# Fetching Information on the Plant
@MCP.tool()
def plant_info(plant: str) -> dict:
    """
    Retrieves general information about supported plant types in terms of agricultural importance and value.


    Args:
        plant: Type of plant - 'potato', 'tomato', or 'pepper'

    Returns:
        Dictionary with plant information including common diseases
    """
    valid_plants = ["potato", "tomato", "pepper"]
    if plant.lower() not in valid_plants:
        return {
            "error": "Invalid plant type",
            "supported_plants": valid_plants
        }

    try:
        resp = requests.get(
            f"{FASTAPI_URL}/plant_info/{plant.lower()}",
            timeout=10
        )

        if resp.status_code == 404:
            return {
                "error": "Endpoint not implemented",
                "details": "FastAPI server does not have /plant_info endpoint"
            }

        if resp.status_code != 200:
            return {"error": "API error", "details": resp.text}

        return resp.json()

    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed"}
    except Exception as e:
        return {"error": str(e)}


# @MCP.tool()
# def video_link(plant: str, disease: str) -> dict:
#     """
#     Retrieves video link information about supported plant and the type of the disease.
#
#     Args:
#         plant: Type of plant - 'potato', 'tomato', or 'pepper'
#         disease: Type of plant disease for- 'potato', 'tomato', or 'pepper' plants
#
#     Returns:
#         YouTube video link with plant and disease information
#     """
#     valid_plants = ["potato", "tomato", "pepper"]
#     if plant.lower() not in valid_plants:
#         return {
#             "error": "Invalid plant type",
#             "supported_plants": valid_plants
#         }
#
#     try:
#         resp = requests.get(
#             f"{FASTAPI_URL}/video_link/{plant.lower()}/{disease.lower()}",
#             timeout=10
#         )
#
#         if resp.status_code == 404:
#             return {
#                 "error": "Endpoint not implemented",
#                 "details": "FastAPI server does not have /video_link endpoint"
#             }
#
#         if resp.status_code != 200:
#             return {"error": "API error", "details": resp.text}
#
#         return resp.json()
#
#     except requests.exceptions.ConnectionError:
#         return {"error": "Connection failed"}
#     except Exception as e:
#         return {"error": str(e)}


if __name__ == "__main__":
    MCP.run()