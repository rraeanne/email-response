# NP FAQ Reply Generator Bot

A web-based bot that helps Ngee Ann Polytechnic employees generate email replies to student FAQs using template responses from the categorized reply database.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Groq API Key
You need a Groq API key from Groq Cloud Console. Set it as an environment variable:

**Windows (Command Prompt):**
```bash
set GROQ_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```bash
$env:GROQ_API_KEY="your_api_key_here"
```

**macOS/Linux:**
```bash
export GROQ_API_KEY=your_api_key_here
```

Or create a `.env` file in the project root:
```
GROQ_API_KEY=your_api_key_here
```

### 3. Ensure Data File
Make sure the template file exists at:
```
data/TEMPLATE_Replies Catergorisation.xlsx
```

## Running the Bot

```bash
python bot.py
```

The bot will start on `http://localhost:5000`

## How to Use

1. Open your browser and go to `http://localhost:5000`
2. Paste the FAQ or student inquiry in the text area
3. Click "Generate Reply"
4. The bot will find and display the best matching template response
5. Click "Copy Reply" to copy it to your clipboard
6. Paste it into your email

## Features

- **Smart Template Matching**: Uses Claude AI to understand the FAQ and find the most relevant template
- **Multiple Categories**: Templates organized by:
  - Bursary (FAQ, Application Outcome, Application Appeal, etc.)
  - Tuition Grant (TG)
  - Scholarship
  - Assistance & Resources
  - HOMES (Income Assessment)
  - And more

- **Easy to Use**: Simple web interface with copy-to-clipboard functionality
- **Fast**: Generates responses in seconds

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Groq API (Mixtral 8x7b)
- **Data**: Excel spreadsheet (openpyxl)

## Project Structure

```
email-response/
├── bot.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── data/
│   └── TEMPLATE_Replies Catergorisation.xlsx
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Troubleshooting

**Bot won't start:**
- Check if port 5000 is already in use: `netstat -ano | findstr :5000`
- Try a different port by modifying `app.run(port=5001)` in bot.py

**API Key Error:**
- Make sure your GROQ_API_KEY is set correctly
- Verify the key is valid on https://console.groq.com

**Excel File Error:**
- Ensure the file path is correct and the file is not corrupted
- Try opening the Excel file manually to verify

## Support

For issues or suggestions, check the project setup and error messages in the browser console.
