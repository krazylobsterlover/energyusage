from energy import app
from energy.views import *

if __name__ == '__main__':

    import logging
    logging.basicConfig(filename='logs/error.log',level=logging.WARNING)
    app.run(host= '0.0.0.0', debug=True)
