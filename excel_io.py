import pandas as pd
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ARQUIVO_DADOS = os.path.join(DATA_DIR, "dados.xlsx")

def salvar_dados(df_produtos, df_vendas):
    with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl") as writer:
        df_produtos.to_excel(writer, sheet_name="Produtos")
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        # Arquivo não existe ainda, retorna DataFrames vazios
        df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro"])
        return df_produtos, df_vendas

    df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
    df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
    return df_produtos, df_vendas
