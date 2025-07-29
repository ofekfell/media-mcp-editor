#!/usr/bin/env python3
"""
Test the proper split implementation
"""

from media_mcp_handler.media_mcp import MediaMCPHandler, send_response
import pathlib

# Test video paths
TESTS_DIR = pathlib.Path(__file__).parent 
ASSETS_DIR = TESTS_DIR / "assets"
TEST_VIDEO = str(ASSETS_DIR / "test_1_16_9.mp4")

def test_duplicate_input_concat():
    """Test concatenating the same video file twice"""
    handler = MediaMCPHandler()
    workflow = {
        'action': 'concat',
        'input': [
            TEST_VIDEO,  # Same file
            TEST_VIDEO   # Same file again
        ]
    }
    try:
        result = handler.render_workflow(workflow)
        response = send_response(result=result)
        
        # Check if we got a successful result (result_path) or an error
        if 'error' in response:
            print(f"FAILED: Proper split concat failed: {response['error']}")
            return False
        elif 'result' in response and 'result_path' in response['result']:
            print("SUCCESS: Proper split concat worked!")
            print(f"Output file: {response['result']['result_path']}")
            return True
        else:
            print(f"FAILED: Unexpected response format: {response}")
            return False
    except Exception as e:
        print(f"FAILED: Proper split concat failed with exception: {e}")
        return False

def test_triple_usage():
    """Test using the same file three times in a complex workflow"""
    handler = MediaMCPHandler()
    workflow = {
        'action': 'concat',
        'input': [
            TEST_VIDEO,  # Usage 1
            TEST_VIDEO,  # Usage 2  
            TEST_VIDEO   # Usage 3
        ]
    }
    try:
        result = handler.render_workflow(workflow)
        response = send_response(result=result)
        
        if 'result' in response and 'result_path' in response['result']:
            print("SUCCESS: Triple usage worked!")
            print(f"Output file: {response['result']['result_path']}")
            return True
        elif 'error' in response:
            print(f"FAILED: Triple usage failed: {response['error']}")
            return False
        else:
            print(f"FAILED: Unexpected response format: {response}")
            return False
    except Exception as e:
        print(f"FAILED: Triple usage failed with exception: {e}")
        return False