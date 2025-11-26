# evaluate_api.py - VERSÃO COM SALVAMENTO CONTÍNUO DE RESULTADOS

import requests
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, f1_score
import time
import os
from datetime import datetime
import csv # Para escrever o CSV de saída

# --- CONFIGURAÇÕES PRINCIPAIS ---
API_URL = "https://chatbot-spam.duckdns.org/api/spam/"
TEMPO_DE_ESPERA_SEGUNDOS = 4.1 # Ajustado para 15 RPM
ARQUIVO_RELATORIO_FINAL = 'evaluation_metrics_report.txt' # Nome do arquivo para salvar as métricas FINAIS

# Defina os arquivos CSV, colunas e limites de linhas
DATASETS_PARA_TESTAR = [
    {
        "nome": "SMS Dataset",
        "arquivo_entrada": "sms_dataset.csv",
        "arquivo_saida": "sms_evaluation_output.csv", # Arquivo para salvar resultados
        "coluna_texto": "Message",
        "coluna_rotulo": "Label",
        "rotulo_positivo": "spam",
        "rotulo_negativo": "ham",
        "max_rows": 2003
    },
    {
        "nome": "Email Dataset",
        "arquivo_entrada": "email_dataset.csv",
        "arquivo_saida": "email_evaluation_output.csv", # Arquivo para salvar resultados
        "coluna_texto": "Email Text",
        "coluna_rotulo": "Email Type",
        "rotulo_positivo": "Phishing Email",
        "rotulo_negativo": "Safe Email",
        "max_rows": 2294
    }
]

# Mapeamento da Resposta da API
def map_risk_to_label(risk_level, positive_label, negative_label):
    if risk_level in ['SUSPICIOUS', 'MALICIOUS']:
        return positive_label
    elif risk_level == 'SAFE':
        return negative_label
    else:
        return negative_label

def process_dataset(config):
    """Lê uma amostra do dataset, chama a API e SALVA cada resultado."""
    
    filename_in = config['arquivo_entrada']
    filename_out = config['arquivo_saida']
    text_column = config['coluna_texto']
    label_column = config['coluna_rotulo']
    positive_label = config['rotulo_positivo']
    negative_label = config['rotulo_negativo']
    max_rows = config.get('max_rows', None)
    
    print(f"\n--- Iniciando Processamento do Dataset: {config['nome']} ---")
    
    try:
        # Lê apenas as linhas necessárias
        df = pd.read_csv(filename_in, nrows=max_rows -1 if max_rows else None)
        print(f"Dataset de entrada '{filename_in}' carregado com {len(df)} amostras.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada '{filename_in}' não encontrado.")
        return False
    except Exception as e:
        print(f"ERRO ao ler o arquivo CSV de entrada: {e}")
        return False

    if text_column not in df.columns or label_column not in df.columns:
        print(f"ERRO: Colunas '{text_column}' ou '{label_column}' não encontradas no arquivo de entrada.")
        return False

    total_samples = len(df)
    start_time = time.time()
    
    # Abre o arquivo CSV de SAÍDA para escrita (append)
    try:
        file_exists = os.path.isfile(filename_out)
        with open(filename_out, 'a', newline='', encoding='utf-8') as csvfile:
            # Define as colunas do arquivo de saída
            fieldnames = ['original_text', 'true_label', 'predicted_label', 'risk_level', 'analysis_details']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escreve o cabeçalho apenas se o arquivo for novo
            if not file_exists:
                writer.writeheader()

            for index, row in df.iterrows():
                # --- Pular linhas já processadas (Opcional, mas útil se parar/reiniciar) ---
                # Poderíamos adicionar aqui uma lógica para ler o 'filename_out' e ver qual foi a última linha processada
                # Por simplicidade, vamos reprocessar por enquanto, mas o resultado será salvo.
                # -----------------------------------------------------------------------------
                
                texto = str(row[text_column])
                rotulo_verdadeiro = str(row[label_column])
                rotulo_verdadeiro_norm = rotulo_verdadeiro.lower()
                positive_norm = positive_label.lower()
                negative_norm = negative_label.lower()
                
                if rotulo_verdadeiro_norm not in [positive_norm, negative_norm]:
                    continue

                predicted_label = negative_norm # Default em caso de erro
                risk_level = "ERROR"
                analysis_details_str = "Erro na chamada da API"

                try:
                    response = requests.post(API_URL, json={'texto': texto}, timeout=90)
                    
                    if response.status_code == 200:
                        resultado_api = response.json()
                        risk_level = resultado_api.get('risk_level', 'INDETERMINADO')
                        predicted_label = map_risk_to_label(risk_level, positive_norm, negative_norm)
                        analysis_details_str = str(resultado_api.get('analysis_details', 'N/A'))
                    else:
                        analysis_details_str = f"API Error {response.status_code}: {response.text}"
                        print(f"\nERRO da API na linha {index+1}: Status {response.status_code}.")

                except requests.exceptions.Timeout:
                    analysis_details_str = "API Timeout"
                    print(f"\nERRO: Timeout na API para a linha {index+1}.")
                except requests.exceptions.RequestException as e:
                    analysis_details_str = f"Connection Error: {e}"
                    print(f"\nERRO de conexão na API para a linha {index+1}: {e}.")
                except Exception as e:
                    analysis_details_str = f"Unexpected Error: {e}"
                    print(f"\nERRO inesperado ao processar linha {index+1}: {e}.")
                
                # *** A MÁGICA: SALVA O RESULTADO IMEDIATAMENTE ***
                writer.writerow({
                    'original_text': texto[:500], # Salva apenas os primeiros 500 caracteres
                    'true_label': rotulo_verdadeiro_norm,
                    'predicted_label': predicted_label,
                    'risk_level': risk_level,
                    'analysis_details': analysis_details_str[:1000] # Limita o tamanho
                })

                # Mostra progresso no terminal
                if (index + 1) % 10 == 0:
                    print(f"  Processado {index + 1}/{total_samples}...")
                
                time.sleep(TEMPO_DE_ESPERA_SEGUNDOS) 

    except Exception as e:
        print(f"\nERRO GERAL durante o processamento de {filename_in}: {e}")
        return False # Indica que houve erro

    end_time = time.time()
    tempo_total_min = (end_time - start_time)/60
    print(f"\n--- Processamento Concluído para {config['nome']} ---")
    print(f"Tempo total: {tempo_total_min:.2f} minutos")
    print(f"Resultados detalhados salvos em: {filename_out}")
    return True # Indica sucesso

def calculate_metrics_from_output(config):
    """Lê o arquivo de saída e calcula as métricas."""
    filename_out = config['arquivo_saida']
    positive_label = config['rotulo_positivo'].lower()
    negative_label = config['rotulo_negativo'].lower()
    
    report_lines = []
    report_lines.append(f"\n--- Métricas de Avaliação para: {config['nome']} ---")
    
    try:
        df_results = pd.read_csv(filename_out)
        if df_results.empty:
            report_lines.append("Arquivo de resultados vazio ou não encontrado.")
            return report_lines
            
        labels_verdadeiros = df_results['true_label'].tolist()
        predicoes_ia = df_results['predicted_label'].tolist()
        
        accuracy = accuracy_score(labels_verdadeiros, predicoes_ia)
        precision = precision_score(labels_verdadeiros, predicoes_ia, pos_label=positive_label, zero_division=0)
        recall = recall_score(labels_verdadeiros, predicoes_ia, pos_label=positive_label, zero_division=0)
        f1 = f1_score(labels_verdadeiros, predicoes_ia, pos_label=positive_label, zero_division=0)
        conf_matrix = confusion_matrix(labels_verdadeiros, predicoes_ia, labels=[negative_label, positive_label])

        report_lines.append(f"\nResultados para '{positive_label}' como classe positiva:")
        report_lines.append(f"Acurácia Geral: {accuracy * 100:.2f}%")
        report_lines.append(f"Precisão (Spam): {precision * 100:.2f}%")
        report_lines.append(f"Recall (Spam):   {recall * 100:.2f}%")
        report_lines.append(f"F1-Score:        {f1 * 100:.2f}%")
        
        report_lines.append("\nMatriz de Confusão:")
        report_lines.append(f"                Previsto '{negative_label}'  Previsto '{positive_label}'")
        report_lines.append(f"Real '{negative_label}'      {conf_matrix[0][0]:<6}           {conf_matrix[0][1]:<6}")
        report_lines.append(f"Real '{positive_label}'      {conf_matrix[1][0]:<6}           {conf_matrix[1][1]:<6}")
        report_lines.append("--------------------------------------------------")
        
    except FileNotFoundError:
        report_lines.append(f"ERRO: Arquivo de resultados '{filename_out}' não encontrado para calcular métricas.")
    except Exception as e:
         report_lines.append(f"ERRO ao calcular métricas do arquivo '{filename_out}': {e}")
         
    return report_lines

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    
    overall_success = True
    
    # Roda o processamento para cada dataset configurado
    for config in DATASETS_PARA_TESTAR:
        success = process_dataset(config)
        if not success:
            overall_success = False # Marca se algum processamento falhou
            
    if not overall_success:
        print("\n\nAVISO: Ocorreram erros durante o processamento. Verifique os logs acima.")
        print("As métricas podem ser calculadas apenas com os resultados salvos até o momento.")

    # Calcula as métricas a partir dos arquivos de saída
    all_report_lines = []
    all_report_lines.append(f"Relatório de Métricas da API VerificAI - Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    all_report_lines.append("==================================================")
    
    for config in DATASETS_PARA_TESTAR:
        metric_lines = calculate_metrics_from_output(config)
        all_report_lines.extend(metric_lines)
        all_report_lines.append("\n") 

    # Salva o relatório de métricas final
    try:
        with open(ARQUIVO_RELATORIO_FINAL, 'w', encoding='utf-8') as f:
            for line in all_report_lines:
                f.write(line + '\n')
        print(f"\n\nRelatório de métricas final salvo no arquivo: {ARQUIVO_RELATORIO_FINAL}")
    except Exception as e:
        print(f"\nERRO ao salvar o arquivo de relatório final: {e}")