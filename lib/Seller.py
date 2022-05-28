from datetime import datetime


class Seller:
    def __init__(self, usr_id, blockchain):
        self.usr_id = usr_id
        self.blockchain = blockchain

    def get_bills(self):
        bills = []
        for blocks in self.blockchain.chain:
            d = []
            if len(blocks.get('transactions')) != 0 and blocks.get('transactions')[0].get('seller_id') == self.usr_id:
                dat = datetime.fromtimestamp(blocks.get('timestamp'))
                d.append(dat)
                bID = blocks.get('bill_id', 'NA')
                d.append(bID)
                for trans in blocks.get('transactions', []):
                    sID = trans.get('seller_id', 'NA')
                    d.append(sID)
                    cID = trans.get('cust_id', 'NA')
                    d.append(cID)
                    amt = trans.get('total', 0)
                    d.append(amt)
                bills.append(d)
        return bills

    def new_bill(self, custID, items, total=0):
        if total == 0:
            for item in items:
                total += item[-1]
        self.blockchain.new_transaction(self.usr_id, custID, items, total)
        block = self.blockchain.commit_block()
        return block.get('bill_id', 'NA')
