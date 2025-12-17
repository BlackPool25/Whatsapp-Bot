"""
Modal Service - Handles Modal API calls for multimodal deepfake detection
"""
import os
import requests
from typing import Dict, Optional

# Modal API Configuration - Balanced 3-Layer Detection Pipeline
# Deployed: https://modal.com/apps/blackpool25/main/deployed/deepfake-detector-balanced-3layer
MODAL_VIDEO_API_URL = os.getenv("MODAL_VIDEO_API_URL", "https://blackpool25--deepfake-detector-balanced-3layer-detect-video.modal.run")
MODAL_API_KEY = os.getenv("MODAL_API_KEY")  # Optional


class ModalDetectionError(Exception):
    """Custom exception for Modal API errors"""
    pass


def detect_video_multimodal(
    video_url: str, 
    enable_fail_fast: bool = False,
    callback_url: Optional[str] = None, 
    task_id: Optional[str] = None
) -> Dict:
    """
    Send video to Modal balanced 3-layer deepfake detection API
    
    Args:
        video_url: Public URL to video file
        enable_fail_fast: Stop early if Layer 1 very confident (>0.8)
        callback_url: Optional webhook for async result callback (not yet implemented)
        task_id: Optional task ID for tracking
    
    Returns:
        dict: Detection result from balanced 3-layer pipeline
        {
            "video_path": str,
            "final_verdict": str,  # "FAKE" or "REAL"
            "confidence": float,  # 0-1 scale
            "stopped_at_layer": str,
            "layer_results": [
                {
                    "layer_name": str,
                    "is_fake": bool,
                    "confidence": float,
                    "processing_time": float,
                    "details": dict
                }
            ],
            "total_time": float
        }
    
    Raises:
        ModalDetectionError: If API call fails
    """
    try:
        # Direct endpoint (not /detect-video suffix)
        endpoint = MODAL_VIDEO_API_URL
        
        payload = {
            "video_url": video_url,
            "enable_fail_fast": enable_fail_fast
        }
        
        headers = {"Content-Type": "application/json"}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        print(f"[Modal Service] Calling {endpoint} with video: {video_url}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=120  # Increased timeout for video processing
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Check for errors
        if "error" in result:
            raise ModalDetectionError(result["error"])
        
        print(f"[Modal Service] Detection complete: {result.get('final_verdict')} ({result.get('confidence', 0):.2%})")
        print(f"[Modal Service] Stopped at: {result.get('stopped_at_layer')}, Total time: {result.get('total_time', 0):.2f}s")
        
        return result
    
    except requests.exceptions.Timeout:
        print(f"Modal API timeout after 120s")
        raise ModalDetectionError("Video processing timed out. Please try a shorter video.")
    except requests.exceptions.RequestException as e:
        print(f"Modal API error: {e}")
        raise ModalDetectionError(f"Failed to process video: {str(e)}")


def check_detection_status(task_id: str) -> Dict:
    """
    Check status of a detection task
    
    Args:
        task_id: Task ID to check
    
    Returns:
        dict: Status information including result if completed
    """
    try:
        endpoint = f"{MODAL_VIDEO_API_URL}/status/{task_id}"
        
        headers = {}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Status check error: {e}")
        raise ModalDetectionError(f"Failed to check status: {str(e)}")


# Keep the old image detection function for backward compatibility
def detect_image_ai(file_content: bytes, mime_type: str = "image/jpeg") -> Dict:
    """
    Legacy image detection function (uses old Modal endpoint)
    For images only - videos should use detect_video_multimodal
    """
    old_modal_url = os.getenv("MODAL_API_URL", "https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run")
    
    try:
        url = f"{old_modal_url}/predict"
        files = {"file": ("image.jpg", file_content, mime_type)}
        
        response = requests.post(url, files=files, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Image detection error: {e}")
        raise ModalDetectionError(f"Image detection failed: {str(e)}")
