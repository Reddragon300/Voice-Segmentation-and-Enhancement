from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.utils import make_chunks
import noisereduce as nr
import os
import sys

class AudioProcessor:
    def __init__(self, audio_file, output_directory):
        self.audio_file = audio_file
        self.output_directory = output_directory

    def process_audio(self, min_sentence_duration=5000, silence_threshold=-40, noise_reduction=True, sample_rate=44100, channels=1, output_format="wav"):
        try:
            # Load the audio file
            audio = AudioSegment.from_file(self.audio_file)

            # Split the audio by silence into sentences or words
            audio_segments = self.split_audio(audio, min_sentence_duration, silence_threshold)

            # Reduce noise if enabled
            if noise_reduction:
                audio = self.apply_noise_reduction(audio, sample_rate, channels)

            # Enhance volume and clarity for each segment
            enhanced_segments = self.enhance_segments(audio_segments)

            # Export the enhanced audio segments
            self.export_segments(enhanced_segments, output_format)

            print("Audio processing completed successfully.")
        except FileNotFoundError:
            print("Input audio file not found. Please provide a valid file path.")
        except Exception as e:
            print(f"An error occurred during audio processing: {str(e)}")
    
        print("Processing Audio ..... Will update when successfully complete....Please Wait....")

    def split_audio(self, audio, min_sentence_duration, silence_threshold):
        audio_segments = split_on_silence(
            audio, min_silence_len=min_sentence_duration, silence_thresh=silence_threshold)
        return audio_segments

    def apply_noise_reduction(self, audio, sample_rate, channels):
        # Create a noise profile from a portion of the audio
        noise_profile = nr.create_noise_profile(audio[:2000].get_array_of_samples(), sample_rate)

        # Convert to the specified sample rate and channels for better noise reduction
        audio = audio.set_frame_rate(sample_rate).set_channels(channels)

        # Apply noise reduction using the noise profile
        audio = nr.reduce_noise(audio.get_array_of_samples(), noise_profile)

        # Convert the processed audio back to an AudioSegment object
        audio = AudioSegment(audio.tobytes(), frame_rate=sample_rate, sample_width=audio.sample_width, channels=channels)

        return audio

    def enhance_segments(self, audio_segments):
        enhanced_segments = []
        for segment in audio_segments:
            enhanced_segment = segment.normalize().high_pass_filter(30)
            enhanced_segments.append(enhanced_segment)
        return enhanced_segments

    def export_segments(self, segments, output_format):
        for i, segment in enumerate(segments):
            output_file = f"{self.output_directory}/clip_{i}.{output_format}"
            segment.export(output_file, format=output_format)

if __name__ == "__main__":
    try:
        audio_file = input("Enter the path to the input audio file: ")
        output_directory = input("Enter the output directory path: ")

        use_default_settings = input("Use default settings? (y/n): ")
        if use_default_settings.lower() == "n":
            min_sentence_duration = int(input("Enter the minimum sentence duration in milliseconds (e.g., 5000): "))
            silence_threshold = int(input("Enter the silence threshold in dB (e.g., -40): "))
            noise_reduction_input = input("Enable noise reduction? (y/n): ")
            if noise_reduction_input.lower() == "y":
                noise_reduction = True
                sample_rate = int(input("Enter the desired sample rate in Hz (e.g., 44100): "))
                channels = int(input("Enter the number of channels (e.g., 1 for mono): "))
            else:
                noise_reduction = False
                sample_rate = 44100  # Default sample rate
                channels = 1  # Default number of channels
            output_format = input("Enter the output file format (e.g., wav): ")
        else:
            min_sentence_duration = 5000  # Default minimum sentence duration
            silence_threshold = -40  # Default silence threshold
            noise_reduction = True  # Default noise reduction setting
            sample_rate = 44100  # Default sample rate
            channels = 1  # Default number of channels
            output_format = "wav"  # Default output file format

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Create an instance of AudioProcessor
        audio_processor = AudioProcessor(audio_file, output_directory)

        # Process the audio
        audio_processor.process_audio(
            min_sentence_duration, silence_threshold, noise_reduction, sample_rate, channels, output_format
        )

    except ValueError:
        print("Invalid input. Please enter a valid integer value for the parameters.")
    except KeyboardInterrupt:
    print("\nProgram execution interrupted. Press Ctrl+C again to confirm cancellation.")
    try:
        while True:
            key_press = input()
            if key_press == '\x03':  # Ctrl+C
                print("\nConfirmation received. Audio processing cancelled.")
                sys.exit(0)
    except KeyboardInterrupt:
        print("\nAudio processing cancelled by user.")
        sys.exit(0)


