# Tutor de Cálculo

Web app de tutoria inteligente para Cálculo, que responde dúvidas, gera exercícios adaptativos por nível e resume a sessão de estudo — usando um LLM local (Mistral 7B via Ollama) combinado com um sistema de busca RAG sobre materiais didáticos próprios.

## ✨ Funcionalidades

- **Chat com contexto (RAG):** antes de responder, o sistema busca os trechos mais relevantes dos materiais de estudo (limites, derivadas, integrais etc.) e usa esse contexto no prompt enviado ao LLM.
- **Geração de exercícios adaptativos:** cria exercícios por tema (Limites, Derivadas, Integrais, Sequências e Séries) e nível de dificuldade (Básico, Intermediário, Avançado), cada um com enunciado, resposta e dica.
- **Resumo automático da sessão:** gera um resumo em português dos conceitos discutidos na conversa.
- **Interface web simples:** chat com painel de configuração de nível/tema, feito em HTML/CSS/JS puro servido por Flask.

## 🏗️ Arquitetura

```
Usuário → Frontend (HTML/CSS/JS)
            ↓
        Flask (app.py)
            ↓
   ┌────────┴─────────┐
   ▼                   ▼
RAGSystem          LLMIntegration
(TF-IDF + busca     (chamadas HTTP
por similaridade     ao Ollama /
de cosseno)          Mistral 7B)
```

- **`rag_system.py`** — carrega os materiais (`.txt`, `.pdf`, `.docx`) da pasta `data/materials/`, constrói um índice TF-IDF e busca os trechos mais relevantes para cada pergunta (similaridade de cosseno). O índice é persistido em `data/processed/rag_index.pkl` para evitar reprocessamento a cada execução.
- **`llm_integration.py`** — envia os prompts para o Ollama (`http://localhost:11434/api/generate`), usando o modelo `mistral:7b`.
- **`app.py`** — servidor Flask com as rotas da aplicação e a lógica do sistema adaptativo de dificuldade.

## 📁 Estrutura do projeto

```
tutor-calculo/
├── app.py                    # Servidor Flask e rotas principais
├── rag_system.py             # Sistema RAG (indexação e busca)
├── llm_integration.py        # Integração com o Ollama/Mistral
├── requirements.txt          # Dependências Python
├── data/
│   ├── materials/            # Materiais didáticos (base de conhecimento)
│   └── processed/            # Índice RAG pré-processado
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
└── Relatorio_Grupo6.pdf      # Relatório do projeto
```

## ✅ Pré-requisitos

- Python 3.8+
- pip 21.0+
- [Ollama](https://ollama.com/download) instalado e rodando localmente

## 🚀 Instalação e execução

1. **Clone o repositório**
   ```bash
   git clone https://github.com/fssantos-beep/tutor-calculo.git
   cd tutor-calculo/tutor-calculo
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instale e configure o Ollama com o modelo Mistral 7B**
   ```bash
   ollama pull mistral:7b
   ollama serve
   ```

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 🔌 Rotas da API

| Rota                    | Método | Descrição                                             |
|--------------------------|--------|--------------------------------------------------------|
| `/`                      | GET    | Interface principal do chat                            |
| `/chat`                  | POST   | Envia uma pergunta e recebe resposta contextualizada    |
| `/generate_exercises`    | POST   | Gera exercícios por tema e nível de dificuldade         |
| `/summary`               | GET    | Retorna um resumo da sessão de estudo atual             |
| `/health`                | GET    | Verifica o status do sistema                            |

## 🛠️ Tecnologias utilizadas

- **Backend:** Python, Flask
- **RAG:** scikit-learn (TF-IDF, similaridade de cosseno), PyPDF2, python-docx
- **LLM:** Ollama + Mistral 7B (execução local)
- **Frontend:** HTML, CSS, JavaScript
