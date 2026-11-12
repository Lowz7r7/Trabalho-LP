"""Controle de itens - Luz Treinamentos (versão fácil, com janela)
Usa só o que vem no Python: tkinter e json.   Para abrir:  python luz_facil.py
"""
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

ARQUIVO = "dados_luz.json"
PIN = "1234"
LOCAIS = {  # cada local tem uma lista de salas
    "Sede": ["Sala de Podcast", "Sala de Treinamentos", "Marketing", "Diretoria", "Administrativo", "Lounge"],
    "Estoque": ["Prateleiras", "Caixas de Evento"],
}
dados = {"itens": [], "consumiveis": [], "registro": []}
usuario = {"nome": ""}

# ARQUIVO
def carregar():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados_salvos = json.load(f)
            dados.update(dados_salvos)
            LOCAIS.update(dados_salvos.get("locais", {}))
    except FileNotFoundError:  # primeira vez: cria uns exemplos
        exemplos = [("Microfone", "Sede", "Sala de Podcast"),
                    ("Projetor", "Sede", "Sala de Treinamentos"),
                    ("Caixa de som", "Estoque", "Prateleiras"),
                    ("Banner Luz", "Estoque", "Caixas de Evento")]
        for nome, local, sala in exemplos:
            dados["itens"].append({"nome": nome, "local": local, "sala": sala, "status": "No local", "evento": ""})
        dados["consumiveis"].append({"nome": "Café", "local": "Sede", "qtd": 6, "minimo": 3})
        dados["consumiveis"].append({"nome": "Papel higiênico", "local": "Sede", "qtd": 12, "minimo": 8})


def salvar():
    dados["locais"] = LOCAIS
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registrar(texto):
    data = datetime.now().strftime("%d/%m/%Y")
    dados["registro"].append(data + " | " + usuario["nome"] + " | " + texto)
    salvar()


# LÓGICA 
def retirar_itens(marcados, evento):
    """Dá saída nos itens marcados. Devolve os nomes dos que já estavam em evento."""
    ja_fora = []
    for i in marcados:
        item = dados["itens"][i]
        if item["status"] == "Em evento":
            ja_fora.append(item["nome"])
        else:
            item["status"] = "Em evento"
            item["evento"] = evento
            registrar(f"SAÍDA: {item['nome']} de {item['local']} > {item['sala']} para {evento}")
    return ja_fora


def devolver_itens(marcados):
    for i in marcados:
        item = dados["itens"][i]
        if item["status"] == "Em evento":
            evento = item["evento"]
            item["status"] = "No local"
            item["evento"] = ""
            registrar(f"VOLTA: {item['nome']} do evento {evento} para {item['local']} > {item['sala']}")


def texto_o_que_esta_fora():
    linhas = []
    for item in dados["itens"]:
        if item["status"] == "Em evento":
            linhas.append(f"{item['nome']}  →  {item['evento']}")
    if len(linhas) == 0:
        return "Tudo está guardado no lugar!"
    return "\n".join(linhas)


# TELA
def desenhar_itens():
    arv.delete(*arv.get_children())
    raiz = arv.insert("", "end", text="🏢 Luz Treinamentos", open=True)
    for local in LOCAIS:
        pasta_local = arv.insert(raiz, "end", text="📍 " + local, open=True)
        for sala in LOCAIS[local]:
            pasta_sala = arv.insert(pasta_local, "end", text="🚪 " + sala)
            for i in range(len(dados["itens"])):
                item = dados["itens"][i]
                if item["local"] == local and item["sala"] == sala:
                    situacao = "✅ No local"
                    if item["status"] == "Em evento":
                        situacao = "🚚 Em evento: " + item["evento"]
                    arv.insert(pasta_sala, "end", iid="item" + str(i), text="📦 " + item["nome"], values=(situacao,))


def desenhar_consumiveis():
    lista_c.delete(0, "end")
    for i in range(len(dados["consumiveis"])):
        c = dados["consumiveis"][i]
        texto = f"{c['nome']} ({c['local']}): {c['qtd']}"
        if c["qtd"] <= c["minimo"]:
            texto = texto + "   ⚠ ACABANDO"
        lista_c.insert("end", texto)
        if c["qtd"] <= c["minimo"]:
            lista_c.itemconfig(i, fg="red")


def atualizar():
    desenhar_itens()
    desenhar_consumiveis()


def itens_marcados():
    """Números dos itens que estão selecionados na árvore."""
    marcados = []
    for no in arv.selection():
        if no.startswith("item"):
            marcados.append(int(no[4:]))
    if len(marcados) == 0:
        messagebox.showinfo("Atenção", "Clique em um ou mais itens da lista (Ctrl para vários).")
    return marcados


def selecionar_local():
    janela = tk.Toplevel(root)
    janela.title("Selecionar local")
    janela.transient(root)
    janela.grab_set()
    resultado = {"local": None}

    ttk.Label(janela, text="Selecione o local:").pack(padx=12, pady=(12, 4))
    local_var = tk.StringVar()
    lista_locais = ttk.Combobox(
        janela, textvariable=local_var, values=list(LOCAIS), state="readonly", width=30
    )
    lista_locais.pack(padx=12, pady=4)
    if LOCAIS:
        lista_locais.current(0)

    def confirmar():
        if local_var.get() not in LOCAIS:
            messagebox.showwarning("Atenção", "Selecione um local.", parent=janela)
            return
        resultado["local"] = local_var.get()
        janela.destroy()

    botoes_local = ttk.Frame(janela)
    botoes_local.pack(fill="x", padx=12, pady=12)
    ttk.Button(botoes_local, text="Selecionar", command=confirmar).pack(side="right")
    janela.protocol("WM_DELETE_WINDOW", janela.destroy)
    janela.wait_window()
    return resultado["local"]


def selecionar_sala(local):
    salas = LOCAIS[local]
    if not salas:
        messagebox.showwarning("Atenção", f"Não há salas cadastradas para {local}.")
        return None

    janela = tk.Toplevel(root)
    janela.title("Selecionar sala")
    janela.transient(root)
    janela.grab_set()
    resultado = {"sala": None}

    ttk.Label(janela, text=f"Selecione a sala em {local}:").pack(padx=12, pady=(12, 4))
    sala_var = tk.StringVar()
    lista_salas = ttk.Combobox(
        janela, textvariable=sala_var, values=salas, state="readonly", width=30
    )
    lista_salas.pack(padx=12, pady=4)
    lista_salas.current(0)

    def criar_sala():
        nome = simpledialog.askstring("Nova sala", "Nome da nova sala:", parent=janela)
        if nome is None or not nome.strip():
            return
        nome = nome.strip()
        if any(nome.casefold() == existente.casefold() for existente in LOCAIS[local]):
            messagebox.showwarning("Atenção", "Essa sala já existe.", parent=janela)
            return
        LOCAIS[local].append(nome)
        salvar()
        lista_salas["values"] = LOCAIS[local]
        sala_var.set(nome)

    def confirmar():
        if sala_var.get() not in LOCAIS[local]:
            messagebox.showwarning("Atenção", "Selecione uma sala.", parent=janela)
            return
        resultado["sala"] = sala_var.get()
        janela.destroy()

    botoes_sala = ttk.Frame(janela)
    botoes_sala.pack(fill="x", padx=12, pady=12)
    ttk.Button(botoes_sala, text="➕ Criar sala", command=criar_sala).pack(side="left")
    ttk.Button(botoes_sala, text="Selecionar", command=confirmar).pack(side="right")
    janela.protocol("WM_DELETE_WINDOW", janela.destroy)
    janela.wait_window()
    return resultado["sala"]


def pedir_local():
    local = selecionar_local()
    if local is None:
        return None
    sala = selecionar_sala(local)
    if sala is None:
        return None
    return (local, sala)


def botao_cadastrar():
    nome = simpledialog.askstring("Novo item", "Nome do item:")
    if nome is None or nome.strip() == "":
        return
    lugar = pedir_local()
    if lugar is not None:
        dados["itens"].append({"nome": nome.strip(), "local": lugar[0], "sala": lugar[1],
                               "status": "No local", "evento": ""})
        registrar(f"Cadastrou {nome.strip()} em {lugar[0]} > {lugar[1]}")
        atualizar()


def botao_mover():
    marcados = itens_marcados()
    if len(marcados) != 1:
        messagebox.showinfo("Atenção", "Escolha UM item para mover.")
        return
    item = dados["itens"][marcados[0]]
    if item["status"] == "Em evento":
        messagebox.showwarning("Atenção", "Esse item está em evento. Devolva antes.")
        return
    lugar = pedir_local()
    if lugar is not None:
        local_anterior = item["local"]
        sala_anterior = item["sala"]
        item["local"] = lugar[0]
        item["sala"] = lugar[1]
        registrar(
            f"Moveu {item['nome']}: {local_anterior} > {sala_anterior} "
            f"para {lugar[0]} > {lugar[1]}"
        )
        atualizar()


def botao_retirar():
    marcados = itens_marcados()
    if len(marcados) == 0:
        return
    evento = simpledialog.askstring("Evento", "Nome do evento:")
    if evento is None or evento.strip() == "":
        return
    ja_fora = retirar_itens(marcados, evento.strip())
    if len(ja_fora) > 0:
        messagebox.showwarning("Atenção", "Já estavam em evento:\n" + "\n".join(ja_fora))
    atualizar()


def botao_devolver():
    marcados = itens_marcados()
    if len(marcados) > 0:
        devolver_itens(marcados)
        atualizar()


def botao_conferir():
    messagebox.showinfo("O que está fora", texto_o_que_esta_fora())


def botao_novo_consumivel():
    nome = simpledialog.askstring("Consumível", "Nome:")
    if nome is None or not nome.strip():
        return
    local = selecionar_local()
    if local is None:
        return
    qtd = simpledialog.askinteger("Consumível", "Quantidade atual:", minvalue=0)
    minimo = simpledialog.askinteger("Consumível", "Avisar quando chegar a:", minvalue=0)
    if qtd is None or minimo is None:
        messagebox.showwarning("Atenção", "Dados inválidos.")
        return
    dados["consumiveis"].append({"nome": nome.strip(), "local": local, "qtd": qtd, "minimo": minimo})
    registrar(f"Cadastrou consumível {nome.strip()}: {qtd}")
    atualizar()


def mexer_consumivel(sinal):
    escolha = lista_c.curselection()
    if len(escolha) == 0:
        messagebox.showinfo("Atenção", "Clique em um consumível.")
        return
    c = dados["consumiveis"][escolha[0]]
    q = simpledialog.askinteger("Quantidade", "Quantas unidades?", minvalue=1)
    if q is None:
        return
    if sinal == -1 and q > c["qtd"]:
        messagebox.showwarning("Atenção", "Não tem essa quantidade!")
        return
    c["qtd"] = c["qtd"] + sinal * q
    registrar(f"{c['nome']} ({c['local']}): {sinal * q:+d}, saldo {c['qtd']}")
    atualizar()


def botao_entrada():
    mexer_consumivel(1)


def botao_saida():
    mexer_consumivel(-1)


def botao_registro():
    tentativas = 0
    while tentativas < 3:  # 3 chances para acertar o PIN
        pin = simpledialog.askstring("Diretoria", "Digite o PIN:", show="*")
        if pin is None:
            return
        if pin == PIN:
            ultimas = dados["registro"][-20:]
            ultimas.reverse()
            messagebox.showinfo("Registro (20 últimos)", "\n".join(ultimas))
            return
        tentativas = tentativas + 1
        messagebox.showerror("Acesso negado", "PIN incorreto.")
    messagebox.showwarning("Bloqueado", "3 tentativas erradas.")


# ----------------------------------------------------- MONTAR A JANELA
carregar()
root = tk.Tk()
root.title("Luz Treinamentos — Controle de Itens")
root.geometry("900x520")

# lado esquerdo: árvore de pastas + botões dos itens
esquerda = ttk.Frame(root)
esquerda.pack(side="left", fill="both", expand=True, padx=8, pady=8)
arv = ttk.Treeview(esquerda, columns=("situacao",), selectmode="extended")
arv.heading("#0", text="Luz  ›  Local  ›  Sala  ›  Item  (clique nas pastas para abrir)")
arv.heading("situacao", text="Situação")
arv.column("#0", width=380)
arv.column("situacao", width=200)
arv.pack(fill="both", expand=True)
botoes = ttk.Frame(esquerda)
botoes.pack(fill="x", pady=6)
ttk.Button(botoes, text="➕ Novo item", command=botao_cadastrar).pack(side="left", padx=2)
ttk.Button(botoes, text="↔ Mover", command=botao_mover).pack(side="left", padx=2)
ttk.Button(botoes, text="🚚 RETIRAR p/ evento", command=botao_retirar).pack(side="left", padx=2)
ttk.Button(botoes, text="✅ DEVOLVER", command=botao_devolver).pack(side="left", padx=2)
ttk.Button(botoes, text="📋 O que está fora?", command=botao_conferir).pack(side="left", padx=2)

# lado direito: consumíveis e registro
direita = ttk.Frame(root)
direita.pack(side="right", fill="y", padx=8, pady=8)
ttk.Label(direita, text="☕ Consumíveis", font=("Segoe UI", 11, "bold")).pack()
lista_c = tk.Listbox(direita, width=34, height=14)
lista_c.pack(fill="x")
ttk.Button(direita, text="⬆ Entrada (comprei)", command=botao_entrada).pack(fill="x", pady=2)
ttk.Button(direita, text="⬇ Saída (usei)", command=botao_saida).pack(fill="x", pady=2)
ttk.Button(direita, text="➕ Novo consumível", command=botao_novo_consumivel).pack(fill="x", pady=2)
ttk.Button(direita, text="🔒 Registro (diretoria)", command=botao_registro).pack(fill="x", pady=(24, 2))

usuario["nome"] = simpledialog.askstring("Quem está usando?", "Seu nome:") or "Sem nome"
atualizar()
root.mainloop()
