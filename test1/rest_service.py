import json
import os

from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename


app = Flask(__name__)


ELASTICSEARCH_URL = os.getenv(
    "ELASTICSEARCH_URL",
    "http://localhost:9200"
)

INDEX_NAME = "service-status"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

es = Elasticsearch(ELASTICSEARCH_URL)


@app.route("/add", methods=["POST"])
def add_status():
    uploaded_file = request.files.get("file")

    if uploaded_file is None:
        return jsonify({
            "error": "No file was uploaded"
        }), 400

    if not uploaded_file.filename:
        return jsonify({
            "error": "Filename is missing"
        }), 400

    filename = secure_filename(uploaded_file.filename)

    if not filename.endswith(".json"):
        return jsonify({
            "error": "Only JSON files are accepted"
        }), 400

    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        uploaded_file.save(file_path)

        with open(file_path, "r") as file:
            status_data = json.load(file)

    except json.JSONDecodeError:
        return jsonify({
            "error": "The uploaded file contains invalid JSON"
        }), 400

    service_name = status_data.get("service_name")
    service_status = status_data.get("service_status")

    if not service_name or service_status not in ["UP", "DOWN"]:
        return jsonify({
            "error": "Invalid service status data"
        }), 400

    try:
        es.index(
            index=INDEX_NAME,
            id=service_name,
            document=status_data,
            refresh="wait_for"
        )

    except Exception as error:
        return jsonify({
            "error": f"Elasticsearch error: {error}"
        }), 500

    return jsonify({
        "message": "Service status stored successfully",
        "service": service_name
    }), 201


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    try:
        result = es.search(
            index=INDEX_NAME,
            query={
                "match_all": {}
            },
            size=100
        )

    except Exception as error:
        return jsonify({
            "application": "rbcapp1",
            "status": "DOWN",
            "error": str(error)
        }), 503

    services = [
        hit["_source"]
        for hit in result["hits"]["hits"]
    ]

    required_services = {
        "httpd",
        "rabbitmq-server",
        "postgresql"
    }

    current_services = {
        service["service_name"]
        for service in services
    }

    if not required_services.issubset(current_services):
        return jsonify({
            "application": "rbcapp1",
            "status": "DOWN",
            "reason": "Not all required services have reported status"
        })

    application_status = "UP"

    for service in services:
        if service.get("service_status") != "UP":
            application_status = "DOWN"
            break

    return jsonify({
        "application": "rbcapp1",
        "status": application_status
    })


@app.route("/healthcheck/<service_name>", methods=["GET"])
def service_healthcheck(service_name):
    try:
        result = es.get(
            index=INDEX_NAME,
            id=service_name
        )

        return jsonify(result["_source"])

    except Exception:
        return jsonify({
            "service": service_name,
            "status": "DOWN"
        }), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
