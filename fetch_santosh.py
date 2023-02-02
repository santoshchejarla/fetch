from datetime import datetime
from collections import deque, defaultdict
import csv
from sys import argv


class read_data:
    def read_data(self, file_name="transactions.csv") -> list:
        """Opens file_name as read the data from the file

        Args:
            file_name (str, optional): file_name to read the data from. Defaults to "transactions.csv".

        Returns:
            list: list of transactions
        """
        transactions = []
        with open(file_name, "r") as tf:
            transactions_data = csv.reader(tf)
            next(transactions_data)
            for transaction in transactions_data:
                payer, points, timestamp = transaction
                timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                transactions.append((payer, int(points), timestamp))
        return transactions


class transaction:
    def __init__(self, amount) -> None:
        """initialized transaction class

        Args:
            amount (int): amount to deduct
        """
        self.payers = defaultdict(deque)
        self.order = deque()
        self.amount = int(amount)

    def load_data(self, file_name="transactions.csv") -> None:
        """loads the transaction data and populats required data structures with values

        Args:
            file_name (str, optional): file_name that contains the transactions. Defaults to "transactions.csv".
        """
        read_data_obj = read_data()
        transactions = read_data_obj.read_data(file_name)
        transactions.sort(key=lambda x: x[-1])
        for transaction in transactions:
            payer, points, ts = transaction
            if points < 0:
                # Negative points indicate debit, so follow the order of transactions to debit the amount
                while points < 0:
                    # Continue debiting the amount untill points become zero
                    first_payer = self.order.popleft()
                    first_points = self.payers[first_payer].popleft()
                    points, first_points = points + first_points, first_points + points
                    if first_points > 0:
                        # If the last debit has some points left add them back to the order
                        self.order.appendleft(first_payer)
                        self.payers[first_payer].appendleft(first_points)
            else:
                self.order.append(payer)
                self.payers[payer].append(points)

    def solve(self) -> dict:
        """solves the given problem

        Returns:
            dict: Dictonary containing payer names as keys and this remaining balance as values
        """
        amount = self.amount
        while amount > 0:
            payer = self.order.popleft()
            if self.payers[payer]:
                transaction_points = self.payers[payer].popleft()
                if transaction_points > amount:
                    self.payers[payer].append(transaction_points - amount)
                    amount = 0
                    break
                else:
                    amount -= transaction_points

        ret = {}
        for payer in self.payers:
            if payer not in ret:
                ret[payer] = 0
            ret[payer] += sum(self.payers[payer])
        return ret


def main():
    if len(argv) < 2:
        print("Please use the format: python3 solve.py $AMOUNT")
        return
    amount = argv[1]
    transaction_obj = transaction(amount)
    transaction_obj.load_data()
    print(transaction_obj.solve())


if __name__ == "__main__":
    main()
