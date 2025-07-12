import pandas as pd
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ARQUIVO_DADOS = os.path.join(DATA_DIR, "dados.xlsx")

def salvar_dados(df_produtos, df_vendas, df_financeiro=None):
    """Salva todos os dados no arquivo Excel"""
    with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl") as writer:
        df_produtos.to_excel(writer, sheet_name="Produtos")
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)
        if df_financeiro is not None:
            df_financeiro.to_excel(writer, sheet_name="Financeiro", index=False)

def carregar_dados():
    """Carrega todos os dados do arquivo Excel"""
    if not os.path.exists(ARQUIVO_DADOS):
        # Arquivo não existe ainda, retorna DataFrames vazios
        df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro"])
        df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        return df_produtos, df_vendas, df_financeiro
    
    try:
        df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
        df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
        
        # Tenta carregar dados financeiros (pode não existir em arquivos antigos)
        try:
            df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Financeiro")
        except:
            df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        
        return df_produtos, df_vendas, df_financeiro
    
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        # Retorna DataFrames vazios em caso de erro
        df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro"])
        df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        return df_produtos, df_vendas, df_financeiro