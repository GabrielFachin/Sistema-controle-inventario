import pandas as pd
from datetime import datetime

class Inventario:
    def __init__(self):
        self.df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        self.df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro"])

    def adicionar_produto(self, nome, preco, custo, estoque):
        if nome in self.df_produtos.index:
            raise Exception("Produto já cadastrado.")
        self.df_produtos.loc[nome] = [preco, custo, estoque]

    def editar_produto(self, nome, novo_preco=None, novo_custo=None):
        if nome not in self.df_produtos.index:
            raise Exception("Produto não encontrado.")
        if novo_preco is not None:
            self.df_produtos.at[nome, "preco"] = novo_preco
        if novo_custo is not None:
            self.df_produtos.at[nome, "custo"] = novo_custo

    def alterar_estoque(self, nome, ajuste):
        if nome not in self.df_produtos.index:
            raise Exception("Produto não encontrado.")
        self.df_produtos.at[nome, "estoque"] += ajuste
        if self.df_produtos.at[nome, "estoque"] < 0:
            raise Exception("Estoque não pode ser negativo.")

    def remover_produto(self, nome):
        if nome not in self.df_produtos.index:
            raise Exception("Produto não encontrado.")
        self.df_produtos.drop(nome, inplace=True)

    def registrar_venda(self, nome_produto, quantidade, desconto=0):
        if nome_produto not in self.df_produtos.index:
            raise Exception("Produto não cadastrado.")

        estoque_atual = self.df_produtos.at[nome_produto, "estoque"]
        if estoque_atual < quantidade:
            raise Exception("Estoque insuficiente.")

        preco = self.df_produtos.at[nome_produto, "preco"]
        custo = self.df_produtos.at[nome_produto, "custo"]
        preco_com_desconto = preco * (1 - desconto)
        lucro = (preco_com_desconto - custo) * quantidade

        self.df_vendas.loc[len(self.df_vendas)] = [
            datetime.today().strftime("%d/%m/%Y"),
            nome_produto,
            quantidade,
            lucro
        ]

        self.df_produtos.at[nome_produto, "estoque"] -= quantidade

    def filtrar_vendas_por_data(self, dia=None, mes=None, ano=None, produto=None):
        df = self.df_vendas.copy()
        if ano:
            df = df[df["data"].str[6:] == f"{int(ano):04d}"]
        if mes:
            df = df[df["data"].str[3:5] == f"{int(mes):02d}"]
        if dia:
            df = df[df["data"].str[:2] == f"{int(dia):02d}"]
        if produto:
            df = df[df["produto"] == produto]
        return df
