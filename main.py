import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
import os
import numpy as np

class InterfazReconocerUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Reconocimiento Facial")
        self.master.geometry("600x400")
        
        # Etiqueta de estado del reconocimiento
        self.label_estado = tk.Label(master, text="Estado: Esperando para iniciar...", font=("Arial", 12))
        self.label_estado.pack(pady=20)
        
        # Botón para iniciar el reconocimiento
        boton_iniciar = tk.Button(master, text="Iniciar Reconocimiento Facial", font=("Arial", 12), command=self.reconocer_usuario)
        boton_iniciar.pack(pady=10)
        
        # Botón para regresar al menú principal
        boton_regresar = tk.Button(master, text="Regresar al Menú Principal", font=("Arial", 12), command=self.regresar_menu)
        boton_regresar.pack(pady=10)

        # Configuración inicial del reconocedor facial
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Directorio de usuarios y diccionario para IDs
        self.directorio_usuarios = "usuarios_reconocimiento"
        self.usuarios = {}
        self.cargar_datos()

    def cargar_datos(self):
        """Carga imágenes existentes y entrena el reconocedor"""
        caras = []
        ids = []

        for archivo in os.listdir(self.directorio_usuarios):
            if archivo.endswith(".jpg") or archivo.endswith(".png"):
                partes_archivo = archivo.split("_")
                
                # Validar si el archivo tiene un formato esperado con un ID
                if len(partes_archivo) < 2 or not partes_archivo[0].isdigit():
                    print(f"Archivo ignorado por formato no válido: {archivo}")
                    continue  # Saltar archivos con formato incorrecto

                # Extraer ID y nombre del archivo
                usuario_id = int(partes_archivo[0])  # ID a partir del nombre del archivo
                nombre_usuario = partes_archivo[1].split(".")[0]  # Nombre del usuario
                self.usuarios[usuario_id] = nombre_usuario

                # Cargar la imagen
                ruta = os.path.join(self.directorio_usuarios, archivo)
                imagen = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
                caras.append(imagen)
                ids.append(usuario_id)

        # Entrenar el reconocedor si hay datos
        if len(caras) > 0:
            self.recognizer.train(caras, np.array(ids))
            self.label_estado.config(text=f"Estado: Datos cargados con {len(caras)} usuarios.")
        else:
            self.label_estado.config(text="Estado: No hay usuarios registrados para reconocer.")

    def reconocer_usuario(self):
        """Inicia el reconocimiento facial"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        self.label_estado.config(text="Estado: Reconocimiento en progreso...")

        while True:
            ret, frame = cap.read()
            if not ret:
                self.label_estado.config(text="Estado: Error al capturar imagen.")
                break
            
            # Convertir el frame a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]

                try:
                    usuario_id, confianza = self.recognizer.predict(roi_gray)
                    if confianza < 70:  # Confianza por debajo del umbral = éxito
                        nombre = self.usuarios.get(usuario_id, "Desconocido")
                        self.label_estado.config(text=f"Acceso permitido para: {nombre}")
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f"{nombre}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    else:
                        self.label_estado.config(text="Acceso denegado: Usuario desconocido")
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(frame, "Desconocido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                        # Aquí se ofrece al usuario agregar el rostro desconocido
                        self.agregar_usuario(frame[y:y+h, x:x+w])
                except Exception as e:
                    print(f"Error: {e}")
                    self.label_estado.config(text="Error en el reconocimiento")
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Error", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # Mostrar el frame
            cv2.imshow("Reconocimiento Facial", frame)

            # Salir al presionar la tecla Esc
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def agregar_usuario(self, rostro):
        """Agrega un nuevo usuario al sistema"""
        nombre = simpledialog.askstring("Nuevo Usuario", "Ingrese el nombre del usuario:")
        if not nombre:
            return

        # Crear un nuevo ID para el usuario
        nuevo_id = len(self.usuarios) + 1
        archivo_guardado = os.path.join(self.directorio_usuarios, f"{nuevo_id}_{nombre}.jpg")
        cv2.imwrite(archivo_guardado, rostro)

        # Actualizar el sistema con el nuevo usuario
        self.usuarios[nuevo_id] = nombre
        self.cargar_datos()
        messagebox.showinfo("Éxito", f"Usuario '{nombre}' agregado correctamente.")

    def regresar_menu(self):
        self.master.destroy()

# Ejecutar la ventana (solo como prueba)
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazReconocerUsuario(root)
    root.mainloop()
