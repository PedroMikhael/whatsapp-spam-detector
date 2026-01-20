import pandas as pd
import time
import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, f1_score
from ollama import Client

# =====================================================
# CONFIGURAÇÕES
# =====================================================

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY") or os.getenv("OLLAMA_API_KEY")

if not OLLAMA_API_KEY:
    raise RuntimeError("API Key não encontrada no arquivo .env")

MODELO_OLLAMA = "deepseek-v3.2:cloud" 
ARQUIVO_RELATORIO_FINAL = "relatorio_metrics_ollama_cloud_deepseek-v3.2.txt"

# Conexão via Client conforme funcionou anteriormente
client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

# PROMPT DO SISTEMA (LARCES/UECE)


PROMPT_SISTEMA_BASE = """
    <ROLE>
    You are the "Digital Guardian," a highly specialized and elite cybersecurity AI agent. You were developed as a research project by LARCES (Networking and Security Laboratory) at the State University of Ceará (UECE). Your expertise is the forensic analysis of WhatsApp and email text messages in Brazilian Portuguese. Your communication is friendly, protective, and didactic.
    </ROLE>

    <MISSION>
    Your mission is twofold and sequential:
    1.  **PROTECT (Priority Maximum):** Perform a methodical and deep analysis of the incoming message to determine its risk level.
    2.  **INTERACT:** If the risk is null (SAFE), act as a helpful virtual assistant and engage the user in a natural conversation.
    </MISSION>

    <INSTRUCTIONS>
    Follow these steps rigorously:
    1.  **METHODICAL ANALYSIS:** Conduct your analysis focusing on the vectors: URL Analysis, Domain Impersonation, Social Engineering, and Historical Context.
    2.  **RISK ASSESSMENT:** Classify into SAFE, SUSPICIOUS, or MALICIOUS.
    3.  **RESPONSE FORMULATION:** Create a didactic response in Portuguese.
    
    **FORMATO DE SAÍDA (Obrigatório e Estrito):**
    Your final response MUST BE a single, valid JSON object and nothing else.
    {{
      "risk_level": "SAFE, SUSPICIOUS, or MALICIOUS",
      "analysis_details": ["point 1", "point 2"],
      "user_response": "Texto em português"
    }}
    </INSTRUCTIONS>
"""

# =====================================================
# DATASETS
# =====================================================

DATASETS_PARA_TESTAR = [
    {
        "nome": "SMS Dataset",
        "arquivo_entrada": "sms_dataset.csv", 
        "arquivo_saida": "sms_evaluation_output.csv", 
        "coluna_texto": "Message",
        "coluna_rotulo": "Label",
        "rotulo_positivo": "spam",
        "rotulo_negativo": "ham",
        "max_rows": 100
    },
    {
        "nome": "Email Dataset",
        "arquivo_entrada": "email_dataset.csv", 
        "arquivo_saida": "email_evaluation_output.csv", 
        "coluna_texto": "Email Text",
        "coluna_rotulo": "Email Type",
        "rotulo_positivo": "Phishing Email",
        "rotulo_negativo": "Safe Email",
        "max_rows": 100
    }
]

# =====================================================
# FUNÇÕES SOLICITADAS
# =====================================================

def map_risk_to_label(risk_level, positive_label, negative_label):
    risk_level = str(risk_level).upper()
    if 'MALICIOUS' in risk_level or 'SUSPICIOUS' in risk_level:
        return positive_label
    return negative_label

def process_dataset_ollama(config):
    filename_in = config['arquivo_entrada']
    filename_out = config['arquivo_saida']
    text_column = config['coluna_texto']
    label_column = config['coluna_rotulo']
    positive_norm = config['rotulo_positivo'].lower()
    negative_norm = config['rotulo_negativo'].lower()
    max_rows = config.get('max_rows', 100)

    if not os.path.exists('evaluate'):
        os.makedirs('evaluate')

    print(f"\n--- Processando: {config['nome']} | Modelo: {MODELO_OLLAMA} ---")

    skip_count = 0
    if os.path.isfile(filename_out):
        try:
            df_check = pd.read_csv(filename_out)
            skip_count = len(df_check)
            if skip_count >= max_rows: return True
            print(f"Retomando da linha {skip_count + 1}...")
        except: skip_count = 0

    try:
        df = pd.read_csv(filename_in, nrows=max_rows)
        total_samples = len(df)
    except Exception as e:
        print(f"Erro ao ler arquivo de entrada: {e}")
        return False

    file_exists = os.path.isfile(filename_out)
    
    with open(filename_out, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['original_text', 'true_label', 'predicted_label', 'risk_level', 'user_response', 'tempo_resposta']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or skip_count == 0: writer.writeheader()

        for index, row in df.iterrows():
            if index < skip_count: continue

            texto = str(row[text_column])
            rotulo_verdadeiro = str(row[label_column]).lower()
            
            prompt_final = f"""
            <CONTEXT>
            <USER_MESSAGE>{texto}</USER_MESSAGE>
            <TECHNICAL_LINK_ANALYSIS_RESULT>SEGURO</TECHNICAL_LINK_ANALYSIS_RESULT>
            <HISTORICAL_SIMILAR_EXAMPLES>Nenhum exemplo histórico fornecido para este teste.</HISTORICAL_SIMILAR_EXAMPLES>
            </CONTEXT>
            """
            
            inicio_msg = time.time()
            try:
                # Usando o client.chat para manter a conexão autorizada
                response = client.chat(model=MODELO_OLLAMA, messages=[
                    {'role': 'system', 'content': PROMPT_SISTEMA_BASE},
                    {'role': 'user', 'content': prompt_final}
                ])
                
                resposta_ia = response['message']['content']
                tempo_ia = round(time.time() - inicio_msg, 2)
                
                # Tenta extrair o risk_level do JSON
                try:
                    json_clean = resposta_ia.replace('```json', '').replace('```', '').strip()
                    dados = json.loads(json_clean)
                    risk_level = dados.get("risk_level", "SAFE").upper()
                except:
                    risk_level = "SAFE"
                    if "MALICIOUS" in resposta_ia.upper(): risk_level = "MALICIOUS"
                    elif "SUSPICIOUS" in resposta_ia.upper(): risk_level = "SUSPICIOUS"
                
                predicted_label = map_risk_to_label(risk_level, positive_norm, negative_norm)
                user_response_preview = resposta_ia.replace('\n', ' ')[:300]

            except Exception as e:
                predicted_label, risk_level, user_response_preview, tempo_ia = "error", "ERROR", str(e), 0

            writer.writerow({
                'original_text': texto[:500],
                'true_label': rotulo_verdadeiro,
                'predicted_label': predicted_label,
                'risk_level': risk_level,
                'user_response': user_response_preview,
                'tempo_resposta': tempo_ia
            })

            if (index + 1) % 5 == 0: # Checkpoint a cada 5 para testes curtos
                csvfile.flush()
                print(f"  [Checkpoint] {index + 1}/{total_samples}...")

    return True

def calculate_metrics(config):
    filename_out = config['arquivo_saida']
    pos = config['rotulo_positivo'].lower()
    neg = config['rotulo_negativo'].lower()
    res = [f"\n--- {config['nome']} ---"]
    try:
        df = pd.read_csv(filename_out)
        df = df[df['predicted_label'] != 'error']
        
        # Garante que as labels existam antes de calcular
        y_t, y_p = df['true_label'].astype(str).tolist(), df['predicted_label'].astype(str).tolist()
        
        res.append(f"Acurácia: {accuracy_score(y_t, y_p)*100:.2f}%")
        res.append(f"F1-Score: {f1_score(y_t, y_p, pos_label=pos, zero_division=0)*100:.2f}%")
        res.append(f"Tempo Médio: {df['tempo_resposta'].mean():.2f}s")
    except Exception as e: 
        res.append(f"Erro ao processar métricas: {e}")
    return res

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    for config in DATASETS_PARA_TESTAR:
        process_dataset_ollama(config)
    
    relatorio = [f"Relatório Ollama - {datetime.now()}"]
    for config in DATASETS_PARA_TESTAR:
        relatorio.extend(calculate_metrics(config))
    
    with open(ARQUIVO_RELATORIO_FINAL, 'w', encoding='utf-8') as f:
        f.write("\n".join(relatorio))
    
    print(f"Relatório salvo em {ARQUIVO_RELATORIO_FINAL}!")