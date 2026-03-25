# WordPress Image Alt-Text Generator

Automatically generates SEO-friendly alt text for WordPress media library images using Google Gemini AI. Takes a CSV export from WordPress, fills in missing alt text with AI-generated descriptions, and outputs a new CSV ready to import back.

---

## How It Works

1. Reads `wordpress_media.csv` (exported from your WordPress media library)
2. For each image where `alt_text` is `NULL`, empty, or missing, it:
   - Sends the image URL to Google Gemini 2.0 Flash
   - Gets back a concise, descriptive sentence for the HTML `alt` attribute
3. Saves progress to `wordpress_media_fixed.csv` every 50 images (crash protection)
4. Skips images that already have alt text — safe to re-run

---

## Setup

### 1. Prerequisites

- Python 3.9+
- A Google Gemini API key (free tier works — get one at [aistudio.google.com](https://aistudio.google.com))

### 2. Install dependencies

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install required packages
pip install google-generativeai pandas python-dotenv
```

### 3. Create your `.env` file

Create a file named `.env` in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

**Never commit this file.** Add `.env` to your `.gitignore`.

### 4. Prepare your CSV

Export your WordPress media library as a CSV with these columns:

| Column | Description |
|---|---|
| `ID` | WordPress attachment post ID |
| `post_title` | Image filename/title |
| `guid` | Full public URL to the image |
| `alt_text` | Existing alt text (use `NULL` for missing) |

Place the file in the project root as `wordpress_media.csv`.

---

## Usage

```bash
python alt_text.py
```

The script will show live progress:

```
--- Starting AI Alt-Text Generation for 312 images ---
This will take about 1 hour on the Free Tier. Do not close this window.
Progress: 14.4% [45/312] Processing: tlc-contact-hero-bg-d...
```

Output is saved to `wordpress_media_fixed.csv`.

---

## Notes

- **Rate limiting:** The script pauses 4 seconds between API calls to stay within the Gemini free tier limits (15 requests/minute). On the free tier, ~300 images takes roughly 20–30 minutes.
- **SVG files:** Gemini cannot process SVG vector files. These rows will receive an error value in the output — review and handle them manually.
- **Re-running:** The script skips rows that already have alt text, so it is safe to stop and restart. Rows where generation failed (containing `"Error:"`) will not be automatically retried — clear those cells manually before re-running if needed.
- **Progress saves:** The CSV is saved every 50 processed images, so you won't lose more than 50 entries if the script is interrupted.

---

## Importing Back to WordPress

After running the script, use a plugin like **WP All Import** or a custom WP-CLI script to update the `_wp_attachment_image_alt` postmeta field for each attachment using the `ID` and `alt_text` columns from `wordpress_media_fixed.csv`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-generativeai` | Gemini AI API client |
| `pandas` | CSV reading and writing |
| `python-dotenv` | Loads API key from `.env` file |
