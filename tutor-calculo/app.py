from flask import Flask, render_template, request, jsonify, session
import os
import json
import traceback
from datetime import datetime
from rag_system import RAGSystem
from llm_integration import LLMIntegration

app = Flask(__name__)
app.secret_key = 'tutor_calculo_key'
app.config['SESSION_TYPE'] = 'filesystem'
rag_system = RAGSystem()

# Integração com LLM local (Mistral 7B)
llm_integration = LLMIntegration()


# SISTEMA ADAPTATIVO DE DIFICULDADE
class SistemaAdaptativo:
    """
    Controla a geração de conteúdo por nível de dificuldade
    """
    def __init__(self):
        self.niveis_dificuldade = {
            "básico": {
                "complexidade": "baixa",
                "exemplos": "simples"
            },
            "intermediário": {
                "complexidade": "média", 
                "exemplos": "práticos"
            },
            "avançado": {
                "complexidade": "alta",
                "exemplos": "técnicos"
            }
        }
    
    def gerar_prompt_exercicio(self, tema, nivel):
        """
        Gera prompt para criação de exercícios adaptativos
        """
        config = self.niveis_dificuldade[nivel]
        
        prompt = f"""
        Gere um exercício de {tema} para nível {nivel}.
        Dificuldade: {config['complexidade']}
        Exemplos: {config['exemplos']}
        
        FORMATO JSON:
        {{
            "exercises": [
                {{
                    "question": "enunciado em português",
                    "answer": "resposta completa", 
                    "hint": "dica útil",
                    "dificuldade": "{nivel}",
                    "conceito": "{tema}"
                }}
            ]
        }}
        """
        return prompt

sistema_adaptativo = SistemaAdaptativo()

# Carrega base de conhecimento RAG
try:
    rag_system.load_index()
    print("Sistema RAG inicializado com sucesso")
except Exception as e:
    print(f"Erro ao carregar RAG: {e}")


@app.route('/')
def index():
    """Página principal com interface do tutor"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def processar_mensagem():
    """
    Processa mensagens do chat integrando RAG + LLM
    """
    try:
        data = request.json
        pergunta = data.get('message', '').strip()
        nivel = data.get('level', 'intermediário')
        tema = data.get('theme', 'geral')
        
        if not pergunta:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Busca de contexto relevante (RAG)
        trechos_relevantes = rag_system.search(pergunta, top_k=2)
        
        # Prepara contexto para o LLM
        contexto = ""
        if trechos_relevantes and trechos_relevantes[0]['score'] > 0.25:
            melhor_trecho = trechos_relevantes[0]['text']
            contexto = f"\nContexto do material: {melhor_trecho}"
        
        # Construção do prompt com contexto
        prompt = f"""
        Você é um tutor de Cálculo. Responda de forma clara e direta.

        PERGUNTA: {pergunta}
        NÍVEL: {nivel}
        {contexto}

        INSTRUÇÕES:
        - Seja conciso (3-4 frases)
        - Explique o conceito principal
        - Use 1 exemplo prático
        - Responda em português

        RESPOSTA:
        """
        
        # Geração da resposta pelo LLM
        resposta = llm_integration.generate_response(prompt)
        
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'user': pergunta,
            'tutor': resposta,
            'timestamp': datetime.now().isoformat(),
            'theme': tema,
            'level': nivel
        })
        
        session.modified = True
        
        return jsonify({
            'response': resposta,
            'context_used': len(contexto) > 0
        })
        
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/generate_exercises', methods=['POST'])
def gerar_exercicios():
    """
    Gera exercícios adaptativos baseados no tema e nível
    """
    try:
        data = request.json
        tema = data.get('theme', 'derivadas')
        dificuldade = data.get('difficulty', 'intermediário')
        quantidade = min(int(data.get('quantity', 3)), 5)
        
        # Gera exercícios usando o sistema adaptativo
        exercicios_gerados = []
        
        for i in range(quantidade):
            prompt = sistema_adaptativo.gerar_prompt_exercicio(tema, dificuldade)
            resposta = llm_integration.generate_response(prompt, max_tokens=600)
            
            try:
                resposta_limpa = resposta.strip()
                
                if resposta_limpa.startswith('{'):
                    dados_exercicio = json.loads(resposta_limpa)
                else:
                    dados_exercicio = {
                        "exercises": [{
                            "question": f"Exercício de {tema}",
                            "answer": "Resposta do exercício",
                            "hint": "Use os conceitos aprendidos",
                            "dificuldade": dificuldade,
                            "conceito": tema
                        }]
                    }
                
                if 'exercises' in dados_exercicio:
                    exercicios_gerados.extend(dados_exercicio['exercises'])
                    
            except json.JSONDecodeError:
                exercicios_gerados.append({
                    "question": f"Calcule um exemplo de {tema}",
                    "answer": "Resposta do cálculo",
                    "hint": "Revise os conceitos básicos",
                    "dificuldade": dificuldade,
                    "conceito": tema
                })
        
        return jsonify({"exercises": exercicios_gerados[:quantidade]})
            
    except Exception as e:
        print(f"Erro na geração de exercícios: {e}")
        return jsonify({"exercises": []})

@app.route('/summary', methods=['GET'])
def resumo_sessao():
    """
    Gera resumo automático da sessão de estudo
    """
    try:
        historico = session.get('chat_history', [])
        
        if not historico:
            return jsonify({'summary': 'Nenhuma conversa registrada.'})
        
        # Usa LLM para gerar resumo das conversas
        conversas_recentes = historico[-4:]
        
        prompt = f"""
        Faça um resumo breve (2-3 frases) em português dos conceitos discutidos.
        
        Conversas: {json.dumps(conversas_recentes, ensure_ascii=False)}
        
        Resumo conciso:
        """
        
        resumo = llm_integration.generate_response(prompt, max_tokens=150)
        return jsonify({'summary': resumo})
    
    except Exception as e:
        return jsonify({'summary': 'Erro ao gerar resumo.'})

@app.route('/health', methods=['GET'])
def status_sistema():
    """Endpoint para verificar saúde do sistema"""
    return jsonify({
        'status': 'operacional', 
        'modelo': 'mistral:7b',
        'sistema': 'Tutor de Cálculo'
    })

if __name__ == '__main__':
    print("Tutor de Cálculo - Sistema Iniciado")
    print("Acesse: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)