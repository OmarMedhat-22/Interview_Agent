import requests

API_KEY = "AIzaSyDRQwSyO3z5DZMokTPSfiDg7H-5BuqugB0"

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Available Gemini Models:\n")
    print("-" * 60)
    for model in data.get("models", []):
        name = model.get("name", "").replace("models/", "")
        display_name = model.get("displayName", "")
        supported_methods = model.get("supportedGenerationMethods", [])
        
        if "generateContent" in supported_methods:
            print(f"Model: {name}")
            print(f"  Display Name: {display_name}")
            print(f"  Methods: {', '.join(supported_methods)}")
            print()
else:
    print(f"Error: {response.status_code}")
    print(response.text)
