import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not found in . env file")

client = InferenceClient(token=HF_TOKEN)


class LLMClient:
    
    @staticmethod
    def call_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.7, retries: int = 2) -> str:
        """
        Call LLM with prompt and return response (with retry logic)
        """
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.2-3B-Instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                result = response.choices[0].message.content.strip()
                
                if result:
                    return result
                else:
                    print(f"⚠️ Empty response on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"❌ LLM Error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(1)  # Wait before retry
        
        return None
    
    @staticmethod
    def call_llm_with_context(system_prompt: str, user_message: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Call LLM with system prompt and user message
        """
        try:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.2-3B-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role":  "user",
                        "content": user_message
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response. choices[0].message.content. strip()
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return None