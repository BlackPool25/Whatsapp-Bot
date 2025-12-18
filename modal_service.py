"""
Modal Service - Handles Modal API calls for multimodal deepfake detection
"""
import os
import requests
from typing import Dict, Optional

# Modal API Configuration - Multimodal Detection
# Video: https://modal.com/apps/blackpool25/main/deployed/deepfake-detector-balanced-3layer
# Image: https://modal.com/apps/blackpool25/main/deployed/ai-vs-real-detector
# Text: https://modal.com/apps/blackpool25/main/deployed/ai-text-detector
MODAL_VIDEO_API_URL = os.getenv("MODAL_VIDEO_API_URL", "https://blackpool25--deepfake-detector-balanced-3layer-detect-video.modal.run")
MODAL_IMAGE_API_URL = os.getenv("MODAL_IMAGE_API_URL", "https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run")
MODAL_TEXT_API_URL = os.getenv("MODAL_TEXT_API_URL", "https://blackpool25--ai-text-detector-detect-endpoint.modal.run")
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
        # Modal FastAPI endpoint expects query parameters for simple types
        endpoint = MODAL_VIDEO_API_URL
        
        params = {
            "video_url": video_url,
            "enable_fail_fast": enable_fail_fast
        }
        
        headers = {}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        print(f"[Modal Service] Calling {endpoint}")
        print(f"[Modal Service] Video URL: {video_url}")
        
        response = requests.post(
            endpoint,
            params=params,  # Use params, not json for FastAPI function parameters
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


# Image and Text detection functions
def detect_image_ai(file_content: bytes, mime_type: str = "image/jpeg") -> Dict:
    """
    Detect AI-generated images using Modal endpoint
    
    Args:
        file_content: Image file bytes
        mime_type: MIME type of image
    
    Returns:
        dict: Detection result with predictions, top_prediction, confidence
        {
            "predictions": [{"label": "REAL"|"AI", "score": float}],
            "top_prediction": "REAL"|"AI",
            "confidence": float (0-1)
        }
    """
    try:
        import base64
        
        # Convert image bytes to base64
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        url = f"{MODAL_IMAGE_API_URL}/predict"
        payload = {
            "image": image_base64,
            "return_all_scores": True
        }
        
        headers = {"Content-Type": "application/json"}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        print(f"[Modal Service] Detecting image at {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"[Modal Service] Image detection complete: {result.get('top_prediction')}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Image detection error: {e}")
        raise ModalDetectionError(f"Image detection failed: {str(e)}")


def detect_text_ai(text: str) -> Dict:
    """
    Detect AI-generated text using Modal endpoint
    
    Args:
        text: Text content to analyze (minimum 20 characters)
    
    Returns:
        dict: Detection result
        {
            "success": bool,
            "result": {
                "prediction": "AI"|"Human"|"UNCERTAIN",
                "is_ai": bool,
                "confidence": float (0-1),
                "confidence_percent": str,
                "agreement": str
            },
            "error": str (if success=false)
        }
    """
    try:
        # Validate minimum length
        if len(text.strip()) < 20:
            return {
                "success": False,
                "error": "Text too short",
                "detail": "Minimum 20 characters required"
            }
        
        url = MODAL_TEXT_API_URL
        
        payload = {
            "text": text,
            "format": "web",
            "include_breakdown": True,
            "enable_provenance": False
        }
        
        headers = {"Content-Type": "application/json"}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        print(f"[Modal Service] Detecting text at {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            print(f"[Modal Service] Text detection complete: {result['result']['prediction']}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Text detection error: {e}")
        raise ModalDetectionError(f"Text detection failed: {str(e)}")
