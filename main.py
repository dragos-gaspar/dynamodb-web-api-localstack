import os

from app import create_app


os.environ['AWS_ENDPOINT'] = 'localhost'


if __name__ == '__main__':
    app = create_app()
    app.run()
