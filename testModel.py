import google.generativeai as genai

# API 키 입력 (여기에 실제 키 입력)
API_KEY = "AIzaSyBDxuOYYFevpT3sespsrijOToRmS03Bvls"  # 🔑 실제 키로 교체
genai.configure(api_key=API_KEY)

print("=" * 60)
print("🔍 사용 가능한 Gemini 모델 목록")
print("=" * 60)

try:
    models = list(genai.list_models())
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ 모델명: {model.name}")
            print(f"   표시명: {model.display_name}")
            print(f"   설명: {model.description[:80]}...")
            
    print("\n" + "=" * 60)
    print(f"총 {len([m for m in models if 'generateContent' in m.supported_generation_methods])}개 모델 사용 가능")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 에러: {e}")
