from flask import Flask
from controllers import controllers as controllers_bp
import os

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    templates_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir
    )

    app.register_blueprint(controllers_bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
