from wsgiref.simple_server import make_server
from pyramid.config import Configurator

def main():
    config = Configurator()
    config.add_route('hello', '/')
    config.scan('views')
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 6547, app)
    print ('Starting up server on http://localhost:6547')
    server.serve_forever()