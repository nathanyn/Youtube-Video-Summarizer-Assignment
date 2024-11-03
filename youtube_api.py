from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, render_template, request

import config
import json

# Set up OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    video_url = request.form['video_url']
    video_id = extract_video_id(video_url)
    
    try:
        # Download the transcript from the YouTube video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en']).fetch()

        # Extract and concatenate all text elements
        concatenated_text = " ".join(item['text'] for item in transcript)

        # Call the OpenAI API to summarize the transcript
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Summarize the following text: " + concatenated_text}
            ])

        summary = response.choices[0].message.content
        return render_template('index.html', summary=summary)
    except Exception as e:
        return render_template('index.html', error=str(e))


def extract_video_id(url):
    # Extract video ID from the YouTube URL
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1]
    else:
        return None

if __name__ == "__main__":
    app.run(debug=True)
