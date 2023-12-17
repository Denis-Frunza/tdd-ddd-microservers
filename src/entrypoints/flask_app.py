from datetime import datetime

from flask import Flask, jsonify, request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import src.domain.model as model
import src.adapters.orm as orm
import src.adapters.repository as repository
import src.service_layer.services as services
from src.domain.exceptions import OutOfStock, InvalidSku


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (OutOfStock, InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route("/add_batch", methods=['POST'])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json['eta']

    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json['ref'],
        request.json['sku'],
        request.json['qty'],
        eta,
        repo,
        session
    )

    return 'OK', 201
