# WhatsApp Spam Detector API 🤖

An intelligent API powered by Google's Gemini, designed to detect spam and phishing in WhatsApp messages. It leverages real-time link scanning via the Google Safe Browsing API and acts as a hybrid conversational assistant.

This project was developed as an academic requirement for the Computer Science course at UECE, under the supervision of Professor Rafael Lopes Gomes.

---

## ✨ Live Demo & Documentation

The API is live and fully documented with Swagger UI. You can interact with the endpoint in real-time here:

**➡️ [https://chatbot-spam.duckdns.org/swagger/](https://chatbot-spam.duckdns.org/swagger/)**

---

## 🚀 Core Features

-   **AI-Powered Analysis:** Utilizes Google's Gemini 1.5 Flash model to perform nuanced, context-aware analysis of messages, far surpassing traditional rule-based systems.
-   **Real-time Link Scanning:** Integrates with the Google Safe Browsing API (v4) to check URLs for malware, phishing, and other threats in real-time.
-   **Hybrid Conversational Agent:** Acts as a "Digital Guardian." It protects users by identifying threats and providing clear, didactic warnings. For safe messages, it functions as a helpful conversational assistant.
-   **WhatsApp Webhook Integration:** Fully integrated with the Meta for Developers platform to receive and respond to WhatsApp messages instantly.
-   **Production-Grade Deployment:** Deployed on Amazon Web Services (AWS) using a professional-grade, automated server stack.

---

## 🛠️ Architecture & Tech Stack

This project was built with scalability and reliability in mind, using industry-standard tools for deployment.

**Application & AI:**
-   **Backend:** Python, Django
-   **External APIs:**
    -   Google Gemini API
    -   Google Safe Browsing API
    -   WhatsApp Business API (Meta)

**Infrastructure (DevOps):**
-   **Cloud Provider:** AWS EC2 (Ubuntu 22.04)
-   **Web Server / Reverse Proxy:** Nginx
-   **WSGI Server:** Gunicorn
-   **Service Management:** systemd (for `gunicorn.socket` and `gunicorn.service`)
-   **Security:** Let's Encrypt SSL Certificate managed by Certbot for HTTPS; Environment variables for secrets management.
-   **DNS:** DuckDNS
-   **Version Control:** Git & GitHub

The production environment follows a reverse proxy architecture:
`User Request -> Nginx (Port 443/80) -> Gunicorn Socket -> Gunicorn Workers -> Django Application`

---

## ⚙️ Local Setup & Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/PedroMikhael/whatsapp-spam-detector.git](https://github.com/PedroMikhael/whatsapp-spam-detector.git)
    cd whatsapp-spam-detector
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    py -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run database migrations and start the server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
    The server will be available at `http://127.0.0.1:8000/`.

---

## 📖 API Usage

The primary webhook for receiving messages is:

-   **Endpoint:** `/api/spam/`
-   **Method:** `POST` (for WhatsApp messages), `GET` (for webhook verification)

The interaction is done via the WhatsApp Business API. When a message is sent to the configured number, the API processes it and sends a reply.

### Example AI Response (Sent back to the user via WhatsApp)

**For a malicious message:**
> 🚨 ALERTA MÁXIMO! Esta mensagem é extremamente perigosa. O link fornecido foi identificado como malicioso pelo sistema de Navegação Segura do Google. **NÃO CLIQUE NESSE LINK**. A recomendação é apagar esta conversa e bloquear o número. Fique seguro! 👍

**For a safe message:**
> Olá! Este é um projeto acadêmico de segurança digital. Como posso te ajudar? 😊

---

## 👨‍💻 Authors

-   Pedro Mikhael
-   João Victor
