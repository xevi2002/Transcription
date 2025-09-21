import asyncio
import platform
import speech_recognition as sr
from js import document, alert

FPS = 30

async def main():
    # Inicialitzar el reconeixedor
    recognizer = sr.Recognizer()
    
    # Suposem que l'àudio es carrega des d'un input de fitxer HTML
    # Exemple: <input type="file" id="audioInput" accept="audio/mp3,audio/m4a">
    audio_input = document.getElementById('audioInput')
    if not audio_input or not audio_input.files.length:
        alert("Si us plau, seleccioneu un fitxer d'àudio MP3 o M4A.")
        return

    audio_file = audio_input.files[0]
    audio_data = await load_audio_file(recognizer, audio_file)

    if audio_data:
        # Transcriure l'àudio en paràgrafs basant-se en pauses
        paragraphs = await transcribe_to_paragraphs(recognizer, audio_data)
        
        # Mostrar els paràgrafs al DOM (pots ajustar l'ID de l'element)
        result_div = document.getElementById('transcriptionResult')
        if result_div:
            result_div.innerHTML = "<p>" + "</p><p>".join(paragraphs) + "</p>"
        else:
            alert("No s'ha trobat l'element per mostrar els resultats.")

async def load_audio_file(recognizer, audio_file):
    try:
        # Crear un objecte AudioFile compatible amb speech_recognition
        audio = await recognizer.AudioFile(audio_file)
        with audio as source:
            audio_data = recognizer.record(source)
        return audio_data
    except Exception as e:
        alert(f"Error en carregar el fitxer d'àudio: {str(e)}")
        return None

async def transcribe_to_paragraphs(recognizer, audio_data):
    paragraphs = []
    current_paragraph = ""
    silence_threshold = 0.5  # Llindar de silenci en segons per separar paràgrafs
    
    try:
        # Dividir l'àudio en fragments basant-se en pauses
        audio_chunks = split_audio_on_silence(recognizer, audio_data, silence_threshold)
        
        for chunk in audio_chunks:
            try:
                text = recognizer.recognize_google(chunk, language="ca-ES")  # Idioma català
                current_paragraph += text + " "
                
                # Si hi ha una pausa significativa, considera un nou paràgraf
                if len(current_paragraph.split()) > 10:  # Mínim 10 paraules per paràgraf
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
            except sr.UnknownValueError:
                continue  # Ignorar fragments no recognoscibles
            except sr.RequestError as e:
                alert(f"Error en la API de reconeixement: {str(e)}")
                return paragraphs
        
        # Afegir l'últim paràgraf si queda text
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
        
        return paragraphs
    except Exception as e:
        alert(f"Error en transcriure l'àudio: {str(e)}")
        return []

def split_audio_on_silence(recognizer, audio_data, silence_threshold):
    # Simulació de divisió basada en pauses (en un entorn real, requeriria anàlisi d'energia)
    # Aquí usem un enfocament simplificat; en producció, usa una biblioteca com pydub
    chunks = []
    duration = len(audio_data.get_raw_data()) / (audio_data.sample_rate * 2)  # Durada aproximada en segons
    chunk_size = int(duration / 5)  # Dividir en 5 parts com a exemple
    for i in range(0, len(audio_data.get_raw_data()), chunk_size * audio_data.sample_rate * 2):
        chunk_data = audio_data.get_segment(i / (audio_data.sample_rate * 2), (i + chunk_size) / (audio_data.sample_rate * 2))
        chunks.append(chunk_data)
    return chunks

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())