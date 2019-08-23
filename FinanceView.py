import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import sys
import settings


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
    postDetails = {
        "fname" : "",
        "lname" : "",
        "requestjson" : "Submit"
    }
    incomePostDetails = {
        "fname" : "",
        "lname" : "",
        "requestIncomeJson" : "Submit"
    }
    userDetails = settings.load_user_settings()
    postUrl = userDetails['url']
    postDetails["fname"] = userDetails['userName']
    postDetails["lname"] = userDetails['pword']
    incomePostDetails["fname"] = userDetails['userName']
    incomePostDetails["lname"] = userDetails['pword']

    # read in the json file
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    datesPath = pathToDirectory + "/dates.json"

    with open(datesPath) as jsonfile:
        dates = json.load(jsonfile)

    # get current day
    currentYear = str(datetime.date.today().year)

    purchase_Response = fetchData(postDetails=postDetails, postUrl=postUrl)
    data = pd.DataFrame(json.loads(purchase_Response.text))
    # convert price to float
    data = data.astype({"TransactionPrice": float})
    expenseTotal = getTotalsOfIncome(data, moneySelection="Expense")


    print(expenseTotal)

    income_Response = fetchData(postDetails=incomePostDetails, postUrl=postUrl)
    incomeData = pd.DataFrame(json.loads(income_Response.text))
    incomeData = incomeData.astype({"Amount": float})
    incomeAmount = getTotalsOfIncome(incomeData, moneySelection="Income")


    print(incomeAmount)

    # set figure options
    font = {'size' : 5}
    plt.rc('font', **font)
    fig = plt.figure(figsize=(20,9), constrained_layout=False)
    fig.subplots_adjust(hspace=0.83, wspace=0.15)
    fig.suptitle('Total Lifetime Net Income: ' + str(incomeAmount - expenseTotal))


    # uncomment to print whole database
    # DataPrinter(data, "PurchaseId")
    # set the date column as datetime
    data["DateofTransaction"] = pd.to_datetime(data["DateofTransaction"])
    incomeData["IncomeDate"] = pd.to_datetime(incomeData["IncomeDate"])

    for i, month in enumerate(dates):
        # must clear the array each loop!
        totalsOfIncome = []
        totalsOfPurchases = []

        if (month != "februaryLEAP"):
            print("----------------------------------------" + month.upper() + "----------------------------------------")
            monthStartDate = currentYear + "-" + dates[month]['start']
            monthEndDate = currentYear + "-" + dates[month]['end']

            monthStartDateObject = datetime.datetime.strptime(monthStartDate, '%Y-%m-%d')
            monthEndDateObject = datetime.datetime.strptime(monthEndDate, '%Y-%m-%d')


            mask = (data['DateofTransaction'] >= monthStartDateObject) & (data['DateofTransaction'] <= monthEndDateObject)
            expenseMonthData = data.loc[mask]
            monthlyExpenseTotal = getTotalsOfIncome(expenseMonthData, 'Expense')

            incomeMask = (incomeData['IncomeDate'] >= monthStartDateObject) & (incomeData['IncomeDate'] <= monthEndDateObject)
            incomeMonthData = incomeData.loc[incomeMask]
            monthlyIncomeTotal = getTotalsOfIncome(incomeMonthData, 'Income')



            # #detect empty dataframe and dont make graph
            if expenseMonthData.empty == False:
                # print by client name each income table
                incomeMonthData.set_index("ClientName", inplace=True)
                incomeIndex = incomeMonthData.index
                incomeIndex = incomeIndex.drop_duplicates(keep='first')
                for clientName in incomeIndex:
                    clientSpecificData = incomeMonthData.loc[clientName]
                    print(clientSpecificData, end="\n\n")

                expenseMonthData.set_index("ExpenseName", inplace=True)
                index = expenseMonthData.index
                # get rid of the duplicates.. use as bar graph titles
                index = index.drop_duplicates(keep='first')

                # get data for each ExpenseCategory
                for item in index:
                    itemData = expenseMonthData.loc[item]
                    print(itemData, end="\n\n")
                    totalsOfPurchases.append(round(itemData['TransactionPrice'].sum(), 2))

                y_pos = np.arange(len(index))
                # i is the number of iterations from the master for loop
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

            print("----------------------------------------" + month.upper() + "----------------------------------------")
    plt.show()

if __name__=="__main__":
    main()
