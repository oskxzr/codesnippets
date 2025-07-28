import dotenv
dotenv.load_dotenv()

import os
import ai
import time
import uuid
import json

from algoliasearch.search.client import SearchClientSync
_client = SearchClientSync(os.environ["ALGOLIA_KEY"], os.environ["ALGOLIA_SECRET"])

from flask import Flask, send_from_directory, render_template, request

app = Flask(__name__)

assets_id = str(uuid.uuid4())
app.jinja_env.globals["ASSET_ID"] = assets_id

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assets/<asset_id>/<path:filename>")
def assets(asset_id, filename):
    """Assets endpoints, so that we don't rely on the cache for new versions"""
    if asset_id != assets_id: return

    return send_from_directory("assets", filename)

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.json.get("prompt")
    return {"sucess": True, "response": json.loads(ai.generate(prompt))}

@app.route("/search")
def search():
    query = request.args.get("q")
    results = _client.search_single_index("snippets", {"query": query}).to_dict()
    return {"results": results}

@app.route("/copy/<id>")
def copy(id):
    data = _client.get_object("snippets", id)
    data["clicks"] += 1
    data["lastClicked"] = time.time()
    _client.save_object("snippets", data)
    return {"success": True}


@app.route("/save", methods=["POST"])
def save():
    data = request.json
    snippet_id = str(uuid.uuid4())
    data["objectID"] = snippet_id
    data["clicks"] = 1
    data["created"] = time.time()
    data["lastClicked"] = time.time()

    _client.save_object("snippets", data)

    return {"success": True}


if __name__ == "__main__":
    app.run(port=6555, debug=True)