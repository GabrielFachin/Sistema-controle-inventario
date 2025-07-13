import pandas as pd
import os

ARQUIVO_DADOS = "dados.xlsx"

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        # Cria a estrutura inicial
        df_produtos = pd.DataFrame(columns=["preco", "estoque"])  # Removido "custo"
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])  # Alterado "lucro" para "valor_venda"
        df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])  # Renomeado de "gastos" para "financeiro"
        
        # Chama a função de salvar dados para garantir que as planilhas sejam criadas
        salvar_dados(df_produtos, df_vendas, df_financeiro)
        return df_produtos, df_vendas, df_financeiro  # Retorna as tabelas vazias que foram criadas
    
    else:
        # Lê os dados existentes
        df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
        df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
        
        # Verifica se existe a planilha "Financeiro" ou "Gastos" (compatibilidade)
        try:
            df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Financeiro")
        except:
            try:
                df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Gastos")
            except:
                # Se não existir nenhuma, cria uma nova
                df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])

        return df_produtos, df_vendas, df_financeiro

def salvar_dados(df_produtos, df_vendas, df_financeiro):
    with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl", mode="w") as writer:
        df_produtos.to_excel(writer, sheet_name="Produtos")
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)
        df_financeiro.to_excel(writer, sheet_name="Financeiro", index=False)  # Renomeado de "Gastos" para "Financeiro"