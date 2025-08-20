import google.generativeai as genai
import os

from settings import GEMINI_MODEL, GOOGLE_API_KEY

# --- Gemini setup (사용 중인 키/모델 유지) ---
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

try:
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"모델 초기화 중 오류 발생: {e}")
    model = None

def get_gemini_response(prompt):
    if not model:
        return "모델이 올바르게 초기화되지 않았습니다."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise f"API 호출 중 오류가 발생했습니다: {e}"