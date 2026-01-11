# VerificAI 

**VerificAI: Proteção inteligente para suas mensagens.**

An intelligent, AI-powered system designed to analyze messages and forwarded emails for spam, phishing, and malicious content. It leverages Google's Gemini for contextual understanding, Google Safe Browsing for real-time link scanning, and provides user feedback mechanisms.

This project was developed as an academic requirement for the Computer Science course at UECE (State University of Ceará), within the LARCES (Computer Networks and Security Laboratory), under the supervision of Professor Rafael Lopes Gomes.

---

## Live Demo & Documentation

The core web API is live and documented with Swagger UI:

** [https://chatbot-spam.duckdns.org/swagger/](https://chatbot-spam.duckdns.org/swagger/)**
---

## Core Features

-   **AI-Powered Analysis (Gemini):** Utilizes Google's Gemini 2.5 Flash model via API for sophisticated, context-aware analysis of message content and intent.
-   **Real-time Link Scanning (Google Safe Browsing):** Integrates with the Google Safe Browsing API (v4) to check URLs within messages for known threats (malware, phishing, etc.).
-   **Dual Channel Support:**
    -   **Email:** Monitors a dedicated Gmail account, processes forwarded emails, analyzes their content, and replies to the original sender with the verdict.
-   **Professional Admin Dashboard:** Uses Django Admin with the Jazzmin theme for a clean interface to view and manage collected feedback data, including an automated accuracy calculation.
-   **Production-Grade Deployment:** Deployed on AWS EC2 using a robust stack (Nginx, Gunicorn, Systemd) with automated service management and HTTPS security.

---

## Architecture & Tech Stack

**Application & AI:**
-   **Backend:** Python, Django
-   **External APIs:**
    -   Google Gemini API
    -   Google Safe Browsing API
    -   Gmail API (Google Cloud)
-   **Libraries:** `google-generativeai`, `google-api-python-client`, `requests`, `python-decouple`

**Infrastructure (DevOps):**
-   **Cloud Provider:** AWS EC2 (Ubuntu 22.04)
-   **Web Server / Reverse Proxy:** Nginx (for the Django API/Admin)
-   **WSGI Server:** Gunicorn (runs the Django application)
-   **Background Service:** Custom Python script (`email_bot.py`) for Gmail monitoring.
-   **Service Management:** systemd (manages both `gunicorn.service` and `emailbot.service`)
-   **Security:** Let's Encrypt SSL (via Certbot), Environment variables for secrets, GitHub Push Protection.
-   **DNS:** DuckDNS
-   **Version Control:** Git & GitHub

**Architecture Overview:**
-   **Email:** `User Forwards Email -> Gmail Account -> email_bot.py (via Gmail API Polling) -> Gemini/Safe Browsing -> email_bot.py -> Gmail API -> Email Reply`
---

## Setup & Installation (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/PedroMikhael/message-spam-detector.git](https://github.com/PedroMikhael/message-spam-detector.git)
    cd message-spam-detector
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    py -m venv venv
    .\venv\Scripts\activate
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the project root and add your secret keys:
    ```
    SECRET_KEY='your_django_secret_key'
    GEMINI_API_KEY='your_gemini_api_key'
    SAFE_BROWSING_API_KEY='your_safe_browsing_api_key'
    ```

5.  **Set up Google OAuth Credentials for Email:**
    -   Follow Google Cloud instructions to create an **OAuth 2.0 Client ID for Desktop app**.
    -   Download the `credentials.json` file and place it in the project root.
    -   Run the authorization script **once** to generate `token.json`:
        ```bash
        python autorizar_gmail.py 
        ```
        *(Follow the on-screen instructions to authorize via your browser).*

6.  **Run database migrations and start the Django server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

7.  **(Optional) Run the Email Bot locally:**
    Open a *separate terminal*, activate the `venv`, and run:
    ```bash
    python email_bot.py
    ```

---

## Usage
-   **Email:** Forward a suspicious email to the dedicated Gmail address (`chatbot.larces@gmail.com`). The bot will reply to the *original sender* of the forwarded email with its analysis and feedback links.
-   **Admin Panel:** Access `https://chatbot-spam.duckdns.org/admin/` to view collected feedback and performance statistics.

### Example AI Response (Via WhatsApp or Email)

**For a malicious message:**
>  ALERTA MÁXIMO! Esta mensagem é extremamente perigosa. O link fornecido foi identificado como malicioso pelo sistema de Navegação Segura do Google. **NÃO CLIQUE NESSE LINK**. A recomendação é apagar esta conversa e bloquear o número. Fique seguro! 
>
> ---
> *Minha análise foi útil?*
> **[Sim, acertou]** **[Não, errou]** 

---

## Authors

-   Pedro Mikhael
-   João Victor
