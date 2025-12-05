"""FastAPI Server"""
import dotenv
dotenv.load_dotenv()
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image
import os
from gtts import gTTS
import uuid
from groq import Groq
import json
import re
# Initializing .env

# =========================================================
# FASTAPI + CORS
# =========================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    # return FileResponse("index.html", media_type="text/html")
    return {"API Server is running.."}


# health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FastAPI server is running"}

# =========================================================
# Helper — Load image
# =========================================================
def read_file_as_image(data) -> np.ndarray:
    return np.array(Image.open(BytesIO(data)))


# =========================================================
# ENV VARIABLES
# =========================================================
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise RuntimeError("❌ HF_TOKEN is missing! Set it in your Environment Variables.")

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("❌ GROQ_API_KEY is missing! Set it in your Environment Variables.")

# Groq Client (NO LangChain)
groq_client = Groq(api_key=groq_api_key)

# =========================================================
# HuggingFace Login (LOCAL DEV ONLY)
# =========================================================
if os.getenv("LOCAL_DEV", "false").lower() == "true":
    try:
        from huggingface_hub import login
        print("🔐 Logging into HuggingFace Hub (local only)...")
        login(token=hf_token)
    except Exception as e:
        print("⚠ HuggingFace login skipped:", e)
else:
    print("Production mode — skipping HF login")


# =========================================================
# Load CNN Models
# =========================================================
# POTATO_MODEL = tf.keras.models.load_model("hf://kaisarhossain/potato_disease_model_v2")
# PEPPER_MODEL = tf.keras.models.load_model("hf://kaisarhossain/pepper_disease_model_v2")
# TOMATO_MODEL = tf.keras.models.load_model("hf://kaisarhossain/tomato_disease_model_v2")

# Prediction Models
POTATO_MODEL = tf.keras.models.load_model("models/potato/potato_disease_model_v2.keras")
PEPPER_MODEL = tf.keras.models.load_model("models/pepper/pepper_disease_model_v2.keras")
TOMATO_MODEL = tf.keras.models.load_model("models/tomato/tomato_disease_model_v2.keras")


POTATO_CLASSES = ["Early Blight", "Late Blight", "Healthy"]
PEPPER_CLASSES = ["Bacterial Spot", "Healthy"]
TOMATO_CLASSES = [
    "Target Spot", "Mosaic Virus", "Yellow Leaf Curl Virus", "Bacterial Spot",
    "Early Blight", "Healthy", "Late Blight", "Leaf Mold",
    "Septoria Leaf Spot", "Two Spotted Spider Mite"
]


# =========================================================
# Backup Cure Data (fallback)
# =========================================================
def load_cure_data():
    with open("plant_disease_cure.json", "r") as f:
        return json.load(f)

cure_data = load_cure_data()


# =========================================================
# LLM — Direct Groq API Call
# =========================================================

def clean_llm_json(raw_text: str):
    """
    Removes code fences and extracts JSON objects.
    """
    # Remove markdown code fences ```json ... ```
    cleaned = re.sub(r"```.*?```", lambda m: m.group(0).strip("`"), raw_text, flags=re.DOTALL)

    # If still wrapped, remove any remaining backticks
    cleaned = cleaned.replace("```", "").strip()

    # Extract JSON block explicitly (safest)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": raw_text}


def generate_llm_explanation(plant, disease):
    prompt = f"""
    You are an expert agriculture advisor.

    STRICT RULES:
    - Respond ONLY with valid JSON.
    - Do NOT wrap JSON in backticks.
    - Do NOT include any explanation before or after the JSON.
    - Do NOT use markdown formatting.
    - The JSON must be the ONLY content returned.

    Return a JSON object exactly like this:

    {{
        "disease_overview": "",
        "symptoms": "",
        "cause": "",
        "recommended_treatment": "",
        "prevention_tips": ""
    }}

    Fill each field with accurate information.

    PLANT: {plant}
    DISEASE: {disease}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    # New correct extraction
    return response.choices[0].message.content


# =========================================================
# Audio Agent — GTTS
# =========================================================
def generate_audio(text: str):
    audio_id = f"{uuid.uuid4()}.mp3"
    audio_dir = "audio"

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    file_path = f"{audio_dir}/{audio_id}"

    tts = gTTS(text)
    tts.save(file_path)

    return file_path

def generate_llm_info(plant):
    prompt = f"""
    You are an expert agriculture advisor. Retrieves crisp general information about the crop {plant} in terms of agricultural importance and value. Provide plant {plant} information including common diseases.

    STRICT RULES:
    - Respond ONLY with valid JSON.
    - Do NOT wrap JSON in backticks.
    - Do NOT include any explanation before or after the JSON.
    - Do NOT use markdown formatting.
    - The JSON must be the ONLY content returned.

    Return a JSON object exactly like this:

    {{
        "plant_info": "",
        "common_diseases": ""
    }}

    Fill the field with accurate information.

    PLANT: {plant}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    # New correct extraction
    return response.choices[0].message.content


def generate_llm_video_link(plant, disease):
    prompt = f"""
    You are an expert agriculture advisor. Suggest one most relevant cure YouTube video URL link for Plant {plant} and Disease {disease}.

    STRICT RULES:
    - Provide only a valid YouTube video URL.
    - Respond ONLY with valid JSON.
    - Do NOT wrap JSON in backticks.
    - Do NOT include any explanation before or after the JSON.
    - Do NOT use markdown formatting.
    - The JSON must be the ONLY content returned.

    Return a JSON object exactly like this:

    {{
        "link": ""
    }}

    Fill the field with accurate information.

    PLANT: {plant}
    DISEASE: {disease}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content

# =========================================================
# Agentic Pipeline Endpoint
# =========================================================
@app.post("/analyze")
async def analyze(plant: str, file: UploadFile = File(...)):

    # ------------------ Vision Agent ---------------------
    img = read_file_as_image(await file.read())
    img = np.expand_dims(img, 0)

    if plant.lower() == "potato":
        preds = POTATO_MODEL.predict(img)
        disease = POTATO_CLASSES[int(np.argmax(preds[0]))]

    elif plant.lower() == "pepper":
        preds = PEPPER_MODEL.predict(img)
        disease = PEPPER_CLASSES[int(np.argmax(preds[0]))]

    elif plant.lower() == "tomato":
        preds = TOMATO_MODEL.predict(img)
        disease = TOMATO_CLASSES[int(np.argmax(preds[0]))]

    else:
        raise HTTPException(400, "Invalid plant type. Use potato/pepper/tomato.")

    confidence = float(np.max(preds[0]))

    # ------------------ Language Agent --------------------
    llm_json_str = generate_llm_explanation(plant, disease)

    try:
        explanation = json.loads(llm_json_str)
    except:
        explanation = {"error": "LLM produced invalid JSON", "raw": llm_json_str}

    # ------------------ Audio Agent -----------------------
    if disease.lower() == "healthy":
        speech = (
            f"The {plant} plant, is detected healthy."
        )
    else:
        speech = (
            f"For {plant} plant, the detected disease is {disease}. "
            f"The recommended treatment is: {explanation.get('recommended_treatment', 'No treatment available with me at this moment. Please contact a plant pathologist.')}."
        )

    audio_path = generate_audio(speech)
    audio_url = f"/audio/{audio_path.split('/')[-1]}"

    # ------------------ Final Response --------------------
    return {
        "plant": plant,
        "predicted_disease": disease,
        "confidence": confidence,
        "explanation": explanation,
        "audio_url": audio_url
    }


@app.get("/audio/{filename}")
def serve_audio(filename: str):
    return FileResponse(f"audio/{filename}", media_type="audio/mpeg")


@app.get("/plant_info/{plant}")
async def plant_info(plant: str):
    if plant.lower() in ("potato", "tomato", "pepper"):
        # ------------------ Language Agent --------------------
        llm_json_plant_info = generate_llm_info(plant)

        try:
            info = json.loads(llm_json_plant_info)
        except:
            info = {"error": "LLM produced invalid JSON", "raw": llm_json_plant_info}
    else:
        raise HTTPException(400, "Invalid plant type. Use potato/pepper/tomato.")
    # ------------------ Final Response --------------------
    return {
        "info": info
    }

# @app.get("/video_link/{plant}/{disease}")
# async def video_link(plant: str, disease: str):
#     if plant.lower() in ("potato", "tomato", "pepper"):
#         # ------------------ Language Agent --------------------
#         llm_json_plant_video_link = generate_llm_video_link(plant, disease)
#
#         try:
#             link = json.loads(llm_json_plant_video_link)
#         except:
#             link = {"error": "LLM produced invalid JSON", "raw": llm_json_plant_video_link}
#     else:
#         raise HTTPException(400, "Invalid plant type. Use potato/pepper/tomato.")
#     # ------------------ Final Response --------------------
#     return {
#         "link": link
#     }