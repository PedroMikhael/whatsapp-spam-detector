import os
import requests
import json
import re
from django.conf import settings
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

genai.configure(api_key=settings.GEMINI_API_KEY)

try:
    embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
   
    vector_store = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_function
    )
    RAG_ATIVO = True
    print("✅ RAG: Banco de dados vetorial carregado com sucesso.")
except Exception as e:
    RAG_ATIVO = False
    print(f"⚠️ RAG: Não foi possível carregar o banco vetorial. Erro: {e}")


def buscar_exemplos_similares(texto_usuario):
    """Busca exemplos parecidos no banco de dados vetorial."""
    if not RAG_ATIVO:
        return ""
    
    try:
        
        resultados = vector_store.similarity_search(texto_usuario, k=3)
        
        contexto_rag = "\n--- HISTORICAL SIMILAR EXAMPLES (from Vector Database) ---\n"
        if not resultados:
             contexto_rag += "No similar historical data found.\n"
        else:
            for i, doc in enumerate(resultados):
                rotulo = doc.metadata.get('label', 'Unknown')
                conteudo = doc.page_content.replace("\n", " ")[:300] 
                contexto_rag += f"Example {i+1} (Actual Label: {rotulo}): \"{conteudo}\"\n"
        
        return contexto_rag
    except Exception as e:
        print(f"Erro na busca RAG: {e}")
        return ""

def verificar_link_com_safe_browsing(link: str) -> str:
    url_api = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    api_key = settings.SAFE_BROWSING_API_KEY
    payload = {"client": {"clientId": "spamapiproject", "clientVersion": "1.0.0"},"threatInfo": {"threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],"platformTypes": ["ANY_PLATFORM"],"threatEntryTypes": ["URL"],"threatEntries": [{"url": link}]}}
    params = {'key': api_key}
    try:
        response = requests.post(url_api, params=params, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'matches' in data:
            threat_type = data['matches'][0]['threatType']
            return f"PERIGOSO (Threat detected: {threat_type})"
        else:
            return "SEGURO"
    except requests.exceptions.RequestException as e:
        return "INDETERMINADO (Verification failed)"


def analisar_com_gemini(texto: str) -> dict:
    links_encontrados = re.findall(r'(https?://\S+)', texto)
    resultado_safe_browsing = "Nenhum link na mensagem."
    if links_encontrados:
        primeiro_link = links_encontrados[0]
        resultado_safe_browsing = verificar_link_com_safe_browsing(primeiro_link)
    
    contexto_historico = buscar_exemplos_similares(texto)

    prompt = f"""
    <ROLE>
    You are the "Digital Guardian," a highly specialized and elite cybersecurity AI agent. You were developed as a research project by LARCES (Networking and Security Laboratory) at the State University of Ceará (UECE). Your expertise is the forensic analysis of WhatsApp and email text messages in Brazilian Portuguese. Your communication is friendly, protective, and didactic.
    </ROLE>

    <MISSION>
    Your mission is twofold and sequential:
    1.  **PROTECT (Priority Maximum):** Perform a methodical and deep analysis of the incoming message to determine its risk level.
    2.  **INTERACT:** If the risk is null (SAFE), act as a helpful virtual assistant and engage the user in a natural conversation.
    </MISSION>

    <CONTEXT>
    <USER_MESSAGE>{texto}</USER_MESSAGE>
    <TECHNICAL_LINK_ANALYSIS_RESULT>{resultado_safe_browsing}</TECHNICAL_LINK_ANALYSIS_RESULT>
    {contexto_historico} 
    </CONTEXT>

    <INSTRUCTIONS>
    Follow these steps rigorously:

    1.  **METHODICAL ANALYSIS:** Conduct your analysis focusing on the following vectors of attack:
        -   **URL Analysis:** Evaluate the `TECHNICAL_LINK_ANALYSIS_RESULT`. A result of "PERIGOSO" immediately classifies the message as "MALICIOUS". **The SAFE result from this tool is only a recommendation and CAN BE OVERRIDDEN by contextual analysis.**
        -   **Domain Impersonation (CRITICAL FALSO NEGATIVE CHECK):** If a link is present AND the message impersonates an entity (e.g., UECE, Banco do Brasil, Cearaprev), check if the link's domain matches the official entity's domain. **If the link is for an 'official action' (recadastramento, payment, etc.) but uses a non-official, unrelated domain (e.g., 'globalindiaschool.org' instead of 'uece.br'), the risk level MUST be increased to MALICIOUS, regardless of the 'SEGURO' technical result.** This is the primary defense against new, uncategorized phishing sites.
        -   **Social Engineering:** Identify tactics of **greed** (prizes, easy money), **urgency** (threats, deadlines), **authority** (impersonating a bank or government), or **scarcity** (limited spots).
        -   **Historical Context (RAG):** Use the examples provided in the "HISTORICAL SIMILAR EXAMPLES" section. If similar historical messages were labeled SPAM/PHISHING, significantly increase the risk level.

    2.  **RISK ASSESSMENT:** Classify the risk into ONE of three levels: `SAFE`, `SUSPICIOUS`, or `MALICIOUS`.

    3.  **RESPONSE FORMULATION:** Create a didactic and protective response in **Portuguese** for the user, explaining the reason for your decision. If a link was analyzed and the result was 'SEGURO' but the message was still classified as SUSPICIOUS or MALICIOUS due to domain mismatch/social engineering, ensure this reasoning is clear.

    **FORMATO DE SAÍDA (Obrigatório e Estrito):**
    Your final response MUST BE a single, valid JSON object and nothing else. The structure is:
    {{
      "risk_level": "SAFE, SUSPICIOUS, or MALICIOUS",
      "analysis_details": ["A list of strings, where each string is a specific, technical point of your analysis."],
      "user_response": "The exact and elaborated Portuguese text to be sent back to the user."
    }}
    </INSTRUCTIONS>
    
    ---
    **MENSAGEM REAL PARA ANÁLISE:**
    "{texto}"
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if not match:
            raise ValueError("Nenhum JSON válido encontrado na resposta da IA.")
        resultado_json = json.loads(match.group(0))
        
        if "risk_level" not in resultado_json or "user_response" not in resultado_json:
             raise ValueError("A resposta da IA não contém as chaves esperadas.")

        print("Análise do Gemini recebida com sucesso:", resultado_json)
        return resultado_json

    except Exception as e:
        print(f"Erro ao chamar ou processar a resposta da API do Gemini: {e}")
        return {
            "risk_level": "INDETERMINADO",
            "analysis_details": [f"Erro interno ao processar a mensagem com a IA: {e}"],
            "user_response": "Desculpe, não consegui processar sua mensagem neste momento. 🙁"
        }

def enviar_mensagem_whatsapp(numero_destinatario: str, mensagem: str):
    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": numero_destinatario, "type": "text", "text": {"body": mensagem}}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        return False, str(e)
    

def adicionar_ao_chromadb(texto: str, rotulo: str) -> bool:
    """
    Adiciona um novo documento (texto e rótulo) ao banco de dados ChromaDB.
    Isso é o 'treinamento' do Active Learning.
    """
    global vector_store, RAG_ATIVO
    
    if not RAG_ATIVO:
        print("⚠️ RAG: Treinamento falhou. O banco de dados vetorial não foi carregado.")
        return False
        
    try:
       
        novo_documento = Document(
            page_content=texto,
            metadata={"label": rotulo}
        )
        
        
        vector_store.add_documents([novo_documento])
        
        
        vector_store.persist()
        
        print(f"✅ RAG: Mensagem adicionada com sucesso ao ChromaDB. Novo rótulo: {rotulo}")
        return True
        
    except Exception as e:
        print(f"❌ RAG: Erro ao adicionar documento ao ChromaDB: {e}")
        return False