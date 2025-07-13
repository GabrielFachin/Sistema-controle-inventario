import pandas as pd
import os

ARQUIVO_DADOS = "dados.xlsx"

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        # Cria a estrutura inicial
        df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro"])
        df_gastos = pd.DataFrame(columns=["data", "categoria", "descricao", "valor"])
        
        # Chama a função de salvar dados para garantir que as planilhas sejam criadas
        salvar_dados(df_produtos, df_vendas, df_gastos)
        return df_produtos, df_vendas, df_gastos  # Retorna as tabelas vazias que foram criadas
    
    else:
        # Lê os dados existentes
        df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
        df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
        df_gastos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Gastos")

        return df_produtos, df_vendas, df_gastos

def salvar_dados(df_produtos, df_vendas, df_gastos):
    with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl", mode="w") as writer:
        df_produtos.to_excel(writer, sheet_name="Produtos")
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)
        df_gastos.to_excel(writer, sheet_name="Gastos", index=False)
