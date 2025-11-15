# FocusUP

Um aplicativo web feito em Django pra ajudar na rotina das pessoas, usando gamificação pra isso.

O app usa a IA do Ollama pra gerar as tarefas de um jeito mais inteligente.

## Tecnologias

* Python
* Django
* Ollama AI
* HTML/CSS/JS

## Como Rodar o Projeto

1.  **Clone o projeto:**
    ```bash
    git clone [https://github.com/devluan7/FocusUP_DSC.git](https://github.com/devluan7/FocusUP_DSC.git)
    cd FocusUP_DSC
    ```

2.  **Crie e ative o ambiente virtual (venv):**
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate

    # No Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale o que precisa:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Rode as migrações:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (opcional, pra usar o /admin):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Inicie o servidor:**
    ```bash
    python manage.py runserver
    ```

O app vai estar rodando em `http://127.0.0.1:8000/`.
