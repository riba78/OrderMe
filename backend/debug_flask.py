"""
Debug Flask App with full error logging
"""
import logging
import sys
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Enable SQLAlchemy engine logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Create and run app
app = create_app()
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TRAP_HTTP_EXCEPTIONS'] = True
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['DEBUG'] = True

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False) 