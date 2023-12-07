# Websoocked
import asyncio
import websockets
import json
import base64

async def text_to_speech(voice_id):
    model = 'eleven_monolingual_v1'
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model}"

    async with websockets.connect(uri) as websocket:

        # Initialize the connection
        bos_message = {
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": True
            },
            "xi_api_key": "0c300f0ff3e0754065480afa3f822a09",  # Replace with your API key
        }
        await websocket.send(json.dumps(bos_message))

        # Send "Hello World" input
        input_message = {
            "text": "Hello World ",
            "try_trigger_generation": True
        }
        await websocket.send(json.dumps(input_message))

        # Send EOS message with an empty string instead of a single space
        # as mentioned in the documentation
        eos_message = {
            "text": ""
        }
        await websocket.send(json.dumps(eos_message))

        # Added a loop to handle server responses and print the data received
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print("Server response:", data)

                if data["audio"]:
                    chunk = base64.b64decode(data["audio"])
                    print("Received audio chunk")
                else:
                    print("No audio data in the response")
                    break
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

asyncio.get_event_loop().run_until_complete(text_to_speech("EXAVITQu4vr4xnSDxMaL"))
