import pandas as pd
import numpy as np

def validar_qualidade_csv(caminho_arquivo):
    try:
        # Carregar o dataset
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
        print(f"--- Relatório de Qualidade: {caminho_arquivo} ---\n")
    except Exception as e:
        return f"Erro ao ler o arquivo: {e}"

    # 1. Informações Gerais
    print(f"Total de Registros: {df.shape[0]}")
    print(f"Total de Colunas: {df.shape[1]}")
    print("-" * 30)

    # 2. Verificação de Valores Nulos (Completude)
    nulos = df.isnull().sum()
    print("Valores Nulos por Coluna:")
    print(nulos[nulos > 0] if nulos.any() else "Nenhum valor nulo encontrado.")
    print("-" * 30)

    # 3. Verificação de Duplicatas (Unicidade)
    duplicados = df.duplicated().sum()
    print(f"Linhas Duplicadas: {duplicados}")
    print("-" * 30)

    # 4. Verificação de Tipos de Dados
    print("Tipos de Dados:")
    print(df.dtypes)
    print("-" * 30)

    # 5. Análise Estatística Rápida (Outliers e Consistência)
    # Mostra apenas colunas numéricas
    print("Resumo Estatístico (Colunas Numéricas):")
    print(df.describe())
    
    return df

# Exemplo de uso:
# validar_qualidade_csv('seus_dados.csv')

# if __name__ == "__main__":
validar_qualidade_csv('pickup_sales_dataset.csv')