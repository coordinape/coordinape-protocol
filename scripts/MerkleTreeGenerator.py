from brownie import web3
import csv
import json

def main():
    csv_name = 'raffle_winners.csv'
    amount = 1000 * (10 ** 18)

    rows = fetch_addresses(csv_name)
    rows = fill_gap(rows)
    
    items = generate_tree(rows, amount)
    json_merkle = json.dumps(items, indent=4, sort_keys=True)
    file = open('raffle_winner_tree.json', 'w')
    file.write(str(json_merkle))
    file.close()

def generate_leaf(index, account, amount):
    return web3.soliditySha3(
        [ 'uint256' , 'address', 'uint256'], [index, web3.toChecksumAddress(account), amount])

def compute_node(h1, h2):
    if h1 <= h2:
        return web3.soliditySha3(
            [ 'bytes32' , 'bytes32'], [h1, h2])
    else:
        return web3.soliditySha3(
            [ 'bytes32' , 'bytes32'], [h2, h1])

def fetch_addresses(file_name):
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

def generate_tree(rows, amount):
    items = {'claims':{}}
    leaves = []
    index = 0
    for row in rows:
        leaves.append(generate_leaf(index, row[0], amount))
        if row[0] != '0x0000000000000000000000000000000000000000':
            items['claims'].setdefault(row[0], {'index':index, 'amount':amount, 'proof':[]})
        index += 1
    level = 0
    while len(leaves) > 1:
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