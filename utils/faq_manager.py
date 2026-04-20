import json
import os
import uuid
from datetime import datetime

FAQ_JSON_PATH = 'data/uploaded_faqs.json'

def load_uploaded_faqs():
    """Load all uploaded FAQs from JSON file"""
    if not os.path.exists(FAQ_JSON_PATH):
        return []

    try:
        with open(FAQ_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('faqs', [])
    except Exception as e:
        print(f"Error loading FAQs: {e}")
        return []

def save_faq_json(faqs):
    """Save FAQs to JSON file"""
    os.makedirs(os.path.dirname(FAQ_JSON_PATH), exist_ok=True)

    try:
        with open(FAQ_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({'faqs': faqs}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving FAQs: {e}")
        return False

def add_faq(faq_data, original_filename='Unknown', category='User Uploaded'):
    """
    Add a new FAQ to the JSON file
    faq_data can be a string (old format) or dict with 'q', 'a', 'section' (new format)
    """
    faqs = load_uploaded_faqs()

    # Handle both old string format and new dict format
    if isinstance(faq_data, str):
        # Old format: just text
        text = faq_data
        q_text = "FAQ"
        a_text = text[:100]
    else:
        # New format: dict with question and answer
        q_text = faq_data.get('q', 'FAQ')
        a_text = faq_data.get('a', '')
        section = faq_data.get('section', 'User Uploaded')
        text = f"Q: {q_text}\nA: {a_text}"

    new_faq = {
        'id': str(uuid.uuid4()),
        'category': category,
        'text': text,
        'original_filename': original_filename,
        'uploaded_date': datetime.now().strftime('%Y-%m-%d'),
        'question': q_text if isinstance(faq_data, dict) else None,
        'answer': a_text if isinstance(faq_data, dict) else None,
        'section': faq_data.get('section', 'General') if isinstance(faq_data, dict) else 'General',
    }

    faqs.append(new_faq)
    save_faq_json(faqs)
    return new_faq

def delete_faq(faq_id):
    """Delete an FAQ by ID"""
    faqs = load_uploaded_faqs()
    faqs = [f for f in faqs if f['id'] != faq_id]
    save_faq_json(faqs)
    return True

def edit_faq(faq_id, updated_text):
    """Edit an FAQ's text"""
    faqs = load_uploaded_faqs()
    for faq in faqs:
        if faq['id'] == faq_id:
            faq['text'] = updated_text
            break
    save_faq_json(faqs)
    return True

def get_faq_by_id(faq_id):
    """Get a single FAQ by ID"""
    faqs = load_uploaded_faqs()
    for faq in faqs:
        if faq['id'] == faq_id:
            return faq
    return None

def extract_faqs_from_text(text):
    """
    Extract FAQ entries from text using intelligent chunking.
    Supports multiple formats:
    1. Q[num].[num]: ... A: ... pattern (numbered FAQs)
    2. Plain Q&A where questions end with "?" (simple Q&A)
    """
    import re

    # First, try detecting which format is used
    if re.search(r'^Q\d+\.\d+:', text, re.MULTILINE):
        # Format 1: Numbered Q1.1 pattern
        return _extract_numbered_faqs(text)
    else:
        # Format 2: Simple Q&A with questions ending in "?"
        return _extract_simple_faqs(text)


def _extract_numbered_faqs(text):
    """Extract FAQ entries with Q[num].[num]: pattern"""
    import re
    faqs = []
    lines = text.split('\n')

    # Skip table of contents
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^Q\d+\.\d+:', line.strip()):
            start_idx = i
            break
    lines = lines[start_idx:]

    current_q = None
    current_a = None
    current_section = 'General'

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Detect section headers
        if re.match(r'^[A-Z][A-Za-z\s&\-\/\(\)]+$', line_stripped) and ':' not in line_stripped:
            if line_stripped and len(line_stripped) < 50:
                current_section = line_stripped
                continue

        # Detect Q&A pattern: Q[num].[num]:
        q_match = re.match(r'^Q\d+\.\d+:\s*(.+)$', line_stripped)
        if q_match:
            # Save previous Q&A
            if current_q and current_a:
                faqs.append({
                    'section': current_section,
                    'q': current_q.strip(),
                    'a': current_a.strip()
                })
            current_q = q_match.group(1)
            current_a = None
        # Detect answer pattern
        elif line_stripped.startswith('A:'):
            current_a = line_stripped[2:].strip()
        elif current_q and current_a is None:
            current_q += ' ' + line_stripped
        elif current_a is not None:
            current_a += ' ' + line_stripped

    # Save last Q&A
    if current_q and current_a:
        faqs.append({
            'section': current_section,
            'q': current_q.strip(),
            'a': current_a.strip()
        })

    return faqs


def _extract_simple_faqs(text):
    """Extract FAQ entries where questions end with '?'"""
    import re
    faqs = []
    lines = text.split('\n')

    current_q = None
    current_a_lines = []

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            continue

        # Detect question (ends with ?)
        if line_stripped.endswith('?'):
            # Save previous Q&A if exists
            if current_q and current_a_lines:
                answer_text = ' '.join(current_a_lines).strip()
                if answer_text:  # Only save if there's actual answer content
                    faqs.append({
                        'section': 'General',
                        'q': current_q.strip(),
                        'a': answer_text
                    })

            # Start new Q&A
            current_q = line_stripped
            current_a_lines = []
        elif current_q:
            # This is part of the answer
            current_a_lines.append(line_stripped)

    # Save last Q&A
    if current_q and current_a_lines:
        answer_text = ' '.join(current_a_lines).strip()
        if answer_text:
            faqs.append({
                'section': 'General',
                'q': current_q.strip(),
                'a': answer_text
            })

    return faqs
