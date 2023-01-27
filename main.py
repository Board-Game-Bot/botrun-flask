from flask import Flask, request, jsonify
from pkg.sandbox import SandBox

app = Flask(__name__)

@app.route("/")
def hello_flask():
  return "<p>Hello Flask</p>"

@app.route("/api/runbot/start/", methods=['POST'])
def start():
  uuid = request.form["uuid"]
  code = request.form["code"]
  lang = request.form["lang"]
  
  if SandBox.bots.get(uuid) is None:
    SandBox.bots[uuid] = SandBox(uuid, code, lang)

  return jsonify({
    'result': 'ok'
  })

@app.route("/api/runbot/compile/", methods=['POST'])
def compile():
  uuid = request.form['uuid']
  sandbox = SandBox.bots.get(uuid)

  result = sandbox.compile()
  if sandbox is None:
    return jsonify({
      'result': 'sandbox does not exist'
    })

  return jsonify({
    'result': result
  })

@app.route("/api/runbot/prepare/", methods=['POST'])
def prepare():
  uuid = request.form['uuid']
  data = request.form['data']

  sandbox = SandBox.bots.get(uuid)
  if sandbox is None:
    return jsonify({
      'result': 'sandbox does not exist'
    })
   
  result = sandbox.prepare(data)
  return jsonify({
    'result': result
  })

@app.route("/api/runbot/run/", methods=['POST'])
def run():
  uuid = request.form['uuid']
  sandbox = SandBox.bots.get(uuid)
  if sandbox is None:
    return jsonify({
      'result': 'sandbox does not exist'
    })

  data = sandbox.run()
  return jsonify({
      'result': 'ok',
      'data': data
  })

@app.route("/api/runbot/stop/", methods=['POST'])
def stop():
  uuid = request.form['uuid']
  sandbox = SandBox.bots.get(uuid)
  
  if sandbox is not None:
    sandbox.stop()
    del SandBox.bots[uuid]
  
  return jsonify({
    'result': 'ok'
  })

if __name__ == "__main__":
  app.run(debug=False, port=8000)
