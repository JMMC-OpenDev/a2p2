#
# simple app to run a server that could handle some info reported by a2p2 while a chara queueserver url is provided
# use pip install flask if not present
#

from flask import Flask, request
app = Flask(__name__)
r=0
@app.route('/test', methods=['POST'])
def result():
    print(f"data: {request.get_data()}") 
    print(f"json: {request.get_json()}") 
    return 'Received !' # response to your request.

app.run(host="localhost", port=2468, debug=True)

