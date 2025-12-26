import os
import json
import customtkinter as ctk
from tkinter import filedialog
from customtkinter import CTk

from financeiro import ler_planilha

CONFIG_FILE = "config.json"


def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def atualizar_interface(aviso_label, caminho_label, btn_iniciar):
    caminho = config.get("planilha_path")
    if caminho and os.path.exists(caminho):
        caminho_label.configure(text=f"Planilha selecionada:\n{caminho}")
        aviso_label.configure(text="")
        btn_iniciar.configure(state="normal")
    else:
        caminho_label.configure(text="⚠️ Nenhuma planilha selecionada.")
        aviso_label.configure(text="Selecione uma planilha para iniciar as análises")
        btn_iniciar.configure(state="disabled")

def selecionar_planilha(aviso_label, caminho_label, btn_iniciar):
    caminho = filedialog.askopenfilename(
        title="Selecione a planilha de dados",
        filetypes=[("Planilhas Excel", "*.xlsx *.xls")]
    )
    if caminho:
        config["planilha_path"] = caminho
        salvar_config(config)
    atualizar_interface(aviso_label, caminho_label, btn_iniciar)

def iniciar_sistema(app, aviso_label):
    caminho = config.get("planilha_path")
    if caminho and os.path.exists(caminho):
        app.destroy()
        tema_atual = config.get("tema", "Dark")
        ler_planilha(caminho, tema_atual)
        import interface
    else:
        aviso_label.configure(text="❌ Selecione uma planilha antes de iniciar.", text_color="red")

def mudar_tema(choice):

    if choice == "Claro":
        choice = "Light"
    elif choice == "Escuro":
        choice = "Dark"

    ctk.set_appearance_mode(choice)
    config["tema"] = choice
    salvar_config(config)

def mudar_cor(choice):

    if choice == "azul":
        choice = "blue"
    elif choice == "verde":
        choice = "green"
    elif choice == "azul-escuro":
        choice = "dark-blue"

    ctk.set_default_color_theme(choice)
    config["cor"] = choice
    salvar_config(config)


config = carregar_config()

tema_padrao = config.get("tema", "Escuro")
cor_padrao = config.get("cor", "azul-escuro")

ctk.set_appearance_mode(tema_padrao)
ctk.set_default_color_theme(cor_padrao)

app = CTk()
app.geometry("700x450")
app.title("Análise Financeira - Inicial")

label_titulo = ctk.CTkLabel(app, text="Bem-vindo ao Software de Análise Financeira", font=("Arial", 20))
label_titulo.pack(pady=(10,20))

caminho_label = ctk.CTkLabel(app, text="", font=("Arial", 13), wraplength=600, justify="center")
caminho_label.pack(pady=(10,0))

aviso_label = ctk.CTkLabel(app, text="", font=("Arial", 13))
aviso_label.pack(pady=5)

btn_planilha = ctk.CTkButton(app, text="Selecionar planilha", command=lambda: selecionar_planilha(aviso_label, caminho_label, btn_iniciar))
btn_planilha.pack(pady=10)

btn_iniciar = ctk.CTkButton(app, text="Iniciar sistema", command=lambda: iniciar_sistema(app, aviso_label), state="disabled", width=200)
btn_iniciar.pack(pady=15)

label_titulo = ctk.CTkLabel(app, text="Configurações do sistema:", font=("Arial", 12))
label_titulo.pack(pady=(20,0))

frame_seletores = ctk.CTkFrame(app, fg_color="transparent")
frame_seletores.pack(pady=15)

label_tema = ctk.CTkLabel(frame_seletores, text="Tema:", font=("Arial", 13))
label_tema.grid(row=0, column=0, padx=10)

tema_menu = ctk.CTkOptionMenu(frame_seletores, values=["Claro", "Escuro"], command=mudar_tema)
tema_menu.set(tema_padrao)
tema_menu.grid(row=0, column=1, padx=10)

label_cor = ctk.CTkLabel(frame_seletores, text="Cor:", font=("Arial", 13))
label_cor.grid(row=0, column=2, padx=10)

cor_menu = ctk.CTkOptionMenu(frame_seletores, values=["azul", "verde", "azul-escuro"], command=mudar_cor)
cor_menu.set(cor_padrao)
cor_menu.grid(row=0, column=3, padx=10)

atualizar_interface(aviso_label, caminho_label, btn_iniciar)

app.mainloop()
