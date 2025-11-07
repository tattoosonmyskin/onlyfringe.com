"""
OnlyFringe - Fact-Based Debate Platform
Main application file
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, User, Argument, Source, Rebuttal, RebuttalSource
from fact_checker import FactChecker
import json
import os

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)

# Initialize fact checker
fact_checker = FactChecker()

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    db.create_all()

@app.route('/')
def index():
    """Serve the main landing page"""
    return send_from_directory('static', 'index.html')

@app.route('/api')
def api_index():
    """API welcome endpoint"""
    return jsonify({
        'message': 'Welcome to OnlyFringe API - Fact-Based Debate Platform',
        'description': 'A platform for public debate requiring fact-based arguments with sources and AI fact-checking',
        'endpoints': {
            'GET /api/arguments': 'List all verified arguments',
            'POST /api/arguments': 'Submit a new argument',
            'GET /api/arguments/<id>': 'Get a specific argument',
            'POST /api/arguments/<id>/rebuttals': 'Submit a rebuttal to an argument',
            'POST /api/users': 'Create a new user',
            'GET /api/users/<id>': 'Get user information'
        }
    })

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400
    
    # Check if user exists
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        return jsonify({'error': 'User with this username or email already exists'}), 409
    
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Argument endpoints
@app.route('/api/arguments', methods=['GET'])
def list_arguments():
    """List all verified arguments"""
    status = request.args.get('status', 'approved')
    category = request.args.get('category')
    
    query = Argument.query
    
    if status:
        query = query.filter_by(verification_status=status)
    if category:
        query = query.filter_by(category=category)
    
    arguments = query.order_by(Argument.created_at.desc()).all()
    return jsonify([arg.to_dict() for arg in arguments])

@app.route('/api/arguments/<int:argument_id>', methods=['GET'])
def get_argument(argument_id):
    """Get a specific argument with all rebuttals"""
    argument = Argument.query.get_or_404(argument_id)
    return jsonify(argument.to_dict())

@app.route('/api/arguments', methods=['POST'])
def submit_argument():
    """Submit a new argument for fact-checking"""
    data = request.json
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    if not data.get('user_id'):
        return jsonify({'error': 'User ID is required'}), 400
    
    if not data.get('sources') or len(data['sources']) < Config.MIN_SOURCES_REQUIRED:
        return jsonify({
            'error': f'At least {Config.MIN_SOURCES_REQUIRED} sources are required'
        }), 400
    
    content_length = len(data['content'])
    if content_length < Config.MIN_ARGUMENT_LENGTH:
        return jsonify({
            'error': f'Argument must be at least {Config.MIN_ARGUMENT_LENGTH} characters'
        }), 400
    
    if content_length > Config.MAX_ARGUMENT_LENGTH:
        return jsonify({
            'error': f'Argument must not exceed {Config.MAX_ARGUMENT_LENGTH} characters'
        }), 400
    
    # Verify user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Validate sources
    source_validation = fact_checker.validate_sources(data['sources'])
    invalid_sources = [s for s in source_validation if not s['is_valid_url']]
    if invalid_sources:
        return jsonify({
            'error': 'Invalid source URLs',
            'invalid_sources': invalid_sources
        }), 400
    
    # Create argument
    argument = Argument(
        title=data['title'],
        content=data['content'],
        category=data.get('category'),
        user_id=data['user_id']
    )
    
    # Add sources
    for source_data in data['sources']:
        source = Source(
            url=source_data['url'],
            title=source_data.get('title'),
            description=source_data.get('description')
        )
        argument.sources.append(source)
    
    # Run AI fact-check
    fact_check_result = fact_checker.check_argument(
        data['content'],
        data['sources']
    )
    
    argument.ai_fact_check_result = json.dumps(fact_check_result)
    
    # Determine verification status based on AI result
    if fact_check_result.get('is_valid') and fact_check_result.get('score', 0) >= 70:
        argument.verification_status = 'approved'
        argument.is_verified = True
    else:
        argument.verification_status = 'rejected'
        argument.is_verified = False
    
    db.session.add(argument)
    db.session.commit()
    
    # Return argument with fact-check results
    response = argument.to_dict()
    response['fact_check'] = fact_check_result
    
    return jsonify(response), 201

@app.route('/api/arguments/<int:argument_id>/rebuttals', methods=['POST'])
def submit_rebuttal(argument_id):
    """Submit a rebuttal to an argument"""
    argument = Argument.query.get_or_404(argument_id)
    
    # Only allow rebuttals to approved arguments
    if argument.verification_status != 'approved':
        return jsonify({'error': 'Can only rebut approved arguments'}), 400
    
    data = request.json
    
    # Validate required fields
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    if not data.get('user_id'):
        return jsonify({'error': 'User ID is required'}), 400
    
    if not data.get('sources') or len(data['sources']) < Config.MIN_SOURCES_REQUIRED:
        return jsonify({
            'error': f'At least {Config.MIN_SOURCES_REQUIRED} sources are required'
        }), 400
    
    # Verify user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Validate sources
    source_validation = fact_checker.validate_sources(data['sources'])
    invalid_sources = [s for s in source_validation if not s['is_valid_url']]
    if invalid_sources:
        return jsonify({
            'error': 'Invalid source URLs',
            'invalid_sources': invalid_sources
        }), 400
    
    # Create rebuttal
    rebuttal = Rebuttal(
        argument_id=argument_id,
        user_id=data['user_id'],
        content=data['content']
    )
    
    # Add sources
    for source_data in data['sources']:
        source = RebuttalSource(
            url=source_data['url'],
            title=source_data.get('title'),
            description=source_data.get('description')
        )
        rebuttal.sources.append(source)
    
    # Run AI fact-check for rebuttal
    fact_check_result = fact_checker.check_rebuttal(
        data['content'],
        argument.content,
        data['sources']
    )
    
    rebuttal.ai_fact_check_result = json.dumps(fact_check_result)
    
    # Determine verification status based on AI result
    if fact_check_result.get('is_valid') and fact_check_result.get('score', 0) >= 70:
        rebuttal.verification_status = 'approved'
        rebuttal.is_verified = True
    else:
        rebuttal.verification_status = 'rejected'
        rebuttal.is_verified = False
    
    db.session.add(rebuttal)
    db.session.commit()
    
    # Return rebuttal with fact-check results
    response = rebuttal.to_dict()
    response['fact_check'] = fact_check_result
    
    return jsonify(response), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'ai_enabled': bool(Config.OPENAI_API_KEY)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Debug mode should be disabled in production for security
    # Set via environment variable: FLASK_DEBUG=1 for development
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
