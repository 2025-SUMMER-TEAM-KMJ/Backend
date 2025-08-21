import google.generativeai as genai
from settings import GEMINI_MODEL, GOOGLE_API_KEY

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"모델 초기화 중 오류 발생: {e}")
    model = None

def get_gemini_response(prompt, gemini_model=GEMINI_MODEL, temperature=0.7):
    model = genai.GenerativeModel(gemini_model, generation_config=genai.GenerationConfig(
        temperature=temperature
    ))

    if not model:
        return "모델이 올바르게 초기화되지 않았습니다."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("API 호출 중 에러가 발생했습니다.")
        raise e