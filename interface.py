import tkinter as tk
from tkinter import ttk, messagebox
from inventario import Inventario
from datetime import datetime
import excel_io

inventario = Inventario()
filtro_atual = {"dia": None, "mes": None, "ano": None, "produto": None}

def iniciar_interface():
    root = tk.Tk()
    root.title("Controle de Estoque e Vendas")
    root.geometry("1000x700")

    # Carrega dados do Excel no inventário
    df_produtos, df_vendas = excel_io.carregar_dados()
    inventario.df_produtos = df_produtos
    inventario.df_vendas = df_vendas

    aba = ttk.Notebook(root)
    aba.pack(fill="both", expand=True)

    aba_vendas = ttk.Frame(aba)
    aba_historico = ttk.Frame(aba)
    aba_estoque_total = ttk.Frame(aba)
    aba.add(aba_vendas, text="Vendas")
    aba.add(aba_historico, text="Histórico")
    aba.add(aba_estoque_total, text="Estoque")

    # --- ABA VENDAS ---
    frame_venda = ttk.LabelFrame(aba_vendas, text="Registrar Venda")
    frame_venda.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_venda, text="Produto:").grid(row=0, column=0)
    tk.Label(frame_venda, text="Quantidade:").grid(row=0, column=2)
    tk.Label(frame_venda, text="Desconto (%):").grid(row=0, column=4)

    combo_produtos = ttk.Combobox(frame_venda, width=20)
    entry_quantidade = tk.Entry(frame_venda, width=10)
    entry_desconto = tk.Entry(frame_venda, width=10)

    combo_produtos.grid(row=0, column=1)
    entry_quantidade.grid(row=0, column=3)
    entry_desconto.grid(row=0, column=5)

    def atualizar_combo_produtos():
        produtos = list(inventario.df_produtos.index)
        combo_produtos['values'] = produtos
        if produtos:
            combo_produtos.current(0)

    def registrar_venda():
        try:
            produto = combo_produtos.get()
            qtd = int(entry_quantidade.get())
            desconto = float(entry_desconto.get() or 0) / 100
            inventario.registrar_venda(produto, qtd, desconto)
            atualizar_tree_vendas_dia()
            atualizar_tabela_produtos()
            entry_quantidade.delete(0, tk.END)
            entry_desconto.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    btn_vender = tk.Button(frame_venda, text="Registrar Venda", command=registrar_venda)
    btn_vender.grid(row=0, column=6, padx=10)

    frame_vendas_dia = ttk.LabelFrame(aba_vendas, text="Vendas do Dia")
    frame_vendas_dia.pack(padx=10, pady=10, fill="both", expand=True)

    tree_vendas_dia = ttk.Treeview(frame_vendas_dia, columns=("data", "produto", "quantidade", "lucro"), show="headings")
    tree_vendas_dia.heading("data", text="Data")
    tree_vendas_dia.heading("produto", text="Produto")
    tree_vendas_dia.heading("quantidade", text="Quantidade")
    tree_vendas_dia.heading("lucro", text="Lucro")
    tree_vendas_dia.pack(fill="both", expand=True)

    lbl_vazio_vendas = tk.Label(frame_vendas_dia, text="Nenhuma venda realizada hoje.", fg="gray")

    def atualizar_tree_vendas_dia():
        hoje_str = datetime.today().strftime("%d/%m/%Y")
        df = inventario.df_vendas
        vendas_hoje = df[df["data"] == hoje_str]
        tree_vendas_dia.delete(*tree_vendas_dia.get_children())

        if vendas_hoje.empty:
            lbl_vazio_vendas.pack()
        else:
            lbl_vazio_vendas.pack_forget()
            for _, row in vendas_hoje.iterrows():
                tree_vendas_dia.insert("", tk.END, values=(row["data"], row["produto"], row["quantidade"], f"R${row['lucro']:.2f}"))

    # --- ABA HISTÓRICO ---
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

        tree_vendas.delete(*tree_vendas.get_children())
        for _, row in df.iterrows():
            tree_vendas.insert("", tk.END, values=(row["data"], row["produto"], row["quantidade"], f"R${row['lucro']:.2f}"))

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

    tree_vendas = ttk.Treeview(frame_vendas, columns=("data", "produto", "quantidade", "lucro"), show="headings")
    for col in ("data", "produto", "quantidade", "lucro"):
        tree_vendas.heading(col, text=col.capitalize())
    tree_vendas.pack(fill="both", expand=True)

    def ao_trocar_aba(event):
        if aba.index("current") == 1:
            atualizar_historico()

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

    tree_produtos = ttk.Treeview(tree_frame, columns=("nome", "estoque", "custo", "preco"), show="headings", yscrollcommand=scroll_estoque.set)
    tree_produtos.heading("nome", text="PRODUTO")
    tree_produtos.heading("estoque", text="ESTOQUE")
    tree_produtos.heading("custo", text="CUSTO")
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
            tree_produtos.insert("", tk.END, iid=nome, values=(nome.upper(), row["estoque"], f"R${row['custo']:.2f}", f"R${row['preco']:.2f}"), tags=('bold',))
        atualizar_combo_produtos()
        atualizar_combo_filtro_produto()
        desabilitar_botoes()

    def abrir_popup_novo_produto():
        popup = tk.Toplevel(root)
        popup.title("Adicionar Novo Produto")
        popup.geometry("400x250")

        tk.Label(popup, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(popup, text="Estoque:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(popup, text="Custo:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Label(popup, text="Preço:").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        e_nome = tk.Entry(popup, font=("Arial", 12))
        e_estoque = tk.Entry(popup, font=("Arial", 12))
        e_custo = tk.Entry(popup, font=("Arial", 12))
        e_preco = tk.Entry(popup, font=("Arial", 12))

        e_nome.grid(row=0, column=1, padx=5, pady=5)
        e_estoque.grid(row=1, column=1, padx=5, pady=5)
        e_custo.grid(row=2, column=1, padx=5, pady=5)
        e_preco.grid(row=3, column=1, padx=5, pady=5)

        def confirmar():
            try:
                nome = e_nome.get()
                estoque = int(e_estoque.get())
                custo = float(e_custo.get())
                preco = float(e_preco.get())
                inventario.adicionar_produto(nome, preco, custo, estoque)
                popup.destroy()
                atualizar_tabela_produtos()
                atualizar_tree_vendas_dia()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(popup, text="Confirmar", font=("Arial", 12), command=confirmar).grid(row=4, column=0, columnspan=2, pady=10)

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
        tk.Label(popup, text="Novo custo:").grid(row=2, column=0, sticky="e")
        tk.Label(popup, text="Ajustar estoque (+/-):").grid(row=3, column=0, sticky="e")

        e_preco = tk.Entry(popup)
        e_custo = tk.Entry(popup)
        e_ajuste = tk.Entry(popup)

        e_preco.grid(row=1, column=1, padx=5, pady=2)
        e_custo.grid(row=2, column=1, padx=5, pady=2)
        e_ajuste.grid(row=3, column=1, padx=5, pady=2)

        def confirmar():
            try:
                preco = e_preco.get()
                custo = e_custo.get()
                ajuste = e_ajuste.get()

                inventario.editar_produto(
                    nome,
                    float(preco) if preco else None,
                    float(custo) if custo else None
                )
                if ajuste:
                    inventario.alterar_estoque(nome, int(ajuste))

                popup.destroy()
                atualizar_tabela_produtos()
                atualizar_tree_vendas_dia()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(popup, text="Salvar", command=confirmar).grid(row=4, column=0, pady=10)
        tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=4, column=1, pady=10)

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
        excel_io.salvar_dados(inventario.df_produtos, inventario.df_vendas)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", salvar_automaticamente)

    atualizar_combo_produtos()
    atualizar_combo_filtro_produto()
    atualizar_tree_vendas_dia()
    atualizar_tabela_produtos()
    desabilitar_botoes()

    root.mainloop()
