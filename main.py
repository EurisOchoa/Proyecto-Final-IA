import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import face_recognition
import os
import numpy as np
from PIL import Image, ImageTk
import dlib
import threading

class InterfazReconocerUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Reconocimiento Facial")
        self.master.geometry("1200x700")  # Ventana más grande para la nueva interfaz
        self.master.minsize(1000, 600)    # Tamaño mínimo para que la interfaz sea usable

        # Configuración de estilo
        self.configurar_estilo()

        # Dividir la ventana en dos marcos principales
        self.panel_principal = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel izquierdo (barra lateral)
        self.panel_izquierdo = ttk.Frame(self.panel_principal, width=300)
        self.panel_principal.add(self.panel_izquierdo, weight=1)

        # Panel derecho (cámara y controles)
        self.panel_derecho = ttk.Frame(self.panel_principal)
        self.panel_principal.add(self.panel_derecho, weight=3)

        # Configurar el panel izquierdo (barra lateral)
        self.configurar_panel_izquierdo()

        # Configurar el panel derecho (cámara y controles)
        self.configurar_panel_derecho()

        # Variables para el reconocimiento facial
        self.directorio_usuarios = "usuarios_reconocimiento"
        self.usuarios = []
        self.encodings = []
        self.imagenes = {}

        # Para la cámara
        self.camara_activa = False
        self.cap = None
        self.frame_actual = None

        # Inicializar dlib
        self.inicializar_dlib()

        # Cargar datos de usuarios
        self.cargar_datos()

    def configurar_estilo(self):
        """Configura el estilo visual de la interfaz"""
        estilo = ttk.Style()
        estilo.configure('TFrame', background='#f0f0f0')
        estilo.configure('TButton', font=('Arial', 12))
        estilo.configure('TLabel', font=('Arial', 12), background='#f0f0f0')
        estilo.configure('Titulo.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        estilo.configure('Estado.TLabel', font=('Arial', 12, 'italic'), background='#f0f0f0')

    def configurar_panel_izquierdo(self):
        """Configura el panel izquierdo (barra lateral)"""
        # Título del panel
        ttk.Label(self.panel_izquierdo, text="Usuario Reconocido", style='Titulo.TLabel').pack(pady=10)

        # Marco para la imagen del usuario
        self.frame_imagen_usuario = ttk.Frame(self.panel_izquierdo, borderwidth=2, relief="groove")
        self.frame_imagen_usuario.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Etiqueta para la imagen
        self.label_imagen = ttk.Label(self.frame_imagen_usuario, text="No hay usuario reconocido")
        self.label_imagen.pack(pady=20, padx=20, expand=True)

        # Información del usuario
        self.frame_info_usuario = ttk.Frame(self.panel_izquierdo)
        self.frame_info_usuario.pack(pady=10, padx=10, fill=tk.X)
        
        # Nombre del usuario
        ttk.Label(self.frame_info_usuario, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.label_nombre = ttk.Label(self.frame_info_usuario, text="---")
        self.label_nombre.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Similitud
        ttk.Label(self.frame_info_usuario, text="Similitud:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.label_similitud = ttk.Label(self.frame_info_usuario, text="---")
        self.label_similitud.grid(row=1, column=1, sticky=tk.W, pady=5)

    def configurar_panel_derecho(self):
        """Configura el panel derecho (cámara y controles)"""
        # Panel superior para los controles
        panel_controles = ttk.Frame(self.panel_derecho)
        panel_controles.pack(pady=10, fill=tk.X)

        # Estado
        self.label_estado = ttk.Label(panel_controles, text="Estado: Esperando para iniciar...", style='Estado.TLabel')
        self.label_estado.pack(side=tk.LEFT, padx=10)

        # Botones
        self.boton_iniciar = ttk.Button(panel_controles, text="Iniciar Reconocimiento Facial", command=self.iniciar_reconocimiento)
        self.boton_iniciar.pack(side=tk.RIGHT, padx=10)
        
        self.boton_detener = ttk.Button(panel_controles, text="Detener", command=self.detener_reconocimiento, state=tk.DISABLED)
        self.boton_detener.pack(side=tk.RIGHT, padx=10)
        
        self.boton_regresar = ttk.Button(panel_controles, text="Regresar al Menú Principal", command=self.regresar_menu)
        self.boton_regresar.pack(side=tk.RIGHT, padx=10)

        # Panel para la cámara
        self.panel_camara = ttk.Frame(self.panel_derecho, borderwidth=2, relief="groove")
        self.panel_camara.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Etiqueta para mostrar la cámara
        self.label_camara = ttk.Label(self.panel_camara, text="La cámara se mostrará aquí")
        self.label_camara.pack(pady=40, expand=True)

    def inicializar_dlib(self):
        """Inicializa los modelos de dlib"""
        # Inicializar variables por defecto
        self.predictor = None
        self.facerec = None
        self.detector = dlib.get_frontal_face_detector()
        
        # Verificar si existen los archivos de modelo
        modelos_faltan = []
        
        if os.path.exists("shape_predictor_68_face_landmarks.dat"):
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        else:
            modelos_faltan.append("shape_predictor_68_face_landmarks.dat")
            
        if os.path.exists("dlib_face_recognition_resnet_model_v1.dat"):
            self.facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
        else:
            modelos_faltan.append("dlib_face_recognition_resnet_model_v1.dat")
        
        if modelos_faltan:
            mensaje = "No se encontraron los siguientes archivos de modelo:\n"
            mensaje += "\n".join(modelos_faltan)
            mensaje += "\n\nPor favor, descárgalos desde GitHub:\n"
            mensaje += "- shape_predictor: https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2\n"
            mensaje += "- face_recognition: https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2"
            messagebox.showerror("Error: Modelos faltantes", mensaje)

    def cargar_datos(self):
        """Carga imágenes y genera codificaciones faciales"""
        if not os.path.exists(self.directorio_usuarios):
            os.makedirs(self.directorio_usuarios)

        self.usuarios = []
        self.encodings = []
        self.imagenes = {}

        for archivo in os.listdir(self.directorio_usuarios):
            if archivo.endswith(".jpg") or archivo.endswith(".png"):
                ruta = os.path.join(self.directorio_usuarios, archivo)
                imagen = face_recognition.load_image_file(ruta)
                face_locations = face_recognition.face_locations(imagen)

                # Verificar que haya un rostro en la imagen
                if len(face_locations) == 0:
                    print(f"No se detectaron rostros en {archivo}, ignóralo.")
                    continue

                encoding = face_recognition.face_encodings(imagen, face_locations)
                if len(encoding) > 0:  # Si se detecta un rostro
                    self.encodings.append(encoding[0])
                    self.usuarios.append(archivo.split(".")[0])  # Extraer el nombre (sin extensión)
                    self.imagenes[archivo.split(".")[0]] = ruta  # Guardar la ruta de la imagen

        if self.usuarios:
            self.label_estado.config(text=f"Estado: Datos cargados para {len(self.usuarios)} usuarios.")
        else:
            self.label_estado.config(text="Estado: No hay usuarios registrados para reconocer.")

    def iniciar_reconocimiento(self):
        """Inicia el proceso de reconocimiento facial"""
        # Verificar si los modelos están disponibles
        if self.predictor is None or self.facerec is None:
            messagebox.showerror("Error", "Los modelos de dlib no están disponibles. Por favor, descárgalos primero.")
            return

        # Verificar si ya hay una cámara activa
        if self.camara_activa:
            return
            
        # Inicializar la cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        # Cambiar el estado de los botones
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
            self.thread_camara.join(timeout=1.0)
            
        # Liberar la cámara si está abierta
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            
        # Restaurar la interfaz
        self.boton_iniciar.config(state=tk.NORMAL)
        self.boton_detener.config(state=tk.DISABLED)
        self.label_estado.config(text="Estado: Reconocimiento detenido.")
        
        # Limpiar la imagen de la cámara
        self.label_camara.config(text="La cámara se mostrará aquí", image='')
        
        # Limpiar la información del usuario
        self.mostrar_usuario_reconocido("", 0)

    def procesar_video(self):
        """Procesa el video de la cámara en un hilo separado"""
        while self.camara_activa:
            ret, frame = self.cap.read()
            if not ret:
                self.label_estado.config(text="Estado: Error al capturar imagen.")
                self.camara_activa = False
                break
                
            # Hacer una copia del frame para mostrar en la interfaz
            self.frame_actual = frame.copy()
                
            # Realizar el reconocimiento facial
            self.reconocer_rostro(frame)
                
            # Convertir el frame a un formato que pueda mostrar Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Redimensionar manteniendo la proporción
            ancho_panel = self.panel_camara.winfo_width()
            alto_panel = self.panel_camara.winfo_height()
            
            if ancho_panel > 1 and alto_panel > 1:  # Asegurar que el panel ya tiene dimensiones
                proporcion = min(ancho_panel / img.width, alto_panel / img.height)
                nuevo_ancho = int(img.width * proporcion)
                nuevo_alto = int(img.height * proporcion)
                img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            
            # Mostrar en la interfaz
            img_tk = ImageTk.PhotoImage(img)
            self.label_camara.config(image=img_tk)
            self.label_camara.image = img_tk  # Mantener una referencia
            
            # Dar tiempo al sistema para actualizar la interfaz
            self.master.update_idletasks()
            self.master.update()

    def reconocer_rostro(self, frame):
        """Realiza el reconocimiento facial en un frame"""
        # Convertir el frame a RGB para face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detectar rostros usando dlib directamente
        dlib_faces = self.detector(rgb_frame, 1)
        
        if len(dlib_faces) == 0:
            # Si dlib no detecta rostros, intentar con face_recognition
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) == 0:
                self.label_estado.config(text="Estado: No se detectaron rostros en el marco.")
                return
        else:
            # Convertir dlib_faces a formato face_locations
            face_locations = [(rect.top(), rect.right(), rect.bottom(), rect.left()) for rect in dlib_faces]

        try:
            # Método 1: Usar dlib directamente para obtener encodings
            face_encodings = []
            for rect in dlib_faces:
                # Obtener los landmarks faciales usando el predictor
                shape = self.predictor(rgb_frame, rect)
                # Calcular la codificación facial
                face_encoding = np.array(self.facerec.compute_face_descriptor(rgb_frame, shape))
                face_encodings.append(face_encoding)
            
            # Si no se detectaron rostros con dlib pero sí con face_recognition
            if len(face_encodings) == 0 and len(face_locations) > 0:
                # Método 2: Usar face_recognition como respaldo
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if len(face_encodings) == 0:
                return
                
        except Exception as e:
            print(f"Error al calcular las codificaciones faciales: {e}")
            self.label_estado.config(text=f"Estado: Error al calcular codificaciones: {str(e)}")
            return

        # Procesar cada rostro detectado
        for i, face_encoding in enumerate(face_encodings):
            # Obtener las coordenadas para dibujar el rectángulo
            if i < len(face_locations):
                if len(dlib_faces) > 0 and i < len(dlib_faces):
                    # Si usamos dlib, obtenemos las coordenadas del rectángulo
                    rect = dlib_faces[i]
                    top, right, bottom, left = rect.top(), rect.right(), rect.bottom(), rect.left()
                else:
                    # Si usamos face_recognition, las coordenadas están en orden diferente
                    top, right, bottom, left = face_locations[i]
            else:
                # En caso de que haya discrepancia entre encodings y locations
                continue
            
            # Comparar con los encodings existentes
            matches = []
            face_distances = []
            
            for encoding in self.encodings:
                # Calcular la distancia euclidiana
                dist = np.linalg.norm(face_encoding - encoding)
                face_distances.append(dist)
                # Determinar si es una coincidencia (distancia menor que el umbral)
                matches.append(dist < 0.6)  # Umbral ajustable
            
            name = "Desconocido"
            similitud = 0

            if True in matches and len(face_distances) > 0:
                match_index = np.argmin(face_distances)
                name = self.usuarios[match_index]
                similitud = (1 - face_distances[match_index]) * 100  # Convertir distancia a porcentaje
                
                # Mostrar la información del usuario en la barra lateral
                self.mostrar_usuario_reconocido(name, similitud)

            # Dibujar el recuadro alrededor del rostro y mostrar el porcentaje de similitud
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            texto = f"{name} ({similitud:.2f}%)"
            cv2.putText(frame, texto, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    def mostrar_usuario_reconocido(self, nombre, similitud):
        """Muestra la información del usuario reconocido en la barra lateral"""
        if nombre:
            # Actualizar la etiqueta con el nombre
            self.label_nombre.config(text=nombre)
            
            # Actualizar la etiqueta con la similitud
            self.label_similitud.config(text=f"{similitud:.2f}%")
            
            # Mostrar la imagen del usuario si existe
            if nombre in self.imagenes:
                ruta_imagen = self.imagenes[nombre]
                try:
                    img = Image.open(ruta_imagen)
                    
                    # Calcular el tamaño para ajustar al frame de imagen
                    ancho_frame = self.frame_imagen_usuario.winfo_width()
                    alto_frame = self.frame_imagen_usuario.winfo_height()
                    
                    if ancho_frame > 1 and alto_frame > 1:  # Asegurar que el frame ya tiene dimensiones
                        proporcion = min(ancho_frame / img.width, alto_frame / img.height)
                        nuevo_ancho = int(img.width * proporcion * 0.9)  # 90% del espacio disponible
                        nuevo_alto = int(img.height * proporcion * 0.9)
                        img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
                    
                    img_tk = ImageTk.PhotoImage(img)
                    self.label_imagen.config(image=img_tk, text="")
                    self.label_imagen.image = img_tk  # Mantener una referencia
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")
                    self.label_imagen.config(text=f"Error al cargar la imagen: {str(e)}", image="")
            else:
                self.label_imagen.config(text="No hay imagen disponible", image="")
        else:
            # Limpiar la información
            self.label_nombre.config(text="---")
            self.label_similitud.config(text="---")
            self.label_imagen.config(text="No hay usuario reconocido", image="")

    def regresar_menu(self):
        """Cierra la ventana de reconocimiento facial"""
        # Detener la cámara si está activa
        if self.camara_activa:
            self.detener_reconocimiento()
            
        self.master.destroy()

# Ejecutar la ventana (solo como prueba)
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReconocerUsuario(root)
    root.mainloop()
