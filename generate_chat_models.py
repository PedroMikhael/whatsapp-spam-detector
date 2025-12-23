import matplotlib.pyplot as plt
import numpy as np

# Estrutura: [Acurácia(%), Tempo(s), F1-Score(%)]

# 1. GEMINI 2.0-FLASH (BASELINE)
gemini_sms = [89.90, 1.0, 70.59]
gemini_email = [89.90, 1.0, 84.38]

# 2. LLAMA 3.2 3B (MODELO LEVE)
llama3b_sms = [86.80, 2.49, 45.90]
llama3b_email = [66.60, 5.67, 44.52]

# 3. LLAMA 3.1 8B (SEM PROMPT/ERRO)
# Note o tempo alto e acurácia baixa
llama8b_v1_sms = [29.00, 15.76, 25.26]
llama8b_v1_email = [50.00, 14.79, 50.00]

# 4. LLAMA 3.1 8B (FINAL/OTIMIZADO)

llama8b_v2_sms = [69.30, 4.10, 49.09]
llama8b_v2_email = [85.49, 6.54, 83.84]

models_labels = ["Gemini 1.5 (Cloud)", "Llama 3B (Local)", "Llama 8B (Sem Prompt)", "Llama 8B (Otimizado)"]
colors = ['gold', 'skyblue', 'salmon', 'limegreen'] 
markers = ['*', 'o', 'X', 'o'] 

def plotar_dispersao_4modelos(titulo, arquivo, d_gemini, d_3b, d_v1, d_v2):
    plt.figure(figsize=(11, 7))
    
    
    data_points = [d_gemini, d_3b, d_v1, d_v2]
    
    for i, data in enumerate(data_points):
        acc = data[0]
        time = data[1]
        f1 = data[2]
        
       
        plt.scatter(time, acc, s=f1*12, c=colors[i], marker=markers[i], 
                    edgecolors='black', linewidth=1.5, alpha=0.8, label=models_labels[i])
        
        
        offset_y = -25 if i == 0 else 15
        plt.annotate(f"F1: {f1}%", (time, acc), xytext=(0, offset_y), 
                     textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

        
        if i == 3: 
            plt.annotate("", xy=(time, acc), xytext=(d_v1[1], d_v1[0]),
                         arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, ls='--'))
            plt.text((time + d_v1[1])/2, (acc + d_v1[0])/2, "Evolução via Prompt", 
                     fontsize=8, color='gray', ha='center', rotation=15)

    plt.title(f"{titulo}\n(Tamanho = F1-Score | Seta = Ganho com Prompt Engineering)", fontsize=14, fontweight='bold')
    plt.xlabel("Tempo de Resposta (s) - Quanto menor, melhor", fontsize=11)
    plt.ylabel("Acurácia (%) - Quanto maior, melhor", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower right')
    
    
    plt.xlim(0, 18) 
    plt.ylim(20, 105) 
    
    plt.tight_layout()
    plt.savefig(arquivo)
    print(f"✅ Gráfico salvo: {arquivo}")

plotar_dispersao_4modelos("SMS: Impacto do Prompt na Performance", "scatter_sms_4modelos.png", 
                          gemini_sms, llama3b_sms, llama8b_v1_sms, llama8b_v2_sms)

plotar_dispersao_4modelos("Email: Impacto do Prompt na Performance", "scatter_email_4modelos.png", 
                          gemini_email, llama3b_email, llama8b_v1_email, llama8b_v2_email)


def plotar_barras_4modelos():
    labels = ['SMS', 'Email']
    x = np.arange(len(labels))
    width = 0.2 
    
    
    acc_gemini = [gemini_sms[0], gemini_email[0]]
    acc_3b = [llama3b_sms[0], llama3b_email[0]]
    acc_v1 = [llama8b_v1_sms[0], llama8b_v1_email[0]]
    acc_v2 = [llama8b_v2_sms[0], llama8b_v2_email[0]]

    fig, ax = plt.subplots(figsize=(12, 6))
    
    
    r1 = ax.bar(x - 1.5*width, acc_gemini, width, label=models_labels[0], color=colors[0])
    r2 = ax.bar(x - 0.5*width, acc_3b, width, label=models_labels[1], color=colors[1])
    r3 = ax.bar(x + 0.5*width, acc_v1, width, label=models_labels[2], color=colors[2], hatch='//') 
    r4 = ax.bar(x + 1.5*width, acc_v2, width, label=models_labels[3], color=colors[3])

    ax.set_ylabel('Acurácia (%)', fontsize=12)
    ax.set_title('Comparativo Final: O Impacto da Engenharia de Prompt', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=4) 
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.0f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    autolabel(r1)
    autolabel(r2)
    autolabel(r3)
    autolabel(r4)

    plt.tight_layout()
    plt.savefig("barra_comparativa_4modelos.png")
    print(f"✅ Gráfico salvo: barra_comparativa_4modelos.png")

plotar_barras_4modelos()