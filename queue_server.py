#
# simple app to run a server that could handle some info reported by a2p2 while a chara queueserver url is provided

# use pip install flask if not present
#

from flask import Flask, request, jsonify
import socket
import json
from datetime import datetime
from pprint import pprint

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def handleOB():
    ob_json = request.get_json()
    print("Received OB :")
    pprint(ob_json)

    # Pick up data from this dictionnary and put it in your system

    return 'Received !' # next job is to handle it !

@app.route('/test', methods=['GET'])
def status():
    data= {
            "service": "OB2 - OBBroker",
            "version": 0.1,
            "datetime": datetime.now().isoformat(),
            "hostname": socket.gethostname(),
            }
    return jsonify(data), 200


app.run(host="0.0.0.0", port=2468, debug=True)

