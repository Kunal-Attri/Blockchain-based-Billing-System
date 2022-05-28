

@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.commit_block()
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['user_id']
    if not all(k in values for k in required):
        return 'Missing values - user_id', 400

    user_id = values['user_id']

    # checking optional criterias and creating new transaction
    completed = values.get('completed', 0)
    if completed == 1:
        if 'work_id' in values:
            work_id = values['work_id']
            work_info = blockchain.get_work_info(work_id)
            if work_info is not None:
                index = blockchain.new_transaction(user_id, work_info, completed, work_id)
            else:
                return 'Invalid values - work_id', 400
        else:
            return 'Missing values - work_id', 400
    else:
        if 'work_info' in values:
            work_info = values['work_info']
            index = blockchain.new_transaction(user_id, work_info)
        else:
            return 'Missing values - work_info', 400

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


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
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200



while True:
    print("""
Actions: 
1. Login
2. New User
3. Show full chain
4. Show all nodes
5. Start Server node
6. Exit""")
    inp = get_integer("\nInput: ")
    if inp == 1:
        usr_id = input("User ID: ")
        if authenticate_user(usr_id):
            user_main(usr_id, blockchain)
        else:
            print("User ID not valid...")
    elif inp == 2:
        usr_id = uuid()
        add_user(usr_id)
        print(f"Your user id is: {usr_id}")
        print("You must save it now to login!")
    elif inp == 3:
        print(f'Length of chain: {len(blockchain.chain)} blocks')
        print(f'Chain: {tabulate(blockchain.chain)}')
    elif inp == 4:
        print(f'No of nodes: {len(blockchain.nodes)} nodes')
        print(f'Nodes: f{blockchain.nodes}')
    elif inp == 5:
        if len(MY_IP) <= 10:
            port = get_integer("Port (default - 5000): ", defaultVal=5000)
            node_thread = Thread(target=node_server, args=[12133])
            node_thread.daemon = True
            node_thread.start()
            MY_IP += f"{extract_ip()}:{port}"    # 12133
            blockchain.my_ip = MY_IP
            if MAIN_SERVER != MY_IP:
                requests.post(f"{MAIN_SERVER}/nodes/register", json={"nodes": [MY_IP], "new": 'True'})
                sleep(2)
                blockchain.resolve_conflicts()
        else:
            print('Server already running...')
    elif inp == 6:
        if len(MY_IP) > 10 and MY_IP != MAIN_SERVER:
            requests.post(f"{MAIN_SERVER}/nodes/unregister", json={"nodes": [MY_IP], "new": 'True'})
            sleep(2)
        exit()