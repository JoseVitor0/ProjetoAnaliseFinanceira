import calendar
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
import locale
locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
from datetime import *



#Limpeza de valores para melhor interpretação da biblioteca pandas.
def limpar_valor(valor_str):
    if isinstance(valor_str, str):
         valor_str = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    return float(valor_str)

#Aplica a limpeza de valores, converte as datas para melhor interpretação da biblioteca também e separa gastos
#ganhos e poupança
def operacoes_iniciais(df):

    df["Valor"] = df["Valor"].apply(limpar_valor)
    df["Saldo"] = df["Saldo"].apply(limpar_valor)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df["Tipo"] = df["Valor"].apply(lambda x: "Receita" if x > 0 else "Despesa")

    df.loc[(df["Tipo"] == "Despesa") & (df["Descrição"].str.lower().str.contains("poupança")),"Tipo"] = "Reserva"

#Faz a leitura da planilha e entrega o dataframe para as operações necessárias.
def ler_planilha(caminho_planilha, tema):
    global df
    global tema_atual
    tema_atual = tema

    print(f"🔍 Tema recebido no financeiro.py: {tema}")

    df = pd.read_excel(caminho_planilha)
    operacoes_iniciais(df)

def get_df_gastos_mensais():
    global df
    df["AnoMes"] = df["Data"].dt.to_period("M")
    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()

def get_df_gastos_mensais_string(df):
    gastos = df[df["Tipo"] == "Despesa"].copy()
    gastos["AnoMes"] = gastos["Data"].dt.to_period("M")
    gastos["AnoMesStr"] = gastos["AnoMes"].dt.to_timestamp().dt.strftime("%B/%Y").str.capitalize()

    return gastos

#Calcula todas as receitas, gastos e valor destinado para poupança.
def get_saldo_gasto_poupanca(opcao):

    total_receita = df[df["Tipo"] == "Receita"]["Valor"].sum()
    total_poupanca = df[df["Tipo"] == "Reserva"]["Valor"].sum()
    total_despesa = df[df["Tipo"] == "Despesa"]["Valor"].sum()
    
    if opcao == 2: 
        return(f"{total_despesa:.2f}")
    if opcao == 1:
        return (f"{total_receita + total_despesa + total_poupanca:.2f}")
    if opcao == 8:
        return(f"{-total_poupanca:.2f}")

def get_mes_max_min_gastos():
    global df

    df["AnoMes"] = df["Data"].dt.to_period("M")
    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()

    gastos_mensais.index = gastos_mensais.index.to_timestamp()
    gastos_mensais.index = gastos_mensais.index.strftime("%B/%Y")

    mes_max = gastos_mensais.idxmax()
    mes_min = gastos_mensais.idxmin()

    valor_max = gastos_mensais.max()
    valor_min = gastos_mensais.min()

    return mes_max, mes_min, valor_max, valor_min


#Calcula todos os gastos por cada mês e retorna um gráfico para exibição dos valores calculados
def gastos_mes():
    
    df["AnoMes"] = df["Data"].dt.to_period("M")

    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()

    mes_max, mes_min, valor_max, valor_min = get_mes_max_min_gastos()

    gastos_mensais.index = gastos_mensais.index.to_timestamp()
    labels = gastos_mensais.index.strftime("%B/%Y")

    fig = Figure(figsize=(10, 5), dpi=100)
    ax = fig.add_subplot(111)

    colors = ["darkred" if gasto == float(valor_max) else "lightcoral" if gasto == float(valor_min) else "red" for gasto in gastos_mensais.values]

    ax.bar(labels, gastos_mensais, color=colors)
    ax.set_title("Gastos por Mês")
    ax.set_ylabel("Valor Gasto (R$)")
    ax.set_xlabel("Mês")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    for i, valor in enumerate(gastos_mensais):
        ax.text(i, valor + 5, f"R$ {abs(valor):.2f}", ha='center', va='bottom', fontsize=8)

    fig.tight_layout()
    return fig


def gastos_por_terco(mes_str):

    global df

    """
    Retorna os gastos de um mês divididos por terço (1º, 2º, 3º).
    mes_str deve ser no formato "Julho/2025", igual ao AnoMesStr da planilha.
    """
    # Filtrar apenas as despesas
    gastos = get_df_gastos_mensais_string(df)

    # Filtrar o mês desejado
    gastos_mes = gastos[gastos["AnoMesStr"] == mes_str].copy()

    if gastos_mes.empty:
        return {"1º terço": 0, "2º terço": 0, "3º terço": 0}

    # Descobrir o último dia do mês
    data_exemplo = gastos_mes.iloc[0]["Data"]
    ultimo_dia = calendar.monthrange(data_exemplo.year, data_exemplo.month)[1]

    # Definir os terços
    terco_1 = gastos_mes[gastos_mes["Data"].dt.day <= 10]
    terco_2 = gastos_mes[(gastos_mes["Data"].dt.day > 10) & (gastos_mes["Data"].dt.day <= 20)]
    terco_3 = gastos_mes[gastos_mes["Data"].dt.day > 20]

    # Somar os valores de cada terço
    return {
        "1º terço": float(terco_1["Valor"].sum() * -1),
        "2º terço": float(terco_2["Valor"].sum() * -1),
        "3º terço": float(terco_3["Valor"].sum() * -1)
    }

#Verifica os meses disponíveis com gastos cadastrados, serve de auxílio a próxima função
def get_meses_disponiveis():
    global df
    gastos = get_df_gastos_mensais_string(df)

    ordem_cronologica = gastos.drop_duplicates("AnoMes").sort_values("AnoMes")
    meses_disponiveis = ordem_cronologica["AnoMesStr"].tolist()

    return meses_disponiveis

#Calcula e exibe todos os gastos de um mês específico selecionado, tendo duas opções de gráfico para visualização
def gerar_grafico_gastos_mes(mes_escolhido: str, tipo: str):
    global df
    gastos = get_df_gastos_mensais_string(df)

    detalhado = gastos[gastos["AnoMesStr"] == mes_escolhido]

    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    if tipo == "barras":
        agrupado = detalhado.groupby("Descrição")["Valor"].sum().abs().sort_values()

        fig.set_size_inches(10, 0.5 * max(len(agrupado), 1))

        bars = ax.barh(agrupado.index, agrupado.values, color="skyblue")
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 5, bar.get_y() + bar.get_height() / 2,
                    f"R$ {width:.2f}", va='center', fontsize=9)

        ax.set_title(f"Gastos por Categoria - {mes_escolhido}")
        ax.set_xlabel("Valor (R$)")
        ax.set_ylabel("Descrição")
        ax.grid(axis='x', linestyle='--', alpha=0.6)

    elif tipo == "linha":
        detalhado["Dia"] = detalhado["Data"].dt.day
        diarios = detalhado.groupby("Data")[["Valor"]].sum().abs()

        fig = Figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        ax.plot(diarios.index, diarios["Valor"], marker="o", color="red", label="Despesas Diárias")

        for data, valor in diarios["Valor"].items():
            descricoes = detalhado[detalhado["Data"] == data]["Descrição"].unique()
            data_formatada = data.strftime("%d/%m")
            texto = f"{data_formatada}\nR$ {valor:.2f}\n" + ", ".join(descricoes[:2])
            ax.text(data, valor + 5, texto, ha='center', fontsize=8)

        ax.set_title(f"Gastos Diários - {mes_escolhido}")
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor (R$)")
        ax.grid(True, linestyle="--", alpha=0.6)

    elif tipo == "valor":
        total_gastos = detalhado["Valor"].sum()
        return total_gastos * -1

    else:

        gastos_tercos = gastos_por_terco(mes_escolhido)

        fig = Figure(figsize=(6, 4))
        ax2 = fig.add_subplot(111)

        labels = list(gastos_tercos.keys())
        valores = list(gastos_tercos.values())

        bars = ax2.bar(labels, valores, color="lightblue")  # usa diretamente as labels no eixo X

        ax2.set_title(f"Valor gasto por Terço do Mês - {mes_escolhido}\n(Períodos de 10 dias)")
        ax2.set_xlabel("Terço")
        ax2.set_ylabel("Valor (R$)")

        for bar, valor in zip(bars, valores):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    f"R$ {valor:.2f}", ha='center', va='bottom', fontsize=9)

        ax2.grid(axis="y", linestyle="--", alpha=0.6)
        fig.tight_layout()


        
    fig.tight_layout()
    return fig

#Encontra os gastos do dia especificado e exibe um gráfico.
def gerar_grafico_gastos_dia(dia_escolhido: str):

    gastos = df[df["Tipo"] == "Despesa"].copy()

    data_formatada = datetime.strptime(dia_escolhido, "%d/%m/%Y").date()

    detalhado = gastos[gastos["Data"].dt.date == data_formatada]

    if detalhado.empty:
        print(f"Nenhum gasto encontrado para o dia {dia_escolhido}")
        return None

    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    agrupado = detalhado.groupby("Descrição")["Valor"].sum().abs().sort_values()

    bars = ax.barh(agrupado.index, agrupado.values, color="skyblue")
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2,
                f"R$ {width:.2f}", va='center', fontsize=9)

    ax.set_title(f"Gastos Detalhados - {dia_escolhido}")
    ax.set_xlabel("Valor (R$)")
    ax.set_ylabel("Descrição")
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    fig.tight_layout()
    return fig

#Verifica quais são as categorias com os maiores valores de gastos acumulados
def gastos_categoria():
    # Filtra despesas e agrupa por descrição
    gastos_cat = df[df["Tipo"] == "Despesa"].groupby("Descrição")["Valor"].sum().abs().nlargest(10).sort_values(ascending=False)

    meses = get_meses_disponiveis()

    fig = Figure(figsize=(8, 6))
    ax = fig.add_subplot(111)

    # Cria gráfico de pizza sem labels diretos
    wedges, texts, autotexts = ax.pie(
        gastos_cat.values,
        labels=None,
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.tab20.colors,
        textprops={'fontsize': 9}
    )

    # Monta a legenda com valores reais
    legend_labels = [f"{cat}: R$ {val:.2f}" for cat, val in zip(gastos_cat.index, gastos_cat.values)]
    ax.legend(wedges, legend_labels, title="Categorias", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)


    ax.set_title(f"Top 10 Gastos por Categoria - {meses[0]} a {meses[-1]}")
    fig.tight_layout()

    return fig



#Calcula em cada mês qual foi o valor gasto e o valor ganho e exibe um gráfico de comparação.
def comparar_ganhos_gastos():
    
    df["AnoMes"] = df["Data"].dt.to_period("M")

    ganhos_mensais = df[df["Tipo"] == "Receita"].groupby("AnoMes")["Valor"].sum()
    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()

    comparativo = pd.concat([ganhos_mensais, gastos_mensais], axis=1)
    comparativo.columns = ["Receita", "Despesa"]
    comparativo = comparativo.fillna(0)

    comparativo.index = comparativo.index.to_timestamp()
    comparativo.index = comparativo.index.strftime("%B/%Y")

    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    ax.plot(comparativo.index, comparativo["Receita"], marker='o', label="Receita", color="green")
    ax.plot(comparativo.index, comparativo["Despesa"], marker='o', label="Despesa", color="red")

    for i, (mes, row) in enumerate(comparativo.iterrows()):
        ax.text(i, row["Receita"] + 5, f"R$ {row['Receita']:.2f}", ha='center', va='bottom', fontsize=8, color="green")
        ax.text(i, row["Despesa"] + 5, f"R$ {row['Despesa']:.2f}", ha='center', va='bottom', fontsize=8, color="red")

    ax.set_title("Comparativo de Receita vs Despesa por Mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Valor (R$)")
    ax.set_xticks(range(len(comparativo.index)))
    ax.set_xticklabels(comparativo.index, rotation=45)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()

    return fig

#Mostra quando foi o valor destinado a poupança por mês
def reserva_por_mes():
    
    reservas = df[df["Tipo"] == "Reserva"].copy()

    reservas["AnoMes"] = reservas["Data"].dt.to_period("M")
    reservas_mensais = reservas.groupby("AnoMes")["Valor"].sum().abs()

    reservas_mensais.index = reservas_mensais.index.to_timestamp()
    reservas_mensais.index = reservas_mensais.index.strftime("%B/%Y")

    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    bars = ax.bar(reservas_mensais.index, reservas_mensais.values, color="green")

    ax.set_title("Valor Reservado (Poupança) por Mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Valor Reservado (R$)")
    ax.set_xticks(range(len(reservas_mensais.index)))
    ax.set_xticklabels(reservas_mensais.index, rotation=45)

    for bar, valor in zip(bars, reservas_mensais.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"R$ {valor:.2f}", ha='center', va='bottom', fontsize=9)

    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()

    return fig


def get_variacao_saldo():
    from datetime import datetime, timedelta
    global df, tema_atual

    data_atual = datetime.today().date()
    semana = data_atual - timedelta(days=7)

    semana_df = df[(df["Data"].dt.date >= semana) & (df["Data"].dt.date <= data_atual)]

    if semana_df.empty:
        print("Nenhum dado encontrado para a semana atual.")
        return 0

    text_data = semana_df["Data"].dt.strftime("%d/%m/%Y").tolist()
    text_valores = semana_df["Valor"].apply(lambda x: f"R$ {x:.2f}").tolist()
    text_descricoes = semana_df["Descrição"].tolist()

    lista_semana = [
        f"Data: {data:<12} Valor: {valor:<12} Descrição: {descricao}"
        for data, valor, descricao in zip(text_data, text_valores, text_descricoes)
    ]

    # Define o tema visual
    fig = Figure(figsize=(10, len(lista_semana) + 1))
    ax = fig.add_subplot(111)
    ax.axis('off')

    if tema_atual.lower() == "dark":
        fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        text_color = "white"
    else:
        fig.patch.set_facecolor("#f3f3f3")
        ax.set_facecolor("#f3f3f3")
        text_color = "black"

    for i, linha in enumerate(lista_semana):
        ax.text(
            0, 1 - (i + 1) / (len(lista_semana) + 1),
            linha,
            fontsize=12,
            fontfamily="monospace",
            va='top',
            color=text_color  # ← texto agora muda de cor com o tema
        )

    fig.tight_layout()
    return fig

def filtrar_gastos_mes(df, mes_str, dia_min, dia_limite):
    """Filtra os gastos de um mês até o dia limite"""
    gastos = get_df_gastos_mensais_string(df)
    return gastos[(gastos["AnoMesStr"] == mes_str) & (gastos["Data"].dt.day >= dia_min) & (gastos["Data"].dt.day <= dia_limite)]

def obter_maiores_gastos(df_gastos, n=5):
    """Retorna os n maiores gastos (valores mais negativos)"""
    return df_gastos.nsmallest(n, "Valor")[["Descrição", "Valor", "Data"]]

def calcular_variacao_gastos(valor_atual, valor_anterior):
    """Calcula a variação percentual entre os gastos"""
    if valor_anterior == 0:
        return 0
    return ((valor_atual - valor_anterior) / abs(valor_anterior)) * 100 * -1

def get_variacao_gastos():
    global df
    hoje = datetime.today()
    dia_atual = hoje.day

    # Strings de mês
    mes_atual_str = hoje.strftime("%B/%Y").capitalize()
    mes_anterior = (hoje.replace(day=1) - timedelta(days=1))
    mes_anterior_str = mes_anterior.strftime("%B/%Y").capitalize()

    # Dados filtrados
    gastos_mes_atual = filtrar_gastos_mes(df, mes_atual_str, 0, dia_atual)
    gastos_mes_anterior = filtrar_gastos_mes(df, mes_anterior_str, 0, dia_atual)
    gastos = df[df["Tipo"] == "Despesa"].copy()
    gastos["AnoMes"] = gastos["Data"].dt.to_period("M")
    mes_anterior_period = pd.Period(mes_anterior.strftime("%Y-%m"))

    completo_mes_anterior = gastos[gastos["AnoMes"] == mes_anterior_period]

    # Totais
    total_mes_atual = gastos_mes_atual["Valor"].sum() * -1
    total_mes_anterior = gastos_mes_anterior["Valor"].sum() * -1
    total_completo_mes_anterior = completo_mes_anterior["Valor"].sum() * -1

    # Variação
    variacao = calcular_variacao_gastos(total_mes_atual, total_mes_anterior)
    diferenca = 1 - (variacao / 100)

    # Maiores gastos
    maiores_atuais = obter_maiores_gastos(gastos_mes_atual)
    maiores_anteriores = obter_maiores_gastos(gastos_mes_anterior)

    maiores_atuais["Data"] = maiores_atuais["Data"].dt.strftime("%d/%m")
    maiores_anteriores["Data"] = maiores_anteriores["Data"].dt.strftime("%d/%m")

    maiores_atuais = maiores_atuais.values.tolist()
    maiores_anteriores = maiores_anteriores.values.tolist()

    return {
        "mes_atual": mes_atual_str,
        "mes_anterior": mes_anterior_str,
        "dia": dia_atual,
        "total_atual": total_mes_atual,
        "total_anterior": total_mes_anterior,
        "variacao": variacao,
        "tendencia": total_completo_mes_anterior * diferenca,
        "maiores_atuais": maiores_atuais,
        "maiores_anteriores": maiores_anteriores
    }

def get_meses_dentro_da_media():
    global df

    df["AnoMes"] = df["Data"].dt.to_period("M")
    df["AnoMesStr"] = df["AnoMes"].dt.to_timestamp().dt.strftime("%B/%Y").str.capitalize()
    df["AnoMes"] = df["AnoMes"].astype(str)

    # Agrupar gastos por mês (exceto o mês atual)
    mes_atual = datetime.today().strftime("%Y-%m")
    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()
    gastos_mensais = gastos_mensais[gastos_mensais.index != mes_atual]

    if gastos_mensais.empty:
        return []

    # Passo 1: Excluir valores abaixo de 50% da média inicial
    media_inicial = gastos_mensais.mean()
    limite_min_exclusao = media_inicial * 0.5
    gastos_sem_valores_muito_baixos = gastos_mensais[gastos_mensais >= limite_min_exclusao]

    # Passo 2: Calcular nova média e limites com os dados filtrados
    nova_media = gastos_sem_valores_muito_baixos.mean()
    limite_inferior = nova_media * 0.70
    limite_superior = nova_media * 1.30

    # Passo 3: Selecionar os meses dentro da nova faixa
    meses_validos = gastos_sem_valores_muito_baixos[
        (gastos_sem_valores_muito_baixos >= limite_inferior) &
        (gastos_sem_valores_muito_baixos <= limite_superior)
    ].index.tolist()

    # Converter para formato legível: "Julho/2025"
    meses_formatados = []
    for mes in meses_validos:
        ano, mes_num = mes.split("-")
        data = datetime(int(ano), int(mes_num), 1)
        nome_formatado = data.strftime("%B/%Y").capitalize()
        meses_formatados.append(nome_formatado)

    return meses_formatados


def get_gastos_terco(opcao):
    global df

    mes_atual = datetime.today().strftime("%B/%Y").capitalize()
    
    meses_disponiveis = get_meses_dentro_da_media()

    meses_disponiveis = [mes for mes in meses_disponiveis if mes != mes_atual]

    terco_1 = []
    terco_2 = []
    terco_3 = []

    for mes in meses_disponiveis:
        gastos_mes = gastos_por_terco(mes)
        terco_1.append(gastos_mes["1º terço"])
        terco_2.append(gastos_mes["2º terço"])
        terco_3.append(gastos_mes["3º terço"])


    total_tercos = (sum(terco_1) , sum(terco_2) , sum(terco_3) )
    index = ("1º Terço", "2º Terço", "3º Terço")

    media_tercos = (sum(terco_1) / len(terco_1), sum(terco_2) / len(terco_2), sum(terco_3) / len(terco_3))

    if opcao == 1:
        return total_tercos, media_tercos
    
    fig = Figure(figsize=(12, 5))
    ax = fig.add_subplot(121)

    bars = ax.bar(index, total_tercos, color="blue")

    ax.set_title("Total gasto por Terços do Mês")
    ax.set_xlabel("Terço")
    ax.set_ylabel("Valor (R$)")
    ax.set_xticks(range(len(index)))
    ax.set_xticklabels(index, rotation=45)

    for bar, valor in zip(bars, total_tercos):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"R$ {valor:.2f}", ha='center', va='bottom', fontsize=9)

    ax.grid(axis="y", linestyle="--", alpha=0.6)

    ax2 = fig.add_subplot(122)

    bars = ax2.bar(index, media_tercos, color="lightblue")

    ax2.set_title("Média de gastos por Terços do Mês")
    ax2.set_xlabel("Terço")
    ax2.set_ylabel("Valor (R$)")
    ax2.set_xticks(range(len(index)))
    ax2.set_xticklabels(index, rotation=45)

    for bar, valor in zip(bars, media_tercos):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"R$ {valor:.2f}", ha='center', va='bottom', fontsize=9)

    ax2.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()

    if opcao == 2:
        return fig
    
def calcular_diferenca(valor1, valor2, percentual):
    return (valor1 - valor2) / valor2 * percentual

def calcular_diferenca_percentual(valor1, valor2, percentual):
    return (valor1 / valor2) * percentual

def calcular_limites(valor, percentual):
    return valor * percentual

def get_valor_medio_ganhos():
    global df

    df["AnoMes"] = df["Data"].dt.to_period("M")
    df["AnoMes"] = df["AnoMes"].astype(str)

    receitas_mensais = df[df["Tipo"] == "Receita"].groupby("AnoMes")["Valor"].sum().abs()
    media_receitas = receitas_mensais.mean()
    limite_inferior_receitas = calcular_limites(media_receitas, 0.70)
    limite_superior_receitas = calcular_limites(media_receitas, 1.30)
    receitas_sem_outliers = receitas_mensais[(receitas_mensais >= limite_inferior_receitas) & (receitas_mensais <= limite_superior_receitas)]
    media_limpa_ganhos = receitas_sem_outliers.mean()

    return media_limpa_ganhos

def get_valor_medio_gastos():
    global df

    df["AnoMes"] = df["Data"].dt.to_period("M")
    mes_atual = datetime.today().strftime("%Y-%m")
    df["AnoMes"] = df["AnoMes"].astype(str)

    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()
    gastos_mensais = gastos_mensais[gastos_mensais.index != mes_atual]

    media_gastos = gastos_mensais.mean()
    limite_inferior = calcular_limites(media_gastos, 0.70)
    limite_superior = calcular_limites(media_gastos, 1.30)
    gastos_sem_outliers = gastos_mensais[(gastos_mensais >= limite_inferior) & (gastos_mensais <= limite_superior)]
    media_limpa_gastos = gastos_sem_outliers.mean()

    return media_limpa_gastos


def get_medias():
    global df
    df["AnoMes"] = df["Data"].dt.to_period("M")

    mes_atual = datetime.today().strftime("%Y-%m")
    df["AnoMes"] = df["AnoMes"].astype(str)

    gastos_mensais = df[df["Tipo"] == "Despesa"].groupby("AnoMes")["Valor"].sum().abs()
    gastos_mensais = gastos_mensais[gastos_mensais.index != mes_atual]

    hoje = datetime.today()
    dia_atual = hoje.day
    mes_atual_str = hoje.strftime("%B/%Y").capitalize()

    gastos_mes_atual = filtrar_gastos_mes(df, mes_atual_str, 0, dia_atual).groupby("AnoMes")["Valor"].sum().abs()
    total_gastos_mes_atual = gastos_mes_atual.values.sum()

    media_limpa_gastos = get_valor_medio_gastos()

    media_limpa_ganhos = get_valor_medio_ganhos()

    ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
    porcentagem_mes = calcular_diferenca_percentual(dia_atual, ultimo_dia, 100)

    diferenca_media_gastos = int(calcular_diferenca_percentual(total_gastos_mes_atual, media_limpa_gastos, 100))

    diferenca_gasto_media_ganhos = calcular_diferenca_percentual(total_gastos_mes_atual, media_limpa_ganhos, 100)

    expectativa_gastos = (total_gastos_mes_atual * 100) / porcentagem_mes
    mes_max, mes_min, valor_max, valor_min = get_mes_max_min_gastos()

    total_tercos, media_tercos = get_gastos_terco(1)
    tercos_mes_atual = gastos_por_terco(mes_atual_str)

    resumo = {
        "gasto_atual": round(total_gastos_mes_atual, 2),
        "media_limpa_gastos": round(media_limpa_gastos, 2),
        "media_limpa_receitas": round(media_limpa_ganhos, 2),
        "porcentagem_mes": round(porcentagem_mes, 2),
        "dia_atual": dia_atual,
        "percentual_gasto_vs_media": diferenca_media_gastos,
        "percentual_gasto_vs_receita": round(diferenca_gasto_media_ganhos, 2),
        "expectativa_fim_mes": round(expectativa_gastos, 2),
        "mes_maior_gasto": mes_max,
        "valor_maior_gasto": round(valor_max, 2),
        "mes_menor_gasto": mes_min,
        "valor_menor_gasto": round(valor_min, 2),
        "atingiu_maior_gasto": valor_max == total_gastos_mes_atual,
        "gasto_tercos": {},
    }

    if dia_atual >= 10 and tercos_mes_atual['1º terço'] > 0:
        percentual = calcular_diferenca(tercos_mes_atual['1º terço'], media_tercos[0], 100)
        resumo["gasto_tercos"]["1º terço"] = {
            "valor": round(tercos_mes_atual['1º terço'], 2),
            "media": round(media_tercos[0], 2),
            "percentual": round(percentual, 2)
        }

    if dia_atual >= 20 and tercos_mes_atual['2º terço'] > 0:
        percentual = calcular_diferenca(tercos_mes_atual['2º terço'], media_tercos[1], 100)
        resumo["gasto_tercos"]["2º terço"] = {
            "valor": round(tercos_mes_atual['2º terço'], 2),
            "media": round(media_tercos[1], 2),
            "percentual": round(percentual, 2)
        }

    if dia_atual >= ultimo_dia - 10 and tercos_mes_atual['3º terço'] > 0:
        percentual = calcular_diferenca(tercos_mes_atual['3º terço'], media_tercos[2], 100)
        resumo["gasto_tercos"]["3º terço"] = {
            "valor": round(tercos_mes_atual['3º terço'], 2),
            "media": round(media_tercos[2], 2),
            "percentual": round(percentual, 2)
        }

    return resumo


    



