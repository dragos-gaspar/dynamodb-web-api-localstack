from flask import request, Blueprint, Response, jsonify

from app.database import db


bp = Blueprint('bp', __name__)


@bp.route("/", methods=["GET"])
def test_method() -> Response:
    return jsonify({"Proiect BDAS": "DynamoDB"})


@bp.route("/tables", methods=["GET"])
def view_tables():
    tables_response = db.get_tables_names()
    return jsonify(tables_response)


@bp.route("/<table>", methods=["GET"])
def print_table(table: str):
    items = db.print_table(table)
    return jsonify({"Table Name": table, "Items": items})


@bp.route("/insert/<table>", methods=["POST"])
def insert(table: str):
    data = request.json
    db.insert(table, data)
    return jsonify(f"Inserted item into table {table}.")


@bp.route("/query/<table>", methods=["GET"])
def query_table(table: str):
    query = request.json
    response = db.query_table(table, query)
    return jsonify(response)


@bp.route("/update/<table>", methods=["PATCH"])
def update_entry(table: str):
    query = request.json
    response = db.update_entry(table, query)
    return jsonify(f"Updated {response['Attributes']}")


@bp.route("/delete/<table>", methods=["DELETE"])
def delete_entry(table: str):
    query = request.json
    response = db.delete_entry(table, query)
    return jsonify(response)
