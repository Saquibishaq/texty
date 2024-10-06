import requests
from gtts import gTTS
from transformers import pipeline
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import os

# Pixabay API key (replace this with your actual API key)
PIXABAY_API_KEY = "Y45901871-577ac26a62f94274074f7578a"  # Replace with your actual API key

# Function to fetch images from Pixabay
def fetch_images(query, index, num_images=5):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page={num_images}"
    response = requests.get(url).json()

    image_paths = []
    if 'hits' in response and len(response['hits']) > 0:
        for i, hit in enumerate(response['hits']):
            image_url = hit['largeImageURL']
            image_path = os.path.join('resources', f'image_{index}_{i}.jpg')

            img_data = requests.get(image_url).content
            with open(image_path, 'wb') as handler:
                handler.write(img_data)

            image_paths.append(image_path)
    else:
        print(f"No images found for query: {query}")

    return image_paths

# Function to generate a story from a prompt using GPT-2
def generate_story(prompt):
    try:
        # Create a text-generation pipeline using the GPT-2 model and run on CPU
        story_generator = pipeline('text-generation', model='gpt2', device=-1)  # Use -1 for CPU

        # Generate story with specified parameters
        story = story_generator(
            prompt,
            max_length=500,
            num_return_sequences=1,
            truncation=True,
            pad_token_id=50256  # Default pad token ID for GPT-2
        )
        
        return story[0]['generated_text']
    except Exception as e:
        print(f"Error generating story: {str(e)}")  # Log any errors
        raise  # Re-raise the exception for higher-level handling
# Function to generate a video from a text prompt
def generate_video_from_text(prompt):
    # Step 2: Generate story from the prompt
    generated_story = generate_story(prompt)

    # Step 3: Convert the generated story into speech
    tts = gTTS(text=generated_story, lang='en')
    audio_file = os.path.join('resources', "generated_story.mp3")
    tts.save(audio_file)

    # Step 4: Split the story into sentences
    sentences = generated_story.split('. ')
    if sentences[-1] == '':
        sentences = sentences[:-1]

    # Step 5: Fetch images for each sentence and store paths
    image_paths_per_sentence = []
    for i, sentence in enumerate(sentences):
        keywords = sentence.split()[:3]
        query = "+".join(keywords)
        image_paths = fetch_images(query, i, num_images=5)

        if len(image_paths) > 0:
            image_paths_per_sentence.append(image_paths)
        else:
            # Fallback to generating a blank image with the sentence text
            img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            d.text((20, 360), sentence, font=font, fill=(255, 255, 0))
            fallback_image_path = os.path.join('resources', f'fallback_image_{i}.jpg')
            img.save(fallback_image_path)
            image_paths_per_sentence.append([fallback_image_path])

    # Step 6: Create video clips from images
    audio_clip = AudioFileClip(audio_file)

    # Limit the total video duration to 30 seconds
    max_video_duration = 30
    sentence_duration = max_video_duration / len(sentences)

    clips = []
    for i, sentence_images in enumerate(image_paths_per_sentence):
        sub_clips = []
        image_duration = sentence_duration / len(sentence_images)

        for image_path in sentence_images:
            image_clip = ImageClip(image_path).set_duration(image_duration)
            sub_clips.append(image_clip)

        sentence_clip = concatenate_videoclips(sub_clips, method="compose")
        clips.append(sentence_clip)

    # Step 7: Concatenate all the sentence clips
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio_clip)

    # Step 8: Set final video duration to max_video_duration
    final_video = final_video.set_duration(max_video_duration)

    # Step 9: Save the final video
    video_file = os.path.join('resources', "video_generated.mp4")
    final_video.write_videofile(video_file, fps=24)

    # Step 10: Return the video file path
    return video_file
