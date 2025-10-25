"""
WhatsApp Service - Handles all WhatsApp Cloud API interactions
"""
import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID


def send_whatsapp_message(to, text):
    """
    Send a text message via WhatsApp Cloud API
    
    Args:
        to (str): Recipient phone number
        text (str): Message text to send
    
    Returns:
        dict: Response from WhatsApp API
    """
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        print(f"Message sent to {to}: {response_data}")
        return response_data
    except Exception as e:
        print(f"Error sending message to {to}: {e}")
        return None


def download_whatsapp_media(media_id):
    """
    Download media file from WhatsApp Cloud API
    
    Args:
        media_id (str): WhatsApp media ID
    
    Returns:
        tuple: (file_content, mime_type, media_data) or (None, None, None) on error
    """
    try:
        # Step 1: Get media URL
        url = f"https://graph.facebook.com/v17.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error getting media URL: {response.text}")
            return None, None, None
        
        media_data = response.json()
        media_url = media_data.get('url')
        mime_type = media_data.get('mime_type')
        
        if not media_url:
            print("No media URL found")
            return None, None, None
        
        # Step 2: Download the actual file
        download_response = requests.get(media_url, headers=headers)
        
        if download_response.status_code != 200:
            print(f"Error downloading media: {download_response.text}")
            return None, None, None
        
        return download_response.content, mime_type, media_data
    
    except Exception as e:
        print(f"Error in download_whatsapp_media: {e}")
        return None, None, None


def mark_message_as_read(message_id):
    """
    Mark a message as read
    
    Args:
        message_id (str): WhatsApp message ID
    
    Returns:
        dict: Response from WhatsApp API
    """
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return None
