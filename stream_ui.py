import tkinter as tk
import sounddevice as sd
import numpy as np
from threading import Thread, Event

class StreamThread(Thread):
    def __init__(self):
        super().__init__()
        self.dispoitivo_input = 1
        self.dispoitivo_output = 5
        self.tamano_bloque = 5500
        self.frecuencia_muestreo = 44100
        self.canales = 1
        self.tipo_dato = np.int16
        self.latencia = "high"

    def callback_stream(self, indata, outdata, frames, time, status):
        global app

        data = indata[:,0]
        transformada = np.fft.rfft(data)
        periodo_muestreo = 1/self.frecuencia_muestreo
        frecuencias = np.fft.rfftfreq(len(data), periodo_muestreo)
        frecuencia_fundamental = frecuencias[np.argmax(np.abs(transformada))]

        app.etiqueta_valor_ff["text"] = frecuencia_fundamental
        if frecuencia_fundamental >= 435  and frecuencia_fundamental <= 445:
            app.etiqueta_nota["text"] = "A4 Correcta"

        elif frecuencia_fundamental >= 325  and frecuencia_fundamental <= 335:
            app.etiqueta_nota["text"] = "E4 Correcta"

        elif frecuencia_fundamental >= 256  and frecuencia_fundamental <= 266:
            app.etiqueta_nota["text"] = "C4 Correcta"

        elif frecuencia_fundamental >= 387  and frecuencia_fundamental <= 397:
            app.etiqueta_nota["text"] = "G4 Correcta"

        else:
            app.etiqueta_nota["text"] = "Es recomendable ajustar la cuerda"


    def run(self):
        try:
            self.event = Event()
            with sd.Stream(
                device=(self.dispoitivo_input, self.dispoitivo_output), #Se eligen dispositivos (entrada, salida)
                blocksize= self.tamano_bloque, # 0 significa que la tarjeta de sonido decide el mejor tamaño
                samplerate= self.frecuencia_muestreo, # frecuencia de muestreo
                channels= self.canales, #numero de canales1
                dtype= self.tipo_dato, #Tipo de dato (profundidad de bits)
                latency=self.latencia, # Latencia, que tanto tiempo pasa desde entrada hasta la salida
                callback= self.callback_stream
            ) as self.stream:
                self.event.wait()

        except Exception as e:
            print(str(e))



#Heredamos de Tk para hacer una ventana
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #Establecer tiutlo de la ventana
        self.title("Ukelele")
        #Establecemos tamaño
        self.geometry("400x300")

        boton_iniciar = tk.Button(self, width=20, text ="Iniciar grabación", command=lambda: self.click_boton_iniciar())
        boton_iniciar.grid(column=0, row= 0)

        boton_detener = tk.Button(self, width=20, text="Detener grabación", command= lambda: self.click_boton_detener())
        boton_detener.grid(column=1, row=0)

        etiqueta_estado = tk.Label(text="Estado: ")
        etiqueta_estado.grid(column=0, row=1)

        self.etiqueta_valor_estado = tk.Label(text="-")
        self.etiqueta_valor_estado.grid(column=1, row=1)

        etiqueta_Nombre_Nota = tk.Label(text="Nota: ")
        etiqueta_Nombre_Nota.grid(column=0, row=3)

        self.etiqueta_nota = tk.Label(text="-")
        self.etiqueta_nota.grid(column=1, row=3)

        etiqueta_nota = tk.Label(text= "Necesita afinamiento: ")
        etiqueta_nota.grid(column=0, row= 2)

        self.etiqueta_valor_ff = tk.Label(text="-" ) ## Poner aquí si se debe ajustar
        self.etiqueta_valor_ff.grid(column=1, row= 2)

        self.stream_thread = StreamThread()

    def click_boton_iniciar(self):
        if not self.stream_thread.is_alive():
            self.stream_thread.daemon = True
            self.stream_thread.start()
        
    
    def click_boton_detener(self):
        if self.stream_thread.is_alive():
            self.etiqueta_valor_estado["text"] = "Grabación detenida"
            self.stream_thread.stream.abort()
            self.stream_thread.event.set()
            self.stream_thread.join()

app = App()
def main():
    app.mainloop()

if __name__ == "__main__":
    main()
    