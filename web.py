from cherrypy import wsgiserver
from flask import Flask, request, jsonify
from gifs import ItGifs

app = Flask(__name__)
gifs = ItGifs()

@app.route("/")
def root():
    return "Hello World", 418

@app.route("/<string:tags>", methods=["GET"])
def get_gif(tags):
    images = gifs.get_image(tags)
    if not images:
        return jsonify({"error": "not found"}), 404
    return jsonify(images), 200

@app.route("/id/<int:idimg>", methods=["GET"])
def get_gif_by_id(idimg):
    images = gifs.get_image_with_id(idimg)
    if not images:
        return jsonify({"error": "not found"}), 404
    return jsonify(images), 200

@app.route("/", methods=["POST"])
def create_gif():
    if request.headers.get('Content-Type') == 'application/json':
        content = request.get_json()
        url, source, tags = content.get("url"), content.get("source"), content.get("tags")
    else:
        url, source, tags = request.form.get("url"), request.form.get("source"), request.form.get("tags")
    if not url or not source or not tags:
        return jsonify({"error": "missing parameter"}), 416
    ret = gifs.add_image(url, source, tags)
    return jsonify({"added": ret}), 200

@app.route("/id/<int:img_id>", methods=["DELETE"])
def delete_gif(img_id):
    gifs.del_image(img_id)
    return jsonify({}), 200

if __name__ == "__main__":
    dispatcher = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), dispatcher)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        gifs.close()
