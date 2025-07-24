from flask import Flask, request, jsonify, redirect
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from.models import url_store
from.utils import generate_short_code, validate_url

from. import ApiError

app = Flask(__name__)

# --- Error Handlers ---
# Register handlers for consistent JSON error responses 
@app.errorhandler(ApiError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(NotFound)
def handle_not_found(e):
    # The user's test expects a specific health check at '/', so we can
    # assume other not-found paths are API errors.
    return jsonify(error="Not Found"), 404

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
    return jsonify(error="Method Not Allowed"), 405

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    # This will catch malformed JSON errors from request.get_json()
    return jsonify(error="Bad Request: Malformed JSON"), 400


# --- API Routes ---
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint to match the provided test."""
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    }), 200

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Endpoint to shorten a long URL."""
    if not request.is_json:
        raise ApiError("Invalid JSON format", 400)

    data = request.get_json()
    if not data or 'url' not in data:
        raise ApiError("Missing 'url' key in request body", 400)

    long_url = data['url']
    if not validate_url(long_url):
        raise ApiError("Invalid URL provided", 400)

    # Generate a unique short code, handling potential collisions [1]
    while True:
        short_code = generate_short_code()
        if url_store.is_code_available(short_code):
            break
    
    url_store.save_url(short_code, long_url)
    
    short_url = request.host_url + short_code
    
    return jsonify({
        "short_code": short_code,
        "short_url": short_url
    }), 201

@app.route('/<string:short_code>', methods=['GET'])
def redirect_to_url(short_code):
    """Redirects a short code to its original long URL."""
    long_url = url_store.get_url_and_increment_clicks(short_code)
    
    if long_url:
        return redirect(long_url, code=302)
    else:
        # Raise a 404 error, which will be caught by the handler
        raise NotFound()

@app.route('/api/stats/<string:short_code>', methods=['GET'])
def get_url_stats(short_code):
    """Retrieves analytics for a short code."""
    stats = url_store.get_stats(short_code)
    
    if stats:
        return jsonify({
            "url": stats['long_url'],
            "created_at": stats['created_at'].isoformat() + "Z", # ISO 8601 format
            "clicks": stats['clicks']
        }), 200
    else:
        raise NotFound()