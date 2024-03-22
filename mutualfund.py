import datetime
from motormongo import StakeholdersDB, HoldingsDB, TransactionsDB


class Transactions:
    db = TransactionsDB

    async def log_new_stakeholder(stakeholder_id, name, investment, profit_shares):
        now = datetime.datetime.now() # format:  "%Y-%m-%d %H:%M:%S.%f"
        Transactions.db.add(
            {
                "type": "StakeHolders",
                "action": "Create",
                "data": f"StakehoderID: {stakeholder_id}, Name: {name}, Investment: {investment}, Shares: {profit_shares}",
                "timestamp": now
            }
        )
    
    async def log_update_stakeholder(stakeholder_id, old_investment, new_investment, old_profit_shares, new_profit_shares):
        now = datetime.datetime.now()
        Transactions.db.add(
            {
                "type": "StakeHolders",
                "action": "Update",
                "data": f"StakeholderID: {stakeholder_id}, Old_Investment: {old_investment}, New_Investment: {new_investment}, Old_Profit_Shares: {old_profit_shares}, New_Profit_Shares: {new_profit_shares}",
                "timestamp": now
            }
        )

    async def log_remove_stakeholder(stakeholder_id):
        now = datetime.datetime.now()
        Transactions.db.add(
            {
                "type": "Stakeholders",
                "action": "Remove",
                "data": f"StakeholderID: {stakeholder_id}",
                "timestamp": now
            }
        )

    async def log_new_holding(coin_name, amount, avg_price):
        now = datetime.datetime.now()
        TransactionsDB.db.add(
            {
                "type": "Holdings",
                "action": "Create",
                "data": f"Coin Name: {coin_name}, Amount: {amount}, Entry Average: {avg_price}",
                "timestamp": now
            }
        )

    async def log_update_holding(coin_name, old_amount, new_amount, old_avg, new_avg):
        now = datetime.datetime.now()
        TransactionsDB.db.add(
            {
                "type": "Holdings",
                "action": "Update",
                "data": f"Coin Name: {coin_name}, Old Amount: {old_amount}, New Amount: {new_amount}, Old Entry Average: {old_avg}, Entry Average: {new_avg}",
                "timestamp": now
            }
        )

    async def log_close_holding(coin_name, selling_price):
        now = datetime.datetime.now()
        TransactionsDB.db.add(
            {
                "type": "Holdings",
                "action": "Close",
                "data": f"Coin Name: {coin_name}, Selling Price: {selling_price}",
                "timestamp": now
            }
        )

    async def log_profit_loss(profit_loss):
        now = datetime.datetime.now()
        Transactions.db.add(
            {
                "type": "Profit/Loss",
                "action": "Profit" if profit_loss > 0 else "Loss",
                "amount": profit_loss,
                "timestamp": now
            }
        )


class Stakeholders:
    db = StakeholdersDB

    async def add_stakeholder(stakeholder_id, name, investment, profit_shares):
        await Stakeholders.db.add({
            "stakeholder_id": stakeholder_id,
            "stakeholder_name": name,
            "investment": investment,
            "profit_shares": profit_shares
        })
        
        await Transactions.log_new_stakeholder(stakeholder_id, name, investment, profit_shares)

    async def remove_stakeholder(stakeholder_id):
        await Stakeholders.db.remove({"stakeholder_id": stakeholder_id})
        await Transactions.log_remove_stakeholder(stakeholder_id)

    async def get_stakeholder_by_id(stakeholder_id):
        return await Stakeholders.db.find({"stakeholder_id": stakeholder_id})
    
    async def update_stakeholder(stakeholder_id, new_investment, new_profit_shares=None):
        data = Stakeholders.get_stakeholder_by_id(stakeholder_id)
        if new_profit_shares == None:
            await Stakeholders.db.modify(
                {"stakeholder_id": stakeholder_id},
                {"investment": new_investment}
            )
            await Transactions.log_update_stakeholder(stakeholder_id, data['investment'], new_investment, data['profit_shares'], data['profit_shares'])

        else:    
            await Stakeholders.db.modify(
                {"stakeholder_id": stakeholder_id},
                {"investment": new_investment, "profit_shares": new_profit_shares}
            )
            await Transactions.log_update_stakeholder(stakeholder_id, data['investment'], new_investment, data['profit_shares'], new_profit_shares)

    async def get_all_stakeholders():
        return await Stakeholders.db.full()
    

class Holdings:
    db = HoldingsDB

    async def add_holding(coin_name, amount, avg_price):
        await Holdings.db.add({
            "coin_name": coin_name,
            "amount": amount,
            "avg_price": avg_price
        })
        await Transactions.log_new_holding(coin_name, amount, avg_price)

    async def get_holding_by_coin(coin_name):
        return await Holdings.db.find({"coin_name": coin_name})

    async def update_holding(coin_name, new_amount, new_avg_price):
        data = Holdings.get_holding_by_coin(coin_name)
        await Holdings.db.modify(
            {"coin_name": coin_name},
            {"amount": new_amount, "avg_price": new_avg_price}
        )
        await Transactions.log_update_holding(coin_name, data['amount'], new_amount, data['avg_price'], new_avg_price)

    async def close_holding(coin_name, selling_price):
        holding = await Holdings.db.find({"coin_name": coin_name})
        await Holdings.db.remove({"coin_name": coin_name})
        await Transactions.log_close_holding(coin_name, selling_price)
        profit_loss = (selling_price - holding['avg_price']) * holding['amount']
        Holdings.split_profits(profit_loss)

    async def reduce_holding(coin_name, reduction_amount, selling_price):
        holding = await Holdings.db.find({"coin_name": coin_name})
        new_amount = holding['amount'] - reduction_amount
        await Holdings.update_holding(coin_name, new_amount, holding['avg_price'])
        await Transactions.log_update_holding(coin_name, holding["amount"], new_amount, holding["avg_price"], holding["avg_price"])
        profit_loss = (selling_price - holding['avg_price']) * reduction_amount
        Holdings.split_profits(profit_loss)

    async def split_profits(profit_loss):
        stakeholders = await Stakeholders.get_all_stakeholders()
        total_principal = sum(stakeholder['investment'] for stakeholder in stakeholders)
        final_profits = dict()
        for stakeholder in stakeholders:
            stakeholder_investment = stakeholder['investment']
            for shid, percent in stakeholder['profit_shares'].items():
                if final_profits.get(shid):
                    final_profits[shid] += (stakeholder_investment * percent / 100)
                else:
                    final_profits[shid] + (stakeholder_investment * percent / 100)

        await Transactions.log_profit_loss(profit_loss)
        for shid, value in final_profits.items():
            sh = Stakeholders.get_stakeholder_by_id(shid)
            new_investment = sh["investment"] + (profit_loss * value / total_principal)
            Stakeholders.update_stakeholder(shid, new_investment)

    async def get_all_holdings():
        return await Holdings.db.full()
    