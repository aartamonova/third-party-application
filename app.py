import os
from third_party_app import app, index_routes, errors_routes

app.register_blueprint(index_routes.bp)
app.register_blueprint(errors_routes.bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5006))
    app.run(debug=True, host='0.0.0.0', port=port)
