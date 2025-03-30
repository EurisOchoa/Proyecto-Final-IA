import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import face_recognition
import os
import numpy as np
from PIL import Image, ImageTk
import dlib
import threading
import time

class InterfazReconocerUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Modelo De Reconocimiento Facial Mejorado")
        self.master.geometry("1200x700")
        self.master.minsize(1000, 600)
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        # Variables de configuración
        self.directorio_usuarios = "usuarios_reconocimiento"
        self.umbral_base = 0.5  # Más estricto para evitar falsos positivos
        self.umbral_gafas = 0.65  # Más estricto para variaciones con gafas
        self.frecuencia_actualizacion = 0.1  # Segundos entre actualizaciones

        # Variables de estado
        self.camara_activa = False
        self.cap = None
        self.frame_actual = None
        self.ultimo_reconocimiento = 0
        self.usuario_actual = None

        # Inicializar modelos
        self.inicializar_modelos()

        # Configurar interfaz
        self.configurar_estilo()
        self.configurar_interfaz()

        # Cargar datos de usuarios
        self.cargar_datos()

    def inicializar_modelos(self):
        """Inicializa los modelos de dlib y face_recognition"""
        self.detector = dlib.get_frontal_face_detector()
        
        # Intentar cargar modelos de dlib
        self.predictor = None
        self.facerec = None
        
        try:
            if os.path.exists("shape_predictor_68_face_landmarks.dat"):
                self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            if os.path.exists("dlib_face_recognition_resnet_model_v1.dat"):
                self.facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar modelos: {str(e)}")

    def configurar_estilo(self):
        """Configura el estilo visual de la interfaz"""
        estilo = ttk.Style()
        estilo.configure('TFrame', background='#f0f0f0')
        estilo.configure('TButton', font=('Arial', 12))
        estilo.configure('TLabel', font=('Arial', 12), background='#f0f0f0')
        estilo.configure('Titulo.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        estilo.configure('Estado.TLabel', font=('Arial', 12, 'italic'), background='#f0f0f0')

    def configurar_interfaz(self):
        """Configura los elementos de la interfaz gráfica"""
        # Panel principal dividido
        self.panel_principal = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel izquierdo (información del usuario)
        self.configurar_panel_izquierdo()

        # Panel derecho (cámara y controles)
        self.configurar_panel_derecho()

    def configurar_panel_izquierdo(self):
        """Configura el panel izquierdo con información del usuario"""
        self.panel_izquierdo = ttk.Frame(self.panel_principal, width=300)
        self.panel_principal.add(self.panel_izquierdo, weight=1)

        # Título
        ttk.Label(
            self.panel_izquierdo, 
            text="Usuario Reconocido", 
            style='Titulo.TLabel'
        ).pack(pady=10)

        # Marco para la imagen del usuario
        self.frame_imagen_usuario = ttk.Frame(
            self.panel_izquierdo, 
            borderwidth=2, 
            relief="groove"
        )
        self.frame_imagen_usuario.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Etiqueta para la imagen
        self.label_imagen = ttk.Label(
            self.frame_imagen_usuario, 
            text="No hay usuario reconocido"
        )
        self.label_imagen.pack(pady=20, padx=20, expand=True)

        # Información del usuario
        self.frame_info_usuario = ttk.Frame(self.panel_izquierdo)
        self.frame_info_usuario.pack(pady=10, padx=10, fill=tk.X)
        
        # Nombre del usuario
        ttk.Label(
            self.frame_info_usuario, 
            text="Nombre:"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.label_nombre = ttk.Label(
            self.frame_info_usuario, 
            text="---"
        )
        self.label_nombre.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Similitud
        ttk.Label(
            self.frame_info_usuario, 
            text="Similitud:"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.label_similitud = ttk.Label(
            self.frame_info_usuario, 
            text="---"
        )
        self.label_similitud.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Lista de usuarios registrados
        ttk.Label(
            self.panel_izquierdo,
            text="Usuarios Registrados:",
            style='Titulo.TLabel'
        ).pack(pady=(20, 5))

        self.lista_usuarios = tk.Listbox(
            self.panel_izquierdo,
            height=8,
            font=('Arial', 10)
        )
        self.lista_usuarios.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Botón para actualizar lista
        ttk.Button(
            self.panel_izquierdo,
            text="Actualizar Lista",
            command=self.actualizar_lista_usuarios
        ).pack(pady=5)

    def configurar_panel_derecho(self):
        """Configura el panel derecho con la cámara y controles"""
        self.panel_derecho = ttk.Frame(self.panel_principal)
        self.panel_principal.add(self.panel_derecho, weight=3)

        # Panel superior para los controles
        panel_controles = ttk.Frame(self.panel_derecho)
        panel_controles.pack(pady=10, fill=tk.X)

        # Estado
        self.label_estado = ttk.Label(
            panel_controles, 
            text="Estado: Esperando para iniciar...", 
            style='Estado.TLabel'
        )
        self.label_estado.pack(side=tk.LEFT, padx=10)

        # Botones
        self.boton_iniciar = ttk.Button(
            panel_controles, 
            text="Iniciar Reconocimiento", 
            command=self.iniciar_reconocimiento
        )
        self.boton_iniciar.pack(side=tk.RIGHT, padx=5)
        
        self.boton_detener = ttk.Button(
            panel_controles, 
            text="Detener", 
            command=self.detener_reconocimiento, 
            state=tk.DISABLED
        )
        self.boton_detener.pack(side=tk.RIGHT, padx=5)
        
        self.boton_configurar = ttk.Button(
            panel_controles,
            text="Configuración",
            command=self.mostrar_configuracion
        )
        self.boton_configurar.pack(side=tk.RIGHT, padx=5)

        # Panel para la cámara
        self.panel_camara = ttk.Frame(
            self.panel_derecho, 
            borderwidth=2, 
            relief="groove"
        )
        self.panel_camara.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Etiqueta para mostrar la cámara
        self.label_camara = ttk.Label(
            self.panel_camara, 
            text="La cámara se mostrará aquí"
        )
        self.label_camara.pack(pady=40, expand=True)

    def mostrar_configuracion(self):
        """Muestra una ventana de configuración"""
        config_window = tk.Toplevel(self.master)
        config_window.title("Configuración")
        config_window.geometry("400x300")
        
        ttk.Label(config_window, text="Umbral de reconocimiento base (0.1-1.0):").pack(pady=5)
        self.entry_umbral_base = ttk.Entry(config_window)
        self.entry_umbral_base.insert(0, str(self.umbral_base))
        self.entry_umbral_base.pack(pady=5)
        
        ttk.Label(config_window, text="Umbral para gafas (0.1-1.0):").pack(pady=5)
        self.entry_umbral_gafas = ttk.Entry(config_window)
        self.entry_umbral_gafas.insert(0, str(self.umbral_gafas))
        self.entry_umbral_gafas.pack(pady=5)
        
        ttk.Label(config_window, text="Frecuencia de actualización (segundos):").pack(pady=5)
        self.entry_frecuencia = ttk.Entry(config_window)
        self.entry_frecuencia.insert(0, str(self.frecuencia_actualizacion))
        self.entry_frecuencia.pack(pady=5)
        
        ttk.Button(
            config_window,
            text="Guardar",
            command=self.guardar_configuracion
        ).pack(pady=10)

    def guardar_configuracion(self):
        """Guarda la configuración modificada"""
        try:
            nuevo_umbral_base = float(self.entry_umbral_base.get())
            nuevo_umbral_gafas = float(self.entry_umbral_gafas.get())
            nueva_frecuencia = float(self.entry_frecuencia.get())
            
            if 0.1 <= nuevo_umbral_base <= 1.0 and 0.1 <= nuevo_umbral_gafas <= 1.0 and nueva_frecuencia > 0:
                self.umbral_base = nuevo_umbral_base
                self.umbral_gafas = nuevo_umbral_gafas
                self.frecuencia_actualizacion = nueva_frecuencia
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            else:
                messagebox.showerror("Error", "Los valores deben estar entre 0.1 y 1.0 para los umbrales")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")

    def cargar_datos(self):
        """Carga imágenes y genera codificaciones faciales"""
        self.usuarios = []
        self.encodings = []
        self.imagenes = {}
        self.nombres_base = set()

        if not os.path.exists(self.directorio_usuarios):
            os.makedirs(self.directorio_usuarios)
            self.label_estado.config(text="Estado: No hay usuarios registrados.")
            return

        for archivo in os.listdir(self.directorio_usuarios):
            if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                ruta = os.path.join(self.directorio_usuarios, archivo)
                try:
                    imagen = face_recognition.load_image_file(ruta)
                    face_locations = face_recognition.face_locations(imagen)
                    
                    if len(face_locations) == 0:
                        print(f"No se detectaron rostros en {archivo}, ignorando...")
                        continue

                    face_encodings = face_recognition.face_encodings(imagen, face_locations)
                    
                    for encoding in face_encodings:
                        self.encodings.append(encoding)
                        nombre_base = os.path.splitext(archivo)[0]
                        self.nombres_base.add(nombre_base)
                        self.usuarios.append(nombre_base)
                        self.imagenes[nombre_base] = ruta
                        
                except Exception as e:
                    print(f"Error al procesar {archivo}: {str(e)}")

        self.actualizar_lista_usuarios()
        
        if self.usuarios:
            self.label_estado.config(text=f"Estado: Datos cargados para {len(self.nombres_base)} usuarios.")
        else:
            self.label_estado.config(text="Estado: No hay usuarios registrados para reconocer.")

    def actualizar_lista_usuarios(self):
        """Actualiza la lista de usuarios registrados"""
        self.lista_usuarios.delete(0, tk.END)
        for nombre in sorted(self.nombres_base):
            self.lista_usuarios.insert(tk.END, nombre.replace("_", " "))

    def iniciar_reconocimiento(self):
        """Inicia el proceso de reconocimiento facial"""
        if self.camara_activa:
            return
            
        # Verificar si hay usuarios registrados
        if not self.usuarios:
            messagebox.showwarning("Advertencia", "No hay usuarios registrados para reconocer.")
            return

        # Inicializar la cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        # Configurar interfaz
        self.boton_iniciar.config(state=tk.DISABLED)
        self.boton_detener.config(state=tk.NORMAL)
        self.label_estado.config(text="Estado: Reconocimiento en progreso...")
        
        # Iniciar thread para manejar la cámara
        self.camara_activa = True
        self.thread_camara = threading.Thread(target=self.procesar_video, daemon=True)
        self.thread_camara.start()

    def detener_reconocimiento(self):
        """Detiene el proceso de reconocimiento facial"""
        self.camara_activa = False
        
        # Esperar a que termine el hilo de la cámara
        if hasattr(self, 'thread_camara') and self.thread_camara.is_alive():
            self.thread_camara.join(timeout=2.0)
            
        # Liberar la cámara
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        # Restaurar interfaz
        self.boton_iniciar.config(state=tk.NORMAL)
        self.boton_detener.config(state=tk.DISABLED)
        self.label_estado.config(text="Estado: Reconocimiento detenido.")
        self.label_camara.config(text="La cámara se mostrará aquí", image='')

    def procesar_video(self):
        """Procesa el video de la cámara en un hilo separado"""
        while self.camara_activa and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                self.label_estado.config(text="Estado: Error al capturar imagen.")
                self.camara_activa = False
                break
                
            # Hacer una copia del frame para mostrar
            self.frame_actual = frame.copy()
            
            # Realizar reconocimiento solo si ha pasado el tiempo de espera
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_reconocimiento >= self.frecuencia_actualizacion:
                self.reconocer_rostro(frame)
                self.ultimo_reconocimiento = tiempo_actual
                
            # Mostrar frame en la interfaz
            self.mostrar_frame(frame)
            
            # Dar tiempo al sistema para actualizar
            self.master.update_idletasks()

    def mostrar_frame(self, frame):
        """Muestra el frame de la cámara en la interfaz"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Redimensionar manteniendo proporción
        ancho_panel = self.panel_camara.winfo_width()
        alto_panel = self.panel_camara.winfo_height()
        
        if ancho_panel > 1 and alto_panel > 1:
            proporcion = min(ancho_panel / img.width, alto_panel / img.height)
            nuevo_ancho = int(img.width * proporcion)
            nuevo_alto = int(img.height * proporcion)
            img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(img)
        self.label_camara.config(image=img_tk)
        self.label_camara.image = img_tk

    def reconocer_rostro(self, frame):
        """Realiza el reconocimiento facial en un frame con mejor manejo de desconocidos"""
        # Reducir tamaño para mejorar rendimiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detectar rostros
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if not face_locations:
            self.label_estado.config(text="Estado: No se detectaron rostros.")
            if self.usuario_actual:
                self.mostrar_usuario_reconocido("Desconocido", 0)
                self.usuario_actual = "Desconocido"
            return

        # Calcular encodings
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for i, face_encoding in enumerate(face_encodings):
            # Comparar con encodings existentes
            face_distances = face_recognition.face_distance(self.encodings, face_encoding)
            
            # Encontrar la mejor coincidencia
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            # Determinar si es una coincidencia válida
            name = "Desconocido"
            similitud = 0
            
            if best_distance <= self.umbral_base:
                name = self.usuarios[best_match_index]
                similitud = (1 - best_distance) * 100
                
                # Solo actualizar si es un nuevo usuario o mayor similitud
                if (self.usuario_actual != name or 
                    (self.usuario_actual == name and similitud > float(self.label_similitud.cget("text").replace("%", "")))):
                    self.mostrar_usuario_reconocido(name, similitud)
                    self.usuario_actual = name
            else:
                # Persona claramente desconocida
                if self.usuario_actual != "Desconocido":
                    self.mostrar_usuario_reconocido("Desconocido", 0)
                    self.usuario_actual = "Desconocido"

            # Escalar coordenadas para el frame original
            top, right, bottom, left = face_locations[i]
            top *= 2; right *= 2; bottom *= 2; left *= 2
            
            # Dibujar recuadro y texto con color diferente para desconocidos
            color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)  # Verde para conocidos, Rojo para desconocidos
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, 
                f"{name.split('_')[0]} ({similitud:.1f}%)", 
                (left, top - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.9, 
                color, 
                2
            )

    def mostrar_usuario_reconocido(self, nombre, similitud):
        """Muestra la información del usuario reconocido"""
        nombre_base = nombre.split('_')[0] if nombre and nombre != "Desconocido" else "Desconocido"
        
        self.label_nombre.config(text=nombre_base)
        self.label_similitud.config(text=f"{similitud:.1f}%" if nombre and nombre != "Desconocido" else "---")
        
        if nombre and nombre != "Desconocido" and nombre in self.imagenes:
            try:
                img = Image.open(self.imagenes[nombre])
                
                # Ajustar tamaño al frame
                ancho_frame = self.frame_imagen_usuario.winfo_width()
                alto_frame = self.frame_imagen_usuario.winfo_height()
                
                if ancho_frame > 1 and alto_frame > 1:
                    proporcion = min(ancho_frame / img.width, alto_frame / img.height)
                    nuevo_ancho = int(img.width * proporcion * 0.9)
                    nuevo_alto = int(img.height * proporcion * 0.9)
                    img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
                
                img_tk = ImageTk.PhotoImage(img)
                self.label_imagen.config(image=img_tk, text="")
                self.label_imagen.image = img_tk
            except Exception as e:
                print(f"Error al cargar imagen: {str(e)}")
                self.label_imagen.config(text="Error al cargar imagen", image="")
        else:
            self.label_imagen.config(
                text="Usuario desconocido" if nombre == "Desconocido" else "No hay usuario reconocido", 
                image=""
            )

    def cerrar_ventana(self):
        """Cierra la ventana de manera segura"""
        self.detener_reconocimiento()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReconocerUsuario(root)
    root.mainloop()
