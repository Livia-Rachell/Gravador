import wave
import pyaudio
import keyboard

FRAMESPERBUFFER = 1024
FORRMAT = pyaudio.paInt16
CHANNELS = 1 #mono ou estéreo.
RATE = 44100

audio = pyaudio.PyAudio()

stream = audio.open(
    input=True, #Não é execução, é recepção.
    format=FORRMAT,
    channels=CHANNELS,
    rate=RATE,
    frames_per_buffer=FRAMESPERBUFFER,
)
print("Gravando... Pressione 'p' para parar.")

frames = []
while True:
    buffer = stream.read(FRAMESPERBUFFER)
    frames.append(buffer)
    if keyboard.is_pressed('p'):
        break

nome_arquivo = input("Digite o nome do arquivo: ")
nome_arquivo += ".wav"

stream.start_stream()
stream.close()
audio.terminate()

print("Gravação concluída.")

waveform = wave.open(nome_arquivo, "wb")
waveform.setnchannels(CHANNELS)
waveform.setframerate(RATE)
waveform.setsampwidth(audio.get_sample_size(FORRMAT))
waveform.writeframes(b"".join(frames))
waveform.close()