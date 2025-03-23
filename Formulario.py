import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import time

class InterfazAgregarUsuario:
    def __init__(self, master):
        self.master = master
        self.master.title("Agregar Nuevo Usuario")
        self.master.geometry("600x400")
        self.master.configure(bg="#6A5ACD")  # Fondo púrpura elegante

        # Título del sistema
        label_titulo = tk.Label(
            master,
            text="Agregar Nuevo Usuario",
            font=("Wide Latin", 14),
            bg="#6A5ACD",
            fg="white"
        )
        label_titulo.pack(pady=20)

        # Crear campos de entrada para nombre y apellido
        tk.Label(
            master,
            text="Nombre:",
            font=("Arial", 14),
            bg="#6A5ACD",
            fg="white"
        ).pack(pady=5)

        self.entry_nombre = tk.Entry(master, font=("Arial", 14))
        self.entry_nombre.pack(pady=5)

        tk.Label(
            master,
            text="Apellido:",
            font=("Arial", 14),
            bg="#6A5ACD",
            fg="white"
        ).pack(pady=5)

        self.entry_apellido = tk.Entry(master, font=("Arial", 14))
        self.entry_apellido.pack(pady=5)

        # Botón para tomar foto
        boton_foto = tk.Button(
            master,
            text="Capturar Foto",
            font=("Arial", 14),
            bg="#800080",
            fg="white",
            width=20,
            command=self.mostrar_camara
        )
        boton_foto.pack(pady=15)

        # Espacio para mostrar la imagen capturada
        self.label_imagen = tk.Label(master, bg="gray")
        self.label_imagen.pack(pady=10)

        # Botón para regresar
        boton_regresar = tk.Button(
            master,
            text="Regresar al Menú Principal",
            font=("Arial", 14),
            bg="#800080",
            fg="white",
            width=25,
            command=self.regresar_menu
        )
        boton_regresar.pack(pady=5)

    def mostrar_camara(self):
        # Validar que los campos no estén vacíos
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        if not nombre or not apellido:
            tk.messagebox.showerror("Error", "Debe ingresar el nombre y apellido.")
            return

        # Acceder a la cámara
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            tk.messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Dibujar un recuadro guía para el rostro
            height, width = frame.shape[:2]
            x1, y1, x2, y2 = int(width * 0.3), int(height * 0.2), int(width * 0.7), int(height * 0.8)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Capturar Foto", frame)

            # Detectar si el rostro está dentro del recuadro
            roi = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                # Esperar 1 segundo antes de capturar la imagen
                time.sleep(1)

                # Guardar la imagen automáticamente
                directorio_usuarios = "usuarios_reconocimiento"
                if not os.path.exists(directorio_usuarios):
                    os.makedirs(directorio_usuarios)

                id_usuario = f"{nombre}_{apellido}.jpg"
                ruta_imagen = os.path.join(directorio_usuarios, id_usuario)
                cv2.imwrite(ruta_imagen, roi)

                self.mostrar_imagen(ruta_imagen)
                break

            # Presione "q" para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def mostrar_imagen(self, ruta_imagen):
        # Cargar la imagen
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((200, 200))  # Ajustar tamaño
        imagen_tk = ImageTk.PhotoImage(imagen)

        # Actualizar el label para mostrar la imagen
        self.label_imagen.config(image=imagen_tk)
        self.label_imagen.image = imagen_tk

    def regresar_menu(self):
        self.master.destroy()

# Ejecutar el formulario
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAgregarUsuario(root)
    root.mainloop()
