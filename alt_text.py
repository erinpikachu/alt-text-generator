import google.generativeai as genai
import pandas as pd
import time
import sys
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()  # This looks for the .env file
API_KEY = os.getenv('GEMINI_API_KEY') # This pulls the key from the .env
INPUT_FILE = 'wordpress_media.csv' 
OUTPUT_FILE = 'wordpress_media_fixed.csv'
# ---------------------

if not API_KEY:
    print("Error: No API Key found in .env file!")
    sys.exit()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_alt_text(url):
    
    try:
        prompt = "Describe this image in one concise sentence for an HTML alt-text attribute. Focus on the subject and context. No intro text."
        response = model.generate_content([prompt, {"url": url}])
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Load data
df = pd.read_csv(INPUT_FILE)

print(f"--- Starting AI Alt-Text Generation for {len(df)} images ---")
print("This will take about 1 hour on the Free Tier. Do not close this window.")

for index, row in df.iterrows():
    # Progress indicator
    percent = round(((index + 1) / len(df)) * 100, 1)
    sys.stdout.write(f"\rProgress: {percent}% [{index+1}/{len(df)}] Processing: {row['post_title'][:30]}...")
    sys.stdout.flush()

    # Check if we actually need to generate one
    needs_alt = (
        pd.isna(row['alt_text'])
        or row['alt_text'] in ['NULL', '', 'None']
        or str(row['alt_text']).startswith('Error:')
    )

    if needs_alt:
        # Skip SVG files — Gemini cannot process vector graphics
        if row['guid'].lower().endswith('.svg'):
            df.at[index, 'alt_text'] = 'Decorative vector graphic'
        else:
            df.at[index, 'alt_text'] = generate_alt_text(row['guid'])
            # Free tier safety delay (prevents 429 Rate Limit errors)
            time.sleep(4)

    # Optional: Save every 50 images so you don't lose progress if the internet cuts out
    if index > 0 and index % 50 == 0:
        df.to_csv(OUTPUT_FILE, index=False)

# Final Save
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n\nSuccess! All {len(df)} rows processed.")
print(f"Results saved to: {OUTPUT_FILE}")