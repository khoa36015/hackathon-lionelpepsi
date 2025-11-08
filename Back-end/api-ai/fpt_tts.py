"""
FPT.AI Text-to-Speech Integration
Provides Vietnamese voice synthesis using FPT.AI API
"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

FPT_API_KEY = os.getenv("FPT_API_KEY", "8OuJvLUvBBfqok7MkamxBelt4yb3JHWF")
FPT_TTS_URL = "https://api.fpt.ai/hmi/tts/v5"

# Available Vietnamese voices
VOICES = {
    "banmai": "Nữ Bắc (Ban Mai)",
    "lannhi": "Nữ Nam (Lan Nhi)", 
    "leminh": "Nam Bắc (Lê Minh)",
    "myan": "Nữ Trung (Mỹ An)",
    "thuminh": "Nữ Bắc (Thu Minh)",
    "giahuy": "Nam Trung (Gia Huy)",
    "linhsan": "Nữ Nam (Linh San)"
}

def synthesize_speech(text, voice="banmai", speed=0, format="mp3"):
    """
    Convert text to speech using FPT.AI API
    
    Args:
        text (str): Text to convert (max 5000 characters)
        voice (str): Voice name (banmai, lannhi, leminh, myan, thuminh, giahuy, linhsan)
        speed (int): Speed adjustment (-3 to +3, 0 is normal)
        format (str): Output format (mp3 or wav)
    
    Returns:
        dict: Response with audio URL or error
    """
    if not text or len(text.strip()) < 3:
        return {"error": "Text must be at least 3 characters"}
    
    if len(text) > 5000:
        return {"error": "Text exceeds 5000 character limit"}
    
    if not FPT_API_KEY:
        return {"error": "FPT_API_KEY not configured"}
    
    headers = {
        "api_key": FPT_API_KEY,
        "voice": voice,
        "speed": str(speed),
        "format": format,
        "Cache-Control": "no-cache"
    }
    
    try:
        response = requests.post(
            FPT_TTS_URL,
            headers=headers,
            data=text.encode('utf-8'),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("error") == 0:
                # Success - return audio URL
                return {
                    "success": True,
                    "audio_url": data.get("async"),
                    "request_id": data.get("request_id"),
                    "message": "Audio will be ready in a few seconds"
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error from FPT.AI")
                }
        else:
            return {
                "success": False,
                "error": f"FPT.AI API returned status {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request to FPT.AI timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error calling FPT.AI: {str(e)}"
        }

def wait_for_audio(audio_url, max_wait=30, check_interval=2):
    """
    Wait for audio file to be ready and return it
    
    Args:
        audio_url (str): URL of the audio file
        max_wait (int): Maximum seconds to wait
        check_interval (int): Seconds between checks
    
    Returns:
        bool: True if audio is ready, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.head(audio_url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        time.sleep(check_interval)
    
    return False

def get_available_voices():
    """
    Get list of available Vietnamese voices
    
    Returns:
        dict: Dictionary of voice codes and names
    """
    return VOICES

