from tkinter import filedialog
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from financeiro import *
import os
from avisos import AvisoTemporario
import json
from customtkinter import CTk
from pyautogui import hotkey
from CTkMessagebox import CTkMessagebox


def maximizar_janela():
    hotkey('win', 'up')


CONFIG_FILE = "config.json"

def carregar_planilha():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            caminho = config.get("planilha_path")

            if caminho and os.path.exists(caminho):
                print(f"Planilha carregada de: {caminho}")
                return

    root = CTk()
    root.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione a planilha de dados",
        filetypes=[("Planilhas Excel", "*.xlsx *.xls")]
    )

    if not caminho:
        print("Nenhuma planilha selecionada.")
        return None

    with open(CONFIG_FILE, "w") as f:
        json.dump({"planilha_path": caminho}, f)

    print(f"Planilha carregada e caminho salvo: {caminho}")

    ler_planilha(caminho)


carregar_planilha()   


app = ctk.CTk()
app.geometry("1000x800")
app.title("Análise financeira")

def iniciar_janela(app):
    janela = ctk.CTkToplevel(app)
    janela.lift()
    janela.attributes("-topmost", True)
    janela.after(10, lambda: janela.attributes("-topmost", False))

    return janela

def botao_voltar(janela):

    btn_voltar = ctk.CTkButton(
    master=janela,
    text="Voltar",
    command=janela.destroy,
    width=200
    )
    btn_voltar.pack(pady=10)

def abrir_saldo_atual():
    janela = iniciar_janela(app)
    janela.geometry("800x600")
    janela.title("Saldo Atual")

    saldo = get_saldo_gasto_poupanca(1)

    label = ctk.CTkLabel(janela, text=f"Seu saldo atual é: {saldo}", font=("Arial", 18))
    label.pack(pady=10)

    botao_voltar(janela)

    label = ctk.CTkLabel(janela, text="Últimos 7 dias:", font=("Arial", 16))
    label.pack(pady=10)

   

    fig = get_variacao_saldo()
    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)


def abrir_gastos_terco():
    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Gastos por Terço do Mês")

    fig = get_gastos_terco(2)

    frame_botoes = ctk.CTkFrame(janela)
    frame_botoes.pack(pady=10)
    

    botao_voltar(frame_botoes)
    

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)



def abrir_gastos_mensais():
    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Gastos por Mês")

    fig = gastos_mes()

    meses = get_meses_disponiveis()
    gastos = get_saldo_gasto_poupanca(2)

    gastos = float(gastos) * -1

    label = ctk.CTkLabel(janela, text=f"Gastos totais acumulados\n({meses[0]} - {meses[-1]}):\nR$ {gastos:.2f}", font=("Arial", 18))
    label.pack(pady=20)

    botao_voltar(janela)

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)


def abrir_gastos_mes_especifico():
    janela = iniciar_janela(app)
    janela.geometry("1200x600")
    janela.title("Gastos por Mês Específico")
    

    meses = [str(m) for m in get_meses_disponiveis()]
    tipos_grafico = ["Barras por categoria", "Linha por dia", "Gastos por terço"]

    aviso = AvisoTemporario(janela)

    label_instrucao = ctk.CTkLabel(janela, text="Selecione o mês e o tipo de gráfico:", font=("Arial", 16))
    label_instrucao.pack(pady=10)

    frame_opcoes = ctk.CTkFrame(janela)
    frame_opcoes.pack(pady=10)

    var_mes = ctk.StringVar(value="Selecione o mês")
    var_tipo = ctk.StringVar(value="Barras por categoria")

    menu_meses = ctk.CTkOptionMenu(master=frame_opcoes, values=meses, variable=var_mes)
    menu_meses.grid(row=0, column=0, padx=10)

    menu_tipo = ctk.CTkOptionMenu(master=frame_opcoes, values=tipos_grafico, variable=var_tipo)
    menu_tipo.grid(row=0, column=1, padx=10)

    def gerar_grafico():
        janela.after(200, maximizar_janela)
        for widget in frame_canvas.winfo_children():
            widget.destroy()

        mes = var_mes.get()

        if mes == "Selecione o mês":
            aviso.mostrar("Informe o mês!", "erro")
            return

        tipo_selecionado = var_tipo.get()

        tipo_param = ""
        if tipo_selecionado == "Barras por categoria":
            tipo_param = "barras"
        elif tipo_selecionado == "Linha por dia":
            tipo_param = "linha"
        elif tipo_selecionado == "Gastos por terço":
            tipo_param = "terco"

        fig = gerar_grafico_gastos_mes(mes, tipo=tipo_param)
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    botao_gerar = ctk.CTkButton(frame_opcoes, text="Gerar Gráfico", command=gerar_grafico)
    botao_gerar.grid(row=0, column=2, padx=10)

    btn_voltar = ctk.CTkButton(
    master=frame_opcoes,
    text="Voltar",
    command=janela.destroy
    )
    btn_voltar.grid(row=0, column=3, padx=10)

    frame_canvas = ctk.CTkFrame(janela)
    frame_canvas.pack(expand=True, fill="both", padx=10, pady=10)

    
    
def abrir_gastos_categoria():

    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Top 10 Gastos por Categoria (total)")

    fig = gastos_categoria()

    botao_voltar(janela)

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)    

def abrir_diferenca_receita_gasto():
    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Diferença de Ganhos X Gastos")

    botao_voltar(janela)

    fig = comparar_ganhos_gastos()

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

def abrir_poupanca():

    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Valor guardado por mês")

    poupanca = get_saldo_gasto_poupanca(8)

    label = ctk.CTkLabel(janela, text=f"Valor total guardado: R$ {poupanca}", font=("Arial", 18))
    label.pack(pady=20)

    botao_voltar(janela)

    fig = reserva_por_mes()

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)


def abrir_alimentar_planilha():

    aviso.mostrar("Aviso! Não é possível fazer análises com a planilha aberta!\nSalve e feche a planilha caso queira fazer análises.", "aviso")

    caminho_arquivo = "Finanças.xlsx"
    os.startfile(caminho_arquivo)

def abrir_gastos_dia_especifico():

    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Gastos por dia específico")

  
    aviso = AvisoTemporario(janela)

    def gerar_grafico():
        aviso.esconder()  # Limpa aviso anterior
       

        dia = dia_entrada.get()
        if not dia:
            aviso.mostrar("⚠️ Preencha o campo com a data.", "erro")
            return

        fig = gerar_grafico_gastos_dia(dia)

        if fig is None:
            aviso.mostrar(f"📌 Nenhum gasto encontrado para {dia}.", "aviso")
            return
        
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    

    label = ctk.CTkLabel(janela, text="Informe o dia no formato dd/mm/aaaa", font=("Arial", 18))
    label.pack(pady=10)

    dia_entrada = ctk.CTkEntry(janela, placeholder_text="DIA (dd/mm/aaaa)", width=200)
    dia_entrada.pack(pady=10)

    botao = ctk.CTkButton(janela, text="Enviar", command=gerar_grafico, width=200)
    botao.pack(pady=10)


def abrir_estatisticas_mes():
    janela = iniciar_janela(app)
    janela.geometry("1200x700")
    janela.title("Estatísticas do Mês Atual")

    titulo = ctk.CTkLabel(janela, text="📊 Estatísticas Financeiras do Mês Atual", font=("Arial", 20, "bold"))
    titulo.pack(pady=15)

    # Frames laterais
    frame_esquerdo = ctk.CTkFrame(janela, width=600)
    frame_esquerdo.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    frame_direito = ctk.CTkFrame(janela, width=600)
    frame_direito.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # ---------------------- Frame Esquerdo (Comparativo Atual x Anterior) ----------------------
    dados = get_variacao_gastos()

    titulo_esq = ctk.CTkLabel(frame_esquerdo, text="📈 Comparativo com Mês Anterior", font=("Arial", 16, "bold"))
    titulo_esq.pack(pady=10)

    texto_esq = f"""
        🔎 Comparando os gastos acumulados até o dia {dados['dia']}:

        ➡️ Mês atual ({dados['mes_atual']}): R$ {dados['total_atual']:.2f}
        ➡️ Mês anterior ({dados['mes_anterior']}): R$ {dados['total_anterior']:.2f}
        """

    if dados['total_atual'] > dados['total_anterior']:
        texto_esq += f"""
            🔺 Seus gastos aumentaram {abs(dados['variacao']):.2f}% em relação ao mesmo período do mês anterior.
            📈 Caso essa tendência continue, o total estimado para o fim do mês será de R$ {dados['tendencia']:.2f}.
            """
    elif dados['total_atual'] < dados['total_anterior']:
        texto_esq += f"""
            🟢 Seus gastos estão {dados['variacao']:.2f}% menores do que no mesmo período do mês passado.
            📉 A projeção atual indica um total de R$ {dados['tendencia']:.2f} até o fim do mês.
            """
    else:
        texto_esq += "\n⚖️ Os gastos estão exatamente iguais ao mês anterior até esta data."

    label_texto_esq = ctk.CTkLabel(frame_esquerdo, text=texto_esq, font=("Arial", 14), justify="left")
    label_texto_esq.pack(pady=10)

    # Maiores gastos lado a lado
    frame_gastos = ctk.CTkFrame(frame_esquerdo)
    frame_gastos.pack(pady=10)

    frame_atuais = ctk.CTkFrame(frame_gastos)
    frame_atuais.pack(side="left", padx=10)

    ctk.CTkLabel(frame_atuais, text="🧾 Maiores gastos do mês atual:", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    for desc, val, data in dados["maiores_atuais"]:
        ctk.CTkLabel(frame_atuais, text=f"- {desc}: R$ {abs(val):.2f} ({data})", anchor="w", justify="left").pack(anchor="w")

    frame_anteriores = ctk.CTkFrame(frame_gastos)
    frame_anteriores.pack(side="left", padx=10)

    ctk.CTkLabel(frame_anteriores, text="📜 Maiores gastos no mês anterior\n(mesmo período):", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    for desc, val, data in dados["maiores_anteriores"]:
        ctk.CTkLabel(frame_anteriores, text=f"- {desc}: R$ {abs(val):.2f} ({data})", anchor="w", justify="left").pack(anchor="w")

    # ---------------------- Frame Direito (Médias e Expectativas) ----------------------
    dicionario = get_medias()

    titulo_dir = ctk.CTkLabel(frame_direito, text="📊 Médias e Expectativas", font=("Arial", 16, "bold"))
    titulo_dir.pack(pady=10)

    diferenca_gastos_media = "acima" if dicionario['percentual_gasto_vs_media'] > 0 else "abaixo"

    textos = [
        f"📌 Total gasto até agora: R$ {dicionario['gasto_atual']}",
        f"⏳ Esse valor foi acumulado em {dicionario['dia_atual']} dias, ou {int(dicionario['porcentagem_mes'])}% do mês.",
        f"💸 Sua média de gastos mensais é R$ {dicionario['media_limpa_gastos']}\nO valor de gastos atual está {abs(dicionario['percentual_gasto_vs_media'])}% {diferenca_gastos_media} da média",
        f"💰 Sua média mensal de ganhos é de R$ {dicionario['media_limpa_receitas']}\nO valor de gastos atuais correspondem a {dicionario['percentual_gasto_vs_receita']}% dessa média.",
        f"📅 Considerando o valor gasto no período do mês atual, o total esperado para o fim do mês é de R$ {dicionario['expectativa_fim_mes']} (sujeito a variações diárias)."
    ]

    for t in textos:
        ctk.CTkLabel(frame_direito, text=t, font=("Arial", 14), justify="left", wraplength=550).pack(pady=5)

    # Terços do mês
    for terco in ["1º terço", "2º terço", "3º terço"]:
        if dicionario['dia_atual'] >= 10 and terco in dicionario['gasto_tercos'] and dicionario['gasto_tercos'][terco]:
            val = dicionario['gasto_tercos'][terco]['valor']
            media = dicionario['gasto_tercos'][terco]['media']
            texto = f"📌 {terco.title()} do mês: R$ {val:.2f} gastos | Média histórica: R$ {media:.2f}"
            ctk.CTkLabel(frame_direito, text=texto, font=("Arial", 14)).pack(pady=4)

def abrir_simular_gastos():
    janela = iniciar_janela(app)
    janela.geometry("1000x600")
    janela.title("Simular Gastos")

    titulo = ctk.CTkLabel(
        janela, 
        text="Simular Gastos/Ganhos", 
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=10)

    mes_atual = datetime.today().strftime("%B/%Y").capitalize()
    valor_gastos = float(gerar_grafico_gastos_mes(mes_atual, "valor"))
    saldo = float(get_saldo_gasto_poupanca(1))
    media_gastos = get_valor_medio_gastos()
    media_ganhos = get_valor_medio_ganhos()

    # Frame de valores com visual uniforme
    frame_valores = ctk.CTkFrame(
        janela, 
        fg_color=None  # herda a cor do fundo
    )
    fonte_valores = ("Arial", 15, "bold")

    label_saldo = ctk.CTkLabel(
        frame_valores, 
        text=f"Saldo: R$ {saldo:.2f}", 
        font=fonte_valores, 
        anchor="center"
    )
    label_saldo.grid(row=1, column=0, padx=20, pady=10)

    label_gastos = ctk.CTkLabel(
        frame_valores, 
        text=f"Valor gasto esse mês: R$ {valor_gastos:.2f}", 
        font=fonte_valores,
        anchor="center"
    )
    label_gastos.grid(row=1, column=1, padx=20, pady=10)

    label_media_gastos = ctk.CTkLabel(
        frame_valores, 
        text=f"Média de Gastos: R$ {media_gastos:.2f}", 
        font=fonte_valores,
        anchor="center"
    )
    label_media_gastos.grid(row=1, column=2, padx=20, pady=10)

    label_ganhos = ctk.CTkLabel(
        frame_valores, 
        text=f"Média de Ganhos: R$ {media_ganhos:.2f}", 
        font=fonte_valores,
        anchor="center"
    )
    label_ganhos.grid(row=1, column=3, padx=20, pady=10)

    frame_valores.pack(pady=20)
        
    simulacoes = []  

    def adicionar_simulacao():
        nonlocal saldo, valor_gastos  

        try:
            valor = float(valor_simular.get())
        except ValueError:
            valor = (valor_simular.get()).replace(",", ".")
            try:
                valor = float(valor)
            except ValueError:
                print("Valor inválido")
                return

        descricao = descricao_simular.get()
        simulacoes.append((descricao, valor))

        tipo = "ganho"
        if valor < 0:
            tipo = "gasto"
            valor_gastos -= valor

        saldo += valor
        
        label_saldo.configure(text=f"Saldo: R$ {saldo:.2f}")
        label_gastos.configure(text=f"Gastos: R$ {valor_gastos:.2f}")

        caixa_listagem.insert("end", f"{descricao:<40}{valor:^20}{tipo:>20}\n")

        descricao_simular.delete(0, "end")
        valor_simular.delete(0, "end")

    def gerar_arquivo():
        nonlocal saldo, valor_gastos

        simulacao = caixa_listagem.get("1.0", "end-1c")
        valor_saldo = saldo
        gastos = valor_gastos

        texto = f"Simulação:\n{simulacao}\n\nSaldo: R$ {valor_saldo:.2f}\nGastos: R$ {gastos:.2f}"
        txt = open("relatorio.txt", "w")
        txt.write(texto)
        txt.close()

        CTkMessagebox(
            title="Relatório Gerado",
            message="O relatório foi gerado com sucesso!",
            icon="info"
        )


    # Frame de entrada
    frame_simular = ctk.CTkFrame(janela, fg_color="transparent")

    valor_simular = ctk.CTkEntry(frame_simular, placeholder_text="Valor", width=200)
    valor_simular.grid(row=0, column=0, padx=10, pady=10)

    descricao_simular = ctk.CTkEntry(frame_simular, placeholder_text="Descrição", width=200)
    descricao_simular.grid(row=0, column=1, padx=10, pady=10)

    botao_simular = ctk.CTkButton(frame_simular, text="Simular", command=adicionar_simulacao)
    botao_simular.grid(row=0, column=2, padx=10, pady=10)

    botao_gerar = ctk.CTkButton(frame_simular, text="Gerar Arquivo", command=gerar_arquivo)
    botao_gerar.grid(row=0, column=3, padx=10, pady=10)

    frame_simular.pack(pady=2)

    tip = ctk.CTkLabel(janela, text="*Insira valores negativos para gastos.", font=("Arial", 12, "italic"))
    tip.pack(pady=10)

    # Caixa de listagem com fonte monoespaçada para alinhar colunas
    caixa_listagem = ctk.CTkTextbox(
        janela,
        width=660,
        height=400,
        font=("Courier New", 14),  # fonte monoespaçada
        fg_color=None,  # herda a cor do fundo
        text_color="white"
    )
    caixa_listagem.pack(pady=10)

    caixa_listagem.insert("end", f"{'Descrição':<40}{'Valor':^20}{'Tipo':>20}\n")
    caixa_listagem.insert("end", "-" * 80 + "\n")

    caixa_listagem.pack(pady=10)


label_titulo = ctk.CTkLabel(app, text=f"Bem vindo ao Software de análise financeira!\n{datetime.now().strftime('%d/%m/%Y')}", font=("Arial", 22))
label_titulo.pack(pady=10)

aviso = AvisoTemporario(app)

label_opcoes = ctk.CTkLabel(app, text="Escolha uma das opções de análise:", font=("Arial", 16))
label_opcoes.pack(pady=10)

botao_consulta_saldo = ctk.CTkButton(app, text="Consulta de Saldo Atual", command=abrir_saldo_atual, width=400)
botao_consulta_saldo.pack(pady=10)

botao_estatisticas_mes = ctk.CTkButton(app, text="Resumo mês atual", command=abrir_estatisticas_mes, width=400)
botao_estatisticas_mes.pack(pady=10)

botao_consulta_gastos_mensais = ctk.CTkButton(app, text="Consulta de Gastos por mês", command=abrir_gastos_mensais, width=400)
botao_consulta_gastos_mensais.pack(pady=10)

botao_gastos_dia_especifico = ctk.CTkButton(app, text="Simular Gastos/Ganhos Mês", command=abrir_simular_gastos, width=400)
botao_gastos_dia_especifico.pack(pady=10)

botao_consulta_gastos_mes_especifico = ctk.CTkButton(app, text="Consulta de Gastos por mês específico", command=abrir_gastos_mes_especifico, width=400)
botao_consulta_gastos_mes_especifico.pack(pady=10)

botao_consulta_gastos_terco = ctk.CTkButton(app, text="Consulta de Gastos por terço do mês", command=abrir_gastos_terco, width=400)
botao_consulta_gastos_terco.pack(pady=10)

botao_gastos_categoria = ctk.CTkButton(app, text="Consulta de Gastos por gênero", command=abrir_gastos_categoria, width=400)
botao_gastos_categoria.pack(pady=10)

botao_diferenca_receita_gasto = ctk.CTkButton(app, text="Diferença Saldo/Gasto por mês", command=abrir_diferenca_receita_gasto, width=400)
botao_diferenca_receita_gasto.pack(pady=10)

botao_valor_guardado_mes = ctk.CTkButton(app, text="Poupança", command=abrir_poupanca, width=400)
botao_valor_guardado_mes.pack(pady=10)

botao_alimentar_planilha = ctk.CTkButton(app, text="Alimentar planilha", command=abrir_alimentar_planilha, width=400)
botao_alimentar_planilha.pack(pady=10)

app.after(100, maximizar_janela)
app.mainloop()

