from flask import Flask, render_template, request, jsonify
import openpyxl
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq client with error handling
client = None
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    client = Groq(api_key=api_key)
    print("✓ Groq API available")
except Exception as e:
    print(f"Warning: Groq initialization failed: {e}")
    print("Set GROQ_API_KEY environment variable to use the bot")

# Load Excel templates
def load_templates():
    """Load Bursary templates organized by subcategories"""
    wb = openpyxl.load_workbook('data/TEMPLATE_Replies Catergorisation.xlsx')
    ws = wb['Bursary']

    templates = {}

    # Row 2 contains category names
    category_row = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]

    # Extract categories and their column indices
    categories = {}
    for col_idx, category in enumerate(category_row):
        if category:
            categories[col_idx] = category

    # Initialize category lists
    for cat in categories.values():
        templates[cat] = []

    # Extract templates from rows 3 onwards
    for row in ws.iter_rows(min_row=3, values_only=True):
        for col_idx, category in categories.items():
            cell_value = row[col_idx]
            if cell_value and isinstance(cell_value, str) and len(cell_value.strip()) > 20:
                templates[category].append(cell_value.strip())

    return templates

# Initialize templates
TEMPLATES = load_templates()

# Flatten all templates for easier searching with category info
ALL_TEMPLATES = []
for category, texts in TEMPLATES.items():
    for text in texts:
        ALL_TEMPLATES.append({
            'category': category,
            'text': text
        })

from difflib import SequenceMatcher

def find_best_template(faq):
    """Use Groq to find the best matching Bursary template for a FAQ"""

    # Calculate similarity scores for each template
    template_scores = []
    faq_lower = faq.lower()

    for template in ALL_TEMPLATES:
        template_text = template['text'].lower()
        # Simple similarity: count matching words
        faq_words = set(faq_lower.split())
        template_words = set(template_text.split())

        # Calculate overlap
        overlap = len(faq_words & template_words)

        template_scores.append({
            'template': template,
            'score': overlap
        })

    # Sort by relevance score (highest first) and take top 20
    sorted_templates = sorted(template_scores, key=lambda x: x['score'], reverse=True)[:20]

    # Create a formatted list of top templates
    templates_text = "\n\n---\n\n".join([
        f"[{t['template']['category']}]\n{t['template']['text']}"
        for t in sorted_templates
    ])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f"""You are an email response assistant for Ngee Ann Polytechnic student Bursary inquiries.

A student sent this inquiry:
"{faq}"

Below are reference templates from similar past inquiries:

REFERENCE TEMPLATES:
{templates_text}

STRICT INSTRUCTIONS:
1. Carefully review ALL the reference templates above
2. ONLY provide information that is explicitly mentioned or clearly implied in the templates
3. Generate an ORIGINAL response that:
   - Directly addresses the student's specific inquiry
   - Uses ONLY accurate information found in the templates
   - Maintains the professional tone and style of the templates
   - Does NOT copy any template verbatim
4. If the answer to the student's inquiry is NOT found in the templates, say: "I don't have enough information to answer this inquiry. Please escalate to the appropriate department."
5. Every fact or policy mentioned MUST be backed by evidence from the templates above

Write your response:"""
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all Bursary templates organized by subcategories"""
    return jsonify({
        'templates': ALL_TEMPLATES,
        'categories': list(TEMPLATES.keys()),
        'total': len(ALL_TEMPLATES)
    })

@app.route('/api/generate-reply', methods=['POST'])
def generate_reply():
    """Generate a reply for the given FAQ"""
    if not client:
        return jsonify({'error': 'Groq API not configured. Set GROQ_API_KEY environment variable.'}), 500

    data = request.json
    faq = data.get('faq', '').strip()

    if not faq:
        return jsonify({'error': 'FAQ cannot be empty'}), 400

    try:
        reply = find_best_template(faq)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
