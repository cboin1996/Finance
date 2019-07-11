import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import sys


def fetchData(postDetails, postUrl):
    with requests.Session() as s:
        try:
            response = s.post(postUrl, data=postDetails)
            return response
        except:
            print("Error")

def DataPrinter(DataFrame, indexChoice):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    DataFrame.set_index(indexChoice)
    print(DataFrame)

def getTotalsOfIncome(DataFrame, moneySelection):

    if (moneySelection=="Income"):
        return round(DataFrame["Amount"].sum(),2)

    if (moneySelection=="Expense"):
        return round(DataFrame["TransactionPrice"].sum(),2)

    else:
        return print("No option for your function bro.")

def main():
    # will be populated by command line arguments
    postDetails = {}
    incomePostDetails = {}
    postUrl = sys.argv[1]
    postDetails["fname"] = sys.argv[2]
    postDetails["lname"] = sys.argv[3]
    incomePostDetails["fname"] = sys.argv[2]
    incomePostDetails["lname"] = sys.argv[3]

    # read in the json file
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    datesPath = pathToDirectory + "/dates.json"
    with open(datesPath) as jsonfile:
        dates = json.load(jsonfile)

    # get current day
    currentYear = str(datetime.date.today().year)

    purchase_Response = fetchData(postDetails=postDetails, postUrl=postUrl)
    data = pd.DataFrame(json.loads(purchase_Response.text))
    data = data.astype({"TransactionPrice": float})
    expenseTotal = getTotalsOfIncome(data, moneySelection="Expense")


    print(expenseTotal)

    income_Response = fetchData(postDetails=incomePostDetails, postUrl=postUrl)
    incomeData = pd.DataFrame(json.loads(income_Response.text))
    incomeData = incomeData.astype({"Amount": float})
    incomeAmount = getTotalsOfIncome(incomeData, moneySelection="Income")


    print(incomeAmount)

    # set figure options
    font = {'size' : 6}
    plt.rc('font', **font)
    fig = plt.figure(figsize=(10,9), constrained_layout=False)
    fig.subplots_adjust(hspace=0.83, wspace=0.4)
    fig.suptitle('Total Lifetime Net Income: ' + str(incomeAmount - expenseTotal))


    # uncomment to print whole database
    # DataPrinter(data, "PurchaseId")
    data["DateofTransaction"] = pd.to_datetime(data["DateofTransaction"])
    incomeData["IncomeDate"] = pd.to_datetime(incomeData["IncomeDate"])
    # counter

    for i, month in enumerate(dates):
        # must clear the array each loop!
        totalsOfIncome = []
        totalsOfPurchases = []

        if (month != "februaryLEAP"):
            print("--------------------" + month + "--------------------")
            monthStartDate = currentYear + "-" + dates[month]['start']
            monthEndDate = currentYear + "-" + dates[month]['end']

            monthStartDateObject = datetime.datetime.strptime(monthStartDate, '%Y-%m-%d')
            monthEndDateObject = datetime.datetime.strptime(monthEndDate, '%Y-%m-%d')


            mask = (data['DateofTransaction'] > monthStartDateObject) & (data['DateofTransaction'] <= monthEndDateObject)
            expenseMonthData = data.loc[mask]
            monthlyExpenseTotal = getTotalsOfIncome(expenseMonthData, 'Expense')

            incomeMask = (incomeData['IncomeDate'] > monthStartDateObject) & (incomeData['IncomeDate'] <= monthEndDateObject)
            incomeMonthData = incomeData.loc[incomeMask]
            monthlyIncomeTotal = getTotalsOfIncome(incomeMonthData, 'Income')



            # #detect empty dataframe and dont make graph
            if expenseMonthData.empty == False:
                # set price data to float type for summing
                expenseMonthData.set_index("ExpenseName", inplace=True)
                index = expenseMonthData.index
                # get rid of the duplicates.. use as bar graph titles
                index = index.drop_duplicates(keep='first')

                # get data for each ExpenseCategory
                for item in index:
                    itemData = expenseMonthData.loc[item]
                    print(itemData)
                    totalsOfPurchases.append(round(itemData['TransactionPrice'].sum(), 2))

                y_pos = np.arange(len(index))

                ax = fig.add_subplot(6, 2, i)
                ax.bar(y_pos, totalsOfPurchases, align='center', alpha=0.5)
                ax.set_xticks(y_pos)
                ax.set_xticklabels(index)
                ax.set_ylabel('Dollas')
                graphTitleTop = "Expenses in: " + monthStartDate + " to " + monthEndDate + "\n"
                graphTitleMiddle = "Income: %s || Expenses %s \n" % (monthlyIncomeTotal, monthlyExpenseTotal)
                graphTitleBottom = "Monthly Net Income: " + str(round(monthlyIncomeTotal - monthlyExpenseTotal, 2))
                ax.set_title(graphTitleTop + graphTitleMiddle + graphTitleBottom)

                for i, purchaseTotal in enumerate(totalsOfPurchases):

                    ax.text(i, 0.95*purchaseTotal, purchaseTotal, ha='center')

            print("-----------------------------------------------------")
    plt.show()

if __name__=="__main__":
    main()
