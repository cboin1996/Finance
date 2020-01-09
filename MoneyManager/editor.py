import mysql.connector
import os
import json

class SQLViewer:
    def __init__(self, file_path):
        with open(file_path) as file:
            user_info = json.load(file)

        mydb = mysql.connector.connect(
          host=user_info["host"],
          user=user_info["uname"],
          passwd=user_info["pword"],
          database=user_info["database"]
        )

def main():
    path_to_settings = os.path.join(os.path.dirname(__file__), 'acct.json')



    mycursor = mydb.cursor()
    mycursor.execute("SELECT CBPurchasing.PurchaseId, CBPurchasing.TransactionPrice, CBPurchasing.DateofTransaction, CBVendors.StoreName, CBExpenses.ExpenseName FROM CBPurchasing INNER JOIN CBVendors ON CBPurchasing.StoreNameID=CBVendors.StoreNameID INNER JOIN CBExpenses ON CBPurchasing.ExpenseID = CBExpenses.ExpenseID ORDER BY Cast(DateOfTransaction AS datetime);")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
if __name__=="__main__":
    main()
