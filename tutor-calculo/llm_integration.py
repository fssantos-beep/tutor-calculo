import requests

class LLMIntegration:
    """
    Gerencia comunicação com LLM local via Ollama
    """
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral:7b"  # Modelo LLM utilizado
    
    def generate_response(self, prompt, max_tokens=500):
        """
        Envia prompt para LLM e retorna resposta
        """
        try:
            resposta = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": max_tokens,
                        "top_k": 40,
                        "top_p": 0.7
                    }
                },
                timeout=60
            )
            
            if resposta.status_code == 200:
                resultado = resposta.json()
                return resultado.get('response', '').strip()
            else:
                return "Erro na geração da resposta."
                
        except requests.exceptions.ConnectionError:
            return "Erro: Verifique se o Ollama está rodando."
        except Exception as e:
            return f"Erro: {str(e)}"