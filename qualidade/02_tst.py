import pandas as pd
import os

# Digite o nome do seu arquivo aqui
ARQUIVO = '03_pickup_sales_dataset.csv'

print("LOG: Iniciando o script...")

# Verificação de segurança 1: O arquivo realmente existe nesta pasta?
if not os.path.exists(ARQUIVO):
    print(f"ERRO: O arquivo '{ARQUIVO}' não foi encontrado na pasta atual!")
    print(f"Arquivos que existem nesta pasta: {os.listdir('.')}")
else:
    print(f"LOG: Arquivo encontrado. Tamanho: {os.path.getsize(ARQUIVO)} bytes.")
    
    try:
        print("LOG: Tentando ler o CSV com o Pandas...")
        df = pd.read_csv(ARQUIVO, sep=';', encoding='utf-8')
        
        # O flush=True força o terminal a cuspir o texto na tela na hora
        print("\n====================================", flush=True)
        print(f"SUCESSO! Linhas: {df.shape[0]} | Colunas: {df.shape[1]}", flush=True)
        print("====================================\n", flush=True)
        
        print("--- VALORES NULOS ---", flush=True)
        print(df.isnull().sum(), flush=True)
        
        print("\n--- DUPLICADAS ---", flush=True)
        print(f"Total: {df.duplicated().sum()}", flush=True)

    except Exception as e:
        print(f"\nERRO CRÍTICO DO PANDAS: {e}", flush=True)

print("\nLOG: Fim do script.")