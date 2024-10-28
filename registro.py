import cv2
import face_recognition # type: ignore
import numpy as np
import os
import mysql.connector 
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Conexión a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="clase_ds3a"
    )

conexion = conectar_db()

# Función para registrar un nuevo estudiante
def registrar():
    def capture_image():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return None

        cv2.namedWindow("Camera")
        for i in range(4):
            ret, frame = cap.read()
            if ret:
                cv2.putText(frame, f"Esperando... {4 - i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.imshow("Camera", frame)
                cv2.waitKey(1000)
            else:
                break

        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        return frame if ret else None

    def save_data(image, name):
        _, buffer = cv2.imencode('.jpg', image)
        img_blob = buffer.tobytes()

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO estudiantes(nombre, imagen) VALUES (%s, %s)", (name, img_blob))
            conexion.commit()
            folder_name = "fotos"
            os.makedirs(folder_name, exist_ok=True)
            cv2.imwrite(os.path.join(folder_name, f"{name}.jpg"), image)
            messagebox.showinfo("Información", "Datos guardados correctamente.")
        except mysql.connector.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def open_input_interface(captured_image):
        input_window = tk.Tk()
        input_window.title("Ingrese su nombre")
        input_window.geometry("400x200")

        label = tk.Label(input_window, text="Nombre:", font=("Helvetica", 14))
        label.pack(pady=10)

        name_entry = tk.Entry(input_window, font=("Helvetica", 14))
        name_entry.pack(pady=10)

        def on_save():
            name = name_entry.get().strip()
            if name:
                save_data(captured_image, name)
                input_window.destroy()

        save_button = tk.Button(input_window, text="Guardar", command=on_save, font=("Helvetica", 14))
        save_button.pack(pady=10)

        input_window.mainloop()

    captured_image = capture_image()
    if captured_image is not None:
        open_input_interface(captured_image)

# Función para el botón "Escanear"
def escanear():
    # Código de escaneo que ya proporcionaste aquí
    path = 'fotos'
    images = []
    classNames = []
    myList = os.listdir(path)

    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        if curImg is not None:
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodes = face_recognition.face_encodings(img)
            if encodes:
                encodeList.append(encodes[0])
        return encodeList

    encodeListKnown = findEncodings(images)
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                now = datetime.now()
                fecha = now.strftime("%d/%m/%Y")
                hora = now.strftime("%H:%M")
                dia = now.strftime("%A")

                dias_en_espanol = {
                    "Monday": "Lunes",
                    "Tuesday": "Martes",
                    "Wednesday": "Miércoles",
                    "Thursday": "Jueves",
                    "Friday": "Viernes",
                    "Saturday": "Sábado",
                    "Sunday": "Domingo"
                }
                dia_espanol = dias_en_espanol[dia]

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(img, f'Alumno registrado: {name}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                cv2.imshow('Camara', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Función para el botón "Salir"
def salir():
    root.quit()

# Configuración de la interfaz
root = tk.Tk()
root.title("Sistema de Reconocimiento")
root.geometry("300x200")
root.configure(bg="light blue")

btn_registrar = tk.Button(root, text="Registrar", width=15, command=registrar)
btn_registrar.pack(pady=10)

btn_escanear = tk.Button(root, text="Escanear", width=15, command=escanear)
btn_escanear.pack(pady=10)

btn_salir = tk.Button(root, text="Salir", width=15, command=salir)
btn_salir.pack(pady=10)

root.mainloop()
