"""
Modal AI Service - Handles Modal API calls for AI detection
"""
import os
import base64
import requests
from typing import Dict, Optional, Tuple


# Modal API Configuration
MODAL_API_URL = os.getenv("MODAL_API_URL", "https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run")
MODAL_API_KEY = os.getenv("MODAL_API_KEY")  # Optional, for secured endpoints


class ModalDetectionError(Exception):
    """Custom exception for Modal API errors"""
    pass


def detect_image_ai(file_content: bytes, mime_type: str = "image/jpeg") -> Dict:
    """
    Send image to Modal AI model for deepfake detection
    
    Args:
        file_content (bytes): Image file content
        mime_type (str): MIME type of the image
    
    Returns:
        dict: Detection result with keys:
            - confidence (int): Confidence score 0-100
            - isAI (bool): True if AI-generated, False if human
            - label (str): Human-readable label
            - model (str): Model name used
            - raw_predictions (list): Raw prediction scores from model
    
    Raises:
        ModalDetectionError: If API call fails
    """
    try:
        # Convert image bytes to base64
        base64_image = base64.b64encode(file_content).decode('utf-8')
        
        # Prepare request
        url = f"{MODAL_API_URL}/predict"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authentication if API key is provided
        if MODAL_API_KEY:
            headers["Authorization"] = f"Bearer {MODAL_API_KEY}"
        
        payload = {
            "image": base64_image,
            "return_all_scores": True
        }
        
        print(f"🤖 Calling Modal API: {url}")
        print(f"   Image size: {len(file_content)} bytes")
        print(f"   Base64 length: {len(base64_image)} chars")
        print(f"   Payload keys: {list(payload.keys())}")
        
        # Call Modal API
        print(f"   Making POST request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"Modal API returned status {response.status_code}"
            try:
                error_data = response.json()
                error_msg = f"{error_msg}: {error_data.get('error', 'Unknown error')}"
            except:
                error_msg = f"{error_msg}: {response.text}"
            
            print(f"❌ Modal API error: {error_msg}")
            raise ModalDetectionError(error_msg)
        
        # Parse response
        modal_data = response.json()
        print(f"✅ Modal API response received")
        print(f"   Top prediction: {modal_data.get('top_prediction')}")
        print(f"   Confidence: {modal_data.get('confidence')}")
        
        # Map Modal response to our format
        result = map_modal_response(modal_data)
        
        return result
    
    except requests.exceptions.Timeout:
        error_msg = "Modal API request timed out (30s)"
        print(f"⏱️ {error_msg}")
        raise ModalDetectionError(error_msg)
    
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to Modal API"
        print(f"🔌 {error_msg}")
        raise ModalDetectionError(error_msg)
    
    except ModalDetectionError:
        raise
    
    except Exception as e:
        error_msg = f"Unexpected error calling Modal API: {str(e)}"
        print(f"❌ {error_msg}")
        raise ModalDetectionError(error_msg)


def map_modal_response(modal_data: Dict) -> Dict:
    """
    Map Modal API response to our standard detection result format
    
    Args:
        modal_data (dict): Raw response from Modal API with keys:
            - predictions: [{"label": "REAL", "score": 0.92}, ...]
            - top_prediction: "REAL"
            - confidence: 0.92
    
    Returns:
        dict: Standardized detection result
    """
    top_prediction = modal_data.get("top_prediction", "").upper()
    confidence = modal_data.get("confidence", 0.0)
    predictions = modal_data.get("predictions", [])
    
    # Determine if content is AI-generated
    # Check if top prediction contains "AI" or "FAKE"
    isAI = "AI" in top_prediction or "FAKE" in top_prediction
    
    # Convert confidence from 0-1 to 0-100
    confidence_percent = round(confidence * 100)
    
    # Generate human-readable label
    if isAI:
        label = "AI-Generated Content Detected"
        emoji = "🤖"
    else:
        label = "Authentic Human Content"
        emoji = "✅"
    
    result = {
        "confidence": confidence_percent,
        "isAI": isAI,
        "label": label,
        "emoji": emoji,
        "model": "EfficientFormer-S2V1 (Modal)",
        "raw_predictions": predictions,
        "top_prediction": top_prediction
    }
    
    return result


def health_check() -> Tuple[bool, str]:
    """
    Check if Modal API is reachable and healthy
    
    Returns:
        tuple: (is_healthy: bool, message: str)
    """
    try:
        url = f"{MODAL_API_URL}/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            device = data.get("device", "unknown")
            cuda = data.get("cuda_available", False)
            model_loaded = data.get("model_loaded", False)
            
            if status == "healthy" and model_loaded:
                return True, f"Modal API is healthy (Device: {device}, CUDA: {cuda})"
            else:
                return False, f"Modal API responded but not fully ready: {data}"
        else:
            return False, f"Modal API returned status {response.status_code}"
    
    except Exception as e:
        return False, f"Modal API health check failed: {str(e)}"


def format_detection_response(result: Dict, filename: str) -> str:
    """
    Format detection result into a nice WhatsApp message
    
    Args:
        result (dict): Detection result from detect_image_ai()
        filename (str): Name of analyzed file
    
    Returns:
        str: Formatted WhatsApp message
    """
    emoji = result.get("emoji", "🔍")
    confidence = result.get("confidence", 0)
    label = result.get("label", "Unknown")
    isAI = result.get("isAI", False)
    model = result.get("model", "AI Model")
    
    # Build confidence bar
    bar_length = 10
    filled = int((confidence / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Choose color indicator
    if confidence >= 80:
        confidence_indicator = "🟢"
    elif confidence >= 60:
        confidence_indicator = "🟡"
    else:
        confidence_indicator = "🔴"
    
    message = f"{emoji} *Detection Results*\n\n"
    message += f"📁 File: {filename}\n"
    message += f"🤖 Model: {model}\n\n"
    message += f"━━━━━━━━━━━━━━━━━━\n\n"
    
    if isAI:
        message += f"⚠️ *{label}*\n\n"
        message += f"This content appears to be AI-generated or manipulated.\n\n"
    else:
        message += f"✅ *{label}*\n\n"
        message += f"This content appears to be authentic human-created.\n\n"
    
    message += f"📊 *Confidence Score*\n"
    message += f"{confidence_indicator} {confidence}% {bar}\n\n"
    
    # Add raw predictions if available
    raw_predictions = result.get("raw_predictions", [])
    if raw_predictions and len(raw_predictions) > 0:
        message += f"📈 *Detailed Scores:*\n"
        for pred in raw_predictions[:3]:  # Show top 3
            label_text = pred.get("label", "Unknown")
            score = pred.get("score", 0)
            score_percent = round(score * 100)
            message += f"   • {label_text}: {score_percent}%\n"
        message += "\n"
    
    message += f"━━━━━━━━━━━━━━━━━━\n\n"
    message += f"💡 Type *start* to analyze another file!"
    
    return message


# Test function for debugging
if __name__ == "__main__":
    print("🧪 Testing Modal API connection...")
    
    is_healthy, msg = health_check()
    print(f"Health check: {'✅' if is_healthy else '❌'} {msg}")
    
    if not is_healthy:
        print("\n⚠️ Modal API is not reachable!")
        print(f"   URL: {MODAL_API_URL}")
        print(f"   Make sure the Modal app is deployed and running.")

