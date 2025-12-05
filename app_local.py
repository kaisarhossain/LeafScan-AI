"""Non-MCP Streamlit version 2."""
import streamlit as st
import requests


# -------------------------------
# FASTAPI BACKEND URL
# -------------------------------
BASE_URL = "http://127.0.0.1:8000"

# -------------------------------
# STREAMLIT UI SETUP
# -------------------------------
st.set_page_config(page_title="LeafScan AI", layout="wide", page_icon="🌿")

# -------------------------------
# CUSTOM CSS FOR MOBILE-FRIENDLY DESIGN
# -------------------------------
st.markdown("""
<style>
body, .block-container { padding: 0.5rem 1rem; max-width: 100%; margin: auto; background: linear-gradient(to bottom right, #e0f7fa, #e8f5e9); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
h1 { color: #2e7d32; text-align: center; font-size: 1.8rem; }
.section-container { background-color: rgba(255, 255, 255, 0.85); padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px; }
.stButton>button { background-color: #43a047; color: white; font-weight: bold; border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.9rem; }
.stButton>button:hover { background-color: #2e7d32; }
img { border-radius: 12px; max-width: 100%; height: auto; }
@media (max-width: 600px) { .stColumns { flex-direction: column !important; } .stButton>button { width: 100%; } h1 { font-size: 1.5rem; } h2,h3,h4 { font-size: 0.95rem; } }
</style>
""", unsafe_allow_html=True)
# -------------------------------
# SIDEBAR FOR INPUTS
# -------------------------------
st.sidebar.header("🌿 LeafScan AI")
st.sidebar.write("Upload or capture a leaf image to detect plant disease.")

plant = st.sidebar.selectbox("Select Plant Type:", ["Potato", "Tomato", "Pepper"])

# Allow file upload
file = st.sidebar.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

# Allow camera capture
camera_image = st.sidebar.camera_input("Or Capture from Camera")

# Use camera image if available
if camera_image is not None:
    file = camera_image


# -------------------------------
# MAIN AREA
# -------------------------------
st.title("🌿 LeafScan AI - Plant Health Dashboard")
st.write(
    "LeafScan AI is AI powered plant doctor designed to help gardeners, farmers, and plant researchers quickly identify plant diseases and receive detail guidance for healthy crop management.")
st.write(
    "Detect plant diseases and get actionable guidance for healthy crops.")
st.markdown("---")
# -------------------------------
# BUTTON & ANALYSIS
# -------------------------------
if st.sidebar.button("🔍 Analyze Plant Health"):
    if file is None:
        st.sidebar.error("Please upload or capture an image.")
        st.stop()

    with st.spinner("🧠 Running Agentic Pipeline..."):
        files = {"file": (file.name if hasattr(file, 'name') else 'captured_image.png', file.getvalue(), file.type)}
        params = {"plant": plant}
        # URL for Analyze
        url_analyze = f"{BASE_URL}{'/analyze'}"
        # URL for Plant Info
        endpoint_info = f"/plant_info/{plant.lower()}"
        url_info = f"{BASE_URL}{endpoint_info}"

        try:
            response = requests.post(url_analyze, params=params, files=files)
            response.raise_for_status()
            result = response.json()

            info = requests.get(url_info, timeout=10)
            info.raise_for_status()
            info_json = info.json()

        except Exception as e:
            st.sidebar.error(f"❌ Could not connect to FastAPI server.\n{e}")
            st.stop()

    st.success("✅ Analysis Complete!")

    # --- AUTOPLAY AUDIO IMPLEMENTATION ---
    audio_endpoint = None
    if "audio_url" in result:
        audio_endpoint = f"http://127.0.0.1:8000{result['audio_url']}"

        # Inject invisible HTML audio element with autoplay attribute
        autoplay_html = f"""
            <audio controls autoplay style="display:none;">
                <source src="{audio_endpoint}" type="audio/mp3">
            </audio>
        """
        st.markdown(autoplay_html, unsafe_allow_html=True)

    # -------------------------------
    # TWO COLUMNS: Image + Tabs
    # -------------------------------
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("Uploaded/Captured Leaf Image")
        st.image(file, use_container_width=True)

    with col2:
        tabs = st.tabs(["Prediction", "Cure Details", "Plant Information", "Audio Explanation"])

        # --------- PREDICTION TAB ---------
        with tabs[0]:
            st.subheader("Prediction Result")
            st.markdown(f"""
            **Plant:** {result['plant']}  
            **Disease:** `{result['predicted_disease']}`  
            **Confidence:** `{round(result['confidence'], 2)}`  
            """)

        # --------- CURE TAB ---------
        with tabs[1]:
            st.subheader("🏥 Disease Explanation & Cure")
            explanation = result["explanation"]

            if "error" in explanation:
                st.warning("⚠ Model returned invalid JSON. Showing raw output.")
                st.json(explanation["raw"])
            else:
                # st.markdown(f"""
                # **🩺 Overview:** {explanation['disease_overview']}
                # **👁 Symptoms:** {explanation['symptoms']}
                # **☣ Cause:** {explanation['cause']}
                # **💊 Treatment:** {explanation['recommended_treatment']}
                # **🛡 Prevention Tips:** {explanation['prevention_tips']}
                # """)

                # Using st.container for better visual grouping
                with st.container(border=True):

                    # 1. Overview and Key Details (Always open and prominent)
                    st.markdown("### 🌿 Disease Overview")
                    st.info(explanation['disease_overview'])

                    # 2. Symptoms (Use Expander - initially collapsed)
                    with st.expander("👁️ Symptoms and Identification", expanded=False):
                        symptoms = explanation['symptoms']
                        st.markdown(symptoms)

                    # 3. Cause (Use Expander)
                    with st.expander("☣️ Cause / Pathogen", expanded=False):
                        cause = explanation['cause']
                        st.markdown(cause)

                    st.markdown("---")  # Separator for Cure section

                    # 4. Treatment / Cure (Use a bolder section)
                    st.markdown("### 💊 Recommended Treatment (Cure)")
                    treatment = explanation['recommended_treatment']
                    st.success(treatment)

                    # 5. Prevention Tips (Use Expander)
                    with st.expander("🛡️ Prevention Tips", expanded=False):
                        tips = explanation['prevention_tips']
                        # Using bullet points makes tips more readable
                        if tips != 'No preventative measures provided.':
                            for tip in tips.split('.'):
                                if tip.strip():
                                    st.markdown(f"* {tip.strip()}.")
                        else:
                            st.markdown(tips)

        # --------- PLANT INFO ---------
        with tabs[2]:
            st.subheader("🌿 Plant Quick Facts")
            plant_info = info_json["info"]

            if "error" in plant_info:
                st.warning("⚠ Model returned invalid JSON. Showing raw output.")
                st.json(plant_info["raw"])
            else:
                # 1. Detailed Information (Collapsed by default)
                with st.expander(
                        "📘 About the Plant", expanded=False):
                    st.markdown(f"""{plant_info['plant_info']}  """)
                # 2. Common Diseases (Prominently displayed)
                with st.expander("🦠 Common Diseases", expanded=False):
                    st.markdown(f"""{plant_info['common_diseases']}  """)

        # --------- AUDIO TAB WITH AUTOPLAY ---------
        with tabs[3]:
            st.subheader("🔊 Audio Explanation")
            if "audio_url" in result:
                audio_endpoint = f"http://127.0.0.1:8000{result['audio_url']}"
                st.audio(audio_endpoint, format="audio/mp3")
            else:
                st.info("Audio explanation not available for this analysis.")

st.info("Use the sidebar to upload/capture another image or change plant type.")

st.markdown("---")
st.markdown("Created by: Kaisar Hossain | GitHub: https://kaisarhossain.github.io/projects/")
st.markdown("Powered by: Computer Vision, LLM, Acoustic AI & Agentic AI.")