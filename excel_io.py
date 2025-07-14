import pandas as pd
import os

ARQUIVO_DADOS = "dados.xlsx"

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        # Cria a estrutura inicial
        df_produtos = pd.DataFrame(columns=["preco", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
        df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        
        # Chama a função de salvar dados para garantir que as planilhas sejam criadas
        salvar_dados(df_produtos, df_vendas, df_financeiro)
        return df_produtos, df_vendas, df_financeiro
    
    else:
        # Lê os dados existentes
        df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
        
        # Lê vendas e trata possíveis diferenças de coluna
        df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
        
        # Verifica se existe coluna "lucro" e converte para "valor_venda"
        if "lucro" in df_vendas.columns and "valor_venda" not in df_vendas.columns:
            df_vendas = df_vendas.rename(columns={"lucro": "valor_venda"})
        
        # Garante que todas as colunas necessárias existem
        colunas_necessarias = ["data", "produto", "quantidade", "valor_venda", "venda_id"]
        for col in colunas_necessarias:
            if col not in df_vendas.columns:
                df_vendas[col] = None
        
        # Reordena colunas para consistência
        df_vendas = df_vendas[colunas_necessarias]
        
        # Verifica se existe a planilha "Financeiro" ou "Gastos" (compatibilidade)
        try:
            df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Financeiro")
        except:
            try:
                df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Gastos")
            except:
                # Se não existir nenhuma, cria uma nova
                df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        
        # Garante que todas as colunas necessárias existem no financeiro
        colunas_financeiro = ["data", "tipo", "descricao", "valor"]
        for col in colunas_financeiro:
            if col not in df_financeiro.columns:
                df_financeiro[col] = None
        
        # Reordena colunas para consistência
        df_financeiro = df_financeiro[colunas_financeiro]

        return df_produtos, df_vendas, df_financeiro

def salvar_dados(df_produtos, df_vendas, df_financeiro):
    # Garante que os DataFrames tenham as colunas corretas antes de salvar
    
    # Produtos
    if not df_produtos.empty:
        colunas_produtos = ["preco", "estoque"]
        for col in colunas_produtos:
            if col not in df_produtos.columns:
                df_produtos[col] = 0
        df_produtos = df_produtos[colunas_produtos]
    
    # Vendas
    if not df_vendas.empty:
        colunas_vendas = ["data", "produto", "quantidade", "valor_venda", "venda_id"]
        for col in colunas_vendas:
            if col not in df_vendas.columns:
                df_vendas[col] = None
        df_vendas = df_vendas[colunas_vendas]
    
    # Financeiro
    if not df_financeiro.empty:
        colunas_financeiro = ["data", "tipo", "descricao", "valor"]
        for col in colunas_financeiro:
            if col not in df_financeiro.columns:
                df_financeiro[col] = None
        df_financeiro = df_financeiro[colunas_financeiro]
    
    with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl", mode="w") as writer:
        df_produtos.to_excel(writer, sheet_name="Produtos")
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)
        df_financeiro.to_excel(writer, sheet_name="Financeiro", index=False)