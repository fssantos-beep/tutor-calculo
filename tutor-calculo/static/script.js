class TutorApp {
    constructor() {
        this.currentExercises = [];
        this.isLoading = false;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Enviar mensagem
        document.getElementById('sendMessage').addEventListener('click', () => this.sendMessage());
        
        // Enter para enviar, Shift+Enter para nova linha
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Gerar exercícios
        document.getElementById('generateExercisesBtn').addEventListener('click', () => this.generateExercises());

        // Resumo da sessão
        document.getElementById('summaryBtn').addEventListener('click', () => this.getSummary());

        // Auto-expand textarea
        this.setupTextareaAutoResize();
    }

    setupTextareaAutoResize() {
        const textarea = document.getElementById('messageInput');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });
    }

    async sendMessage() {
        if (this.isLoading) return;

        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) {
            messageInput.focus();
            return;
        }

        // Adiciona mensagem do usuário ao chat
        this.addMessageToChat('user', message);
        
        // Limpa e reseta o textarea
        messageInput.value = '';
        messageInput.style.height = 'auto';
        messageInput.focus();

        this.setLoading(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    level: document.getElementById('level').value,
                    theme: document.getElementById('theme').value
                })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Adiciona resposta do tutor
            this.addMessageToChat('tutor', data.response);

        } catch (error) {
            this.addMessageToChat('tutor', `Erro: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    async generateExercises() {
        if (this.isLoading) return;
        
        this.setLoading(true);

        try {
            const response = await fetch('/generate_exercises', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme: document.getElementById('theme').value,
                    difficulty: document.getElementById('level').value,
                    quantity: 3
                })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.displayExercises(data.exercises);

        } catch (error) {
            alert(`Erro ao gerar exercícios: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    async getSummary() {
        try {
            const response = await fetch('/summary');
            const data = await response.json();

            document.getElementById('summaryContent').innerHTML = 
                `<p>${this.formatText(data.summary)}</p>`;

        } catch (error) {
            document.getElementById('summaryContent').innerHTML = 
                `<p>Erro ao carregar resumo: ${error.message}</p>`;
        }
    }

    addMessageToChat(sender, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const header = sender === 'user' ? 'Você' : 'Tutor';
        
        messageDiv.innerHTML = `
            <div class="message-header">${header}</div>
            <div class="message-content">${this.formatText(content)}</div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    displayExercises(exercises) {
        this.currentExercises = exercises;
        const exercisesContainer = document.getElementById('exercisesContent');

        let exercisesHTML = '<h4>Exercícios Gerados:</h4>';

        if (exercises && exercises.length > 0) {
            exercises.forEach((exercise, index) => {
                exercisesHTML += `
                    <div class="exercise-item">
                        <div class="exercise-question">
                            <strong>Exercício ${index + 1}:</strong> ${this.formatText(exercise.question)}
                        </div>
                        <button class="toggle-answer" onclick="tutorApp.toggleAnswer(${index})">
                            Mostrar Resposta
                        </button>
                        <div class="exercise-answer" id="answer-${index}">
                            <strong>Resposta:</strong> ${this.formatText(exercise.answer)}
                            ${exercise.hint ? `<br><strong>Dica:</strong> ${this.formatText(exercise.hint)}` : ''}
                        </div>
                    </div>
                `;
            });
        } else {
            exercisesHTML += '<p>Nenhum exercício foi gerado. Tente novamente.</p>';
        }

        exercisesContainer.innerHTML = exercisesHTML;
    }

    toggleAnswer(index) {
        const answerElement = document.getElementById(`answer-${index}`);
        const button = answerElement.previousElementSibling;

        if (answerElement.classList.contains('show')) {
            answerElement.classList.remove('show');
            button.textContent = 'Mostrar Resposta';
        } else {
            answerElement.classList.add('show');
            button.textContent = 'Ocultar Resposta';
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }

    formatText(text) {
        if (!text) return '';
        return text
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>')
            .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
    }

    setLoading(loading) {
        this.isLoading = loading;
        const buttons = document.querySelectorAll('button');
        const inputs = document.querySelectorAll('select, textarea');

        buttons.forEach(button => {
            if (button.id !== 'sendMessage') {
                button.disabled = loading;
            }
        });
        
        inputs.forEach(input => {
            input.disabled = loading;
        });
        const sendButton = document.getElementById('sendMessage');
        if (loading) {
            sendButton.textContent = 'Enviando...';
            sendButton.disabled = true;
        } else {
            sendButton.textContent = 'Enviar';
            sendButton.disabled = false;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.tutorApp = new TutorApp();
    document.getElementById('messageInput').focus();
});