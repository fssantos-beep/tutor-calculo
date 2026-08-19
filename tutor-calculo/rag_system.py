import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx

class RAGSystem:
    """
    Sistema RAG para busca semântica em materiais didáticos
    """
    
    def __init__(self, data_path="data/materials/"):
        self.data_path = data_path
        self.chunks = [] # Trechos do texto da base de conhecimento
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        self.tfidf_matrix = None # Matriz de similaridade
    
    def load_documents(self):
        """
        Carrega e processa todos os documentos da base de conhecimento
        """
        # Garante que a pasta existe
        os.makedirs(self.data_path, exist_ok=True)
        
        # Processa cada arquivo na pasta de materiais
        for filename in os.listdir(self.data_path):
            caminho_arquivo = os.path.join(self.data_path, filename)
            trechos = []
            
            # Suporte a múltiplos formatos
            if filename.endswith('.pdf'):
                trechos = self._extrair_pdf(caminho_arquivo)
            elif filename.endswith('.docx'):
                trechos = self._extrair_docx(caminho_arquivo)
            elif filename.endswith('.txt'):
                trechos = self._extrair_txt(caminho_arquivo)
                
            self.chunks.extend(trechos)
    
    def _extrair_pdf(self, caminho_arquivo):
        """Extrai texto de arquivos PDF"""
        trechos = []
        try:
            with open(caminho_arquivo, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                for pagina in leitor.pages:
                    texto = pagina.extract_text()
                    if texto:
                        trechos.append(texto)
        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
        return trechos
    
    def _extrair_docx(self, caminho_arquivo):
        """Extrai texto de arquivos DOCX"""
        trechos = []
        try:
            doc = docx.Document(caminho_arquivo)
            paragrafos = [para.text for para in doc.paragraphs if para.text.strip()]
            texto_completo = "\n".join(paragrafos)
            if texto_completo:
                trechos.append(texto_completo)
        except Exception as e:
            print(f"Erro ao processar DOCX: {e}")
        return trechos
    
    def _extrair_txt(self, caminho_arquivo):
        """Extrai texto de arquivos TXT"""
        trechos = []
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                texto = arquivo.read()
                if texto:
                    trechos.append(texto)
        except Exception as e:
            print(f"Erro ao processar TXT: {e}")
        return trechos
    
    def build_index(self):
        """
        Constrói índice de busca usando TF-IDF
        """
        if not self.chunks:
            self.load_documents()

        self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
    
    def search(self, query, top_k=3):
        """
        Busca os trechos mais relevantes para uma consulta
        """
        if self.tfidf_matrix is None:
            self.build_index()
        vetor_consulta = self.vectorizer.transform([query])
        similaridades = cosine_similarity(vetor_consulta, self.tfidf_matrix).flatten()
        melhores_indices = similaridades.argsort()[-top_k:][::-1]
        
        resultados = []
        for indice in melhores_indices:
            if similaridades[indice] > 0.1:
                resultados.append({
                    'text': self.chunks[indice],
                    'score': similaridades[indice]
                })
        
        return resultados
    
    def load_index(self, caminho="data/processed/rag_index.pkl"):
        """
        Carrega índice salvo para evitar reprocessamento
        """
        try:
            with open(caminho, 'rb') as arquivo:
                dados = pickle.load(arquivo)
                self.chunks = dados['chunks']
                self.vectorizer = dados['vectorizer']
                self.tfidf_matrix = dados['tfidf_matrix']
        except FileNotFoundError:
            self.build_index()
            self.save_index()
    
    def save_index(self, caminho="data/processed/rag_index.pkl"):
        """
        Salva índice para uso futuro
        """
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'wb') as arquivo:
            pickle.dump({
                'chunks': self.chunks,
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, arquivo)