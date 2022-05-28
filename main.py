import random
import socket
from threading import Thread
from time import sleep

import requests
import streamlit as st
from flask import Flask, jsonify, request

from lib.Blockchain import Blockchain
# Initiating the blockchain
from lib.Customer import Customer
from lib.DB import authenticate_user
from lib.Seller import Seller
from lib.Utilities import get_integer
from lib.data import MAIN_SERVER

blockchain = Blockchain()

# Initiating the Node
app = Flask(__name__)

MY_IP = 'http://'
blockchain.register_node(MAIN_SERVER)


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


def is_port_in_use(myport: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', myport)) == 0


if not is_port_in_use(5000):
    port = 5000
else:
    port = random.randint(10000, 40000)
node_thread = Thread(target=node_server, args=[port])
node_thread.daemon = True
node_thread.start()
MY_IP += f"{extract_ip()}:{port}"
blockchain.my_ip = MY_IP
if MAIN_SERVER != MY_IP:
    requests.post(f"{MAIN_SERVER}/nodes/register", json={"nodes": [MY_IP], "new": 'True'})
    sleep(2)
    blockchain.resolve_conflicts()


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


def main_display():
    st.write(
        "Managing billing systems for businesses in India, implemented using latest technology like blockchain. "
        "Ensuring "
        "security and reliability of  billing transactions between businesses and customers.​")
    st.write("Each block can contain information about a bill.​")
    st.write(
        "Bill Information may include :​ Seller ID​, Customer ID​,Billing Items​, Amount​. A block may have "
        "information "
        "about 'n' Bills.")


def gen_bill(big_txt):
    big_txt = big_txt.split(sep='\n')
    name_list = []
    quant_list = []
    price_list = []
    amount_list = []
    for box in big_txt:
        item_name, quantity, price = box.split(sep=',')
        name_list.append(item_name.strip())
        quant_list.append(int(quantity.strip()))
        price_list.append(float(price.strip()))
        amount_list.append(round(float(int(quantity.strip()) * float(price.strip())), 3))
    final = []
    for i in range(len(name_list)):
        final.append([name_list[i], quant_list[i], price_list[i], amount_list[i]])
    return final


def main_seller(user_id):
    seller = Seller(user_id, blockchain)
    st.header('Seller')
    genNewBill = st.checkbox('Generate new bills')
    prevBillbtn = st.button('Show previous bills')
    custId = st.text_input('Customer ID')
    if prevBillbtn:
        bills = seller.get_bills()
        st.table(bills)
    if genNewBill:
        big_box = st.text_area('Item Name, Quantity, Pricer')
        genBtn = st.button("Generate bill")
        if genBtn:
            newBill = gen_bill(big_box)
            billId = seller.new_bill(custId, newBill)
            st.write("Bill ID: " + billId)


def main_customer(user_id):
    customer = Customer(user_id, blockchain)
    st.header('Customer')
    prevBillbtn = st.button('Show previous bills')
    if prevBillbtn:
        bills = customer.get_bills()
        st.table(bills)


def display(user_id='', passwd=''):
    check = authenticate_user(user_id, passwd)
    if check == -1:
        if user_id != '' and passwd != '':
            with st.sidebar:
                st.error('Invalid ID or password')
        main_display()
    elif check == 0:
        main_customer(user_id)
    elif check == 1:
        main_seller(user_id)


st.title("Blockchain Based Billing System")
with st.sidebar:
    usr_id = st.text_input("Enter your ID")
    password = st.text_input("Enter Your Password", type="password")
    loginBtn = st.button('Login')

display(usr_id, password)
