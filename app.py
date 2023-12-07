from flask import Flask, render_template, request, jsonify
import openai
import sounddevice as sd
import wavio
import numpy as np
import requests
from pydub import AudioSegment
from pydub.playback import play

# Set your OpenAI API key and model ID
openai.api_key = "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"
model_id = "ft:gpt-3.5-turbo-0613:personal::7wxvMtKW"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speck', methods=['post'])
# Function to play the Eleven Labs voice
def speck(text):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL/stream"

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "0c300f0ff3e0754065480afa3f822a09"
    }

    data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers, stream=True)

    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    audio_file = AudioSegment.from_file("output.mp3", format="mp3")

    # Play the audio using pydub's playback
    play(audio_file)

    # Return a simple response to indicate success
    return '', 204

app.config['user_text'] = None

@app.route('/record', methods=['post'])
def voice_record():
    # Define the audio recording parameters
    sample_rate = 16000

    # Define a silence threshold (adjust as needed)
    silence_threshold = 0.01

    while True:
        # Create an empty list to store audio chunks for each interaction
        audio_chunks = []
        # Create a buffer to hold audio energy values for each interaction
        energy_buffer = []

        while True:
            audio_chunk = sd.rec(
                int(1 * sample_rate), samplerate=sample_rate, channels=1
            )
            sd.wait()
            audio_chunks.append(audio_chunk)

            # Calculate the energy of the audio chunk
            energy = np.sum(audio_chunk**2) / (sample_rate * len(audio_chunk))
            energy_buffer.append(energy)

            # Check if the audio chunk contains mostly silence based on energy
            if len(energy_buffer) >= 10:
                average_energy = np.mean(energy_buffer)
                energy_buffer = energy_buffer[1:]

                if average_energy < silence_threshold:
                    break

        print("Finished recording.")

        audio_data = np.concatenate(audio_chunks, axis=0)

        # Save the recorded audio to a WAV file
        wavio.write("user_audio.wav", audio_data, sample_rate, sampwidth=2)

        # Transcribe the recorded audio using OpenAI Whisper
        with open("user_audio.wav", "rb") as audio_file:
            try:
                response = openai.Audio.transcribe("whisper-1", audio_file)
            except openai.error.APIConnectionError as e:
                print(f"API Connection Error: {str(e)}")
                # Log the error or take appropriate action
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                # Log the error or take appropriate action

        text_from_whisper = response["text"]

        # Debugging output
        print("Transcribed Text from Whisper:", text_from_whisper)

        # Set the transcribed text in app.config for later access
        app.config['transcribed_text'] = text_from_whisper

        return render_template("index.html", text=text_from_whisper)


@app.route('/send_message', methods=['POST'])
def send_message():
    # Function to read the entire conversation history from the chat log
    def read_conversation_history(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            conversation = []
            current_role = None
            current_message = []

            for line in lines:
                if line.startswith("You: "):
                    current_role = "user"
                    current_message.append(line[5:].strip())
                elif line.startswith("Assistant: "):  # Include assistant's messages
                    current_role = "assistant"
                    current_message.append(line[11:].strip())
                else:
                    # If the line doesn't start with "You:" or "Assistant:", it's a continuation of the current message
                    current_message.append(line.strip())

                if not line.strip():
                    # Empty line separates messages in the log
                    if current_role and current_message:
                        conversation.append(
                            {"role": current_role, "content": " ".join(current_message)}
                        )
                    current_role = None
                    current_message = []

            return conversation

        except FileNotFoundError:
            print("The 'chat_log.txt' file was not found.")
            return []
        
    # Function to read roleplay text from "roleplay.txt" file
    def read_roleplay_text():
        try:
            with open("roleplay.txt", "r") as file:
                roleplay_text = file.read()
            return roleplay_text
        except FileNotFoundError:
            print("The 'roleplay.txt' file was not found.")
            return ""
    
    # Read roleplay text from the "roleplay.txt" file
    roleplay_text = read_roleplay_text()

    user_input = request.form.get('userInput')

    # Function to append text to a log file
    def append_to_log(user_input):
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(user_input + "\n")


    # Replace this line with the logic that generates the AI's response
    # Define a system message to provide context to the user
    system_message = {"role": "system", "content": roleplay_text}

                # Read the entire conversation history from chat_log.txt
    previous_conversation = read_conversation_history("chat_log.txt")

                # Append the system message to the conversation
    previous_conversation.append(system_message)

                # Add the user's latest message to the conversation
    previous_conversation.append({"role": "user", "content": user_input})

                # Generate response using ChatGPT with the entire conversation history
    response = openai.ChatCompletion.create(
        model=model_id, messages=previous_conversation
    )

    # Extract the assistant's response
    response_message = response.choices[0].message.content.strip()

    print(response_message)

    # Return the response as JSON
    return jsonify(response=response_message)

if __name__ == '__main__':
    app.run(debug=True)