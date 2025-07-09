# Activepieces JSON Workflow Generator

An intelligent workflow generator for Activepieces that uses AI to create automation workflows from natural language descriptions.

## Features

- 🤖 AI-powered workflow generation using OpenAI GPT-4
- 🔌 Support for 150+ integrations (pieces) with 560+ actions and 120+ triggers
- 🌐 Web interface for easy workflow creation
- 📡 REST API for programmatic access
- 💡 Smart piece suggestions based on user prompts
- 📦 Automatic JSON validation and formatting

## Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://bitbucket.org/analytos/json-generator.git
cd json-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Option 1: Set environment variable
     ```bash
     export OPENAI_API_KEY="your-api-key-here"
     ```
   - Option 2: Create a config.py file
     ```bash
     cp config.example.py config.py
     # Edit config.py and add your API key
     ```

## Usage

### Web Interface

1. Start the API server:
```bash
python api.py
```

2. Open your browser to `http://localhost:5000`

3. Enter your workflow description and click "Generate Workflow"

### Command Line

```bash
python json_generator.py
```

### API Endpoints

- `GET /` - Web interface
- `GET /api` - API documentation
- `POST /generate` - Generate a workflow from a prompt
- `GET /pieces` - List all available pieces
- `POST /suggest` - Get piece suggestions for a prompt

### Example API Request

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Send an email when a new row is added to Google Sheets"}'
```

## Supported Integrations

The generator supports 150+ integrations including:

- **Communication**: Gmail, Slack, Discord, Microsoft Teams
- **Productivity**: Google Sheets, Notion, Trello, Asana
- **AI/ML**: OpenAI, Claude, Google Gemini
- **Storage**: Google Drive, Dropbox, Amazon S3
- **Databases**: PostgreSQL, MySQL, MongoDB
- **Automation**: Webhooks, Schedule, Delay
- **And many more...**

## Example Prompts

1. "When a new email arrives in Gmail, save attachments to Google Drive"
2. "Every Monday at 9 AM, fetch data from PostgreSQL and send a Slack summary"
3. "Use OpenAI to analyze customer feedback from Typeform and save insights to Airtable"

## Project Structure

```
json-generator/
├── api.py              # Flask API server
├── json_generator.py   # Core generation logic
├── index.html          # Web interface
├── pieces_index.json   # Database of available pieces
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For issues or questions, please create an issue in the repository.