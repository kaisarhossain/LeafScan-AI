# 🌱 LeafScan AI: Plant Disease Detection using Agentic AI with MCP

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)]()
[![MCP](https://img.shields.io/badge/MCP-Agentic%20Tools-purple.svg)]()

> **An agentic‑AI powered plant health assistant for early disease
> detection, explanations, cures, and audio guidance.**

------------------------------------------------------------------------

## 🚀 Overview

This application is an **Agentic AI Plant Disease Diagnosis System**
powered by:

-   **MCP Server (FastMCP)** exposing AI tools\
-   **FastAPI backend** hosting CNN models + LLM + Audio generator\
-   **Agent‑based tool calling**, enabling reasoning-driven workflows

Users can:

-   Upload an image of **Potato, Tomato, or Pepper** leaves\
-   Automatically detect the plant disease using CNN models\
-   Generate detailed explanations using LLM\
-   Get spoken audio advice\
-   Retrieve plant-level details using a second agentic tool

The Streamlit app interacts *only* with the **MCP Server**, which
orchestrates the entire tool-calling workflow---making the solution
scalable, modular, and easy to extend.

------------------------------------------------------------------------

## ✨ Key Features

### 🌿 **Plant Disease Classification**

-   Upload an image\
-   Select plant type\
-   CNN model identifies the disease\
-   Displays confidence score

### 🤖 **Language Agent: Disease Explanation & Cure**

-   LLM generates:
    -   Overview\
    -   Symptoms\
    -   Causes\
    -   Recommended treatment\
    -   Prevention tips

### 🔊 **Audio Agent**

-   Converts diagnosis + cure into speech\
-   Plays audio in‑app

### 📘 **Plant Information Tool**

-   Provides:
    -   Plant description\
    -   Nutritional/usage details\
    -   Cultivation brief\
-   Triggered regardless of disease state

### ⚙️ **Agentic + MCP Architecture**

-   Streamlit → MCP Client\
-   MCP Client → MCP Server (Tools exposed via FastMCP)\
-   MCP Server → FastAPI → ML Models + LLM + TTS

------------------------------------------------------------------------

## 🧠 Why Agentic AI?

Using an **agentic model** enables:

1.  **Reasoning-driven tool calling**
    -   The agent decides *which* backend tool to call and *in what
        order*.
2.  **Modular scalability**
    -   CNN, LLM, and Audio generator are separate tools.
3.  **Fault tolerance**
    -   If JSON is malformed, the agent can retry or request
        clarification.
4.  **Autonomy**
    -   The AI behaves as an orchestrator, not just a passive model.
5.  **Reusability**
    -   Tools can be used by other apps (mobile, API integrations,
        etc.).

This design closely resembles modern industry-grade **Agentic
Orchestration Systems**.

------------------------------------------------------------------------

## 🏗️ System Architecture

### **High-Level Structure**

    Streamlit UI (MCP Client)
            │
            ▼
    MCP Server (FastMCP)
            ├── analyze_plant (Tool)
            └── plant_info   (Tool)
            └── play_audio   (Tool)
            │
            ▼
    FastAPI Backend
    │
    ├── /analyze  → Vision + LLM + TTS pipeline
    └── /plant_info → LLM-based botanical information
    └── /play_audio → gTTS-based audio generation

------------------------------------------------------------------------

## 🔄 Agentic Flow Diagram

    User Uploads Image + Selects Plant
                   │
                   ▼
           Streamlit (MCP Client)
                   │ calls tool
                   ▼
            MCP Server (FastMCP)
                   │ calls API
                   ▼
               FastAPI Server
        ┌────────────┬──────────────┬─────────────┐
        │ Vision CNN │  LLM Agent   │ Audio Agent │
        └────────────┴──────────────┴─────────────┘
                   │ returns results
                   ▼
            MCP Server aggregates
                   ▼
         Streamlit displays results

------------------------------------------------------------------------

## 🧩 Components

### **1. Streamlit App (MCP Client)**

-   UI for uploading images
-   Calls MCP tools
-   Displays:
    -   Disease result
    -   Confidence
    -   LLM explanation
    -   Plant info
    -   Audio playback

### **2. MCP Server (FastMCP)**

Exposes the following tools:

  -----------------------------------------------------------------------
  Tool Name                                Description
  ---------------------------------------- ------------------------------
  `analyze_plant`                          Calls FastAPI `/analyze` for
                                           disease classification, LLM
                                           explanation, and audio
                                           generation

  `plant_info`                             Calls `/plant_info` for
                                           general plant details

  `play_audio`                             Calls `/play_audio` for
                                           playing the solution audio

  -----------------------------------------------------------------------

### **3. FastAPI Backend**

Contains: - **CNN models** (Potato, Tomato, Pepper) - **LLM explanation
generator** - **gTTS audio agent** - **Endpoints:** `/analyze`,
`/plant_info`, `/audio/{file}`

------------------------------------------------------------------------

## 🛠️ Installation & Setup

1.  Clone repository:

``` bash
git clone <repo-url>
cd plant-agentic-ai
```

2.  Install dependencies:

``` bash
pip install -r requirements.txt
```

3.  Start FastAPI server:

``` bash
uvicorn main:app --reload
```

4.  Start MCP Server:

``` bash
python mcp_server.py
```

5.  Run Streamlit UI:

``` bash
streamlit run app.py
```

------------------------------------------------------------------------

## 📁 Project Structure

    project/
    ├── fastapi_server.py       # FastAPI server exposing api
    ├── mcp_server.py           # FastMCP server accessing api and exposing tools
    ├── app.py                  # Streamlit frontend (Non-MCP client) for Hugging Face deployment/use
    ├── app_local.py            # Streamlit frontend (Non-MCP client) for local use
    ├── mcp_streamlit_agent.py  # Streamlit frontend (MCP Client/Agent) for lcoal use
    ├── mcp_test_script.py      # Testing MCP server Health
    ├── models/                 # Dir: Trained CNN models
    ├── audio/                  # Dir: Generated TTS/audio files
    ├── plant_diseasecure.json  # File for defaut solution as failover
    └── requirements.txt

------------------------------------------------------------------------

## ⚠️ Disclaimer

This tool is for **educational and agricultural assistance**, not a
replacement for certified agronomists or plant pathologists.

------------------------------------------------------------------------

## 👤 Author

**Kaisar Hossain**\
GitHub Portfolio: https://kaisarhossain.github.io/portfolio/
