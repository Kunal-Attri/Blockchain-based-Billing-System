import socket
from flask import Flask, jsonify, request
import requests
import streamlit as st

from lib.Blockchain import Blockchain

# Initiating the blockchain
from lib.data import MAIN_SERVER

blockchain = Blockchain()

# Initiating the Node
app = Flask(__name__)
node_thread = None

MY_IP = 'http://'
blockchain.register_node(MAIN_SERVER)


# for nodes
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/getlock', methods=['POST'])
def get_lock():
    update = blockchain.lock()
    if update:
        response = {
            'lock': 'True'
        }
        return jsonify(response), 200
    else:
        response = {
            'lock': 'False'
        }
        return jsonify(response), 400


@app.route('/releaselock', methods=['POST'])
def release_lock():
    update = blockchain.unlock()
    if update:
        response = {
            'released': 'True'
        }
        return jsonify(response), 201
    else:
        response = {
            'released': 'False'
        }
        return jsonify(response), 401


@app.route('/chain/update', methods=['GET'])
def update_chain():
    updated = blockchain.resolve_conflicts()
    if updated:
        print('Node synced successfully!')
    response = {
        'updated': True,
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    a = list(blockchain.nodes).copy()
    a = ["http://" + i for i in a]
    if socket.gethostbyname(socket.gethostname()) in MAIN_SERVER and values.get('new') == 'True':
        for node in blockchain.nodes:
            requests.post(f"http://{node}/nodes/register", json={"nodes": a})
    return jsonify(response), 201


@app.route('/nodes/unregister', methods=['POST'])
def unregister_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.unregister_node(node)

    response = {
        'message': 'New nodes have been removed',
        'total_nodes': list(blockchain.nodes),
    }
    if socket.gethostbyname(socket.gethostname()) in MAIN_SERVER and values.get('new') == 'True':
        for node in blockchain.nodes:
            if f'http://{node}' != MAIN_SERVER:
                requests.post(f"http://{node}/nodes/unregister", json={"nodes": nodes})
    return jsonify(response), 201


def node_server(my_port):
    app.run(host='0.0.0.0', port=my_port)


def extract_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        IP = sock.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        sock.close()
    return IP


st.title("Blockchain Based Billing System")
st.write("Managing billing systems for business in India, implemented using latest technology like blockchain. Ensuring security and reliability of  billing transactions between businesses and customers.​")
st.write("Each block can contain information about a bill.​")
st.write("Bill Information may include :​ Seller ID​, Customer ID​,Billing Items​, Amount​")

with st.sidebar:
    Id = st.number_input("Enter You ID", min_value=0, step=1, max_value=1)
    password = st.text_input("Enter Your Password", type="password")


def authenticate_user(usr_id, passwd):
    if usr_id == 1:
        return True
    else:
        return False


if authenticate_user(Id, password):
    st.header("Seller side")
    view_history = st.button("View Previous bills")
    make_bill = st.button("Generate a new bill")
    # if make_bill:
    #     make_bill function is called
    # if view_history:
    #     view_history function is called

if authenticate_user(Id, password) is False:
    st.header("Customer side")
    customer_history = st.button("View Your Previous bills")
    # if customer_history:
    #     customer_history function is called
