import pandas as pd
from datetime import datetime
import uuid

class Inventario:
    def __init__(self):
        self.df_produtos = pd.DataFrame(columns=["preco", "custo", "estoque"])
        self.df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "lucro", "venda_id"])
        self.carrinho = []  # Para vendas em pacote
    
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
    
    def adicionar_ao_carrinho(self, nome_produto, quantidade, desconto=0):
        """Adiciona produto ao carrinho para venda em pacote"""
        if nome_produto not in self.df_produtos.index:
            raise Exception("Produto não cadastrado.")
        
        estoque_atual = self.df_produtos.at[nome_produto, "estoque"]
        
        # Verifica quantidade já no carrinho
        quantidade_carrinho = sum(item['quantidade'] for item in self.carrinho if item['produto'] == nome_produto)
        
        if estoque_atual < quantidade + quantidade_carrinho:
            raise Exception("Estoque insuficiente.")
        
        preco = self.df_produtos.at[nome_produto, "preco"]
        custo = self.df_produtos.at[nome_produto, "custo"]
        preco_com_desconto = preco * (1 - desconto)
        lucro = (preco_com_desconto - custo) * quantidade
        
        item = {
            'produto': nome_produto,
            'quantidade': quantidade,
            'desconto': desconto,
            'preco_unitario': preco,
            'preco_com_desconto': preco_com_desconto,
            'lucro': lucro,
            'total_item': preco_com_desconto * quantidade
        }
        
        self.carrinho.append(item)
        return item
    
    def remover_do_carrinho(self, index):
        """Remove item do carrinho pelo índice"""
        if 0 <= index < len(self.carrinho):
            return self.carrinho.pop(index)
        else:
            raise Exception("Índice inválido.")
    
    def limpar_carrinho(self):
        """Limpa todos os itens do carrinho"""
        self.carrinho.clear()
    
    def obter_total_carrinho(self):
        """Retorna o total do carrinho"""
        return sum(item['total_item'] for item in self.carrinho)
    
    def obter_lucro_carrinho(self):
        """Retorna o lucro total do carrinho"""
        return sum(item['lucro'] for item in self.carrinho)
    
    def finalizar_venda_carrinho(self):
        """Finaliza a venda do carrinho"""
        if not self.carrinho:
            raise Exception("Carrinho vazio.")
        
        # Gera ID único para a venda
        venda_id = str(uuid.uuid4())[:8]
        data_venda = datetime.today().strftime("%d/%m/%Y")
        
        # Registra cada item da venda
        for item in self.carrinho:
            self.df_vendas.loc[len(self.df_vendas)] = [
                data_venda,
                item['produto'],
                item['quantidade'],
                item['lucro'],
                venda_id
            ]
            
            # Atualiza estoque
            self.df_produtos.at[item['produto'], "estoque"] -= item['quantidade']
        
        # Calcula lucro total da venda
        lucro_total = self.obter_lucro_carrinho()
        
        # Limpa carrinho
        self.limpar_carrinho()
        
        return venda_id, lucro_total
    
    def registrar_venda(self, nome_produto, quantidade, desconto=0):
        """Registra uma venda simples (mantém compatibilidade)"""
        if nome_produto not in self.df_produtos.index:
            raise Exception("Produto não cadastrado.")
        
        estoque_atual = self.df_produtos.at[nome_produto, "estoque"]
        if estoque_atual < quantidade:
            raise Exception("Estoque insuficiente.")
        
        preco = self.df_produtos.at[nome_produto, "preco"]
        custo = self.df_produtos.at[nome_produto, "custo"]
        preco_com_desconto = preco * (1 - desconto)
        lucro = (preco_com_desconto - custo) * quantidade
        
        # Gera ID único para a venda
        venda_id = str(uuid.uuid4())[:8]
        
        self.df_vendas.loc[len(self.df_vendas)] = [
            datetime.today().strftime("%d/%m/%Y"),
            nome_produto,
            quantidade,
            lucro,
            venda_id
        ]
        
        self.df_produtos.at[nome_produto, "estoque"] -= quantidade
        return venda_id, lucro
    
    def obter_vendas_agrupadas(self):
        """Retorna vendas agrupadas por venda_id"""
        if self.df_vendas.empty:
            return pd.DataFrame(columns=["data", "venda_id", "produto", "quantidade", "lucro"])
        
        vendas_agrupadas = self.df_vendas.groupby(['data', 'venda_id']).agg({
            'produto': lambda x: ', '.join(x) if len(x) > 1 else x.iloc[0],
            'quantidade': 'sum',
            'lucro': 'sum'
        }).reset_index()
        
        # Verifica se o DataFrame não está vazio antes de ordenar
        if not vendas_agrupadas.empty:
            return vendas_agrupadas.sort_values('data', ascending=False)
        else:
            return pd.DataFrame(columns=["data", "venda_id", "produto", "quantidade", "lucro"])
    
    def obter_detalhes_venda(self, venda_id):
        """Retorna os detalhes de uma venda específica"""
        return self.df_vendas[self.df_vendas['venda_id'] == venda_id]
    
    def filtrar_vendas_por_data(self, dia=None, mes=None, ano=None, produto=None):
        """Filtra vendas por data e produto"""
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