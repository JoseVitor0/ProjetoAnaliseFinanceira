import customtkinter as ctk


class AvisoTemporario:
    def __init__(self, master):
        self.label = ctk.CTkLabel(
            master,
            text="",
            text_color="black",
            fg_color="transparent",
            corner_radius=8,
            padx=10,
            pady=10
        )
        self.label.pack(pady=5)
        self._after_id = None
        self.master = master

    def mostrar(self, mensagem: str, tipo: str = "aviso"):
        # Cancela mensagem anterior, se ainda estiver ativa
        if self._after_id:
            self.master.after_cancel(self._after_id)

        # Estilo baseado no tipo
        if tipo == "erro":
            self.label.configure(text=mensagem, fg_color="#ff6666", text_color="white")
        elif tipo == "aviso":
            self.label.configure(text=mensagem, fg_color="#fff176", text_color="black")
        else:
            self.label.configure(text=mensagem, fg_color="transparent")

        # Esconde automaticamente após 4 segundos
        self._after_id = self.master.after(4000, self.esconder)

    def esconder(self):
        self.label.configure(text="", fg_color="transparent")
        self._after_id = None