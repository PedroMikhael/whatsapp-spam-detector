# evaluate_api.py

import requests
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, f1_score
import time
import os

# --- CONFIGURAÇÕES PRINCIPAIS ---
API_URL = "https://chatbot-spam.duckdns.org/api/spam/"
TEMPO_DE_ESPERA_SEGUNDOS = 4.1 # (60 segundos / 15 RPM = 4s. Adicionamos 0.1s de folga)

# Defina os arquivos CSV e suas colunas
DATASETS_PARA_TESTAR = [
    {
        "nome": "SMS Dataset",
        "arquivo": "sms_dataset.csv", # Coloque o nome exato do seu arquivo CSV de SMS
        "coluna_texto": "Message",
        "coluna_rotulo": "Label",
        "rotulo_positivo": "spam", # O que conta como "spam"
        "rotulo_negativo": "ham" # O que conta como "seguro"
    },
    {
        "nome": "Email Dataset",
        "arquivo": "email_dataset.csv", # Coloque o nome exato do seu arquivo CSV de Email
        "coluna_texto": "Email Text",
        "coluna_rotulo": "Email Type",
        "rotulo_positivo": "Phishing Email",
        "rotulo_negativo": "Safe Email"
    }
]

# Mapeamento da Resposta da API para o Rótulo do Dataset
# SAFE -> ham/Safe Email
# SUSPICIOUS -> spam/Phishing Email
# MALICIOUS -> spam/Phishing Email
def map_risk_to_label(risk_level, positive_label, negative_label):
    if risk_level in ['SUSPICIOUS', 'MALICIOUS']:
        return positive_label
    elif risk_level == 'SAFE':
        return negative_label
    else: # INDETERMINADO ou erro
        return negative_label

def evaluate_dataset(config):
    """Lê um dataset, chama a API para cada entrada e calcula as métricas."""
    
    filename = config['arquivo']
    text_column = config['coluna_texto']
    label_column = config['coluna_rotulo']
    positive_label = config['rotulo_positivo']
    negative_label = config['rotulo_negativo']
    
    print(f"\n--- Iniciando Avaliação do Dataset: {config['nome']} ---")
    
    try:
        df = pd.read_csv(filename)
        print(f"Dataset carregado com {len(df)} amostras.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filename}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao ler o arquivo CSV: {e}")
        return

    if text_column not in df.columns or label_column not in df.columns:
        print(f"ERRO: Colunas '{text_column}' ou '{label_column}' não encontradas no arquivo.")
        return

    labels_verdadeiros = []
    predicoes_ia = []
    
    total_samples = len(df)
    start_time = time.time()

    for index, row in df.iterrows():
        texto = str(row[text_column])
        rotulo_verdadeiro = str(row[label_column])

        # Normaliza os rótulos verdadeiros para minúsculas para comparação
        rotulo_verdadeiro_norm = rotulo_verdadeiro.lower()
        positive_norm = positive_label.lower()
        negative_norm = negative_label.lower()
        
        if rotulo_verdadeiro_norm not in [positive_norm, negative_norm]:
            continue
            
        labels_verdadeiros.append(rotulo_verdadeiro_norm)

        try:
            # 1. Chama a sua API
            response = requests.post(API_URL, json={'texto': texto}, timeout=60)
            
            if response.status_code == 200:
                resultado_api = response.json()
                risk_level = resultado_api.get('risk_level', 'INDETERMINADO')
                
                # 2. Mapeia a previsão da IA
                predicao_mapeada = map_risk_to_label(risk_level, positive_norm, negative_norm)
                predicoes_ia.append(predicao_mapeada)
            else:
                # Se a API retornar um erro (400, 500, etc.)
                print(f"ERRO da API na linha {index+1}: Status {response.status_code}. Resposta: {response.text}")
                predicoes_ia.append(negative_norm) # Penaliza a IA

            # Mostra progresso
            if (index + 1) % 5 == 0:
                print(f"  Processado {index + 1}/{total_samples}...")

        except requests.exceptions.RequestException as e:
            print(f"ERRO de conexão/timeout ao chamar a API para a linha {index+1}: {e}. Pulando.")
            predicoes_ia.append(negative_norm)
        except Exception as e:
            print(f"ERRO inesperado ao processar a linha {index+1}: {e}. Pulando.")
            predicoes_ia.append(negative_norm)
            
        # 3. ESPERA O TEMPO CORRETO PARA RESPEITAR O LIMITE DA API
        print(f"Aguardando {TEMPO_DE_ESPERA_SEGUNDOS}s para a próxima requisição...")
        time.sleep(TEMPO_DE_ESPERA_SEGUNDOS) 

    end_time = time.time()
    print(f"\n--- Avaliação Concluída para {config['nome']} ---")
    print(f"Tempo total: {(end_time - start_time)/60:.2f} minutos")

    # Calcula as Métricas
    accuracy = accuracy_score(labels_verdadeiros, predicoes_ia)
    precision = precision_score(labels_verdadeiros, predicoes_ia, pos_label=positive_norm, zero_division=0)
    recall = recall_score(labels_verdadeiros, predicoes_ia, pos_label=positive_norm, zero_division=0)
    f1 = f1_score(labels_verdadeiros, predicoes_ia, pos_label=positive_norm, zero_division=0)
    conf_matrix = confusion_matrix(labels_verdadeiros, predicoes_ia, labels=[negative_norm, positive_norm])

    print(f"\nResultados para '{positive_label}' como classe positiva:")
    print(f"Acurácia Geral: {accuracy * 100:.2f}%")
    print(f"Precisão (Spam): {precision * 100:.2f}% (Das que a IA disse ser spam, quantas eram?)")
    print(f"Recall (Spam):   {recall * 100:.2f}% (De todo o spam real, quanto a IA pegou?)")
    print(f"F1-Score:        {f1 * 100:.2f}% (Média harmônica de precisão e recall)")
    
    print("\nMatriz de Confusão:")
    print(f"                Previsto '{negative_label}'  Previsto '{positive_label}'")
    print(f"Real '{negative_label}'      {conf_matrix[0][0]:<6}           {conf_matrix[0][1]:<6}")
    print(f"Real '{positive_label}'      {conf_matrix[1][0]:<6}           {conf_matrix[1][1]:<6}")
    print("(Linhas = Real, Colunas = Previsto pela IA)")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    for config in DATASETS_PARA_TESTAR:
        evaluate_dataset(config)