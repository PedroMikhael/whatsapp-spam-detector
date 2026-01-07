import matplotlib.pyplot as plt
import numpy as np

# 1. GEMINI 2.0-FLASH (BASELINE)
gemini_sms = [89.90, 2.3, 70.59]
gemini_email = [89.90, 4.28, 84.38]

# 2. LLAMA 3.2 3B (MODELO LEVE)
llama3b_sms = [86.80, 2.49, 45.90]
llama3b_email = [66.60, 5.67, 44.52]

# 3. LLAMA 3.1 8B (SEM PROMPT/ERRO)
llama8b_v1_sms = [29.00, 15.76, 25.26]
llama8b_v1_email = [50.00, 14.79, 50.00]

# 4. LLAMA 3.1 8B (FINAL/OTIMIZADO)
llama8b_v2_sms = [69.30, 4.10, 49.09]
llama8b_v2_email = [85.49, 6.54, 83.84]

# 5. GEMINI 3-FLASH (CLOUD) - NOVO MODELO
gemini3_flash_sms = [98.7, 3.41, 99.2]
gemini3_flash_email = [97.5, 7.96, 98.2]

# 6. DEEPSEEK V3.2 (CLOUD)
deepseek_sms = [90.00, 15.05, 76.19]
deepseek_email = [99.87, 15.28, 99.59]

# 7. GEMMA 3 12B (MODELO NOVO)
gemma3_sms = [96.00, 7.62, 87.50]
gemma3_email = [81.00, 15.62, 72.46]

models_labels = [
    "Gemini 2.0 (Cloud)", 
    "Llama 3B (Local)", 
    "Llama 8B (Sem Prompt)", 
    "Llama 8B (Otimizado)", 
    "Gemini 3 Flash (Cloud)",
    "DeepSeek v3.2 (Cloud)",
    "Gemma 3 12B"
]

colors = ['gold', 'skyblue', 'salmon', 'limegreen', 'darkviolet', 'crimson', 'teal'] 
markers = ['*', 'o', 'X', 'o', 'P', 's', 'D'] 

def plotar_dispersao_7modelos(titulo, arquivo, d_gemini, d_3b, d_v1, d_v2, d_gem3, d_deep, d_gemma3):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    data_points = [d_gemini, d_3b, d_v1, d_v2, d_gem3, d_deep, d_gemma3]
    
    for i, data in enumerate(data_points):
        acc, time, f1 = data[0], data[1], data[2]
        
        ax.scatter(time, acc, s=f1*15, c=colors[i], marker=markers[i], 
                   edgecolors='black', linewidth=1.5, alpha=0.8, label=models_labels[i])
        
        offset_y = 15
        if i == 0: offset_y = -25
        if i == 4: offset_y = 20
        if i == 5: offset_y = -20
            
        ax.annotate(f"F1: {f1}%", (time, acc), xytext=(0, offset_y), 
                    textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

        if i == 3: 
            ax.annotate("", xy=(time, acc), xytext=(d_v1[1], d_v1[0]),
                         arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, ls='--'))
            ax.text((time + d_v1[1])/2, (acc + d_v1[0])/2, "Evolução via Prompt", 
                     fontsize=8, color='gray', ha='center', rotation=15)

    ax.set_title(f"{titulo}\n(Tamanho = F1-Score)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Tempo de Resposta (s) - Menor é melhor", fontsize=11)
    ax.set_ylabel("Acurácia (%) - Maior é melhor", fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', fontsize=10)
    
    ax.set_xlim(0, 20) 
    ax.set_ylim(20, 110) 
    
    plt.tight_layout()
    plt.savefig(arquivo)
    print(f"✅ Gráfico salvo: {arquivo}")

plotar_dispersao_7modelos("SMS: Comparativo Geral de Performance", "scatter_sms_7modelos.png", 
                          gemini_sms, llama3b_sms, llama8b_v1_sms, llama8b_v2_sms, gemini3_flash_sms, deepseek_sms, gemma3_sms)

plotar_dispersao_7modelos("Email: Comparativo Geral de Performance", "scatter_email_7modelos.png", 
                          gemini_email, llama3b_email, llama8b_v1_email, llama8b_v2_email, gemini3_flash_email, deepseek_email, gemma3_email)


def plotar_barras_7modelos():
    labels = ['SMS', 'Email']
    x = np.arange(len(labels))
    width = 0.12 # Reduced width to fit 7 bars
    
    acc_gemini = [gemini_sms[0], gemini_email[0]]
    acc_3b = [llama3b_sms[0], llama3b_email[0]]
    acc_v1 = [llama8b_v1_sms[0], llama8b_v1_email[0]]
    acc_v2 = [llama8b_v2_sms[0], llama8b_v2_email[0]]
    acc_gem3 = [gemini3_flash_sms[0], gemini3_flash_email[0]]
    acc_deep = [deepseek_sms[0], deepseek_email[0]]
    acc_gemma3 = [gemma3_sms[0], gemma3_email[0]]

    fig, ax = plt.subplots(figsize=(15, 8))
    
    r1 = ax.bar(x - 3*width, acc_gemini, width, label=models_labels[0], color=colors[0])
    r2 = ax.bar(x - 2*width, acc_3b, width, label=models_labels[1], color=colors[1])
    r3 = ax.bar(x - 1*width, acc_v1, width, label=models_labels[2], color=colors[2], hatch='//') 
    r4 = ax.bar(x, acc_v2, width, label=models_labels[3], color=colors[3])
    r5 = ax.bar(x + 1*width, acc_gem3, width, label=models_labels[4], color=colors[4])
    r6 = ax.bar(x + 2*width, acc_deep, width, label=models_labels[5], color=colors[5])
    r7 = ax.bar(x + 3*width, acc_gemma3, width, label=models_labels[6], color=colors[6])

    ax.set_ylabel('Acurácia (%)', fontsize=12)
    ax.set_title('Comparativo Final: 7 Modelos (Local vs Cloud)', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=4, fontsize=10) 
    ax.set_ylim(0, 120)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold') # Reduced fontsize

    autolabel(r1); autolabel(r2); autolabel(r3); autolabel(r4); autolabel(r5); autolabel(r6); autolabel(r7)

    plt.tight_layout()
    plt.savefig("barra_comparativa_7modelos.png")
    print(f"✅ Gráfico salvo: barra_comparativa_7modelos.png")

plotar_barras_7modelos()