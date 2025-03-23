import tkinter as tk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk  # Para manejar y mostrar imágenes
import cv2
import os
import time

class InterfazAgregarUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Agregar Nuevo Usuario")
        self.master.geometry("600x400")  # Ampliamos el tamaño de la ventana

        # Crear campos de entrada para nombre y apellido
        tk.Label(master, text="Nombre:", font=("Arial", 12)).pack(pady=5)
        self.entry_nombre = tk.Entry(master, font=("Arial", 12))
        self.entry_nombre.pack(pady=5)

        tk.Label(master, text="Apellido:", font=("Arial", 12)).pack(pady=5)
        self.entry_apellido = tk.Entry(master, font=("Arial", 12))
        self.entry_apellido.pack(pady=5)
        
        # Botón para tomar foto
        boton_foto = tk.Button(master, text="Capturar Foto", font=("Arial", 12), command=self.capturar_foto)
        boton_foto.pack(pady=15)
        
        # Espacio para mostrar la imagen capturada
        self.label_imagen = tk.Label(master, bg="gray")  # Eliminar tamaño fijo para adaptarse
        self.label_imagen.pack(pady=10)
        
        # Botón para regresar
        boton_regresar = tk.Button(master, text="Regresar al Menú Principal", font=("Arial", 12), command=self.regresar_menu)
        boton_regresar.pack(pady=5)

    def capturar_foto(self):
        # Validar que los campos no estén vacíos
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        if not nombre or not apellido:
            tk.messagebox.showerror("Error", "Debe ingresar el nombre y apellido.")
            return
        
        # Iniciar captura de video
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            tk.messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        # Dar tiempo para que la cámara se estabilice
        time.sleep(2)

        # Leer un frame de la cámara
        ret, frame = cap.read()
        if not ret:
            tk.messagebox.showerror("Error", "No se pudo capturar la imagen.")
            cap.release()
            return

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            tk.messagebox.showerror("Error", "No se detectó ningún rostro. Intente nuevamente.")
        else:
            # Usar el primer rostro detectado
            x, y, w, h = faces[0]
            roi_gray = gray[y:y+h, x:x+w]

            # Crear directorio para guardar imágenes
            directorio_usuarios = "usuarios_reconocimiento"
            if not os.path.exists(directorio_usuarios):
                os.makedirs(directorio_usuarios)

            # Guardar la imagen con el nombre y apellido
            id_usuario = f"{nombre}_{apellido}.jpg"
            ruta_imagen = os.path.join(directorio_usuarios, id_usuario)
            cv2.imwrite(ruta_imagen, roi_gray)
            
            # Mostrar la imagen capturada en el recuadro
            self.mostrar_imagen(ruta_imagen)

        cap.release()
        cv2.destroyAllWindows()

    def mostrar_imagen(self, ruta_imagen):
        # Cargar la imagen
        imagen = Image.open(ruta_imagen)
        imagen_tk = ImageTk.PhotoImage(imagen)  # Convertir a formato compatible con Tkinter
        
        # Actualizar el label para mostrar la imagen
        self.label_imagen.config(image=imagen_tk)
        self.label_imagen.image = imagen_tk  # Mantener referencia para evitar que se borre

    def regresar_menu(self):
        self.master.destroy()

# Ejecutar el formulario (solo como prueba)
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAgregarUsuario(root)
    root.mainloop()
