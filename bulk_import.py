#!/usr/bin/env python3
"""
Bulk Import Script for Italian Vocabulary
Adds multiple words to the spaced repetition system at once
"""

import requests
import json
import time
from typing import List, Dict, Optional

# Configuration
API_BASE_URL = "http://100.107.135.85:5000"  # Change this to your server URL
LIBRE_TRANSLATE_URL = "https://libretranslate.de/translate"

def detect_word_type(word: str) -> str:
    """Detect the word type based on Italian grammar patterns"""
    word_lower = word.lower()
    
    # Verbs
    if word_lower.endswith(('are', 'ere', 'ire')):
        return 'verb'
    
    # Adjectives (common endings)
    if word_lower.endswith(('o', 'a', 'e', 'i')):
        if word_lower.endswith(('o', 'a')):
            return 'adjective'
        else:
            return 'noun'
    
    # Prepositions
    prepositions = ['di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'sopra', 'sotto', 'dentro', 'fuori']
    if word_lower in prepositions:
        return 'preposition'
    
    # Conjunctions
    conjunctions = ['e', 'o', 'ma', 'se', 'che', 'perché', 'quando', 'dove', 'come', 'mentre', 'prima', 'dopo']
    if word_lower in conjunctions:
        return 'conjunction'
    
    # Pronouns
    pronouns = ['io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mi', 'ti', 'ci', 'vi', 'si', 'questo', 'quello', 'chi', 'che']
    if word_lower in pronouns:
        return 'pronoun'
    
    # Adverbs
    adverbs = ['molto', 'poco', 'bene', 'male', 'qui', 'là', 'oggi', 'ieri', 'domani', 'sempre', 'mai', 'ancora', 'già', 'subito']
    if word_lower in adverbs:
        return 'adverb'
    
    # Interjections
    interjections = ['ciao', 'ehi', 'oh', 'ah', 'ecco', 'addio', 'salve', 'buongiorno', 'buonanotte']
    if word_lower in interjections:
        return 'interjection'
    
    # Default to noun
    return 'noun'

def generate_example(word: str, word_type: str) -> str:
    """Generate a simple example sentence for the word"""
    if word_type == 'verb':
        if word.endswith('are'):
            return f"Voglio {word}."
        elif word.endswith('ere'):
            return f"Devo {word}."
        elif word.endswith('ire'):
            return f"Posso {word}."
        else:
            return f"Uso {word} spesso."
    
    elif word_type == 'noun':
        if word.endswith('a'):
            return f"Questa è una {word}."
        elif word.endswith('o'):
            return f"Questo è un {word}."
        else:
            return f"Questo è un {word}."
    
    elif word_type == 'adjective':
        return f"È molto {word}."
    
    elif word_type == 'adverb':
        return f"Lo fa {word}."
    
    elif word_type == 'preposition':
        return f"Vado {word} casa."
    
    elif word_type == 'conjunction':
        return f"Voglio {word} non posso."
    
    elif word_type == 'pronoun':
        return f"Ho visto {word}."
    
    else:
        return f"Uso {word} spesso."

def translate_word(word: str) -> Optional[str]:
    """Translate Italian word to English using multiple fallback methods"""
    
    # Method 1: Try LibreTranslate
    try:
        response = requests.post(
            LIBRE_TRANSLATE_URL,
            json={
                'q': word,
                'source': 'it',
                'target': 'en',
                'format': 'text'
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            translation = data.get('translatedText', '')
            if translation and translation != word:
                print(f"  🌐 LibreTranslate: {word} -> {translation}")
                return translation
    except Exception as e:
        print(f"  ⚠️  LibreTranslate failed: {e}")
    
    # Method 2: Try Google Translate (free alternative)
    try:
        google_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'it',
            'tl': 'en',
            'dt': 't',
            'q': word
        }
        
        response = requests.get(google_url, params=params, timeout=15)
        if response.status_code == 200:
            # Parse Google Translate response
            data = response.json()
            if data and len(data) > 0 and len(data[0]) > 0:
                translation = data[0][0][0]
                if translation and translation != word:
                    print(f"  🌐 Google Translate: {word} -> {translation}")
                    return translation
    except Exception as e:
        print(f"  ⚠️  Google Translate failed: {e}")
    
    # Method 3: Basic Italian-English dictionary for common words
    basic_translations = {
        # Common greetings
        'ciao': 'hello/hi',
        'buongiorno': 'good morning',
        'buonasera': 'good evening',
        'buonanotte': 'good night',
        'salve': 'hello',
        'addio': 'goodbye',
        
        # Common expressions
        'grazie': 'thank you',
        'prego': 'you\'re welcome',
        'scusa': 'sorry/excuse me',
        'per favore': 'please',
        'sì': 'yes',
        'no': 'no',
        
        # Basic pronouns
        'io': 'I',
        'tu': 'you',
        'lui': 'he',
        'lei': 'she',
        'noi': 'we',
        'voi': 'you (plural)',
        'loro': 'they',
        
        # Basic verbs
        'essere': 'to be',
        'avere': 'to have',
        'fare': 'to do/make',
        'andare': 'to go',
        'venire': 'to come',
        'stare': 'to stay/be',
        'volere': 'to want',
        'potere': 'can/be able to',
        'dovere': 'must/have to',
        
        # Basic nouns
        'casa': 'house/home',
        'lavoro': 'work',
        'scuola': 'school',
        'famiglia': 'family',
        'amore': 'love',
        'tempo': 'time/weather',
        'giorno': 'day',
        'notte': 'night',
        'acqua': 'water',
        'cibo': 'food',
        
        # Basic adjectives
        'bello': 'beautiful/nice',
        'brutto': 'ugly',
        'grande': 'big/large',
        'piccolo': 'small/little',
        'buono': 'good',
        'cattivo': 'bad',
        'nuovo': 'new',
        'vecchio': 'old',
        'giovane': 'young',
        
        # Basic prepositions
        'di': 'of/from',
        'a': 'to/at',
        'da': 'from/by',
        'in': 'in',
        'con': 'with',
        'su': 'on/up',
        'per': 'for',
        'tra': 'between',
        'fra': 'between',
        
        # Basic conjunctions
        'e': 'and',
        'o': 'or',
        'ma': 'but',
        'se': 'if',
        'che': 'that/which',
        'perché': 'because/why',
        'quando': 'when',
        'dove': 'where',
        'come': 'how/like',
        
        # Basic adverbs
        'molto': 'very/much',
        'poco': 'little/few',
        'bene': 'well',
        'male': 'badly',
        'qui': 'here',
        'là': 'there',
        'oggi': 'today',
        'ieri': 'yesterday',
        'domani': 'tomorrow',
        'sempre': 'always',
        'mai': 'never',
        'ancora': 'still/yet',
        'già': 'already',
        'subito': 'immediately',
        
        # Common interjections
        'ehi': 'hey',
        'oh': 'oh',
        'ah': 'ah',
        'ecco': 'here/there',
        'addio': 'goodbye',
        
        # Numbers
        'uno': 'one',
        'due': 'two',
        'tre': 'three',
        'quattro': 'four',
        'cinque': 'five',
        'sei': 'six',
        'sette': 'seven',
        'otto': 'eight',
        'nove': 'nine',
        'dieci': 'ten',
        
        # Colors
        'rosso': 'red',
        'blu': 'blue',
        'verde': 'green',
        'giallo': 'yellow',
        'nero': 'black',
        'bianco': 'white',
        'grigio': 'gray',
        'marrone': 'brown',
        'rosa': 'pink',
        'arancione': 'orange',
        'viola': 'purple'
    }
    
    word_lower = word.lower()
    if word_lower in basic_translations:
        translation = basic_translations[word_lower]
        print(f"  📚 Dictionary: {word} -> {translation}")
        return translation
    
    # Method 4: Try to guess based on word similarity to English
    # Many Italian words are similar to English
    english_similarities = {
        'azione': 'action',
        'attività': 'activity',
        'bella': 'beautiful',
        'camera': 'room',
        'centro': 'center',
        'città': 'city',
        'classe': 'class',
        'colore': 'color',
        'comunità': 'community',
        'condizione': 'condition',
        'conferenza': 'conference',
        'confronto': 'confrontation',
        'congresso': 'congress',
        'conseguenza': 'consequence',
        'considerazione': 'consideration',
        'costruzione': 'construction',
        'creazione': 'creation',
        'cultura': 'culture',
        'decisione': 'decision',
        'definizione': 'definition',
        'descrizione': 'description',
        'destinazione': 'destination',
        'determinazione': 'determination',
        'differenza': 'difference',
        'direzione': 'direction',
        'distruzione': 'destruction',
        'educazione': 'education',
        'esistenza': 'existence',
        'esperienza': 'experience',
        'espressione': 'expression',
        'famiglia': 'family',
        'formazione': 'formation',
        'fortuna': 'fortune',
        'funzione': 'function',
        'generazione': 'generation',
        'gestione': 'management',
        'identità': 'identity',
        'immagine': 'image',
        'importanza': 'importance',
        'informazione': 'information',
        'intenzione': 'intention',
        'interesse': 'interest',
        'interpretazione': 'interpretation',
        'introduzione': 'introduction',
        'investigazione': 'investigation',
        'lavoro': 'work',
        'libertà': 'liberty',
        'materia': 'matter/material',
        'memoria': 'memory',
        'missione': 'mission',
        'natura': 'nature',
        'necessità': 'necessity',
        'notizia': 'news',
        'occasione': 'occasion',
        'opinione': 'opinion',
        'organizzazione': 'organization',
        'partecipazione': 'participation',
        'passione': 'passion',
        'paura': 'fear',
        'pensiero': 'thought',
        'perdita': 'loss',
        'persona': 'person',
        'possibilità': 'possibility',
        'posizione': 'position',
        'potere': 'power',
        'preparazione': 'preparation',
        'presenza': 'presence',
        'previsione': 'forecast',
        'produzione': 'production',
        'professione': 'profession',
        'progetto': 'project',
        'proposito': 'purpose',
        'protezione': 'protection',
        'qualità': 'quality',
        'quantità': 'quantity',
        'questione': 'question',
        'rapporto': 'report/relationship',
        'realizzazione': 'realization',
        'regione': 'region',
        'relazione': 'relationship',
        'responsabilità': 'responsibility',
        'risposta': 'response',
        'situazione': 'situation',
        'soluzione': 'solution',
        'speranza': 'hope',
        'storia': 'history/story',
        'struttura': 'structure',
        'suggestione': 'suggestion',
        'superficie': 'surface',
        'tendenza': 'tendency',
        'tradizione': 'tradition',
        'trasformazione': 'transformation',
        'trattamento': 'treatment',
        'utilizzazione': 'utilization',
        'valore': 'value',
        'varietà': 'variety',
        'verità': 'truth',
        'vittoria': 'victory',
        'vita': 'life'
    }
    
    if word_lower in english_similarities:
        translation = english_similarities[word_lower]
        print(f"  🔍 Similarity: {word} -> {translation}")
        return translation
    
    # Method 5: Try to remove common Italian endings to find English root
    word_stems = [
        (word_lower[:-3], 'are'),  # Remove -are (verb)
        (word_lower[:-3], 'ere'),  # Remove -ere (verb)
        (word_lower[:-3], 'ire'),  # Remove -ire (verb)
        (word_lower[:-2], 're'),   # Remove -re (verb)
        (word_lower[:-1], 'a'),    # Remove -a (feminine)
        (word_lower[:-1], 'o'),    # Remove -o (masculine)
        (word_lower[:-1], 'e'),    # Remove -e (plural)
        (word_lower[:-1], 'i'),    # Remove -i (plural)
    ]
    
    for stem, ending in word_stems:
        if stem in basic_translations:
            translation = basic_translations[stem]
            print(f"  🔍 Stem match: {word} -> {translation} (removed -{ending})")
            return translation
    
    # Final fallback: return the word with a note
    print(f"  ❌ No translation found for: {word}")
    return f"[Italian: {word}]"

def check_word_exists(word: str) -> bool:
    """Check if a word already exists in the vocabulary"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/sr/words", timeout=10)
        if response.status_code == 200:
            data = response.json()
            existing_words = [w['word'].lower() for w in data.get('words', [])]
            return word.lower() in existing_words
        else:
            print(f"  ⚠️  Could not check for duplicates: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ⚠️  Error checking for duplicates: {e}")
        return False

def add_word_to_vocabulary(word: str, translation: str, word_type: str, example: str) -> bool:
    """Add a single word to the vocabulary via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/sr/words",
            json={
                'word': word,
                'translation': translation,
                'word_type': word_type,
                'example': example,
                'notes': 'Bulk imported'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Added: {word} -> {translation} ({word_type})")
            return True
        else:
            print(f"❌ Failed to add '{word}': {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding '{word}': {e}")
        return False

def bulk_import_words(words: List[str], delay: float = 0.1) -> Dict[str, int]:
    """
    Bulk import a list of Italian words
    
    Args:
        words: List of Italian words to import
        delay: Delay between API calls (seconds) to avoid overwhelming the server
    
    Returns:
        Dictionary with success/failure counts
    """
    print(f"🚀 Starting bulk import of {len(words)} words...")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"⏱️  Delay between requests: {delay}s")
    print("-" * 50)
    
    success_count = 0
    failure_count = 0
    skipped_count = 0
    processed_words = set()  # Track words processed in this session
    
    for i, word in enumerate(words, 1):
        word = word.strip()
        if not word:
            continue
            
        print(f"\n[{i}/{len(words)}] Processing: {word}")
        
        # Skip if word is too short or contains invalid characters
        if len(word) < 2:
            print(f"⚠️  Skipping '{word}': too short")
            skipped_count += 1
            continue
        
        # Skip if word was already processed in this session
        if word.lower() in processed_words:
            print(f"  ⏭️  Skipping '{word}': duplicate in word list")
            skipped_count += 1
            continue
        
        # Mark word as processed
        processed_words.add(word.lower())
        
        # Detect word type
        word_type = detect_word_type(word)
        
        # Check if word already exists
        if check_word_exists(word):
            print(f"  ⏭️  Skipping '{word}': already exists in vocabulary")
            skipped_count += 1
            continue
        
        # Get translation
        translation = translate_word(word)
        if not translation:
            print(f"⚠️  Skipping '{word}': translation failed")
            skipped_count += 1
            continue
        
        # Skip if translation is just a placeholder
        if translation.startswith('[Italian:') and translation.endswith(']'):
            print(f"⚠️  Skipping '{word}': no translation available")
            skipped_count += 1
            continue
        
        # Generate example
        example = generate_example(word, word_type)
        
        # Add to vocabulary
        if add_word_to_vocabulary(word, translation, word_type, example):
            success_count += 1
        else:
            failure_count += 1
        
        # Add delay to avoid overwhelming the server
        if i < len(words):  # Don't delay after the last word
            time.sleep(delay)
    
    print("\n" + "=" * 50)
    print("📊 BULK IMPORT COMPLETED")
    print(f"✅ Successfully added: {success_count}")
    print(f"❌ Failed to add: {failure_count}")
    print(f"⚠️  Skipped: {skipped_count}")
    print(f"📝 Total processed: {len(words)}")
    
    return {
        'success': success_count,
        'failure': failure_count,
        'skipped': skipped_count,
        'total': len(words)
    }

def load_words_from_file(filename: str) -> List[str]:
    """Load words from a text file (one word per line)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        print(f"📁 Loaded {len(words)} words from {filename}")
        return words
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def main():
    """Main function - handles command line arguments and runs bulk import"""
    import sys
    
    print("🇮🇹 Italian Vocabulary Bulk Import Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python bulk_import.py <words_file> [delay]")
        print("  words_file: Text file with one Italian word per line")
        print("  delay: Optional delay between requests (default: 0.1 seconds)")
        print("\nExample: python bulk_import.py italian_words.txt 0.2")
        return
    
    filename = sys.argv[1]
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
    
    # Load words from file
    words = load_words_from_file(filename)
    if not words:
        print("❌ No words to import. Exiting.")
        return
    
    # Confirm before starting
    print(f"\n📋 Ready to import {len(words)} words")
    print(f"⏱️  Estimated time: {len(words) * delay:.1f} seconds")
    
    confirm = input("\nProceed with import? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Import cancelled.")
        return
    
    # Run bulk import
    results = bulk_import_words(words, delay)
    
    # Final summary
    if results['success'] > 0:
        print(f"\n🎉 Successfully imported {results['success']} words!")
        print("You can now use these words in your Italian AI tutor conversations.")
    else:
        print("\n😞 No words were successfully imported. Please check the errors above.")

if __name__ == "__main__":
    main()
