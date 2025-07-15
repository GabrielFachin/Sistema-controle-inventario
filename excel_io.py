import pandas as pd
import os
import shutil
from datetime import datetime

ARQUIVO_DADOS = "dados.xlsx"
ARQUIVO_BACKUP = f"dados_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

def criar_backup():
    """Cria backup do arquivo antes de modificar"""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            shutil.copy2(ARQUIVO_DADOS, ARQUIVO_BACKUP)
            print(f"Backup criado: {ARQUIVO_BACKUP}")
        except Exception as e:
            print(f"Erro ao criar backup: {e}")

def carregar_dados():
    """Carrega dados do Excel ou cria estrutura inicial se não existir"""
    
    # Se o arquivo não existir, cria a estrutura inicial
    if not os.path.exists(ARQUIVO_DADOS):
        print("Arquivo não encontrado. Criando estrutura inicial...")
        df_produtos = pd.DataFrame(columns=["preco", "estoque"])
        df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
        df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        
        # Salva a estrutura inicial
        salvar_dados(df_produtos, df_vendas, df_financeiro)
        return df_produtos, df_vendas, df_financeiro
    
    try:
        # Carrega produtos
        try:
            df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
            print(f"Produtos carregados: {len(df_produtos)} itens")
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            df_produtos = pd.DataFrame(columns=["preco", "estoque"])
        
        # Carrega vendas
        try:
            df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
            print(f"Vendas carregadas: {len(df_vendas)} registros")
            
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
            
        except Exception as e:
            print(f"Erro ao carregar vendas: {e}")
            df_vendas = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
        
        # Carrega financeiro (mantém compatibilidade com formato antigo)
        try:
            # Verifica se existe a planilha "Financeiro" ou "Gastos" (compatibilidade)
            try:
                df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Financeiro")
            except:
                try:
                    df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Gastos")
                except:
                    df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
            
            print(f"Financeiro carregado: {len(df_financeiro)} registros")
            
            # Garante que todas as colunas necessárias existem no financeiro
            colunas_financeiro = ["data", "tipo", "descricao", "valor"]
            for col in colunas_financeiro:
                if col not in df_financeiro.columns:
                    df_financeiro[col] = None
            
            # Reordena colunas para consistência
            df_financeiro = df_financeiro[colunas_financeiro]
            
        except Exception as e:
            print(f"Erro ao carregar financeiro: {e}")
            df_financeiro = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])

        return df_produtos, df_vendas, df_financeiro
        
    except Exception as e:
        print(f"Erro geral ao carregar dados: {e}")
        # Em caso de erro, retorna DataFrames vazios
        return (
            pd.DataFrame(columns=["preco", "estoque"]),
            pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"]),
            pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        )

def salvar_dados(df_produtos, df_vendas, df_financeiro):
    """Salva dados no Excel com verificações de segurança"""
    
    try:
        # Cria backup antes de salvar
        criar_backup()
        
        # Prepara DataFrames para salvar
        # Produtos - sempre mantém estrutura mesmo se vazio
        if df_produtos.empty:
            df_produtos_salvar = pd.DataFrame(columns=["preco", "estoque"])
        else:
            df_produtos_salvar = df_produtos.copy()
            colunas_produtos = ["preco", "estoque"]
            for col in colunas_produtos:
                if col not in df_produtos_salvar.columns:
                    df_produtos_salvar[col] = 0
            df_produtos_salvar = df_produtos_salvar[colunas_produtos]
        
        # Vendas - sempre mantém estrutura mesmo se vazio
        if df_vendas.empty:
            df_vendas_salvar = pd.DataFrame(columns=["data", "produto", "quantidade", "valor_venda", "venda_id"])
        else:
            df_vendas_salvar = df_vendas.copy()
            colunas_vendas = ["data", "produto", "quantidade", "valor_venda", "venda_id"]
            for col in colunas_vendas:
                if col not in df_vendas_salvar.columns:
                    df_vendas_salvar[col] = None
            df_vendas_salvar = df_vendas_salvar[colunas_vendas]
        
        # Financeiro - sempre mantém estrutura mesmo se vazio
        if df_financeiro.empty:
            df_financeiro_salvar = pd.DataFrame(columns=["data", "tipo", "descricao", "valor"])
        else:
            df_financeiro_salvar = df_financeiro.copy()
            colunas_financeiro = ["data", "tipo", "descricao", "valor"]
            for col in colunas_financeiro:
                if col not in df_financeiro_salvar.columns:
                    df_financeiro_salvar[col] = None
            df_financeiro_salvar = df_financeiro_salvar[colunas_financeiro]
        
        # Salva no Excel
        with pd.ExcelWriter(ARQUIVO_DADOS, engine="openpyxl", mode="w") as writer:
            df_produtos_salvar.to_excel(writer, sheet_name="Produtos", index=True)
            df_vendas_salvar.to_excel(writer, sheet_name="Vendas", index=False)
            df_financeiro_salvar.to_excel(writer, sheet_name="Financeiro", index=False)
        
        print(f"Dados salvos com sucesso!")
        print(f"- Produtos: {len(df_produtos_salvar)} itens")
        print(f"- Vendas: {len(df_vendas_salvar)} registros")
        print(f"- Financeiro: {len(df_financeiro_salvar)} registros")
        
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        raise e

def salvar_dados_financeiro_separado(df_produtos, df_vendas, financeiro_obj):
    """Salva dados usando o novo formato de financeiro separado"""
    # Converte o objeto financeiro para o formato antigo para compatibilidade
    df_financeiro_compativel = financeiro_obj.obter_dados_para_salvar()
    salvar_dados(df_produtos, df_vendas, df_financeiro_compativel)

def verificar_integridade():
    """Verifica a integridade do arquivo de dados"""
    if not os.path.exists(ARQUIVO_DADOS):
        print("Arquivo de dados não encontrado!")
        return False
    
    try:
        # Tenta carregar todas as planilhas
        df_produtos = pd.read_excel(ARQUIVO_DADOS, sheet_name="Produtos", index_col=0)
        df_vendas = pd.read_excel(ARQUIVO_DADOS, sheet_name="Vendas")
        df_financeiro = pd.read_excel(ARQUIVO_DADOS, sheet_name="Financeiro")
        
        print("Verificação de integridade:")
        print(f"✓ Produtos: {len(df_produtos)} itens")
        print(f"✓ Vendas: {len(df_vendas)} registros")
        print(f"✓ Financeiro: {len(df_financeiro)} registros")
        
        return True
        
    except Exception as e:
        print(f"Erro na verificação de integridade: {e}")
        return False

def recuperar_backup(arquivo_backup):
    """Recupera dados de um arquivo de backup"""
    if not os.path.exists(arquivo_backup):
        print(f"Arquivo de backup não encontrado: {arquivo_backup}")
        return False
    
    try:
        # Cria backup do arquivo atual antes de recuperar
        if os.path.exists(ARQUIVO_DADOS):
            shutil.copy2(ARQUIVO_DADOS, f"dados_antes_recuperacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        # Restaura o backup
        shutil.copy2(arquivo_backup, ARQUIVO_DADOS)
        print(f"Backup recuperado com sucesso de: {arquivo_backup}")
        
        # Verifica integridade
        return verificar_integridade()
        
    except Exception as e:
        print(f"Erro ao recuperar backup: {e}")
        return False