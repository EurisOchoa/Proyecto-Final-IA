import tkinter as tk
from tkinter import messagebox

class InterfazReconocimientoFacial:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Reconocimiento Facial")
        self.master.geometry("400x300")
        
        # Título del sistema
        label_titulo = tk.Label(master, text="Sistema de Reconocimiento Facial", font=("Arial", 16))
        label_titulo.pack(pady=20)
        
        # Botón para agregar nuevo usuario
        boton_agregar = tk.Button(master, text="Agregar Nuevo Usuario", font=("Arial", 12), command=self.agregar_usuario)
        boton_agregar.pack(pady=10)
        
        # Botón para iniciar reconocimiento facial
        boton_reconocer = tk.Button(master, text="Iniciar Reconocimiento Facial", font=("Arial", 12), command=self.reconocer_usuario)
        boton_reconocer.pack(pady=10)
        
        # Botón para salir
        boton_salir = tk.Button(master, text="Salir", font=("Arial", 12), command=self.salir)
        boton_salir.pack(pady=10)
    
    def agregar_usuario(self):
        messagebox.showinfo("Agregar Usuario", "Función para agregar usuario aún no implementada.")

    def reconocer_usuario(self):
        messagebox.showinfo("Reconocer Usuario", "Función para reconocer usuario aún no implementada.")

    def salir(self):
        respuesta = messagebox.askyesno("Salir", "¿Está seguro de que desea salir?")
        if respuesta:
            self.master.quit()

# Ejecutar la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReconocimientoFacial(root)
    root.mainloop()
