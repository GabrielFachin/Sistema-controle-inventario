import pandas as pd
from datetime import datetime

class Financeiro:
    def __init__(self):
        self.df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        self._inicializar_dia_atual()
        
    def _inicializar_dia_atual(self):
        """Inicializa o dia atual com saldo 0 se não existir"""
        hoje = datetime.today().strftime("%d/%m/%Y")
        if self.df_financeiro.empty or not (self.df_financeiro["data"] == hoje).any():
            entrada_inicial = {
                "data": hoje,
                "tipo": "entrada",
                "descricao": "Saldo inicial do dia",
                "valor": 0
            }
            self.df_financeiro = pd.concat([self.df_financeiro, pd.DataFrame([entrada_inicial])], ignore_index=True)
    
    def adicionar_entrada(self, descricao, valor, data=None):
        """Adiciona uma entrada de receita"""
        if data is None:
            data = datetime.today().strftime("%d/%m/%Y")
        
        nova_entrada = {
            "data": data,
            "tipo": "entrada",
            "descricao": descricao,
            "valor": valor
        }
        self.df_financeiro = pd.concat([self.df_financeiro, pd.DataFrame([nova_entrada])], ignore_index=True)
    
    def adicionar_saida(self, descricao, valor, data=None):
        """Adiciona uma saída de despesa"""
        if data is None:
            data = datetime.today().strftime("%d/%m/%Y")
        
        # Verifica se é possível adicionar despesa (apenas no dia atual)
        hoje = datetime.today().strftime("%d/%m/%Y")
        if data != hoje:
            raise Exception("Não é possível adicionar despesas em datas passadas.")
        
        nova_saida = {
            "data": data,
            "tipo": "saida",
            "descricao": descricao,
            "valor": -abs(valor)  # Garante que saídas sejam negativas
        }
        self.df_financeiro = pd.concat([self.df_financeiro, pd.DataFrame([nova_saida])], ignore_index=True)
    
    def obter_resumo_diario(self):
        """Retorna um resumo agrupado por dia"""
        if self.df_financeiro.empty:
            return pd.DataFrame(columns=["data", "total"])
        
        # Garantir que o dia atual está inicializado
        self._inicializar_dia_atual()
        
        resumo = self.df_financeiro.groupby("data")["valor"].sum().reset_index()
        resumo.columns = ["data", "total"]
        resumo = resumo.sort_values("data", ascending=False)
        return resumo
    
    def obter_detalhes_dia(self, data):
        """Retorna os detalhes de movimentação de um dia específico"""
        detalhes = self.df_financeiro[self.df_financeiro["data"] == data].copy()
        # Filtra o saldo inicial se for 0 e houver outras movimentações
        if len(detalhes) > 1:
            detalhes = detalhes[~((detalhes["descricao"] == "Saldo inicial do dia") & (detalhes["valor"] == 0))]
        return detalhes.sort_values("tipo", ascending=False)  # Entradas primeiro
    
    def obter_resumo_mensal(self, mes=None, ano=None):
        """Retorna um resumo mensal"""
        if self.df_financeiro.empty:
            return pd.DataFrame(columns=["mes_ano", "total"])
        
        df = self.df_financeiro.copy()
        
        if ano:
            df = df[df["data"].str[6:] == f"{int(ano):04d}"]
        if mes:
            df = df[df["data"].str[3:5] == f"{int(mes):02d}"]
        
        # Cria coluna mes_ano
        df["mes_ano"] = df["data"].str[3:5] + "/" + df["data"].str[6:]
        
        resumo = df.groupby("mes_ano")["valor"].sum().reset_index()
        resumo.columns = ["mes_ano", "total"]
        return resumo.sort_values("mes_ano", ascending=False)
    
    def obter_resumo_anual(self):
        """Retorna um resumo anual"""
        if self.df_financeiro.empty:
            return pd.DataFrame(columns=["ano", "total"])
        
        df = self.df_financeiro.copy()
        df["ano"] = df["data"].str[6:]
        
        resumo = df.groupby("ano")["valor"].sum().reset_index()
        resumo.columns = ["ano", "total"]
        return resumo.sort_values("ano", ascending=False)
    
    def filtrar_por_periodo(self, data_inicio=None, data_fim=None):
        """Filtra movimentações por período"""
        if self.df_financeiro.empty:
            return pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        
        df = self.df_financeiro.copy()
        
        if data_inicio:
            df = df[pd.to_datetime(df["data"], format="%d/%m/%Y") >= pd.to_datetime(data_inicio, format="%d/%m/%Y")]
        if data_fim:
            df = df[pd.to_datetime(df["data"], format="%d/%m/%Y") <= pd.to_datetime(data_fim, format="%d/%m/%Y")]
        
        return df.sort_values("data", ascending=False)
    
    def pode_adicionar_despesa(self, data):
        """Verifica se pode adicionar despesa em uma data"""
        hoje = datetime.today().strftime("%d/%m/%Y")
        return data == hoje