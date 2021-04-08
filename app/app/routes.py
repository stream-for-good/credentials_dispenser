from app.models import Provider, Credentials

import json
from flask import request, make_response, render_template, abort, Response
from app.main import app
from app.main import db
from app.set_encoder import SetEncoder
import datetime
import dateparser
import logging
import os
import sqlalchemy


def get_api_root():
    return os.getenv("API_ROOT", "dummy://")


@app.route("/providers/<provider_name>", methods=["POST"])
def create_provider(provider_name):
    provider = db.session.query(Provider).filter(Provider.name == provider_name).first()
    if provider is not None:
        return abort(409)
    else:
        provider = Provider()
        provider.name = provider_name
        db.session.add(provider)
        db.session.commit()
        resp = Response("CREATED", 201)
        resp.headers['Location'] = get_api_root() + f"providers/{provider}"
        return resp


@app.route("/providers", methods=["GET"])
def list_providers():
    providers = db.session.query(Provider).all()

    res = [{"name": provider.name, "id": provider.id, "links": [
        {
            "rel": "provider",
            "href": get_api_root() + f"providers/{provider.name}"
        }]}
           for provider in providers]

    return json.dumps(res, cls=SetEncoder), 200, {'Content-Type': 'application/json'}


@app.route("/providers/<provider_name>", methods=["GET"])
def list_logins_for_provider(provider_name):
    provider = db.session.query(Provider).filter(Provider.name == provider_name).first()
    if provider is None:
        return abort(404)
    else:
        res = {"id":provider.id,"links": [
            {"href": get_api_root() + f"credentials/{credentials.provider_id}/{credentials.login}",
             "rel": f"login-{credentials.login}"} for
            credentials in
            provider.credentials]}
        return json.dumps(res, cls=SetEncoder), 200, {'Content-Type': 'application/json'}


@app.route("/credentials/<provider_id>/<login>", methods=["POST"])
def create_credentials(provider_id, login):
    provider = db.session.query(Provider).filter(Provider.id == provider_id).first()
    if provider is None:
        return abort(404, "No such provider")
    else:
        credentials = db.session.query(Credentials).join(Provider).filter(Provider.id == provider_id).filter(
            Credentials.login == login).first()
        if credentials is not None:
            return abort(409, "Credentials already exist, please use PUT to update password or expiration date")
        credentials = Credentials()
        payload = request.get_json()
        credentials.login = login
        credentials.password = payload["password"]
        credentials.expiration = dateparser.parse(payload["expiration"])
        credentials.provider_id = provider.id
        db.session.add(credentials)
        db.session.commit()
        return make_response("CREATED", 201)


@app.route("/credentials/<provider_id>/<login>", methods=["PUT"])
def update_credentials(provider_id, login):
    credentials = db.session.query(Credentials).join(Provider).filter(Provider.id == provider_id).filter(
        Credentials.login == login).first()

    if credentials is None:
        return abort(404)
    else:
        if request.get_json().get("password",None) is not None:
            credentials.password = request.get_json()["password"]
        if request.get_json().get("expiration", None) is not None:
            credentials.expiration = dateparser.parse(request.get_json().get("expiration"))
        db.session.commit()
        return make_response("UPDATED", 204)


@app.route("/credentials/<provider_id>/<login>", methods=["GET"])
def get_credentials(provider_id, login):
    credentials = db.session.query(Credentials).join(Provider).filter(Provider.id == provider_id).filter(
        Credentials.login == login).filter(Credentials.expiration is None or Credentials.expiration > datetime.datetime.now()).first()
    if credentials is None:
        return abort(404)
    return json.dumps({"credentials": {"login": credentials.login, "password": credentials.password,
                                       "provider": credentials.provider.name, "expiration": credentials.expiration.timestamp()}},
                      cls=SetEncoder), 200, {'Content-Type': 'application/json'}
