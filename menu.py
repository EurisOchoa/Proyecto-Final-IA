import tkinter as tk
from tkinter import messagebox
import os  # Importamos el módulo os para ejecutar scripts externos

class InterfazReconocimientoFacial:
    def __init__(self, master):
        self.master = master
        self.master.title("Modelo De Reconocimiento Facial")
        self.master.geometry("600x400")  # Dimensiones iniciales
        self.master.configure(bg="#6A5ACD")  # Fondo púrpura elegante

        # Título del sistema
        label_titulo = tk.Label(
            master,
            text="Modelo De Reconocimiento Facial",
            font=("Wide Latin", 14),
            bg="#6A5ACD",
            fg="white"
        )
        label_titulo.pack(pady=20)  # Centrado

        # Contenedor para los botones
        frame_botones = tk.Frame(master, bg="#6A5ACD")
        frame_botones.pack(expand=True, fill="both")  # Se adapta al tamaño de la ventana

        # Dimensiones estándar para los botones
        button_width = 25
        button_height = 2

        # Botón para agregar nuevo usuario
        boton_agregar = tk.Button(
            frame_botones,
            text="Agregar Nuevo Usuario",
            font=("Arial", 14),
            bg="#800080",
            fg="white",
            width=button_width,
            height=button_height,
            command=self.agregar_usuario
        )
        boton_agregar.pack(pady=5, anchor="center")
        
        # Botón para iniciar reconocimiento facial
        boton_reconocer = tk.Button(
            frame_botones,
            text="Iniciar Reconocimiento Facial",
            font=("Arial", 14),
            bg="#800080",
            fg="white",
            width=button_width,
            height=button_height,
            command=self.reconocer_usuario
        )
        boton_reconocer.pack(pady=5, anchor="center")
        
        # Botón para salir
        boton_salir = tk.Button(
            frame_botones,
            text="Salir",
            font=("Arial", 14),
            bg="#800080",
            fg="white",
            width=button_width,
            height=button_height,
            command=self.salir
        )
        boton_salir.pack(pady=5, anchor="center")

    def agregar_usuario(self):
        try:
            os.system("python formulario.py")  # Ejecuta el archivo formulario.py
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir formulario.py: {str(e)}")

    def reconocer_usuario(self):
        try:
            os.system("python main.py")  # Ejecuta el archivo main.py
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir main.py: {str(e)}")

    def salir(self):
        respuesta = messagebox.askyesno("Salir", "¿Está seguro de que desea salir?")
        if respuesta:
            self.master.quit()

# Ejecutar la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReconocimientoFacial(root)
    root.mainloop()

