from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import logging
import os
from json_generator import generate_workflow, save_workflow, suggest_pieces_for_prompt, PIECE_INDEX, print_pieces_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/generate', methods=['POST'])
def generate_workflow_endpoint():
    """
    Generate an Activepieces workflow from a prompt
    
    Expected JSON body:
    {
        "prompt": "your workflow description here"
    }
    
    Returns:
    {
        "success": true/false,
        "workflow": {...},  // The generated workflow JSON
        "filename": "saved_file.json",  // If save is successful
        "error": "error message"  // If any error occurs
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract prompt
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "No prompt provided"
            }), 400
        
        # Log the received prompt
        logger.info(f"Received prompt: {prompt}")
        
        # Get piece suggestions based on prompt
        suggestions = suggest_pieces_for_prompt(prompt)
        logger.info(f"Suggested pieces: {suggestions}")
        
        # Generate workflow
        logger.info("Generating workflow...")
        workflow = generate_workflow(prompt)
        
        # Save workflow to file
        filename = save_workflow(workflow)
        logger.info(f"Workflow saved to: {filename}")
        
        # Display the generated JSON in terminal (formatted)
        print("\n" + "="*50)
        print("GENERATED WORKFLOW JSON:")
        print("="*50)
        print(json.dumps(workflow, indent=2))
        print("="*50 + "\n")
        
        # Return success response with suggestions
        return jsonify({
            "success": True,
            "workflow": workflow,
            "filename": filename,
            "suggestions": suggestions,
            "pieces_used": workflow.get("pieces", [])
        }), 200
        
    except Exception as e:
        # Log error
        logger.error(f"Error generating workflow: {str(e)}")
        
        # Return error response
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate-batch', methods=['POST'])
def generate_batch_workflows():
    """
    Generate multiple workflows from a list of prompts
    
    Expected JSON body:
    {
        "prompts": ["prompt1", "prompt2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompts' not in data:
            return jsonify({
                "success": False,
                "error": "No prompts array provided"
            }), 400
        
        prompts = data.get('prompts', [])
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Processing prompt {i+1}/{len(prompts)}: {prompt}")
                workflow = generate_workflow(prompt)
                filename = save_workflow(workflow)
                
                results.append({
                    "success": True,
                    "prompt": prompt,
                    "workflow": workflow,
                    "filename": filename
                })
                
            except Exception as e:
                logger.error(f"Error with prompt {i+1}: {str(e)}")
                results.append({
                    "success": False,
                    "prompt": prompt,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Serve the HTML frontend"""
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    else:
        return jsonify({"error": "Frontend not found"}), 404

@app.route('/pieces', methods=['GET'])
def list_pieces():
    """List all available pieces with their actions and triggers"""
    pieces_summary = {
        "total_pieces": len(PIECE_INDEX),
        "total_actions": sum(len(p.get("actions", [])) for p in PIECE_INDEX.values()),
        "total_triggers": sum(len(p.get("triggers", [])) for p in PIECE_INDEX.values()),
        "categories": {
            "communication": ["@activepieces/piece-gmail", "@activepieces/piece-slack", "@activepieces/piece-discord"],
            "ai_ml": ["@activepieces/piece-openai", "@activepieces/piece-claude", "@activepieces/piece-google-gemini"],
            "storage": ["@activepieces/piece-google-drive", "@activepieces/piece-dropbox", "@activepieces/piece-amazon-s3"],
            "databases": ["@activepieces/piece-postgres", "@activepieces/piece-mysql", "@activepieces/piece-mongodb"],
            "automation": ["@activepieces/piece-schedule", "@activepieces/piece-webhook", "@activepieces/piece-delay"]
        },
        "pieces": PIECE_INDEX
    }
    return jsonify(pieces_summary), 200

@app.route('/pieces/<piece_name>', methods=['GET'])
def get_piece_details(piece_name):
    """Get details about a specific piece"""
    full_piece_name = f"@activepieces/piece-{piece_name}"
    
    if full_piece_name in PIECE_INDEX:
        return jsonify({
            "name": full_piece_name,
            "actions": PIECE_INDEX[full_piece_name].get("actions", []),
            "triggers": PIECE_INDEX[full_piece_name].get("triggers", [])
        }), 200
    else:
        return jsonify({"error": f"Piece '{piece_name}' not found"}), 404

@app.route('/suggest', methods=['POST'])
def suggest_pieces():
    """Suggest pieces based on a prompt"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({
            "success": False,
            "error": "No prompt provided"
        }), 400
    
    prompt = data.get('prompt', '')
    suggestions = suggest_pieces_for_prompt(prompt)
    
    # Get details for each suggested piece
    detailed_suggestions = []
    for piece in suggestions:
        if piece in PIECE_INDEX:
            detailed_suggestions.append({
                "name": piece,
                "actions": PIECE_INDEX[piece].get("actions", [])[:5],  # Top 5 actions
                "triggers": PIECE_INDEX[piece].get("triggers", [])
            })
    
    return jsonify({
        "success": True,
        "prompt": prompt,
        "suggestions": detailed_suggestions
    }), 200

@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        "name": "Activepieces Workflow Generator API",
        "version": "1.0.0",
        "endpoints": {
            "/": "Web interface",
            "/api": "API documentation (this page)",
            "/health": "Health check endpoint",
            "/generate": {
                "method": "POST",
                "description": "Generate a single workflow from a prompt",
                "body": {
                    "prompt": "string - Your workflow description"
                }
            },
            "/generate-batch": {
                "method": "POST",
                "description": "Generate multiple workflows from multiple prompts",
                "body": {
                    "prompts": ["array", "of", "prompts"]
                }
            },
            "/pieces": {
                "method": "GET",
                "description": "List all available pieces with actions and triggers"
            },
            "/pieces/{piece_name}": {
                "method": "GET",
                "description": "Get details about a specific piece"
            },
            "/suggest": {
                "method": "POST",
                "description": "Get piece suggestions based on a prompt",
                "body": {
                    "prompt": "string - Your workflow description"
                }
            }
        }
    }), 200

if __name__ == '__main__':
    # Run the Flask app
    print("Starting Activepieces Workflow Generator API...")
    print("Web interface available at: http://localhost:5000")
    
    # Print pieces summary
    print(f"\n📊 Loaded {len(PIECE_INDEX)} pieces with:")
    print(f"   - {sum(len(p.get('actions', [])) for p in PIECE_INDEX.values())} total actions")
    print(f"   - {sum(len(p.get('triggers', [])) for p in PIECE_INDEX.values())} total triggers")
    
    print("\nEndpoints:")
    print("  GET  /          - Web interface")
    print("  GET  /api       - API documentation")
    print("  GET  /health    - Health check")
    print("  GET  /pieces    - List all available pieces")
    print("  GET  /pieces/<name> - Get piece details")
    print("  POST /suggest   - Get piece suggestions for prompt")
    print("  POST /generate  - Generate workflow from prompt")
    print("  POST /generate-batch - Generate multiple workflows")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)