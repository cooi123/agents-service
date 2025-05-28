from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from .supabase_storage import upload_to_supabase
import wave
import uuid
import io


load_dotenv()


def create_wave_file(pcm, channels=1, rate=24000, sample_width=2) -> bytes:
    """
    Create a wave file in memory and return its bytes
    
    Args:
        pcm: The PCM audio data
        channels: Number of audio channels
        rate: Sample rate
        sample_width: Sample width in bytes
        
    Returns:
        bytes: The wave file data
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return buffer.getvalue()

def text_to_speech(content: str, bucket_name: str = None) -> str:
    """
    Convert text to speech and optionally save to Supabase Storage
    
    Args:
        content (str): The text content to convert to speech
        bucket_name (str, optional): The Supabase storage bucket name to save the audio to
        
    Returns:
        str: The Supabase Storage URL if bucket_name is provided, otherwise the audio data
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=content,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker='Host',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Kore',
                                )
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker='Guest',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Puck',
                                )
                            )
                        ),
                    ]
                )
            )
        )
    )
    
    data = response.candidates[0].content.parts[0].inline_data.data
    print("successfully generated audio")
    wave_data = create_wave_file(data)
    
    if bucket_name:
        file_path = f"audio/{uuid.uuid4()}.wav"
        print("uploading to supabase")
        return upload_to_supabase(wave_data, bucket_name, file_path)
    return wave_data


if __name__ == "__main__":
    content = '*(Intro Music)**\n\n**Host:** Welcome back to "Tech Forward," the podcast that explores the cutting edge of technology. Today, we\'re diving deep into a groundbreaking research paper that revolutionized the field of natural language processing – the Transformer.  I\'m joined by Dr. [Guest Name], one of the lead authors of this landmark paper.  Dr. [Guest Name], welcome to the show!\n\n**Guest:** Thanks for having me!\n\n**Host:** Let\'s start at the beginning. Before the Transformer, machine translation, and other sequential data processing was incredibly slow and computationally expensive. Can you explain why?\n\n**Guest:** Absolutely. Traditional methods relied heavily on recurrent neural networks (RNNs).  These networks processed information sequentially, one word or character at a time.  Think of it like reading a sentence word by word – it’s slow, especially for long sentences. This sequential nature made them difficult to parallelize, meaning we couldn\'t train them efficiently on powerful hardware with multiple processors working in parallel.\n\n**Host:** So the Transformer changed all that. '
    
    print(text_to_speech(content, bucket_name="podcast-audio"))