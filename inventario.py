import pandas as pd
from datetime import datetime
import uuid

class Inventario:
    def __init__(self):
        self.df_produtos = pd.DataFrame(columns=["preco", "estoque"])  # Removido "custo"
        self.df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])  # Alterado "lucro" para "valor_venda"
        self.carrinho = []  # Para vendas em pacote
    
    def adicionar_produto(self, nome, preco, estoque):
        """Adiciona novo produto (sem custo)"""
        if nome in self.df_produtos.index:
            raise Exception("Produto já cadastrado.")
        self.df_produtos.loc[nome] = [preco, estoque]
    
    def editar_produto(self, nome, novo_preco=None):
        """Edita produto (apenas preço)"""
        if nome not in self.df_produtos.index:
            raise Exception("Produto não encontrado.")
        if novo_preco is not None:
            self.df_produtos.at[nome, "preco"] = novo_preco
    
    def alterar_estoque(self, nome, ajuste):
        """Altera estoque do produto"""
        if nome not in self.df_produtos.index:
            raise Exception("Produto não encontrado.")
        self.df_produtos.at[nome, "estoque"] += ajuste
        if self.df_produtos.at[nome, "estoque"] < 0:
            raise Exception("Estoque não pode ser negativo.")
    
    def remover_produto(self, nome):
        """Remove produto do inventário"""
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
        preco_com_desconto = preco * (1 - desconto)
        valor_total = preco_com_desconto * quantidade
        
        item = {
            'produto': nome_produto,
            'quantidade': quantidade,
            'desconto': desconto,
            'preco_unitario': preco,
            'preco_com_desconto': preco_com_desconto,
            'valor_total': valor_total
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
        return sum(item['valor_total'] for item in self.carrinho)
    
    def finalizar_venda_carrinho(self):
        """Finaliza a venda do carrinho"""
        if not self.carrinho:
            raise Exception("Carrinho vazio.")
        
        # Gera ID único para a venda
        venda_id = str(uuid.uuid4())[:8]
        data_venda = datetime.today().strftime("%d/%m/%Y")
        
        # Valor total da venda
        valor_total_venda = 0
        
        # Registra cada item da venda
        for item in self.carrinho:
            nova_venda = {
                "data": data_venda,
                "produto": item['produto'],
                "quantidade": item['quantidade'],
                "valor_venda": item['valor_total'],
                "venda_id": venda_id
            }
            self.df_vendas = pd.concat([self.df_vendas, pd.DataFrame([nova_venda])], ignore_index=True)
            
            # Atualiza estoque
            self.df_produtos.at[item['produto'], "estoque"] -= item['quantidade']
            
            valor_total_venda += item['valor_total']
        
        # Limpa carrinho
        self.limpar_carrinho()
        
        return venda_id, valor_total_venda
    
    def registrar_venda(self, nome_produto, quantidade, desconto=0):
        """Registra uma venda simples"""
        if nome_produto not in self.df_produtos.index:
            raise Exception("Produto não cadastrado.")
        
        estoque_atual = self.df_produtos.at[nome_produto, "estoque"]
        if estoque_atual < quantidade:
            raise Exception("Estoque insuficiente.")
        
        preco = self.df_produtos.at[nome_produto, "preco"]
        preco_com_desconto = preco * (1 - desconto)
        valor_venda = preco_com_desconto * quantidade
        
        # Gera ID único para a venda
        venda_id = str(uuid.uuid4())[:8]
        
        nova_venda = {
            "data": datetime.today().strftime("%d/%m/%Y"),
            "produto": nome_produto,
            "quantidade": quantidade,
            "valor_venda": valor_venda,
            "venda_id": venda_id
        }
        self.df_vendas = pd.concat([self.df_vendas, pd.DataFrame([nova_venda])], ignore_index=True)
        
        self.df_produtos.at[nome_produto, "estoque"] -= quantidade
        return venda_id, valor_venda
    
    def obter_vendas_agrupadas(self):
        """Retorna vendas agrupadas por venda_id"""
        # Retorna DataFrame vazio com estrutura correta se não há vendas
        if self.df_vendas.empty:
            return pd.DataFrame(columns=["data", "venda_id", "produto", "quantidade", "valor_venda"])
        
        # Cria uma cópia do DataFrame para evitar alterações no original
        df_temp = self.df_vendas.copy()
        
        # Agrupa por data e venda_id
        vendas_agrupadas = df_temp.groupby(['data', 'venda_id']).agg({
            'produto': lambda x: ', '.join(x) if len(x) > 1 else x.iloc[0],
            'quantidade': 'sum',
            'valor_venda': 'sum'
        }).reset_index()
        
        # Ordena por data (converte para datetime para ordenação correta)
        try:
            vendas_agrupadas['data_sort'] = pd.to_datetime(vendas_agrupadas['data'], format='%d/%m/%Y')
            vendas_agrupadas = vendas_agrupadas.sort_values('data_sort', ascending=False)
            vendas_agrupadas = vendas_agrupadas.drop('data_sort', axis=1)
        except:
            # Se falhar na conversão, ordena como string
            vendas_agrupadas = vendas_agrupadas.sort_values('data', ascending=False)
        
        return vendas_agrupadas
    
    def obter_detalhes_venda(self, venda_id):
        """Retorna os detalhes de uma venda específica"""
        if self.df_vendas.empty:
            return pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
        return self.df_vendas[self.df_vendas['venda_id'] == venda_id]
    
    def filtrar_vendas_por_data(self, dia=None, mes=None, ano=None, produto=None):
        """Filtra vendas por data e produto"""
        if self.df_vendas.empty:
            return pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
            
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