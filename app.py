import streamlit as st
import json
import requests
from base64 import b64decode

# Load phoneme dataset
with open('phoneme_dataset.json', 'r') as f:
    phoneme_dataset = json.load(f)

# Expanded letter-to-phoneme mapping
letter_to_phoneme = {
    'a': ['/a/', '/aː/', '/ɑ/', '/ə/'], 'b': ['/b/', '/bʱ/'], 'c': ['/k/', '/s/', '/tʃ/'],
    'd': ['/d/', '/dʱ/', '/ɖ/', '/dˤ/'], 'e': ['/e/', '/eː/', '/ɛ/', '/ə/'], 'f': ['/f/'],
    'g': ['/g/', '/gʱ/', '/ɣ/'], 'h': ['/h/', '/ħ/', '/ʕ/'], 'i': ['/i/', '/iː/', '/ɪ/', '/ɨ/'],
    'j': ['/j/', '/dʒ/'], 'k': ['/k/', '/kʰ/'], 'l': ['/l/', '/ɭ/'], 'm': ['/m/'],
    'n': ['/n/', '/ɳ/', '/ŋ/'], 'o': ['/o/', '/oː/', '/ɔ/', '/ø/'], 'p': ['/p/', '/pʰ/'],
    'q': ['/q/'], 'r': ['/r/'], 's': ['/s/', '/sˤ/', '/ʃ/'], 't': ['/t/', '/tʰ/', '/ʈ/', '/tˤ/'],
    'u': ['/u/', '/uː/', '/ʊ/', '/ɯ/'], 'v': ['/ʋ/', '/v/'], 'w': ['/w/'], 'x': ['/x/'],
    'y': ['/y/', '/i/'], 'z': ['/z/', '/ʒ/'],
    'ai': ['/ai/'], 'au': ['/au/'], 'sh': ['/ʃ/'], 'ch': ['/tʃ/'], 'th': ['/θ/', '/ð/'],
    'zh': ['/ʒ/'], 'ph': ['/f/'], 'bh': ['/bʱ/'], 'dh': ['/dʱ/', '/ðˤ/'], 'gh': ['/gʱ/', '/ɣ/'],
    'kh': ['/kʰ/', '/x/'], 'ng': ['/ŋ/'], 'oe': ['/ø/', '/œ/'], 'rh': ['/r/'], 'dj': ['/dʒ/'],
    'ts': ['/tʃ/'], 'dz': ['/dʒ/'], 'sch': ['/ʃ/'], 'str': ['/s/', '/t/', '/r/'],
    'spr': ['/s/', '/p/', '/r/'], 'thr': ['/θ/', '/r/'], 'shr': ['/ʃ/', '/r/'],
    'khr': ['/kʰ/', '/r/'], 'ghr': ['/gʱ/', '/r/']
}

# Language-specific phoneme constraints
language_rules = {
    'Sanskrit': {
        'vowels': ['/a/', '/aː/', '/i/', '/iː/', '/u/', '/uː/', '/e/', '/eː/', '/o/', '/oː/', '/ai/', '/au/'],
        'consonants': ['/p/', '/pʰ/', '/b/', '/bʱ/', '/t/', '/tʰ/', '/d/', '/dʱ/', '/ʈ/', '/ɖ/', '/k/', '/kʰ/', '/g/', '/gʱ/', '/m/', '/n/', '/ɳ/', '/s/', '/ʃ/', '/h/', '/l/', '/ɭ/', '/r/', '/ʋ/', '/j/']
    },
    'Hindi': {
        'vowels': ['/a/', '/aː/', '/i/', '/iː/', '/u/', '/uː/', '/e/', '/eː/', '/o/', '/oː/', '/ai/', '/au/'],
        'consonants': ['/p/', '/pʰ/', '/b/', '/bʱ/', '/t/', '/tʰ/', '/d/', '/dʱ/', '/ʈ/', '/ɖ/', '/k/', '/kʰ/', '/g/', '/gʱ/', '/m/', '/n/', '/ɳ/', '/s/', '/ʃ/', '/h/', '/l/', '/ɭ/', '/r/', '/ʋ/', '/j/']
    },
    'Kannada': {
        'vowels': ['/a/', '/aː/', '/i/', '/iː/', '/u/', '/uː/', '/e/', '/eː/', '/o/', '/oː/'],
        'consonants': ['/p/', '/pʰ/', '/b/', '/bʱ/', '/t/', '/tʰ/', '/d/', '/dʱ/', '/ʈ/', '/ɖ/', '/k/', '/kʰ/', '/g/', '/gʱ/', '/m/', '/n/', '/ɳ/', '/s/', '/ʃ/', '/h/', '/l/', '/ɭ/', '/r/', '/ʋ/', '/j/']
    },
    'Arabic': {
        'vowels': ['/a/', '/aː/', '/i/', '/iː/', '/u/', '/uː/'],
        'consonants': ['/p/', '/b/', '/t/', '/d/', '/k/', '/g/', '/q/', '/ʔ/', '/tˤ/', '/dˤ/', '/m/', '/n/', '/s/', '/ʃ/', '/x/', '/ħ/', '/h/', '/ð/', '/z/', '/ɣ/', '/ʕ/', '/sˤ/', '/ðˤ/', '/dʒ/', '/ʒ/', '/l/', '/r/', '/j/', '/w/']
    },
    'English': {
        'vowels': ['/a/', '/e/', '/i/', '/o/', '/u/', '/ɛ/', '/ɔ/', '/ɑ/', '/ɪ/', '/ʊ/', '/ə/', '/ai/', '/au/'],
        'consonants': ['/p/', '/b/', '/t/', '/d/', '/k/', '/g/', '/m/', '/n/', '/ŋ/', '/f/', '/θ/', '/s/', '/ʃ/', '/h/', '/ð/', '/z/', '/dʒ/', '/ʒ/', '/tʃ/', '/l/', '/r/', '/w/', '/j/']
    }
}

# Custom CMU dictionary parser
def load_cmudict():
    """Load CMUdict from cmudict-0.7b file."""
    cmudict = {}
    with open('cmudict-0.7b', 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith(';;;'):
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            word = parts[0].lower()
            phonemes = parts[1:]
            # Remove stress markers (e.g., AA0 → AA)
            phonemes = [p.rstrip('012') for p in phonemes]
            if word not in cmudict:
                cmudict[word] = []
            cmudict[word].append(phonemes)
    return cmudict

# ARPAbet to IPA mapping
arpabet_to_ipa = {
    'AA': '/ɑ/', 'AE': '/æ/', 'AH': '/ə/', 'AO': '/ɔ/',
    'AW': '/au/', 'AY': '/ai/', 'EH': '/ɛ/', 'ER': '/ɚ/',
    'EY': '/eɪ/', 'IH': '/ɪ/', 'IY': '/i/', 'OW': '/oʊ/',
    'OY': '/ɔɪ/', 'UH': '/ʊ/', 'UW': '/u/',
    'P': '/p/', 'B': '/b/', 'T': '/t/', 'D': '/d/',
    'K': '/k/', 'G': '/g/', 'M': '/m/', 'N': '/n/',
    'NG': '/ŋ/', 'F': '/f/', 'V': '/v/', 'TH': '/θ/',
    'DH': '/ð/', 'S': '/s/', 'Z': '/z/', 'SH': '/ʃ/',
    'ZH': '/ʒ/', 'CH': '/tʃ/', 'JH': '/dʒ/', 'L': '/l/',
    'R': '/r/', 'W': '/w/', 'Y': '/j/', 'HH': '/h/'
}

# Load CMUdict once
cmudict = load_cmudict()

def get_phonemes(name, language):
    """Extract phonemes based on language."""
    phonemes = []
    name = name.lower().strip()
    
    if language == 'English':
        # Use custom CMUdict parser
        if name in cmudict:
            # Take the first pronunciation
            arpabet_phones = cmudict[name][0]
            for phone in arpabet_phones:
                ipa_phone = arpabet_to_ipa.get(phone, '/ə/')
                if ipa_phone in [entry['Phoneme'] for entry in phoneme_dataset]:
                    phonemes.append(ipa_phone)
        else:
            phonemes = letter_based_phoneme_mapping(name, language)
    else:
        phonemes = letter_based_phoneme_mapping(name, language)
    
    return list(set(phonemes))

def letter_based_phoneme_mapping(name, language):
    """Map letters to phonemes, prioritizing longer matches."""
    phonemes = []
    i = 0
    while i < len(name):
        matched = False
        if i + 2 < len(name) and name[i:i+3] in letter_to_phoneme:
            candidates = letter_to_phoneme[name[i:i+3]]
            valid_phonemes = [p for p in candidates if p in language_rules[language]['vowels'] or p in language_rules[language]['consonants']]
            phonemes.extend(valid_phonemes)
            i += 3
            matched = True
        elif i + 1 < len(name) and name[i:i+2] in letter_to_phoneme:
            candidates = letter_to_phoneme[name[i:i+2]]
            valid_phonemes = [p for p in candidates if p in language_rules[language]['vowels'] or p in language_rules[language]['consonants']]
            phonemes.extend(valid_phonemes)
            i += 2
            matched = True
        elif name[i] in letter_to_phoneme:
            candidates = letter_to_phoneme[name[i]]
            valid_phonemes = [p for p in candidates if p in language_rules[language]['vowels'] or p in language_rules[language]['consonants']]
            phonemes.extend(valid_phonemes)
            i += 1
            matched = True
        else:
            i += 1
        if not matched:
            i += 1
    return list(set(phonemes))

def get_phoneme_attributes(phonemes):
    """Retrieve attributes for the phonemes."""
    attributes = []
    for phoneme in phonemes:
        for entry in phoneme_dataset:
            if entry['Phoneme'] == phoneme:
                attributes.append(entry)
                break
    return attributes

def select_lore_template(attributes):
    """Select a lore template based on dominant Bhava."""
    if not attributes:
        return 'Sage'
    bhavas = [attr['Bhava'] for attr in attributes]
    bhava_counts = {'Power': 0, 'Compassion': 0, 'Creativity': 0, 'Stability': 0, 'Expression': 0, 'Intuition': 0}
    for bhava in bhavas:
        if bhava in bhava_counts:
            bhava_counts[bhava] += 1
    dominant_bhava = max(bhava_counts, key=bhava_counts.get)
    if dominant_bhava == 'Power':
        return 'Warrior'
    elif dominant_bhava in ['Compassion', 'Intuition']:
        return 'Sage'
    elif dominant_bhava in ['Creativity', 'Expression']:
        return 'Trickster'
    return 'Sage'

def generate_lore_with_grok(name, attributes, template, api_key):
    """Generate lore using Grok LLM API."""
    chakras = list(set(attr['Chakra'] for attr in attributes))
    elements = list(set(attr['Element'] for attr in attributes))
    bhavas = list(set(attr['Bhava'] for attr in attributes))
    rasas = list(set(attr['Rasa'] for attr in attributes))
    phonemes = [attr['Phoneme'] for attr in attributes]
    
    if template == 'Warrior':
        prompt = f"Create a fantastical, mythical lore (400-600 words) for a warrior named {name}. Their name's sounds ({', '.join(phonemes)}) evoke {', '.join(bhavas)} and are tied to {', '.join(chakras)} chakras and {', '.join(elements)} elements. Weave a tale of epic battles, divine weapons, and a quest to restore balance, infused with {', '.join(rasas)} emotions. Include cultural notes: {'; '.join(attr['Cultural Notes'] for attr in attributes)}."
    elif template == 'Sage':
        prompt = f"Create a fantastical, mythical lore (400-600 words) for a sage named {name}. Their name's sounds ({', '.join(phonemes)}) resonate with {', '.join(bhavas)}, linked to {', '.join(chakras)} chakras and {', '.join(elements)} elements. Craft a story of wisdom, ancient prophecies, and spiritual guidance, filled with {', '.join(rasas)} emotions. Include cultural notes: {'; '.join(attr['Cultural Notes'] for attr in attributes)}."
    else:  # Trickster
        prompt = f"Create a fantastical, mythical lore (400-600 words) for a trickster named {name}. Their name's sounds ({', '.join(phonemes)}) embody {', '.join(bhavas)}, connected to {', '.join(chakras)} chakras and {', '.join(elements)} elements. Spin a tale of cunning, magical pranks, and unexpected heroism, infused with {', '.join(rasas)} emotions. Include cultural notes: {'; '.join(attr['Cultural Notes'] for attr in attributes)}."
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'grok-3',
        'prompt': prompt,
        'max_tokens': 800,
        'temperature': 0.7
    }
    
    try:
        response = requests.post('https://api.x.ai/v1/completions', headers=headers, json=payload)
        response.raise_for_status()
        lore = response.json()['choices'][0]['text'].strip()
        return lore
    except Exception as e:
        return f"Error generating lore: {str(e)}"

def generate_image(name, attributes, template, api_key):
    """Generate a mythical portrait using Grok Image Generation API."""
    elements = list(set(attr['Element'].lower() for attr in attributes))
    
    if template == 'Warrior':
        prompt = f"A majestic portrait of {name}, a fierce warrior in ornate armor, wielding a glowing divine weapon, standing on a battlefield with {', '.join(elements)}. Mythical, vibrant, epic."
    elif template == 'Sage':
        prompt = f"A serene portrait of {name}, a wise sage in flowing robes, surrounded by glowing runes and {', '.join(elements)}, meditating in an ancient temple. Mystical, ethereal."
    else:  # Trickster
        prompt = f"A whimsical portrait of {name}, a cunning trickster with a mischievous grin, juggling magical orbs of {', '.join(elements)}, in a vibrant, enchanted forest. Playful, fantastical."
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt,
        'model': 'flux-1',
        'width': 512,
        'height': 512
    }
    
    try:
        response = requests.post('https://api.x.ai/v1/images/generations', headers=headers, json=payload)
        response.raise_for_status()
        image_data = response.json()['data'][0]['b64_json']
        return b64decode(image_data)
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Streamlit app
st.title("Mythical Lore & Portrait Generator")
st.write("Enter a name and select its language to unveil a fantastical tale and a mythical portrait, woven from ancient sounds and cosmic energies.")

# Input form
with st.form("lore_form"):
    name = st.text_input("Enter a name:", placeholder="e.g., Arjun, Aisha, Emma, Mallappa")
    language = st.selectbox("Select language of the name:", ["English", "Sanskrit", "Hindi", "Kannada", "Arabic"])
    api_key = st.text_input("Enter your xAI API key:", type="password")
    submitted = st.form_submit_button("Generate Lore & Portrait")

if submitted:
    if not name or not api_key:
        st.error("Please provide a name and xAI API key.")
    else:
        # Process the name
        phonemes = get_phonemes(name, language)
        attributes = get_phoneme_attributes(phonemes)
        template = select_lore_template(attributes)
        
        # Generate lore
        st.subheader(f"The Mythical Lore of {name} ({template})")
        with st.spinner("Weaving the cosmic tale..."):
            lore = generate_lore_with_grok(name, attributes, template, api_key)
            st.write(lore)
        
        # Generate image
        st.subheader(f"Portrait of {name}")
        with st.spinner("Painting the mythical visage..."):
            image_data = generate_image(name, attributes, template, api_key)
            if image_data:
                st.image(image_data, caption=f"{name}, the {template}")
        
        # Display phoneme details
        if phonemes:
            st.subheader("Phonemes Detected")
            st.write(", ".join(phonemes))
            st.subheader("Phoneme Attributes")
            for attr in attributes:
                st.write(f"**{attr['Phoneme']}**: {attr['Cultural Notes']} (Chakra: {attr['Chakra']}, Element: {attr['Element']}, Bhava: {attr['Bhava']}, Rasa: {attr['Rasa']})")
        else:
            st.warning("No phonemes matched. The lore and image may be limited.")
