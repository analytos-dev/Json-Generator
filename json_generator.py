import openai
import json
import re
import time

# Load pieces index - try multiple paths
import os
import sys

# Try to find pieces_index.json in multiple locations
possible_paths = [
    "pieces_index.json",  # Current directory
    os.path.join(os.path.dirname(__file__), "pieces_index.json"),  # Same directory as script
    r"C:\Users\sshas\OneDrive\Desktop\Work Related\Json Generator\pieces_index.json"  # Original path
]

PIECE_INDEX = {}
for path in possible_paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            PIECE_INDEX = json.load(f)
        break

if not PIECE_INDEX:
    print("Warning: pieces_index.json not found. Using minimal set.")
    PIECE_INDEX = {
        "@activepieces/piece-gmail": {"actions": ["gmail_send_email"], "triggers": ["new_email"]},
        "@activepieces/piece-google-sheets": {"actions": ["insert_row"], "triggers": []},
        "@activepieces/piece-http": {"actions": ["send_request"], "triggers": []}
    }

# OpenAI setup
# Get API key from environment variable or config file
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    try:
        from config import OPENAI_API_KEY
        api_key = OPENAI_API_KEY
    except ImportError:
        print("Warning: No OpenAI API key found. Set OPENAI_API_KEY environment variable or create config.py")
        api_key = None

if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    print("Error: OpenAI API key is required to run this application")
    sys.exit(1)

def build_piece_description():
    """Build a formatted description of all available pieces"""
    # Only include pieces that have actions or triggers
    relevant_pieces = {k: v for k, v in PIECE_INDEX.items() 
                      if v.get('actions') or v.get('triggers')}
    
    return "\n\n".join([
        f"{piece}:\n  - actions: {', '.join(data['actions']) if data['actions'] else 'none'}\n  - triggers: {', '.join(data['triggers']) if data['triggers'] else 'none'}"
        for piece, data in relevant_pieces.items()
    ])

def suggest_pieces_for_prompt(prompt: str) -> list:
    """Suggest relevant pieces based on keywords in the prompt"""
    prompt_lower = prompt.lower()
    suggestions = []
    
    # Keyword mappings to pieces
    keyword_map = {
        'email': ['@activepieces/piece-gmail', '@activepieces/piece-smtp', '@activepieces/piece-sendgrid'],
        'spreadsheet': ['@activepieces/piece-google-sheets', '@activepieces/piece-microsoft-excel-365'],
        'database': ['@activepieces/piece-postgres', '@activepieces/piece-mysql', '@activepieces/piece-mongodb'],
        'slack': ['@activepieces/piece-slack'],
        'discord': ['@activepieces/piece-discord'],
        'ai': ['@activepieces/piece-openai', '@activepieces/piece-claude', '@activepieces/piece-google-gemini'],
        'chatgpt': ['@activepieces/piece-openai'],
        'schedule': ['@activepieces/piece-schedule'],
        'webhook': ['@activepieces/piece-webhook'],
        'api': ['@activepieces/piece-http', '@activepieces/piece-webhook'],
        'approval': ['@activepieces/piece-approval'],
        'sms': ['@activepieces/piece-twilio', '@activepieces/piece-messagebird'],
        'whatsapp': ['@activepieces/piece-whatsapp'],
        'payment': ['@activepieces/piece-stripe', '@activepieces/piece-square'],
        'crm': ['@activepieces/piece-salesforce', '@activepieces/piece-hubspot', '@activepieces/piece-pipedrive'],
        'calendar': ['@activepieces/piece-google-calendar', '@activepieces/piece-cal-com'],
        'file': ['@activepieces/piece-google-drive', '@activepieces/piece-dropbox', '@activepieces/piece-amazon-s3'],
        'pdf': ['@activepieces/piece-pdf'],
        'image': ['@activepieces/piece-image-helper', '@activepieces/piece-image-ai']
    }
    
    for keyword, pieces in keyword_map.items():
        if keyword in prompt_lower:
            suggestions.extend(pieces)
    
    # Remove duplicates while preserving order
    seen = set()
    return [x for x in suggestions if not (x in seen or seen.add(x))]

def generate_workflow(prompt: str) -> dict:
    system_prompt = f"""
You are a professional Activepieces workflow builder.
Generate a valid Activepieces workflow JSON with this EXACT structure:

{{
  "created": "<timestamp_ms>",
  "updated": "<timestamp_ms>",
  "name": "Workflow Name",
  "description": "",
  "tags": [],
  "pieces": ["@activepieces/piece-name1", "@activepieces/piece-name2"],
  "template": {{
    "displayName": "Workflow Name",
    "trigger": {{
      "name": "trigger",
      "type": "PIECE_TRIGGER",
      "valid": true,
      "displayName": "Trigger Display Name",
      "settings": {{
        "pieceName": "@activepieces/piece-name",
        "triggerName": "trigger_action_name",
        "pieceVersion": "~0.1.0",
        "pieceType": "OFFICIAL",
        "packageType": "REGISTRY",
        "input": {{
          "auth": "{{{{connections['connection-id']}}}}",
          // trigger specific inputs
        }},
        "inputUiInfo": {{}},
        "errorHandlingOptions": {{
          "retryOnFailure": {{"value": false}},
          "continueOnFailure": {{"value": false}}
        }}
      }},
      "nextAction": {{
        // First action here, which contains nextAction for second action, etc.
      }}
    }},
    "connectionIds": ["connection-id1", "connection-id2"],
    "schemaVersion": "2",
    "valid": true
  }},
  "blogUrl": "",
  "type": "workflow"
}}

CRITICAL RULES:
1. NO "steps" array - use nested "nextAction" chains
2. Each action MUST have these in settings:
   - pieceName: "@activepieces/piece-name"
   - actionName: "specific_action_name" (use snake_case)
   - pieceVersion: "~0.1.0"
   - pieceType: "OFFICIAL"
   - packageType: "REGISTRY"
3. Trigger type MUST be "PIECE_TRIGGER"
4. Action type MUST be "PIECE"
5. Variables use {{{{varname}}}} format
6. Connection IDs in array are simple strings like ["gmail", "sheets"]
7. Auth in input uses: "auth": "{{{{connections['connection-name']}}}}"

Available pieces and their actions/triggers:
{build_piece_description()}

IMPORTANT naming conventions and examples:
- Use snake_case for all action/trigger names (e.g., send_email, new_row_added)
- Common pieces and their usage:
  * Gmail: triggerName="new_email", actionName="gmail_send_email"
  * Google Sheets: actionName="insert_row", "find_rows", "update_row"
  * HTTP: pieceName="@activepieces/piece-http", actionName="send_request"
  * Slack: actionName="send_message", "send_approval_message"
  * Discord: actionName="send_message_to_channel"
  * OpenAI: actionName="ask_chatgpt", "generate_image", "extract_structured_data"
  * Schedule: triggers="every_day", "every_hour", "cron_expression"
  * Webhook: triggerName="catch_webhook", actionName="return_response"
  * Store: actionName="get", "put", "delete" (for workflow variables)
  * Delay: actionName="delayFor", "delay_until"
  * Data Mapper: actionName="advanced_mapping"
  * Text Helper: actionName="concat", "replace", "split"

When user mentions:
- "AI/ChatGPT/GPT" → use @activepieces/piece-openai
- "storage/S3" → use @activepieces/piece-amazon-s3
- "database" → consider postgres, mysql, mongodb, supabase pieces
- "email" → consider gmail, smtp, sendgrid, mailchimp
- "messaging" → consider slack, discord, telegram-bot, whatsapp
- "schedule/cron/timer" → use @activepieces/piece-schedule
- "wait/delay/pause" → use @activepieces/piece-delay
- "approve/approval" → use @activepieces/piece-approval

Return ONLY valid JSON, no markdown or comments.
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4000  # Increased for complex workflows
    )

    workflow = json.loads(response.choices[0].message.content)
    return validate_workflow(workflow)

def validate_workflow(workflow: dict) -> dict:
    if not isinstance(workflow, dict):
        raise ValueError("Workflow must be a dictionary.")

    timestamp = str(int(time.time() * 1000))
    workflow["created"] = workflow.get("created", timestamp)
    workflow["updated"] = workflow.get("updated", timestamp)
    workflow["description"] = workflow.get("description", "")
    workflow["tags"] = workflow.get("tags", [])
    workflow["blogUrl"] = workflow.get("blogUrl", "")
    workflow["type"] = "workflow"

    if not isinstance(workflow.get("pieces"), list):
        workflow["pieces"] = []
    
    # Validate that all pieces exist in our index
    for piece in workflow["pieces"]:
        if piece not in PIECE_INDEX:
            print(f"Warning: Unknown piece {piece} - removing from list")
            workflow["pieces"].remove(piece)

    if not isinstance(workflow.get("template"), dict):
        workflow["template"] = {}

    template = workflow["template"]
    template["schemaVersion"] = "2"
    template["valid"] = True
    template["displayName"] = workflow.get("name", "Untitled Workflow")

    if not isinstance(template.get("connectionIds"), list):
        template["connectionIds"] = []

    def patch_step(step):
        if not isinstance(step, dict):
            return
        
        # Ensure proper type
        if "triggerName" in step.get("settings", {}):
            step["type"] = "PIECE_TRIGGER"
        elif step.get("type") not in ["PIECE", "PIECE_TRIGGER", "CODE", "LOOP_ON_ITEMS"]:
            step["type"] = "PIECE"
        
        step.setdefault("valid", True)
        step.setdefault("displayName", step.get("name", "Unnamed Step"))
        
        settings = step.setdefault("settings", {})
        if "pieceName" in settings:
            settings.setdefault("pieceVersion", "~0.1.0")
            settings.setdefault("pieceType", "OFFICIAL")
            settings.setdefault("packageType", "REGISTRY")
        
        settings.setdefault("inputUiInfo", {})
        
        if step["type"] == "PIECE" and "errorHandlingOptions" not in settings:
            settings["errorHandlingOptions"] = {
                "retryOnFailure": {"value": False},
                "continueOnFailure": {"value": False}
            }
        
        # Recursively patch nextAction
        if "nextAction" in step:
            patch_step(step["nextAction"])

    patch_step(template.get("trigger"))

    return workflow

def save_workflow(workflow: dict) -> str:
    clean_name = re.sub(r'[^\w\s-]', '', workflow["name"]).strip().replace(' ', '_')
    filename = f"{clean_name}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    return filename

def print_pieces_summary():
    """Print a summary of available pieces"""
    total_pieces = len(PIECE_INDEX)
    pieces_with_content = sum(1 for p in PIECE_INDEX.values() if p.get('actions') or p.get('triggers'))
    total_actions = sum(len(p.get('actions', [])) for p in PIECE_INDEX.values())
    total_triggers = sum(len(p.get('triggers', [])) for p in PIECE_INDEX.values())
    
    print(f"\n📊 Pieces Summary:")
    print(f"  Total pieces available: {total_pieces}")
    print(f"  Pieces with actions/triggers: {pieces_with_content}")
    print(f"  Total actions: {total_actions}")
    print(f"  Total triggers: {total_triggers}")
    print(f"\n  Popular pieces: Gmail, Google Sheets, Slack, OpenAI, HTTP, Webhook, Schedule")
    print(f"  New AI pieces: Claude, Gemini, Perplexity, DeepSeek")
    print(f"  Storage: S3, Dropbox, Google Drive, OneDrive")
    print(f"  Databases: PostgreSQL, MySQL, MongoDB, Supabase")
    print(f"  Payment: Stripe, Square, Razorpay")
    print(f"  CRM: Salesforce, HubSpot, Pipedrive, Zoho\n")

# Example usage
if __name__ == "__main__":
    print_pieces_summary()
    
    user_prompt = (
        "When a new invoice email arrives in Gmail, extract the attachment, "
        "send it to the /v1/search_from_invoice API using HTTP, "
        "store the result in Google Sheets, and send an alert email."
    )
    
    # Show suggested pieces
    suggestions = suggest_pieces_for_prompt(user_prompt)
    if suggestions:
        print(f"💡 Suggested pieces for your prompt: {', '.join(suggestions)}\n")
    
    try:
        workflow = generate_workflow(user_prompt)
        saved_path = save_workflow(workflow)
        print(f"✅ Workflow saved to: {saved_path}")
        print(json.dumps({k: workflow[k] for k in ["name", "pieces"]}, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")