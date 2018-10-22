from vibora import Vibora, Request
from vibora.responses import JsonResponse

from api.v1.routes import v1


app = Vibora()



if __name__ == '__main__':
    app.add_blueprint(v1, prefixes={'v1': '/v1'})
    app.run(debug=True, host='0.0.0.0', port=5555)