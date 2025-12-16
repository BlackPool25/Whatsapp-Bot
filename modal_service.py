"""
Modal Service - Handles Modal API calls for multimodal deepfake detection
"""
import os
import requests
from typing import Dict, Optional

# Modal API Configuration
MODAL_VIDEO_API_URL = os.getenv("MODAL_VIDEO_API_URL", "https://your-modal-app.modal.run")  # Update after deployment
MODAL_API_KEY = os.getenv("MODAL_API_KEY")  # Optional


class ModalDetectionError(Exception):
    """Custom exception for Modal API errors"""
    pass


def detect_video_multimodal(video_url: str, callback_url: Optional[str] = None, task_id: Optional[str] = None) -> Dict:
    """
    Send video to Modal multimodal detection API
    
    Args:
        video_url: Public URL to video file
        callback_url: Optional webhook for async result callback
        task_id: Optional task ID for tracking
    
    Returns:
        dict: {
            "task_id": str,
            "status": str,
            "message": str
        }
    
    Raises:
        ModalDetectionError: If API call fails
    """
    try:
        endpoint = f"{MODAL_VIDEO_API_URL}/detect_video"
        
        payload = {
            "video_url": video_url,
            "callback_url": callback_url,
            "task_id": task_id
        }
        
        headers = {}
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30  # Just for initiating the task
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Modal API error: {e}")
        raise ModalDetectionError(f"Failed to initiate video detection: {str(e)}")


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
