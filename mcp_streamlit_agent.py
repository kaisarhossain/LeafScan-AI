"""MCP Server based Streamlit app"""
import streamlit as st
import json
import base64
import tempfile
import os
from pathlib import Path
import asyncio

# Importing MCP server
from mcp_server import MCP

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

# Select plant
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

    with st.spinner("🧠 Running Agentic Pipeline via MCP..."):

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(
                file.name if hasattr(file, 'name') else 'captured_image.png').suffix) as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name

        try:
            # Call MCP analyze_plant tool with asyncio.run()
            result = asyncio.run(MCP.call_tool(
                "analyze_plant",
                {
                    "plant": plant.lower(),
                    "image_path": tmp_path
                }
            ))

            # Call MCP plant_info tool with asyncio.run()
            get_info = asyncio.run(MCP.call_tool(
                "plant_info",
                {
                    "plant": plant.lower()
                }
            ))

            # For analyze_plant: FastMCP returns a list of TextContent objects, extract the actual data
            if isinstance(result, list) and len(result) > 0:
                result = result[0]

            # For plant_info: FastMCP returns a list of TextContent objects, extract the actual data
            if isinstance(get_info, list) and len(get_info) > 0:
                get_info = get_info[0]

            # For analyze_plant: If it's a TextContent object, get the text and parse as JSON
            if hasattr(result, 'text'):
                result = json.loads(result.text)

            # For plant_info: If it's a TextContent object, get the text and parse as JSON
            if hasattr(get_info, 'text'):
                get_info = json.loads(get_info.text)
                # print("get_info:", get_info)

            # For analyze_plant: Check for errors
            if "error" in result:
                st.error(f"❌ Analysis failed: {result['error']}")
                if "details" in result:
                    st.write(f"**Details:** {result['details']}")
                if "status_code" in result:
                    st.write(f"**Status Code:** {result['status_code']}")
                st.stop()

            # For plant_info: Check for errors
            if "error" in get_info:
                st.error(f"❌ Analysis failed: {get_info['error']}")
                if "details" in get_info:
                    st.write(f"**Details:** {get_info['details']}")
                if "status_code" in get_info:
                    st.write(f"**Status Code:** {get_info['status_code']}")
                st.stop()

        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")
            import traceback

            st.code(traceback.format_exc())
            st.stop()
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

    st.success("✅ Analysis Complete!")

    # -------------------------------
    # TWO COLUMNS: Image + Tabs
    # -------------------------------
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("Uploaded/Captured Leaf Image")
        st.image(file, width="stretch")

    with col2:
        tabs = st.tabs(["Prediction", "Cure Details", "Plant Information", "Audio Explanation"])

        # --------- PREDICTION TAB ---------
        with tabs[0]:
            st.subheader("✅ Prediction Result")

            # --- 1. Plant and Disease Name ---
            st.markdown(f"## **Plant:** {result.get('plant', 'Unknown')}")
            disease = result.get('predicted_disease', 'Unknown')

            # Simple color logic: Red if Unknown, Green if a specific disease is found
            disease_color = "red" if disease != 'Healthy' else "green"

            st.markdown(f"""
            **Disease:** <span style="color:{disease_color}; font-weight:bold;">{disease}</span>
            """, unsafe_allow_html=True)

            # --- 2. Confidence Score Display ---
            confidence_score = result.get('confidence', 0)
            confidence_percent = round(confidence_score * 100, 2)

            st.markdown(f"""
            **Confidence:** **{confidence_percent}%**
            """)

            # --- 3. Visual Progress Bar ---
            # Created a progress bar that visually shows the confidence level
            # Add a success message if confidence is high
            if confidence_score > 0.8:
                st.success("High confidence prediction!")

            st.progress(confidence_score)

        # --------- CURE TAB (Enhanced) ---------
        with tabs[1]:
            st.subheader("🏥 Disease Explanation & Cure")
            explanation = result.get("explanation", {})

            if "error" in explanation:
                st.error("⚠️ Error retrieving detailed information.")
                st.warning("Model returned invalid JSON. Showing raw output:")
                st.json(explanation.get("raw", explanation))
            else:
                # Using st.container for better visual grouping
                with st.container(border=True):

                    # 1. Overview and Key Details (Always open and prominent)
                    st.markdown("### 🌿 Disease Overview")
                    st.info(explanation.get('disease_overview', 'No detailed overview available for this condition.'))

                    # 2. Symptoms (Use Expander - initially collapsed)
                    with st.expander("👁️ Symptoms and Identification", expanded=False):
                        symptoms = explanation.get('symptoms', 'No specific symptoms listed.')
                        st.markdown(symptoms)

                    # 3. Cause (Use Expander)
                    with st.expander("☣️ Cause / Pathogen", expanded=False):
                        cause = explanation.get('cause', 'No specific cause identified.')
                        st.markdown(f"**Pathogen/Factor:** {cause}")

                    st.markdown("---")  # Separator for Cure section

                    # 4. Treatment / Cure (Use a bolder section)
                    st.markdown("### 💊 Recommended Treatment (Cure)")
                    treatment = explanation.get('recommended_treatment', 'No specific treatment recommended.')
                    st.success(treatment)

                    # 5. Prevention Tips (Use Expander)
                    with st.expander("🛡️ Prevention Tips", expanded=False):
                        tips = explanation.get('prevention_tips', 'No preventative measures provided.')
                        # Using bullet points makes tips more readable
                        if tips != 'No preventative measures provided.':
                            for tip in tips.split('.'):
                                if tip.strip():
                                    st.markdown(f"* {tip.strip()}.")
                        else:
                            st.markdown(tips)

        # --------- PLANT INFO TAB (Enhanced) ---------
        with tabs[2]:
            st.subheader("🌿 Plant Quick Facts")
            info = get_info.get("info", {})

            plant_info = info.get('plant_info', 'No detailed information available.')
            diseases_str = info.get('common_diseases', 'No specific common diseases listed.')

            if "error" in info:
                st.error("⚠️ Error retrieving detailed plant information.")
                st.warning("Model returned invalid JSON. Showing raw output:")
                st.json(info.get("raw", info))
            else:

                # 1. Detailed Information (Collapsed by default)
                with st.expander("📘 About the Plant", expanded=False):
                    st.markdown(plant_info)
                # 2. Common Diseases (Prominently displayed)
                with st.expander("🦠 Common Diseases", expanded=False):
                    st.markdown(diseases_str)

        # Video Link Tab : Currently Not in use
        # --------- VIDEO LINK TAB ---------

        # with tabs[3]:
        #     st.subheader("🎦 Video Link")
        #
        #     disease = result.get('predicted_disease', 'Unknown')
        #
        #     try:
        #         # Call MCP video_link tool with asyncio.run()
        #         get_link = asyncio.run(MCP.call_tool(
        #             "video_link",
        #             {
        #                 "plant": plant.lower(),
        #                 "disease": disease.lower()
        #             }
        #         ))
        #
        #         # For plant_info: FastMCP returns a list of TextContent objects, extract the actual data
        #         if isinstance(get_link, list) and len(get_link) > 0:
        #             get_link = get_link[0]
        #
        #         # For plant_info: If it's a TextContent object, get the text and parse as JSON
        #         if hasattr(get_link, 'text'):
        #             get_link = json.loads(get_link.text)
        #             print("get_info:", get_link)
        #
        #         # For video_link: Check for errors
        #         if "error" in get_info:
        #             st.error(f"❌ Analysis failed: {get_link['error']}")
        #             if "details" in get_info:
        #                 st.write(f"**Details:** {get_link['details']}")
        #             if "status_code" in get_info:
        #                 st.write(f"**Status Code:** {get_link['status_code']}")
        #             st.stop()
        #
        #     except Exception as e:
        #         st.error(f"❌ Error during analysis: {e}")
        #         import traceback
        #
        #         st.code(traceback.format_exc())
        #         st.stop()
        #     finally:
        #         # Clean up temp file
        #         try:
        #             os.unlink(tmp_path)
        #         except:
        #             pass
        #
        #     # Displaying the video link
        #     link = get_link.get("link", {})
        #     video_url = link.get('link', None)  # Extract the video URL
        #
        #     if "error" in info:
        #         st.warning("⚠️ Model returned invalid JSON. Showing raw output.")
        #         st.json(info.get("raw", link))
        #     else:
        #         st.markdown(f"""
        #                     **Video Link:** {video_url if video_url else 'No video link available'}
        #                     """)
        #
        #         # --- Video Display and Controls ---
        #         if video_url:
        #             # st.video() displays the video player with native play/pause/controls.
        #             st.video(video_url)
        #         else:
        #             st.info("Please select a plant to view related video information.")

        # --------- AUDIO TAB WITH AUTOPLAY ---------
        with tabs[3]:
            st.subheader("🔊 Audio Explanation")
            if "audio_url" in result and result["audio_url"]:
                with st.spinner("Loading audio..."):
                    try:
                        # Get audio via MCP play_audio tool with asyncio.run()
                        audio_result = asyncio.run(MCP.call_tool(
                            "play_audio",
                            {"audio_url": result['audio_url']}
                        ))

                        # FastMCP returns a list of TextContent objects, extract the actual data
                        if isinstance(audio_result, list) and len(audio_result) > 0:
                            audio_result = audio_result[0]

                        # If it's a TextContent object, get the text and parse as JSON
                        if hasattr(audio_result, 'text'):
                            audio_result = json.loads(audio_result.text)

                        if "error" in audio_result:
                            st.error(f"Could not load audio: {audio_result['error']}")
                            if "details" in audio_result:
                                st.write(audio_result["details"])
                        elif "audio_data" in audio_result:
                            # Decode base64 audio
                            audio_bytes = base64.b64decode(audio_result["audio_data"])
                            audio_format = audio_result.get('format', 'mp3')

                            # Create audio player with autoplay
                            audio_base64 = audio_result["audio_data"]
                            st.markdown(f"""
                            <audio autoplay controls>
                                <source src="data:audio/{audio_format};base64,{audio_base64}" type="audio/{audio_format}">
                                Your browser does not support the audio element.
                            </audio>
                            """, unsafe_allow_html=True)

                            # Show audio info
                            size_kb = audio_result.get('size_bytes', 0) / 1024
                            st.caption(f"Audio size: {size_kb:.1f} KB")
                        else:
                            st.warning("No audio data in response")

                    except Exception as e:
                        st.error(f"Failed to load audio: {e}")
            else:
                st.info("Audio explanation not available for this analysis.")

st.info("Use the sidebar to upload/capture another image or change plant type.")

st.markdown("---")
st.markdown("The Catholic University of America")
st.markdown("Powered by: Computer Vision • LLM • Acoustic AI • MCP & Agentic AI")