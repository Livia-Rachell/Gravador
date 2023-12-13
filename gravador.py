import pyaudio
import wave

audio = pyaudio.PyAudio()

FORRMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44000
FRAMESPERBUFFER = 1024

stream = audio.open(
    input=True, #Não é execução, é recepção.
    format=FORRMAT, # 16 bits /paInt32 32 bits -> Quanto maior, maior a qualidade do áudio e maior o peso do arquivo. Mais detalhes
    channels=CHANNELS, #mono ou estéreo.
    rate=RATE, #44000 Hz
    frames_per_buffer=FRAMESPERBUFFER,
)

frames = []

try:
    while True:
        buffer = stream.read(FRAMESPERBUFFER)
        frames.append(buffer)
except KeyboardInterrupt:
    pass

stream.start_stream()
stream.close()
audio.terminate()
arquivo_audio = wave.open("gravacao.mp3", "wb")
arquivo_audio.setnchannels(CHANNELS)
arquivo_audio.setframerate(RATE)
arquivo_audio.setsampwidth(audio.get_sample_size(FORRMAT))
arquivo_audio.writeframes(b"".join(frames))
arquivo_audio.close()