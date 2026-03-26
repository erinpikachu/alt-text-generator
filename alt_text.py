import google.generativeai as genai
import pandas as pd
import time
import sys
import os
import requests
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
INPUT_FILE = 'wordpress_media.csv'
OUTPUT_FILE = 'wordpress_media_fixed.csv'

if not API_KEY:
    print("Error: No API Key found in .env file!")
    sys.exit()

model = genai.GenerativeModel('gemini-2.5-flash')
genai.configure(api_key=API_KEY)


def generate_alt_text(url):
    prompt = "Describe this image in one concise sentence for an HTML alt-text attribute. No intro text."
    
    try:
        # Download image
        img_response = requests.get(url, timeout=15)
        img_response.raise_for_status()
        
        content_type = img_response.headers.get('Content-Type', 'image/jpeg').split(';')[0].strip()
        image_part = {"inline_data": {"mime_type": content_type, "data": img_response.content}}

        # AI Attempt
        for attempt in range(3):
            try:
                response = model.generate_content([prompt, image_part])
                return response.text.strip()
            except Exception as e:
                err = str(e).lower()
                if 'quota' in err or '429' in err:
                    print(f"\n  [Rate Limit] Waiting 30s to cool down (Attempt {attempt+1}/3)...")
                    time.sleep(30)
                else:
                    return f"AI Error: {e}"
        return "Error: Quota exceeded"
    except Exception as e:
        return f"Link Error: {e}"

# Load data
df = pd.read_csv(INPUT_FILE)
print(f"--- Starting AI Alt-Text Generation for {len(df)} images ---")

for index, row in df.iterrows():
    # Progress indicator
    percent = round(((index + 1) / len(df)) * 100, 1)
    sys.stdout.write(f"\rProgress: {percent}% [{index+1}/{len(df)}] Processing: {row['post_title'][:20]}...")
    sys.stdout.flush()

    # Check if we need to process
    val = str(row['alt_text'])
    if pd.isna(row['alt_text']) or val in ['NULL', '', 'None'] or val.startswith('Error:'):
        
        if str(row['guid']).lower().endswith('.svg'):
            df.at[index, 'alt_text'] = 'Decorative icon'
        else:
            df.at[index, 'alt_text'] = generate_alt_text(row['guid'])
            print(f"\n Generated Alt: {df.at[index, 'alt_text']}")
            
            # THE SECRET SAUCE: 12 seconds is the magic number for Free Tier stability
            time.sleep(12)

    # Backup save every 25 images
    if index % 25 == 0:
        df.to_csv(OUTPUT_FILE, index=False)

# Final Save
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n\nDone! Results saved to: {OUTPUT_FILE}")