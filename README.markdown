# Phoneme Lore & Portrait Generator

A Streamlit app that generates mythical lore and portraits for a given name based on its phonemes, using xAI's Grok LLM and Image Generation APIs.

## Features
- **Phoneme Mapping**: Uses `pronouncing` for English and custom rules for Sanskrit, Hindi, Kannada, and Arabic.
- **Dynamic Lore**: Warrior, Sage, or Trickster templates based on phoneme attributes.
- **Multilingual Support**: Supports English, Sanskrit, Hindi, Kannada, and Arabic.
- **Image Generation**: Creates mythical portraits via xAI's API.
- **Grok LLM**: Generates rich, fantastical lore (400–600 words).

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/phoneme_lore_app.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For local testing, create `.streamlit/secrets.toml` with your xAI API key:
   ```toml
   [XAI]
   api_key = "your_xai_api_key_here"
   ```
4. Run the app locally:
   ```bash
   streamlit run app.py
   ```

## Deployment
1. Create a public GitHub repository and push the files (exclude `.streamlit/secrets.toml`).
2. Deploy on Streamlit Cloud:
   - Sign in at [Streamlit Community Cloud](https://streamlit.io/cloud).
   - Select the repository and set `app.py` as the main file.
   - Deploy and access the app via the provided URL.

## Files
- `app.py`: Main Streamlit app.
- `phoneme_dataset.json`: Phoneme dataset with attributes.
- `requirements.txt`: Dependencies.
- `README.md`: This file.
- `.streamlit/secrets.toml`: Local API key storage (not for GitHub).

## Usage
1. Enter a name (e.g., Arjun, Aisha, Mallappa).
2. Select the language (English, Sanskrit, Hindi, Kannada, Arabic).
3. Provide your xAI API key.
4. Click "Generate Lore & Portrait" to view the mythical lore and portrait.

## Notes
- Requires an xAI API key for Grok LLM and Image Generation APIs (see [xAI API](https://x.ai/api)).
- The app prompts for the API key to avoid exposing it in the public repository.
- Test with names like "Mallappa" (Kannada) or "Christopher" (English) to verify phoneme mapping.

## Example
**Input**: Name: Mallappa, Language: Kannada
**Phonemes**: /m/, /a/, /aː/, /l/, /ɭ/, /p/
**Lore**: A sage born under the Muladhara chakra, wielding Earth's stability...
**Portrait**: A serene sage in an ancient temple with earthy elements.