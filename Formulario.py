import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
import os
import time
from transformers import pipeline

class InterfazAgregarUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Agregar Nuevo Usuario")
        self.master.geometry("900x550")
        self.master.configure(bg="#6A5ACD")
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background="#6A5ACD")
        self.style.configure('TLabel', background="#6A5ACD", foreground="white", font=("Arial", 12))
        
        # Configurar estilo de botones con texto negro
        self.style.configure('TButton', 
                           font=("Arial", 12, "bold"), 
                           background="#800080", 
                           foreground="black",
                           padding=5)
        self.style.map('TButton', 
                      background=[('active', '#9C009C')],
                      foreground=[('active', 'black')])

        # Frame principal
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título del sistema
        label_titulo = ttk.Label(
            self.main_frame,
            text="Agregar Nuevo Usuario",
            font=("Wide Latin", 14),
            style='TLabel'
        )
        label_titulo.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame para campos de entrada
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Campos de entrada para nombre y apellido
        ttk.Label(input_frame, text="Nombre:", style='TLabel').grid(row=0, column=0, pady=5, sticky="w")
        self.entry_nombre = ttk.Entry(input_frame, font=("Arial", 14))
        self.entry_nombre.grid(row=1, column=0, pady=5, ipady=5)

        ttk.Label(input_frame, text="Apellido:", style='TLabel').grid(row=2, column=0, pady=5, sticky="w")
        self.entry_apellido = ttk.Entry(input_frame, font=("Arial", 14))
        self.entry_apellido.grid(row=3, column=0, pady=5, ipady=5)

        # Frame para botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, pady=20)

        # Botón para previsualizar cámara
        boton_preview = ttk.Button(
            button_frame,
            text="Previsualizar Cámara",
            command=self.preview_camara,
            style='TButton'
        )
        boton_preview.grid(row=0, column=0, padx=5, pady=5, ipadx=10, ipady=5)

        # Botón para tomar foto
        boton_foto = ttk.Button(
            button_frame,
            text="Capturar Foto",
            command=self.mostrar_camara,
            style='TButton'
        )
        boton_foto.grid(row=0, column=1, padx=5, pady=5, ipadx=10, ipady=5)

        # Botón para analizar texto
        boton_analizar = ttk.Button(
            button_frame,
            text="Analizar Sentimiento",
            command=self.analizar_sentimiento,
            style='TButton'
        )
        boton_analizar.grid(row=1, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

        # Botón para regresar
        boton_regresar = ttk.Button(
            button_frame,
            text="Regresar al Menú Principal",
            command=self.regresar_menu,
            style='TButton'
        )
        boton_regresar.grid(row=2, column=0, columnspan=2, pady=5, ipadx=10, ipady=5)

        # Frame para mostrar la imagen
        self.image_frame = ttk.Frame(self.main_frame)
        self.image_frame.grid(row=1, column=1, rowspan=2, padx=10, pady=10)

        # Espacio para mostrar la imagen capturada
        self.label_imagen = ttk.Label(self.image_frame, background="gray")
        self.label_imagen.pack(pady=10)

        # Tooltip
        self.tooltip = ttk.Label(master, background="lightyellow", padding=5, foreground="black")
        
        # Configurar eventos para tooltips
        boton_preview.bind("<Enter>", lambda e: self.mostrar_tooltip("Previsualiza la cámara sin capturar"))
        boton_preview.bind("<Leave>", lambda e: self.tooltip.place_forget())
        boton_foto.bind("<Enter>", lambda e: self.mostrar_tooltip("Captura una foto con la cámara"))
        boton_foto.bind("<Leave>", lambda e: self.tooltip.place_forget())

    def mostrar_tooltip(self, mensaje):
        self.tooltip.config(text=mensaje)
        self.tooltip.place(x=self.master.winfo_pointerx()+10, y=self.master.winfo_pointery()+10)

    def validar_nombre_apellido(self, texto):
        """Valida que el texto solo contenga letras y espacios"""
        return all(c.isalpha() or c.isspace() for c in texto)

    def preview_camara(self):
        """Muestra una previsualización de la cámara sin capturar"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("No se pudo acceder a la cámara.")
            
            preview_window = tk.Toplevel(self.master)
            preview_window.title("Previsualización de Cámara")
            
            label = ttk.Label(preview_window)
            label.pack()
            
            def update_frame():
                ret, frame = cap.read()
                if ret:
                    # Convertir de BGR a RGB para mostrar correctamente los colores
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    label.imgtk = imgtk
                    label.configure(image=imgtk)
                label.after(10, update_frame)
            
            update_frame()
            
            def on_close():
                cap.release()
                preview_window.destroy()
            
            preview_window.protocol("WM_DELETE_WINDOW", on_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def mostrar_camara(self):
        """Muestra la cámara y permite capturar una foto"""
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        
        if not nombre or not apellido:
            messagebox.showerror("Error", "Debe ingresar el nombre y apellido.")
            return
            
        if not self.validar_nombre_apellido(nombre) or not self.validar_nombre_apellido(apellido):
            messagebox.showerror("Error", "Nombre y apellido solo deben contener letras.")
            return

        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("No se pudo acceder a la cámara.")
            
            time.sleep(2)  # Dar tiempo para que la cámara se estabilice
            
            capture_window = tk.Toplevel(self.master)
            capture_window.title("Capturar Foto")
            
            label = ttk.Label(capture_window)
            label.pack()
            
            def update_frame():
                ret, frame = cap.read()
                if ret:
                    # Dibujar un recuadro guía para el rostro
                    height, width = frame.shape[:2]
                    x1, y1, x2, y2 = int(width * 0.3), int(height * 0.2), int(width * 0.7), int(height * 0.8)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Convertir de BGR a RGB para mostrar correctamente los colores
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    label.imgtk = imgtk
                    label.configure(image=imgtk)
                
                label.after(10, update_frame)
            
            update_frame()
            
            def capturar():
                ret, frame = cap.read()
                if ret:
                    height, width = frame.shape[:2]
                    x1, y1, x2, y2 = int(width * 0.3), int(height * 0.2), int(width * 0.7), int(height * 0.8)
                    roi = frame[y1:y2, x1:x2]
                    
                    # Convertir la región de interés a RGB antes de guardar
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    self.guardar_imagen(roi_rgb, nombre, apellido)
                    capture_window.destroy()
            
            btn_capture = ttk.Button(capture_window, text="Capturar", command=capturar, style='TButton')
            btn_capture.pack(pady=10)
            
            def on_close():
                cap.release()
                capture_window.destroy()
            
            capture_window.protocol("WM_DELETE_WINDOW", on_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            if 'cap' in locals():
                cap.release()

    def guardar_imagen(self, imagen, nombre, apellido):
        """Guarda la imagen capturada y la muestra en la interfaz"""
        try:
            directorio_usuarios = "usuarios_reconocimiento"
            os.makedirs(directorio_usuarios, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre}_{apellido}_{timestamp}.jpg".replace(" ", "_").lower()
            ruta_imagen = os.path.join(directorio_usuarios, nombre_archivo)
            
            # La imagen ya está en formato RGB, solo guardar
            cv2.imwrite(ruta_imagen, imagen)
            
            self.mostrar_imagen(ruta_imagen)
            messagebox.showinfo("Éxito", "Imagen guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")

    def mostrar_imagen(self, ruta_imagen):
        """Muestra la imagen capturada en el recuadro designado"""
        try:
            imagen = Image.open(ruta_imagen)
            # Mantener relación de aspecto
            width, height = imagen.size
            new_height = 200
            new_width = int((new_height / height) * width)
            imagen = imagen.resize((new_width, new_height), Image.LANCZOS)
            
            imagen_tk = ImageTk.PhotoImage(imagen)
            self.label_imagen.config(image=imagen_tk)
            self.label_imagen.image = imagen_tk
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la imagen: {str(e)}")

    def analizar_sentimiento(self):
        """Analiza el sentimiento del nombre y apellido ingresados"""
        try:
            if not hasattr(self, 'analizador'):
                self.analizador = pipeline("sentiment-analysis", device=-1)
            
            texto = f"{self.entry_nombre.get()} {self.entry_apellido.get()}"
            if len(texto.strip()) < 3:
                messagebox.showwarning("Advertencia", "El texto es demasiado corto para análisis.")
                return
                
            resultado = self.analizador(texto)
            
            sentimiento = resultado[0]['label']
            probabilidad = resultado[0]['score'] * 100
            
            # Traducir sentimientos al español si es necesario
            if sentimiento == "POSITIVE":
                sentimiento = "POSITIVO"
            elif sentimiento == "NEGATIVE":
                sentimiento = "NEGATIVO"
            
            mensaje = (
                f"Análisis de sentimiento para:\n"
                f"\"{texto}\"\n\n"
                f"Resultado: {sentimiento}\n"
                f"Confianza: {probabilidad:.1f}%"
            )
            messagebox.showinfo("Análisis de Sentimiento", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo analizar el sentimiento: {str(e)}")

    def regresar_menu(self):
        """Cierra la ventana actual"""
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAgregarUsuario(root)
    root.mainloop()
