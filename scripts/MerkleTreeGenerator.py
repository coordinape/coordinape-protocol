from brownie import web3, Wei
import csv
import json

def main():
    csv_name = 'raffle_winners.csv'
    amounts_csv = 'amounts.csv'

    rows = fetch_data_from_csv(csv_name)
    amount_rows = fetch_data_from_csv(amounts_csv)
    rows = fill_gap(rows)
    amount_rows = fill_void(amount_rows)
    
    items = generate_tree(rows, amount_rows)
    json_merkle = json.dumps(items, indent=4, sort_keys=True)
    file = open('raffle_winner_tree.json', 'w')
    file.write(str(json_merkle))
    file.close()

def gen():
    generate_merkle_tree_json('tests/address.csv', 'tests/amounts.csv', 'tests/merkle_test')

def generate_merkle_tree_json(address_csv, amounts_csv, json_name):
    rows = fetch_data_from_csv(address_csv)
    amount_rows = fetch_data_from_csv(amounts_csv)
    rows = fill_gap(rows)
    amount_rows = fill_void(amount_rows)
    
    items = generate_tree(rows, amount_rows)
    json_merkle = json.dumps(items, indent=4, sort_keys=True)
    file = open(json_name + '.json', 'w')
    file.write(str(json_merkle))
    file.close()

def generate_leaf(index, account, amount):
    return web3.soliditySha3(
        [ 'uint256' , 'address', 'uint256'], [index, web3.toChecksumAddress(account), Wei(amount)])

def compute_node(h1, h2):
    if h1 <= h2:
        hash = web3.soliditySha3(
            [ 'bytes32' , 'bytes32'], [h1, h2])
    else:
        hash = web3.soliditySha3(
            [ 'bytes32' , 'bytes32'], [h2, h1])
    print(web3.toHex(h1), web3.toHex(h2), '=>', web3.toHex(hash))
    return hash

def fetch_data_from_csv(file_name):
    rows = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
    return rows

def fill_gap(rows):
    entries = 1
    while len(rows) >= entries:
        entries *= 2
    for i in range(entries - len(rows)):
        rows.append(['0x0000000000000000000000000000000000000000'])
    return rows

def fill_void(rows):
    entries = 1
    while len(rows) >= entries:
        entries *= 2
    for i in range(entries - len(rows)):
        rows.append([0])
    return rows

def generate_tree(rows, amount_rows):
    items = {'claims':{}}
    leaves = []
    index = 0
    for row, amount in zip(rows, amount_rows):
        leaf_hash = generate_leaf(index, row[0], amount[0])
        print(index, row[0], amount[0], '=>', web3.toHex(leaf_hash))
        leaves.append(leaf_hash)
        if row[0] != '0x0000000000000000000000000000000000000000':
            items['claims'].setdefault(row[0], {'index':index, 'amount':amount[0], 'proof':[]})
        index += 1
    level = 0
    while len(leaves) > 1:
        print(f'level {level}')
        for i in range(len(rows)):
            node = i // (2 ** level)
            node = node + 1 if node % 2 == 0 else node - 1
            if rows[i][0] != '0x0000000000000000000000000000000000000000':
                items['claims'][rows[i][0]]['proof'].append(web3.toHex(leaves[node]))
        level += 1
        temp = []
        for i in range(len(leaves) // 2):
            temp.append(compute_node(leaves[2 * i], leaves[2 * i + 1]))
        leaves = temp
    print(f'final root is {web3.toHex(leaves[0])}')
    return items

print('hello world')
gen()
