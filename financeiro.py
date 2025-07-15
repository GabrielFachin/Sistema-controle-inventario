import pandas as pd
from datetime import datetime

class Financeiro:
    def __init__(self):
        self.df_entradas = pd.DataFrame(columns=["data", "descricao", "valor"])
        self.df_saidas = pd.DataFrame(columns=["data", "descricao", "valor"])
        self._migrar_dados_antigos()
        self._inicializar_dia_atual()
        
    def _migrar_dados_antigos(self):
        """Migra dados do formato antigo (df_financeiro) para o novo formato separado"""
        # Esta função será chamada quando carregar dados antigos
        pass
    
    def migrar_de_formato_antigo(self, df_financeiro_antigo):
        """Migra dados do DataFrame antigo para o novo formato separado"""
        if df_financeiro_antigo.empty:
            return
        
        # Separa entradas e saídas
        entradas = df_financeiro_antigo[df_financeiro_antigo["tipo"] == "entrada"].copy()
        saidas = df_financeiro_antigo[df_financeiro_antigo["tipo"] == "saida"].copy()
        
        # Remove colunas desnecessárias e ajusta valores
        if not entradas.empty:
            entradas = entradas[["data", "descricao", "valor"]].copy()
            entradas["valor"] = entradas["valor"].abs()  # Garante valores positivos
            self.df_entradas = pd.concat([self.df_entradas, entradas], ignore_index=True)
        
        if not saidas.empty:
            saidas = saidas[["data", "descricao", "valor"]].copy()
            saidas["valor"] = saidas["valor"].abs()  # Converte para positivo (será tratado como saída)
            self.df_saidas = pd.concat([self.df_saidas, saidas], ignore_index=True)
        
        # Remove entradas de saldo inicial zeradas se houver outras movimentações no mesmo dia
        self._limpar_saldos_iniciais_vazios()
        
    def _limpar_saldos_iniciais_vazios(self):
        """Remove entradas de saldo inicial com valor 0 se houver outras movimentações no dia"""
        if self.df_entradas.empty:
            return
        
        # Agrupa por data e verifica se há outras movimentações além do saldo inicial
        for data in self.df_entradas["data"].unique():
            entradas_dia = self.df_entradas[self.df_entradas["data"] == data]
            saidas_dia = self.df_saidas[self.df_saidas["data"] == data]
            
            # Se há mais de uma entrada no dia ou há saídas, remove saldo inicial zerado
            if len(entradas_dia) > 1 or not saidas_dia.empty:
                self.df_entradas = self.df_entradas[~(
                    (self.df_entradas["data"] == data) & 
                    (self.df_entradas["descricao"] == "Saldo inicial do dia") & 
                    (self.df_entradas["valor"] == 0)
                )]
        
        # Reseta o índice
        self.df_entradas = self.df_entradas.reset_index(drop=True)
        
    def _inicializar_dia_atual(self):
        """Inicializa o dia atual com saldo 0 se não existir nenhuma movimentação"""
        hoje = datetime.today().strftime("%d/%m/%Y")
        
        # Verifica se já existe alguma movimentação hoje
        tem_entrada_hoje = not self.df_entradas.empty and (self.df_entradas["data"] == hoje).any()
        tem_saida_hoje = not self.df_saidas.empty and (self.df_saidas["data"] == hoje).any()
        
        # Se não há movimentações hoje, cria entrada inicial
        if not tem_entrada_hoje and not tem_saida_hoje:
            entrada_inicial = {
                "data": hoje,
                "descricao": "Saldo inicial do dia",
                "valor": 0
            }
            self.df_entradas = pd.concat([self.df_entradas, pd.DataFrame([entrada_inicial])], ignore_index=True)
    
    def adicionar_entrada(self, descricao, valor, data=None):
        """Adiciona uma entrada de receita"""
        if data is None:
            data = datetime.today().strftime("%d/%m/%Y")
        
        nova_entrada = {
            "data": data,
            "descricao": descricao,
            "valor": abs(valor)  # Garante que entradas sejam positivas
        }
        self.df_entradas = pd.concat([self.df_entradas, pd.DataFrame([nova_entrada])], ignore_index=True)
        
        # Remove saldo inicial zerado se houver outras movimentações
        self._limpar_saldos_iniciais_vazios()
    
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
            "descricao": descricao,
            "valor": abs(valor)  # Armazena como positivo, será tratado como saída na apresentação
        }
        self.df_saidas = pd.concat([self.df_saidas, pd.DataFrame([nova_saida])], ignore_index=True)
        
        # Remove saldo inicial zerado se houver outras movimentações
        self._limpar_saldos_iniciais_vazios()
    
    def obter_entradas_por_data(self, data):
        """Retorna todas as entradas de uma data específica"""
        if self.df_entradas.empty:
            return pd.DataFrame(columns=["data", "descricao", "valor"])
        
        entradas_dia = self.df_entradas[self.df_entradas["data"] == data].copy()
        return entradas_dia.sort_values("descricao")
    
    def obter_saidas_por_data(self, data):
        """Retorna todas as saídas de uma data específica"""
        if self.df_saidas.empty:
            return pd.DataFrame(columns=["data", "descricao", "valor"])
        
        saidas_dia = self.df_saidas[self.df_saidas["data"] == data].copy()
        return saidas_dia.sort_values("descricao")
    
    def obter_total_dia(self, data):
        """Retorna o total (entradas - saídas) de um dia específico"""
        total_entradas = 0
        total_saidas = 0
        
        if not self.df_entradas.empty:
            entradas_dia = self.df_entradas[self.df_entradas["data"] == data]
            total_entradas = entradas_dia["valor"].sum()
        
        if not self.df_saidas.empty:
            saidas_dia = self.df_saidas[self.df_saidas["data"] == data]
            total_saidas = saidas_dia["valor"].sum()
        
        return total_entradas - total_saidas
    
    def obter_resumo_diario(self):
        """Retorna um resumo agrupado por dia"""
        # Garantir que o dia atual está inicializado
        self._inicializar_dia_atual()
        
        # Obter todas as datas únicas
        datas_entradas = set(self.df_entradas["data"].tolist() if not self.df_entradas.empty else [])
        datas_saidas = set(self.df_saidas["data"].tolist() if not self.df_saidas.empty else [])
        todas_datas = sorted(datas_entradas.union(datas_saidas), reverse=True)
        
        resumo_data = []
        for data in todas_datas:
            total = self.obter_total_dia(data)
            resumo_data.append({"data": data, "total": total})
        
        return pd.DataFrame(resumo_data)
    
    def obter_resumo_mensal(self, mes=None, ano=None):
        """Retorna um resumo mensal"""
        resumo_diario = self.obter_resumo_diario()
        if resumo_diario.empty:
            return pd.DataFrame(columns=["mes_ano", "total"])
        
        df = resumo_diario.copy()
        
        if ano:
            df = df[df["data"].str[6:] == f"{int(ano):04d}"]
        if mes:
            df = df[df["data"].str[3:5] == f"{int(mes):02d}"]
        
        # Cria coluna mes_ano
        df["mes_ano"] = df["data"].str[3:5] + "/" + df["data"].str[6:]
        
        resumo = df.groupby("mes_ano")["total"].sum().reset_index()
        resumo.columns = ["mes_ano", "total"]
        return resumo.sort_values("mes_ano", ascending=False)
    
    def obter_resumo_anual(self):
        """Retorna um resumo anual"""
        resumo_diario = self.obter_resumo_diario()
        if resumo_diario.empty:
            return pd.DataFrame(columns=["ano", "total"])
        
        df = resumo_diario.copy()
        df["ano"] = df["data"].str[6:]
        
        resumo = df.groupby("ano")["total"].sum().reset_index()
        resumo.columns = ["ano", "total"]
        return resumo.sort_values("ano", ascending=False)
    
    def filtrar_por_periodo(self, data_inicio=None, data_fim=None):
        """Filtra movimentações por período"""
        resultado = []
        
        # Filtra entradas
        entradas_filtradas = self.df_entradas.copy() if not self.df_entradas.empty else pd.DataFrame(columns=["data", "descricao", "valor"])
        if data_inicio and not entradas_filtradas.empty:
            entradas_filtradas = entradas_filtradas[pd.to_datetime(entradas_filtradas["data"], format="%d/%m/%Y") >= pd.to_datetime(data_inicio, format="%d/%m/%Y")]
        if data_fim and not entradas_filtradas.empty:
            entradas_filtradas = entradas_filtradas[pd.to_datetime(entradas_filtradas["data"], format="%d/%m/%Y") <= pd.to_datetime(data_fim, format="%d/%m/%Y")]
        
        # Filtra saídas
        saidas_filtradas = self.df_saidas.copy() if not self.df_saidas.empty else pd.DataFrame(columns=["data", "descricao", "valor"])
        if data_inicio and not saidas_filtradas.empty:
            saidas_filtradas = saidas_filtradas[pd.to_datetime(saidas_filtradas["data"], format="%d/%m/%Y") >= pd.to_datetime(data_inicio, format="%d/%m/%Y")]
        if data_fim and not saidas_filtradas.empty:
            saidas_filtradas = saidas_filtradas[pd.to_datetime(saidas_filtradas["data"], format="%d/%m/%Y") <= pd.to_datetime(data_fim, format="%d/%m/%Y")]
        
        # Combina resultados
        if not entradas_filtradas.empty:
            entradas_filtradas["tipo"] = "entrada"
            resultado.append(entradas_filtradas)
        
        if not saidas_filtradas.empty:
            saidas_filtradas["tipo"] = "saida"
            resultado.append(saidas_filtradas)
        
        if resultado:
            df_resultado = pd.concat(resultado, ignore_index=True)
            return df_resultado.sort_values("data", ascending=False)
        else:
            return pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
    
    def pode_adicionar_despesa(self, data):
        """Verifica se pode adicionar despesa em uma data"""
        hoje = datetime.today().strftime("%d/%m/%Y")
        return data == hoje
    
    def obter_dados_para_salvar(self):
        """Retorna os dados no formato antigo para compatibilidade com o salvamento"""
        resultado = []
        
        # Adiciona entradas
        if not self.df_entradas.empty:
            entradas = self.df_entradas.copy()
            entradas["tipo"] = "entrada"
            entradas = entradas[["data", "tipo", "descricao", "valor"]]
            resultado.append(entradas)
        
        # Adiciona saídas (converte valores para negativos)
        if not self.df_saidas.empty:
            saidas = self.df_saidas.copy()
            saidas["tipo"] = "saida"
            saidas["valor"] = -saidas["valor"]  # Converte para negativo para compatibilidade
            saidas = saidas[["data", "tipo", "descricao", "valor"]]
            resultado.append(saidas)
        
        if resultado:
            df_final = pd.concat(resultado, ignore_index=True)
            return df_final.sort_values("data", ascending=False)
        else:
            return pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])