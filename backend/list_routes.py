"""
Script to list all registered Flask routes
"""
from app import create_app

def list_routes():
    """List all registered routes in the Flask app"""
    app = create_app()
    
    print('App routes:')
    print('-' * 50)
    
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        routes.append((rule.endpoint, rule.rule, methods))
    
    # Sort by endpoint
    for endpoint, rule, methods in sorted(routes):
        print(f"{endpoint:30s} {rule:40s} {methods}")

if __name__ == "__main__":
    list_routes() 