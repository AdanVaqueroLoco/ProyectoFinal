import sounddevice as sd
import numpy as np

periodo_muestreo = 1.0/44100
cuerda = "cuerda"

print(sd.query_devices()) 

#indata: arreglo de numpy con la info recopilada por la tarjeta de sonido
#        a través del dispositivo de entrada
#outdata: arreglo de numpy que se le enviará al dispositivo de salida
#        por default es un silencio (puros 0's)
#frames: numero de muestras que tiene indata
#time: el tiempo que se lleva haciendo el stream
#status: si ha habido algun error

def callback_stream(indata, outdata, frames, time, status):
    global periodo_muestreo
    data = indata[:,0]
    transformada = np.fft.rfft(data)
    frecuencias = np.fft.rfftfreq(len(data), periodo_muestreo)
    print("Frecuencia fundamental: ", frecuencias[np.argmax(np.abs(transformada))])
    #outdata[:] = indata

try:
    with sd.Stream(
        device=(), #elegir dispositivo de audio de entrada y salida, dejar vacio toma los defaults
        blocksize=11025, #0 es que la tarjeta de sonido decide el mejor tamañom es posible que sea variable
        samplerate=44100,
        channels=1,
        dtype = np.int16,
        latency = 'low', 
        callback = callback_stream
    ):
        print('Presiona tecla Enter para salir')
        input()

except Exception as e:
    print(str(e))