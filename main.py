import socket

import requests
import streamlit as st
from flask import Flask, jsonify, request

from lib.Blockchain import Blockchain
# Initiating the blockchain
from lib.DB import authenticate_user
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


def main_display():
    st.title("Blockchain Based Billing System")
    st.write(
        "Managing billing systems for businesses in India, implemented using latest technology like blockchain. Ensuring "
        "security and reliability of  billing transactions between businesses and customers.​")
    st.write("Each block can contain information about a bill.​")
    st.write(
        "Bill Information may include :​ Seller ID​, Customer ID​,Billing Items​, Amount​. A block may have information "
        "about 'n' Bills.")


def main_seller():
    st.title('Seller')


def main_customer():
    st.title('Customer')


def display(user_id='', passwd=''):
    check = authenticate_user(user_id, passwd)
    if check == -1:
        if user_id != '' and passwd != '':
            with st.sidebar:
                st.error('Invalid ID or password')
        main_display()
    elif check == 0:
        main_customer()
    elif check == 1:
        main_seller()


with st.sidebar:
    usr_id = st.text_input("Enter your ID")
    password = st.text_input("Enter Your Password", type="password")
    loginBtn = st.button('Login')

display(usr_id, password)
