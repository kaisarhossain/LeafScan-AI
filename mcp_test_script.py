"""
Test script to verify FastMCP server functionality before running Streamlit app.
Run this in PyCharm to debug any connection issues.
"""

import sys
import os
import asyncio

# Import your MCP server
from mcp_server import MCP

async def test_health_check():
    """Test the health_check tool"""
    print("=" * 60)
    print("Test 1: Health Check")
    print("=" * 60)

    try:
        result = await MCP.call_tool("health_check", {})
        print(f"\n✅ Health check executed successfully!")

        # FastMCP returns a list of TextContent objects, extract the actual data
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        # If it's a TextContent object, get the text and parse as JSON
        if hasattr(result, 'text'):
            import json
            result = json.loads(result.text)

        print(f"\nResponse:")
        print(f"  Status: {result.get('status')}")
        print(f"  Backend URL: {result.get('backend_url')}")

        if result.get("status") == "healthy":
            print("\n✅ FastAPI backend is healthy and reachable!")
            return True
        elif result.get("status") == "unreachable":
            print("\n❌ Cannot reach FastAPI backend")
            print(f"  Details: {result.get('details')}")
            print("\n🔧 Troubleshooting:")
            print("  1. Make sure your FastAPI server is running")
            print("  2. Check if it's accessible at http://localhost:8000")
            print("  3. Try: curl http://localhost:8000/health")
            return False
        else:
            print(f"\n⚠️ Backend returned unexpected status")
            print(f"  Full response: {result}")
            return False

    except Exception as e:
        print(f"\n❌ Health check failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

async def test_analyze_plant(image_path: str = None):
    """Test the analyze_plant tool"""
    print("\n" + "=" * 60)
    print("Test 2: Analyze Plant")
    print("=" * 60)

    if not image_path:
        print("\n⚠️ Skipping: No image path provided")
        print("   To test image analysis, provide an image path:")
        print("   python mcp_test_script.py /path/to/your/image.jpg")
        return None

    if not os.path.exists(image_path):
        print(f"\n❌ Image file not found: {image_path}")
        return False

    print(f"\nAnalyzing image: {image_path}")
    print(f"Plant type: potato")

    try:
        result = await MCP.call_tool(
            "analyze_plant",
            {
                "plant": "potato",
                "image_path": image_path
            }
        )

        # FastMCP returns a list of TextContent objects, extract the actual data
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        # If it's a TextContent object, get the text and parse as JSON
        if hasattr(result, 'text'):
            import json
            result = json.loads(result.text)

        if "error" in result:
            print(f"\n❌ Analysis failed: {result['error']}")
            if "details" in result:
                print(f"   Details: {result['details']}")
            return False
        else:
            print("\n✅ Analysis successful!")
            print(f"\nResults:")
            print(f"  Plant: {result.get('plant')}")
            print(f"  Disease: {result.get('predicted_disease')}")
            print(f"  Confidence: {result.get('confidence', 0):.3f}")

            if "explanation" in result:
                exp = result["explanation"]
                print(f"\n  Explanation sections:")
                for key in exp.keys():
                    print(f"    - {key}")

            if "audio_url" in result:
                print(f"\n  Audio URL: {result['audio_url']}")

                # Test audio retrieval
                print("\n  Testing audio retrieval...")
                audio_result = await MCP.call_tool(
                    "play_audio",
                    {"audio_url": result['audio_url']}
                )

                # FastMCP returns a list of TextContent objects, extract the actual data
                if isinstance(audio_result, list) and len(audio_result) > 0:
                    audio_result = audio_result[0]

                # If it's a TextContent object, get the text and parse as JSON
                if hasattr(audio_result, 'text'):
                    import json
                    audio_result = json.loads(audio_result.text)

                if "error" in audio_result:
                    print(f"    ❌ Audio retrieval failed: {audio_result['error']}")
                elif "audio_data" in audio_result:
                    size_kb = audio_result.get('size_bytes', 0) / 1024
                    print(f"    ✅ Audio retrieved successfully ({size_kb:.1f} KB)")

            return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

async def test_get_plant_info():
    """Test the get_plant_info tool"""
    print("\n" + "=" * 60)
    print("Test 3: Get Plant Info")
    print("=" * 60)

    try:
        result = await MCP.call_tool("get_plant_info", {"plant": "potato"})

        # FastMCP returns a list of TextContent objects, extract the actual data
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        # If it's a TextContent object, get the text and parse as JSON
        if hasattr(result, 'text'):
            import json
            result = json.loads(result.text)

        if "error" in result:
            if result.get("error") == "Endpoint not implemented":
                print("\n⚠️ Plant info endpoint not available on FastAPI server")
                print("   This is optional - the main functionality will still work")
                return None
            else:
                print(f"\n❌ Failed: {result['error']}")
                return False
        else:
            print("\n✅ Plant info retrieved successfully!")
            print(f"\nResponse: {result}")
            return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

async def main():
    print("\n🧪 Testing FastMCP Server\n")
    print("This will test your MCP server tools directly (no Streamlit needed)\n")

    # Test 1: Health Check (REQUIRED)
    health_ok = await test_health_check()

    if not health_ok:
        print("\n" + "=" * 60)
        print("⚠️ HEALTH CHECK FAILED")
        print("=" * 60)
        print("\nThe FastAPI backend must be running for the app to work.")
        print("Please start your FastAPI server and try again.\n")
        return

    # Test 2: Analyze Plant (if image provided)
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    if image_path:
        analyze_ok = await test_analyze_plant(image_path)
        if not analyze_ok:
            print("\n⚠️ Image analysis test failed - check the errors above")
    else:
        await test_analyze_plant(None)  # Just show the skip message

    # Test 3: Get Plant Info (OPTIONAL)
    await test_get_plant_info()

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Testing Complete!")
    print("=" * 60)

    if health_ok:
        print("\n✅ Your MCP server is working correctly!")
        print("\nYou can now run the Streamlit app:")
        print("  streamlit run streamlit_app.py")

        if not image_path:
            print("\nTo test image analysis, run:")
            print("  python mcp_test_script.py /path/to/test/image.jpg")
    else:
        print("\n❌ Please fix the issues above before running the Streamlit app")

if __name__ == "__main__":
    asyncio.run(main())