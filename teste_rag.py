import os
from decouple import config
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma


try:
    os.environ["GOOGLE_API_KEY"] = config('GEMINI_API_KEY')
except:
    print("ERRO: Configure seu .env com a GEMINI_API_KEY")
    exit()


embedding_function = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")

print("Carregando banco de dados vetorial...")
try:
    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding_function
    )
    print(f"Banco carregado! Total de documentos indexados: {vector_store._collection.count()}")
except Exception as e:
    print(f"Erro ao carregar o banco: {e}")
    exit()


print("\n--- TESTE DE RAG (Busca por Similaridade) ---")
print("Digite uma mensagem para ver se encontramos exemplos parecidos no banco.")
print("Digite 'sair' para encerrar.\n")

while True:
    query = input("Mensagem suspeita: ")
    if query.lower() in ['sair', 'exit']:
        break
    
    print(f"\nBuscando exemplos similares para: '{query}'...")
    
    
    results = vector_store.similarity_search(query, k=3)
    
    if not results:
        print("Nenhum resultado encontrado.")
    
    for i, doc in enumerate(results):
        tipo = doc.metadata.get('source', 'Desconhecido')
        rotulo = doc.metadata.get('label', 'Desconhecido')
        conteudo = doc.page_content
        
        print(f"\n--- Resultado {i+1} ({tipo} | {rotulo}) ---")
        print(f"Texto: {conteudo[:200]}...") 
    print("-" * 50)