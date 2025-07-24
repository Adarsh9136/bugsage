#phase 1 llm_chain
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def explain_bug(log: str, lang: str = "en") -> str:
    print(f"[LLM DEBUG] Language requested: {lang}")

    if lang == "fr":
        system_msg = "Vous êtes un expert en débogage logiciel. Expliquez l'erreur suivante en français avec des solutions possibles."
    elif lang == "hi":
        system_msg = "आप एक विशेषज्ञ सॉफ़्टवेयर डिबगिंग विशेषज्ञ हैं। कृपया नीचे दी गई त्रुटि को सरल हिंदी में समझाएं और संभावित समाधान दें।"
    else:
        system_msg = "You are an expert software debugger. Explain the following error in simple English with likely causes and possible fixes."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": log}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM ERROR] Failed to call OpenAI API: {e}")
        raise RuntimeError("LLM processing failed.")
