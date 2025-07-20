import tkinter as tk
from tkinter import ttk, messagebox
from inventario import Inventario
from financeiro import Financeiro
from datetime import datetime
import pandas as pd
import excel_io

inventario = Inventario()
financeiro = Financeiro()
filtro_atual = {"dia": None, "mes": None, "ano": None, "produto": None}

def iniciar_interface():
    root = tk.Tk()
    root.title("Controle de Estoque e Vendas")
    root.geometry("1200x800")

    # Carrega dados do Excel
    df_produtos, df_vendas, df_financeiro = excel_io.carregar_dados()
    inventario.df_produtos = df_produtos
    inventario.df_vendas = df_vendas
    financeiro.df_financeiro = df_financeiro

    aba = ttk.Notebook(root)
    aba.pack(fill="both", expand=True)

    aba_vendas = ttk.Frame(aba)
    aba_historico = ttk.Frame(aba)
    aba_estoque_total = ttk.Frame(aba)
    aba_financeiro = ttk.Frame(aba)
    
    aba.add(aba_vendas, text="Vendas")
    aba.add(aba_historico, text="Histórico")
    aba.add(aba_estoque_total, text="Estoque")
    aba.add(aba_financeiro, text="Financeiro")

    # --- ABA VENDAS ---
    # Frame para tipo de venda
    frame_tipo_venda = ttk.LabelFrame(aba_vendas, text="Tipo de Venda")
    frame_tipo_venda.pack(padx=10, pady=5, fill="x")

    var_tipo_venda = tk.StringVar(value="simples")
    tk.Radiobutton(frame_tipo_venda, text="Venda Simples", variable=var_tipo_venda, value="simples").pack(side="left", padx=10)
    tk.Radiobutton(frame_tipo_venda, text="Venda em Pacote", variable=var_tipo_venda, value="pacote").pack(side="left", padx=10)

    # Frame para adicionar produtos
    frame_venda = ttk.LabelFrame(aba_vendas, text="Adicionar Produto")
    frame_venda.pack(padx=10, pady=5, fill="x")

    tk.Label(frame_venda, text="Produto:").grid(row=0, column=0)
    tk.Label(frame_venda, text="Quantidade:").grid(row=0, column=2)
    tk.Label(frame_venda, text="Desconto (%):").grid(row=0, column=4)

    combo_produtos = ttk.Combobox(frame_venda, width=20)
    entry_quantidade = tk.Entry(frame_venda, width=10)
    entry_desconto = tk.Entry(frame_venda, width=10)

    combo_produtos.grid(row=0, column=1, padx=5)
    entry_quantidade.grid(row=0, column=3, padx=5)
    entry_desconto.grid(row=0, column=5, padx=5)

    def adicionar_produto():
        try:
            produto = combo_produtos.get()
            qtd = int(entry_quantidade.get())
            desconto = float(entry_desconto.get() or 0) / 100
            
            if var_tipo_venda.get() == "simples":
                venda_id, lucro = inventario.registrar_venda(produto, qtd, desconto)
                messagebox.showinfo("Sucesso", f"Venda registrada! Lucro: R${lucro:.2f}")
                atualizar_tree_vendas_dia()
                atualizar_tabela_produtos()
                # Atualiza financeiro
                financeiro.adicionar_entrada(f"Venda - {produto}", lucro)
                atualizar_tree_financeiro()
            else:
                item = inventario.adicionar_ao_carrinho(produto, qtd, desconto)
                atualizar_tree_carrinho()
                messagebox.showinfo("Sucesso", f"Produto adicionado ao carrinho!")
            
            entry_quantidade.delete(0, tk.END)
            entry_desconto.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    btn_adicionar = tk.Button(frame_venda, text="Adicionar", command=adicionar_produto)
    btn_adicionar.grid(row=0, column=6, padx=10)

    # Frame do carrinho (apenas para vendas em pacote)
    frame_carrinho = ttk.LabelFrame(aba_vendas, text="Carrinho")
    frame_carrinho.pack(padx=10, pady=5, fill="both", expand=True)

    tree_carrinho = ttk.Treeview(frame_carrinho, columns=("produto", "quantidade", "desconto", "preco", "total"), show="headings", height=6)
    tree_carrinho.heading("produto", text="Produto")
    tree_carrinho.heading("quantidade", text="Qtd")
    tree_carrinho.heading("desconto", text="Desc %")
    tree_carrinho.heading("preco", text="Preço Unit")
    tree_carrinho.heading("total", text="Total")
    tree_carrinho.pack(fill="both", expand=True)

    frame_carrinho_botoes = tk.Frame(frame_carrinho)
    frame_carrinho_botoes.pack(fill="x", pady=5)

    def remover_do_carrinho():
        selecionado = tree_carrinho.selection()
        if selecionado:
            index = tree_carrinho.index(selecionado[0])
            inventario.remover_do_carrinho(index)
            atualizar_tree_carrinho()

    def finalizar_venda():
        if not inventario.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio!")
            return
        
        try:
            venda_id, lucro_total = inventario.finalizar_venda_carrinho()
            messagebox.showinfo("Sucesso", f"Venda finalizada! Lucro total: R${lucro_total:.2f}")
            atualizar_tree_carrinho()
            atualizar_tree_vendas_dia()
            atualizar_tabela_produtos()
            # Atualiza financeiro
            financeiro.adicionar_entrada(f"Venda em pacote - ID: {venda_id}", lucro_total)
            atualizar_tree_financeiro()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(frame_carrinho_botoes, text="Remover Selecionado", command=remover_do_carrinho).pack(side="left", padx=5)
    tk.Button(frame_carrinho_botoes, text="Limpar Carrinho", command=lambda: [inventario.limpar_carrinho(), atualizar_tree_carrinho()]).pack(side="left", padx=5)
    tk.Button(frame_carrinho_botoes, text="Finalizar Venda", command=finalizar_venda).pack(side="right", padx=5)

    lbl_total_carrinho = tk.Label(frame_carrinho_botoes, text="Total: R$0,00", font=("Arial", 12, "bold"))
    lbl_total_carrinho.pack(side="right", padx=10)

    def atualizar_tree_carrinho():
        tree_carrinho.delete(*tree_carrinho.get_children())
        total = 0
        for item in inventario.carrinho:
            tree_carrinho.insert("", tk.END, values=(
                item['produto'],
                item['quantidade'],
                f"{item['desconto']*100:.1f}%",
                f"R${item['preco_com_desconto']:.2f}",
                f"R${item['total_item']:.2f}"
            ))
            total += item['total_item']
        lbl_total_carrinho.config(text=f"Total: R${total:.2f}")

    # Frame vendas do dia
    frame_vendas_dia = ttk.LabelFrame(aba_vendas, text="Vendas do Dia")
    frame_vendas_dia.pack(padx=10, pady=5, fill="both", expand=True)

    tree_vendas_dia = ttk.Treeview(frame_vendas_dia, columns=("data", "produto", "quantidade", "lucro", "venda_id"), show="headings")
    tree_vendas_dia.heading("data", text="Data")
    tree_vendas_dia.heading("produto", text="Produto(s)")
    tree_vendas_dia.heading("quantidade", text="Qtd Total")
    tree_vendas_dia.heading("lucro", text="Lucro")
    tree_vendas_dia.heading("venda_id", text="ID Venda")
    tree_vendas_dia.pack(fill="both", expand=True)

    def atualizar_tree_vendas_dia():
        hoje_str = datetime.today().strftime("%d/%m/%Y")
        vendas_agrupadas = inventario.obter_vendas_agrupadas()
        vendas_hoje = vendas_agrupadas[vendas_agrupadas["data"] == hoje_str] if not vendas_agrupadas.empty else pd.DataFrame()
        
        tree_vendas_dia.delete(*tree_vendas_dia.get_children())
        
        if not vendas_hoje.empty:
            for _, row in vendas_hoje.iterrows():
                tree_vendas_dia.insert("", tk.END, values=(
                    row["data"], 
                    row["produto"], 
                    row["quantidade"], 
                    f"R${row['lucro']:.2f}",
                    row["venda_id"]
                ))

    # --- ABA FINANCEIRO ---
    frame_resumo = ttk.LabelFrame(aba_financeiro, text="Resumo Diário")
    frame_resumo.pack(padx=10, pady=5, fill="both", expand=True)

    # Tree com scrollbar
    tree_scroll = ttk.Scrollbar(frame_resumo)
    tree_scroll.pack(side="right", fill="y")

    tree_financeiro = ttk.Treeview(
        frame_resumo,
        columns=("data", "entrada", "saida", "total"),
        show="tree headings",
        yscrollcommand=tree_scroll.set
    )
    tree_scroll.config(command=tree_financeiro.yview)
    
    # Configure columns
    tree_financeiro.heading("#0", text="")
    tree_financeiro.heading("data", text="Data")
    tree_financeiro.heading("entrada", text="Total Entradas")
    tree_financeiro.heading("saida", text="Total Saídas")
    tree_financeiro.heading("total", text="Total Geral")
    
    # Configure column widths
    tree_financeiro.column("#0", width=30)
    tree_financeiro.column("data", width=100)
    tree_financeiro.column("entrada", width=150)
    tree_financeiro.column("saida", width=150)
    tree_financeiro.column("total", width=150)
    
    tree_financeiro.pack(fill="both", expand=True)

    def atualizar_tree_financeiro():
        tree_financeiro.delete(*tree_financeiro.get_children())
        resumo = financeiro.obter_resumo_diario_completo()

        hoje_str = datetime.today().strftime("%d/%m/%Y")
        if resumo.empty or hoje_str not in resumo["data"].values:
            resumo = pd.concat([resumo, pd.DataFrame([{
                "data": hoje_str, "entrada": 0.0, "saida": 0.0, "total": 0.0
            }])], ignore_index=True)

        for _, row in resumo.iterrows():
            # Inserir linha principal com totais
            parent = tree_financeiro.insert(
                "", "end",
                values=(
                    row["data"],
                    f"R${row['entrada']:.2f}",
                    f"R${abs(row['saida']):.2f}",
                    f"R${row['total']:.2f}"
                ),
                tags=('day',)
            )

            # Buscar detalhes do dia
            detalhes = financeiro.obter_detalhes_dia(row["data"])
            
            # Inserir entradas
            entradas = detalhes[detalhes["tipo"] == "entrada"]
            if not entradas.empty:
                entrada_header = tree_financeiro.insert(parent, "end", values=("", "ENTRADAS", "", ""), tags=('header',))
                for _, ent in entradas.iterrows():
                    if ent['descricao'] != "Saldo inicial do dia" or ent['valor'] != 0:
                        tree_financeiro.insert(
                            entrada_header, "end",
                            values=("", ent['descricao'], "", f"R${ent['valor']:.2f}"),
                            tags=('entrada',)
                        )

            # Inserir saídas
            saidas = detalhes[detalhes["tipo"] == "saida"]
            if not saidas.empty:
                saida_header = tree_financeiro.insert(parent, "end", values=("", "SAÍDAS", "", ""), tags=('header',))
                for _, sai in saidas.iterrows():
                    tree_financeiro.insert(
                        saida_header, "end",
                        values=("", sai['descricao'], "", f"R${abs(sai['valor']):.2f}"),
                        tags=('saida',)
                    )

        # Configurar estilos
        tree_financeiro.tag_configure('day', font=('Arial', 10, 'bold'))
        tree_financeiro.tag_configure('header', font=('Arial', 9, 'bold'), background='#f0f0f0')
        tree_financeiro.tag_configure('entrada', foreground='green')
        tree_financeiro.tag_configure('saida', foreground='red')

    # Frame para botão de nova despesa
    frame_nova_despesa = ttk.Frame(aba_financeiro)
    frame_nova_despesa.pack(padx=10, pady=5, fill="x")

    def abrir_popup_nova_despesa():
        hoje_str = datetime.today().strftime("%d/%m/%Y")
        popup = tk.Toplevel(root)
        popup.title(f"Lançar Nova Despesa - {hoje_str}")
        popup.geometry("400x150")
        
        frame = ttk.LabelFrame(popup, text=f"Nova Despesa - {hoje_str}")
        frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(frame, text="Descrição:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(frame, text="Valor:").grid(row=1, column=0, padx=5, pady=5)
        
        entry_desc = tk.Entry(frame, width=30)
        entry_valor = tk.Entry(frame, width=15)
        
        entry_desc.grid(row=0, column=1, padx=5, pady=5)
        entry_valor.grid(row=1, column=1, padx=5, pady=5)
        
        def salvar_despesa():
            try:
                desc = entry_desc.get()
                valor = float(entry_valor.get())
                financeiro.adicionar_saida(desc, valor)
                atualizar_tree_financeiro()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tk.Button(frame, text="Salvar", command=salvar_despesa).grid(row=2, column=0, columnspan=2, pady=10)

    btn_nova_despesa = ttk.Button(
        frame_nova_despesa, 
        text="Lançar Nova Despesa", 
        command=abrir_popup_nova_despesa
    )
    btn_nova_despesa.pack(side="left", padx=5)

    # --- ABA HISTÓRICO (Atualizada) ---
    frame_filtro = ttk.LabelFrame(aba_historico, text="Filtrar Vendas")
    frame_filtro.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_filtro, text="Dia:").grid(row=0, column=0)
    entry_dia = tk.Entry(frame_filtro, width=5)
    entry_dia.grid(row=0, column=1)

    tk.Label(frame_filtro, text="Mês:").grid(row=0, column=2)
    entry_mes = tk.Entry(frame_filtro, width=5)
    entry_mes.grid(row=0, column=3)

    tk.Label(frame_filtro, text="Ano:").grid(row=0, column=4)
    entry_ano = tk.Entry(frame_filtro, width=6)
    entry_ano.grid(row=0, column=5)

    tk.Label(frame_filtro, text="Produto:").grid(row=0, column=6)
    combo_filtro_produto = ttk.Combobox(frame_filtro, width=20)
    combo_filtro_produto.grid(row=0, column=7)

    def atualizar_combo_filtro_produto():
        produtos = list(inventario.df_produtos.index)
        combo_filtro_produto["values"] = [""] + produtos

    def atualizar_historico():
        filtro_atual["dia"] = entry_dia.get() or None
        filtro_atual["mes"] = entry_mes.get() or None
        filtro_atual["ano"] = entry_ano.get() or None
        filtro_atual["produto"] = combo_filtro_produto.get() or None

        df = inventario.filtrar_vendas_por_data(**filtro_atual)
        vendas_agrupadas = inventario.obter_vendas_agrupadas()
        
        # Filtra vendas agrupadas se necessário
        if any(filtro_atual.values()):
            # Aplica filtros nas vendas agrupadas
            if filtro_atual["ano"]:
                vendas_agrupadas = vendas_agrupadas[vendas_agrupadas["data"].str[6:] == f"{int(filtro_atual['ano']):04d}"]
            if filtro_atual["mes"]:
                vendas_agrupadas = vendas_agrupadas[vendas_agrupadas["data"].str[3:5] == f"{int(filtro_atual['mes']):02d}"]
            if filtro_atual["dia"]:
                vendas_agrupadas = vendas_agrupadas[vendas_agrupadas["data"].str[:2] == f"{int(filtro_atual['dia']):02d}"]
            if filtro_atual["produto"]:
                vendas_agrupadas = vendas_agrupadas[vendas_agrupadas["produto"].str.contains(filtro_atual["produto"], na=False)]

        tree_vendas.delete(*tree_vendas.get_children())
        
        if not vendas_agrupadas.empty:
            for _, row in vendas_agrupadas.iterrows():
                tree_vendas.insert("", tk.END, values=(
                    row["data"], 
                    row["produto"], 
                    row["quantidade"], 
                    f"R${row['lucro']:.2f}",
                    row["venda_id"]
                ))

    def limpar_filtros():
        entry_dia.delete(0, tk.END)
        entry_mes.delete(0, tk.END)
        entry_ano.delete(0, tk.END)
        combo_filtro_produto.set("")
        filtro_atual.update({"dia": None, "mes": None, "ano": None, "produto": None})
        atualizar_historico()

    tk.Button(frame_filtro, text="Filtrar", command=atualizar_historico).grid(row=0, column=8, padx=5)
    tk.Button(frame_filtro, text="Limpar Filtros", command=limpar_filtros).grid(row=0, column=9)

    frame_vendas = ttk.LabelFrame(aba_historico, text="Vendas")
    frame_vendas.pack(padx=10, pady=10, fill="both", expand=True)

    tree_vendas = ttk.Treeview(frame_vendas, columns=("data", "produto", "quantidade", "lucro", "venda_id"), show="headings")
    tree_vendas.heading("data", text="Data")
    tree_vendas.heading("produto", text="Produto(s)")
    tree_vendas.heading("quantidade", text="Qtd Total")
    tree_vendas.heading("lucro", text="Lucro")
    tree_vendas.heading("venda_id", text="ID Venda")
    tree_vendas.pack(fill="both", expand=True)

    def mostrar_detalhes_venda():
        selecionado = tree_vendas.selection()
        if not selecionado:
            return
        
        item = tree_vendas.item(selecionado[0])
        venda_id = item["values"][4]
        
        popup = tk.Toplevel(root)
        popup.title(f"Detalhes da Venda - ID: {venda_id}")
        popup.geometry("500x300")
        
        detalhes = inventario.obter_detalhes_venda(venda_id)
        
        tree_detalhes_venda = ttk.Treeview(popup, columns=("produto", "quantidade", "lucro"), show="headings")
        tree_detalhes_venda.heading("produto", text="Produto")
        tree_detalhes_venda.heading("quantidade", text="Quantidade")
        tree_detalhes_venda.heading("lucro", text="Lucro")
        tree_detalhes_venda.pack(fill="both", expand=True)
        
        for _, row in detalhes.iterrows():
            tree_detalhes_venda.insert("", tk.END, values=(
                row["produto"], 
                row["quantidade"], 
                f"R${row['lucro']:.2f}"
            ))

    tree_vendas.bind("<Double-1>", lambda e: mostrar_detalhes_venda())

    def ao_trocar_aba(event):
        if aba.index("current") == 1:  # Histórico
            atualizar_historico()
        elif aba.index("current") == 3:  # Financeiro
            atualizar_tree_financeiro()

    aba.bind("<<NotebookTabChanged>>", ao_trocar_aba)

    # --- ABA ESTOQUE ---
    frame_top = ttk.Frame(aba_estoque_total)
    frame_top.pack(padx=10, pady=10, fill="x")

    btn_novo_produto = tk.Button(frame_top, text="+ Novo Produto", command=lambda: abrir_popup_novo_produto())
    btn_novo_produto.pack(side="left", padx=(0, 10))

    btn_editar_produto = tk.Button(frame_top, text="Editar Produto", command=lambda: abrir_popup_editar_produto())
    btn_editar_produto.pack(side="left", padx=(0, 10))
    btn_editar_produto.config(state="disabled")

    btn_remover_produto = tk.Button(frame_top, text="Remover Produto", command=lambda: remover_produto())
    btn_remover_produto.pack(side="left")
    btn_remover_produto.config(state="disabled")

    frame_tabela = ttk.LabelFrame(aba_estoque_total, text="Produtos em Estoque")
    frame_tabela.pack(padx=10, pady=10, fill="both", expand=True)

    tree_frame = tk.Frame(frame_tabela)
    tree_frame.pack(fill="both", expand=True)

    scroll_estoque = ttk.Scrollbar(tree_frame, orient="vertical")
    scroll_estoque.pack(side="right", fill="y")

    # Removido campo "custo" da tabela
    tree_produtos = ttk.Treeview(tree_frame, columns=("nome", "estoque", "preco"), show="headings", yscrollcommand=scroll_estoque.set)
    tree_produtos.heading("nome", text="PRODUTO")
    tree_produtos.heading("estoque", text="ESTOQUE")
    tree_produtos.heading("preco", text="PREÇO")
    tree_produtos.pack(side="left", fill="both", expand=True)

    scroll_estoque.config(command=tree_produtos.yview)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
    style.configure("Treeview", font=("Arial", 10))
    tree_produtos.tag_configure('bold', font=('Arial', 10, 'bold'))

    def atualizar_tabela_produtos():
        tree_produtos.delete(*tree_produtos.get_children())
        for nome, row in inventario.df_produtos.iterrows():
            tree_produtos.insert("", tk.END, iid=nome, values=(nome.upper(), row["estoque"], f"R${row['preco']:.2f}"), tags=('bold',))
        atualizar_combo_produtos()
        atualizar_combo_filtro_produto()
        desabilitar_botoes()

    def atualizar_combo_produtos():
        produtos = list(inventario.df_produtos.index)
        combo_produtos['values'] = produtos
        if produtos:
            combo_produtos.current(0)

    def abrir_popup_novo_produto():
        popup = tk.Toplevel(root)
        popup.title("Adicionar Novo Produto")
        popup.geometry("400x200")

        tk.Label(popup, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(popup, text="Estoque:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(popup, text="Preço:").grid(row=2, column=0, sticky="e", padx=5, pady=5)

        e_nome = tk.Entry(popup, font=("Arial", 12))
        e_estoque = tk.Entry(popup, font=("Arial", 12))
        e_preco = tk.Entry(popup, font=("Arial", 12))

        e_nome.grid(row=0, column=1, padx=5, pady=5)
        e_estoque.grid(row=1, column=1, padx=5, pady=5)
        e_preco.grid(row=2, column=1, padx=5, pady=5)

        def confirmar():
            try:
                nome = e_nome.get()
                estoque = int(e_estoque.get())
                preco = float(e_preco.get())
                inventario.adicionar_produto(nome, preco, estoque)
                popup.destroy()
                atualizar_tabela_produtos()
                atualizar_tree_vendas_dia()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(popup, text="Confirmar", font=("Arial", 12), command=confirmar).grid(row=3, column=0, columnspan=2, pady=10)

    def abrir_popup_editar_produto():
        selecionado = tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        nome = selecionado[0]
        popup = tk.Toplevel(root)
        popup.title(f"Editar Produto: {nome}")

        tk.Label(popup, text=f"Produto: {nome.upper()}").grid(row=0, column=0, columnspan=2, pady=(5,10))

        tk.Label(popup, text="Novo preço:").grid(row=1, column=0, sticky="e")
        tk.Label(popup, text="Ajustar estoque (+/-):").grid(row=2, column=0, sticky="e")

        e_preco = tk.Entry(popup)
        e_ajuste = tk.Entry(popup)

        e_preco.grid(row=1, column=1, padx=5, pady=2)
        e_ajuste.grid(row=2, column=1, padx=5, pady=2)

        def confirmar():
            try:
                preco = e_preco.get()
                ajuste = e_ajuste.get()

                inventario.editar_produto(
                    nome,
                    float(preco) if preco else None
                )
                if ajuste:
                    inventario.alterar_estoque(nome, int(ajuste))

                popup.destroy()
                atualizar_tabela_produtos()
                atualizar_tree_vendas_dia()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(popup, text="Salvar", command=confirmar).grid(row=3, column=0, pady=10)
        tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=3, column=1, pady=10)

    def remover_produto():
        selecionado = tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para remover.")
            return
        nome = selecionado[0]
        if messagebox.askyesno("Confirmação", f"Remover '{nome}' do estoque?"):
            try:
                inventario.remover_produto(nome)
                atualizar_tabela_produtos()
                atualizar_tree_vendas_dia()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def ao_selecionar_produto(event):
        selecionado = tree_produtos.selection()
        if selecionado:
            btn_editar_produto.config(state="normal")
            btn_remover_produto.config(state="normal")
        else:
            desabilitar_botoes()

    def desabilitar_botoes():
        btn_editar_produto.config(state="disabled")
        btn_remover_produto.config(state="disabled")

    tree_produtos.bind("<<TreeviewSelect>>", ao_selecionar_produto)

    def salvar_automaticamente():
        excel_io.salvar_dados(inventario.df_produtos, inventario.df_vendas, financeiro.df_financeiro)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", salvar_automaticamente)

    # Inicialização
    atualizar_combo_produtos()
    atualizar_combo_filtro_produto()
    atualizar_tree_vendas_dia()
    atualizar_tabela_produtos()
    atualizar_tree_financeiro()
    atualizar_tree_carrinho()
    desabilitar_botoes()

    root.mainloop()