import pickle
import lreg_forecaster as fc
from datetime import timedelta
from flask import Flask, jsonify, request, Response, make_response,  current_app
from functools import update_wrapper
from flask_cors import CORS
import logging


app = Flask(__name__)
CORS(app)

logging.basicConfig(filename='api.log', level=logging.DEBUG)
#
# def logger(original):
#     import logging
#     logging.basicConfig(filename='{}.log'.format(original.__name__), level=logging.INFO)
#
#     def wrapper(*args, **kwargs):
#         logging.info(
#             #'Ran by {} data:{} with args: {}, and kwargs: {}'.format(request.remote_addr,request.json, args, kwargs)
#             'hghfhgfhdgfdgddgd'
#         )
#         return original(*args, **kwargs)
#     return wrapper

@app.route("/currencies", methods=['GET'])
def get_currencies():
    """returns the available currencies"""
    logging.info(
          'Ran by {} data:{}'.format(request.remote_addr,request.json)
    )
    response = jsonify(fc.currencies), 200
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['content-type'] = "application/json"
    return response

@app.route("/tocurrencies", methods=['POST'])
def to_currencies():
    logging.info(
        'Ran by {} data:{}'.format(request.remote_addr, request.json)
    )
    if not request.json or not 'currency' in request.json:
        response = jsonify({"error" : "Bad request", "code": "400", "message" : "No currency name or bad format."}, 400)
        make_response(response)
        return response
    currency = request.json['currency']

    response = jsonify(fc.currencies[currency]), 200
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['content-type'] = "application/json"
    return response

#expecting : { "currencyfrom" : "EUR", "currencyto" : "HUF", "days": 5} format
@app.route("/forecast", methods=['POST', 'GET'])
def call_forecaster():
    """Returns forecast for a specific currency for given number of days. (default 5 days)"""
    logging.info(
        'Ran by {} data:{}'.format(request.remote_addr, request.json)
    )

    if not request.json or not 'currencyfrom' in request.json or not 'currencyto' in request.json:
        response = jsonify({"error" : "Bad request", "code": "400", "message" : "No currency name or bad format."}, 400)
        make_response(response)
        return response

    forecast_out = 5
    if 'days' in request.json:
        forecast_out = int(request.json['days'])
    currencyfrom = request.json['currencyfrom']
    currencyto = request.json['currencyto']

    response = jsonify(fc.lin_reg_predict(currencyfrom, currencyto, forecast_out, save_ds=True, savemodel=True, silent=False, cache=False,
                                       train_a_lot=1, retrain=False, refresh_interval=1)), 201
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['content-type'] = "application/json"
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')