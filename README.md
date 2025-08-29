# WhatsApp Spam Detector API 🤖

A robust, rule-based API designed to detect spam in text messages, built with Python and Django, and deployed in a production-ready environment on AWS.

This project was developed as an academic requirement for the computer Science course at UECE, under the supervision of Professor Rafael Lopes Gomes.

---

## 🚀 Core Features

-   **Rule-Based Scoring System:** Analyzes messages against a customizable dictionary of spam keywords and regex patterns.
-   **Content Analysis:** Detects spam indicators like excessive capitalization, special characters, and risky combinations (e.g., shortened links with financial terms).
-   **WhatsApp Webhook Integration:** Fully integrated with the Meta for Developers platform to receive and respond to WhatsApp messages in real-time.
-   **Production-Grade Deployment:** Deployed on Amazon Web Services (AWS) using a professional-grade server stack.
-   **Interactive API Documentation:** Automatically generated and interactive API documentation powered by Swagger (drf-yasg).

## 🛠️ Architecture & Tech Stack

This project was built with scalability and reliability in mind, using industry-standard tools for deployment.

**Application:**
-   **Backend:** Python, Django, Django REST Framework
-   **API Documentation:** drf-yasg (Swagger)

**Infrastructure (DevOps):**
-   **Cloud Provider:** AWS EC2 (Ubuntu 22.04)
-   **Web Server / Reverse Proxy:** Nginx
-   **WSGI Server:** Gunicorn
-   **Service Management:** systemd (for `gunicorn.socket` and `gunicorn.service`)
-   **Security:** Let's Encrypt SSL Certificate managed by Certbot for HTTPS.
-   **DNS:** DuckDNS for dynamic domain name service.
-   **Version Control:** Git & GitHub

The production environment follows a reverse proxy architecture:
`User Request -> Nginx (Port 443/80) -> Gunicorn Socket -> Gunicorn Workers -> Django Application`

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

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The server will be available at `http://127.0.0.1:8000/`.

## 📖 API Usage

The primary endpoint for spam detection is:

-   **Endpoint:** `/api/spam/`
-   **Method:** `POST`

### Request Body

The request must be in `application/json` format.

```json
{
    "texto": "Congratulations! You've won a special prize. Click here now bit.ly/prize123"
}

Com o maior prazer. Depois de toda essa jornada, documentar o projeto é a cereja do bolo. Um bom README no GitHub é o que transforma um monte de código em um portfólio profissional.

Aqui está uma proposta de README.md completo, em inglês, escrito de forma profissional e humana, resumindo tudo que vocês construíram. Ele foi feito para impressionar seu professor e qualquer recrutador que o veja no futuro.

Como Usar
No seu repositório do GitHub, clique em "Add file" -> "Create new file".

Nomeie o arquivo como README.md.

Copie e cole o texto abaixo.

Preencha as informações que estão entre colchetes [], como o nome da sua faculdade, disciplina e links.

Markdown

# WhatsApp Spam Detector API 🤖

A robust, rule-based API designed to detect spam in text messages, built with Python and Django, and deployed in a production-ready environment on AWS.

This project was developed as an academic requirement for the [Your Course/Discipline Name] course at [Your University Name], under the supervision of Professor [Professor's Name].

---

## ✨ Live Demo & Documentation

The API is live and fully documented with Swagger UI. You can interact with the endpoint in real-time here:

**➡️ [https://chatbot-spam.duckdns.org/swagger/](https://chatbot-spam.duckdns.org/swagger/)**

## 🚀 Core Features

-   **Rule-Based Scoring System:** Analyzes messages against a customizable dictionary of spam keywords and regex patterns.
-   **Content Analysis:** Detects spam indicators like excessive capitalization, special characters, and risky combinations (e.g., shortened links with financial terms).
-   **WhatsApp Webhook Integration:** Fully integrated with the Meta for Developers platform to receive and respond to WhatsApp messages in real-time.
-   **Production-Grade Deployment:** Deployed on Amazon Web Services (AWS) using a professional-grade server stack.
-   **Interactive API Documentation:** Automatically generated and interactive API documentation powered by Swagger (drf-yasg).

## 🛠️ Architecture & Tech Stack

This project was built with scalability and reliability in mind, using industry-standard tools for deployment.

**Application:**
-   **Backend:** Python, Django, Django REST Framework
-   **API Documentation:** drf-yasg (Swagger)

**Infrastructure (DevOps):**
-   **Cloud Provider:** AWS EC2 (Ubuntu 22.04)
-   **Web Server / Reverse Proxy:** Nginx
-   **WSGI Server:** Gunicorn
-   **Service Management:** systemd (for `gunicorn.socket` and `gunicorn.service`)
-   **Security:** Let's Encrypt SSL Certificate managed by Certbot for HTTPS.
-   **DNS:** DuckDNS for dynamic domain name service.
-   **Version Control:** Git & GitHub

The production environment follows a reverse proxy architecture:
`User Request -> Nginx (Port 443/80) -> Gunicorn Socket -> Gunicorn Workers -> Django Application`

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

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The server will be available at `http://127.0.0.1:8000/`.

## 📖 API Usage

The primary endpoint for spam detection is:

-   **Endpoint:** `/api/spam/`
-   **Method:** `POST`

### Request Body

The request must be in `application/json` format.

```json
{
    "texto": "Congratulations! You've won a special prize. Click here now bit.ly/prize123"
}


Success Response (200 OK)
The API returns a detailed analysis of the message.

{
    "spam": true,
    "pontuacao": 25.83,
    "mensagem": "Este texto parece ser spam. (Pontuação Final: 25.83)",
    "detalhes": [
        "Palavra: 'prêmio' (1x) -> Pontos: +8",
        "Palavra: 'clique aqui' (1x) -> Pontos: +5",
        "Padrão Regex: '(bit\\.ly|...)' (1x) -> +15 pts"
    ]
}

Authors:
Pedro Mikhael
João Vctor 
