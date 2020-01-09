import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import sys
import settings
# last audit was Aug. 22, therefore only audit from there on for inconsistencies.

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
def dataProcessor(expenseData, incomeData, expense_cats_data, graphTitle, printData=True):
    totalsOfPurchases=[]
    totalsOfIncome=[]
    # print by client name each income table
    incomeData.set_index("ClientName", inplace=True)
    incomeIndex = incomeData.index
    incomeIndex = incomeIndex.drop_duplicates(keep='first')
    for clientName in incomeIndex:
        clientSpecificData = incomeData.loc[clientName]
        if printData:
            print(clientSpecificData, end="\n\n")
        totalsOfIncome.append(round(clientSpecificData['Amount'].sum(),2))

    alpha_Data = expenseData.sort_values('ExpenseName', ascending=True) # sort data by ExpenseName alphabetically
    alpha_Data.set_index("ExpenseName", inplace=True)
    expenses_index = alpha_Data.index
    # get rid of the duplicates.. use as bar graph titles
    expenses_index = expenses_index.drop_duplicates(keep='first')

    alpha_exp_cat_data = expense_cats_data.sort_values('ExpenseName', ascending=True) # get the index from the expense categories data, alphabetically
    alpha_exp_cat_data.set_index("ExpenseName", inplace=True)
    expense_cats_index = alpha_exp_cat_data.index

    for item in expense_cats_index: # iterate the expense cat index, checking data for the index and setting 0 if it is missing
        if item in expenses_index:
            itemData = alpha_Data.loc[item]
            if printData:
                print(itemData, end="\n\n")
            totalsOfPurchases.append(round(itemData['TransactionPrice'].sum(), 2))
        else:
            totalsOfPurchases.append(0)

    return [graphTitle, expense_cats_index, totalsOfPurchases, totalsOfIncome]

def plotter(numFigRows, numFigCols, listOfData, yLabel, fullPlotTitle, fontSize, hspace, wspace, figSize):
    # set figure options
    font = {'size' : fontSize}
    plt.rc('font', **font)
    fig = plt.figure(figsize=figSize, constrained_layout=False)
    fig.subplots_adjust(hspace=hspace, wspace=wspace)
    fig.suptitle(fullPlotTitle)
    for i, dataStructure in enumerate(listOfData):
        y_pos = np.arange(len(dataStructure[1]))
        # i is the number of iterations from the master for loop
        ax = fig.add_subplot(numFigRows, numFigCols, i+1)
        ax.bar(y_pos, dataStructure[2], align='center', alpha=0.5)
        ax.set_xticks(y_pos)
        ax.set_xticklabels(dataStructure[1])
        ax.set_ylabel(yLabel)
        ax.set_title(dataStructure[0])

        for i, purchaseTotal in enumerate(dataStructure[2]):
            ax.text(i, 0.95*purchaseTotal, purchaseTotal, ha='center')
    # uncomment to show graphs one at a time
    # plot.show()

def monthlyPlots(expenseData, incomeData, expense_cats_data, dates, incomeAmount, expenseTotal, currentYear):
    # uncomment to print whole database
    # DataPrinter(data, "PurchaseId")
    # set the date column as datetime
    dataListForPlotting = []
    monthCounter = 0
    expenseData["DateofTransaction"] = pd.to_datetime(expenseData["DateofTransaction"])
    incomeData["IncomeDate"] = pd.to_datetime(incomeData["IncomeDate"])
    for i, month in enumerate(dates):
        # must clear the array each loop!
        totalsOfIncome = []
        totalsOfPurchases = []

        if (month != "februaryLEAP"):
            # FILTERING DATA BY MONTH
            print("----------------------------------------" + month.upper() + "----------------------------------------")
            monthStartDate = currentYear + "-" + dates[month]['start']
            monthEndDate = currentYear + "-" + dates[month]['end']

            monthStartDateObject = datetime.datetime.strptime(monthStartDate, '%Y-%m-%d')
            monthEndDateObject = datetime.datetime.strptime(monthEndDate, '%Y-%m-%d')


            mask = (expenseData['DateofTransaction'] >= monthStartDateObject) & (expenseData['DateofTransaction'] <= monthEndDateObject)
            expenseMonthData = expenseData.loc[mask]
            monthlyExpenseTotal = getTotalsOfIncome(expenseMonthData, 'Expense')

            incomeMask = (incomeData['IncomeDate'] >= monthStartDateObject) & (incomeData['IncomeDate'] <= monthEndDateObject)
            incomeMonthData = incomeData.loc[incomeMask]
            monthlyIncomeTotal = getTotalsOfIncome(incomeMonthData, 'Income')

            # #detect empty dataframe and dont make graph
            if expenseMonthData.empty == False:
                # print by client name each income table
                graphTitle = "Expenses in: %s-%s\nIncome: %s || Expenses %s\nMonthly Net Income: %s" % (
                                                                                                        monthStartDate,
                                                                                                        monthEndDate,
                                                                                                        monthlyIncomeTotal,
                                                                                                        monthlyExpenseTotal,
                                                                                                        str(round(monthlyIncomeTotal - monthlyExpenseTotal, 2))
                                                                                                       )
                dataListForPlotting.append(dataProcessor(expenseMonthData, incomeMonthData, expense_cats_data, graphTitle))
                monthCounter += 1

            print("----------------------------------------" + month.upper() + "----------------------------------------")


    plotter(numFigRows=6,
            numFigCols=2,
            listOfData=dataListForPlotting,
            yLabel="Dollas",
            fullPlotTitle='Total Lifetime Net Income: %s' % (incomeAmount - expenseTotal),
            fontSize=5,
            hspace=0.83,
            wspace=0.15,
            figSize=(20,9))
    return monthCounter

def yearlyPlots(expenseData, incomeData, expense_cats_data, dates, incomeAmount, expenseTotal, currentYear, numberOfMonthsPassed):
    dataListForPlotting = []
    plotTitle = 'Total Lifetime Net Income: %s\nIncome Total: %s || Expenses Total: %s' % (incomeAmount - expenseTotal, incomeAmount, expenseTotal)
    if currentYear != str(datetime.date.today().year):
        monthStartDate = currentYear + "-12-1"
    else:
        monthStartDate = currentYear + "-" + str(datetime.date.today().month) + "-1"
    currentMonthBeginning = datetime.datetime.strptime(monthStartDate, '%Y-%m-%d')

    expenseData["DateofTransaction"] = pd.to_datetime(expenseData["DateofTransaction"])
    mask = (expenseData['DateofTransaction'] < currentMonthBeginning)
    filteredExpenseData = expenseData.loc[mask]

    incomeData["IncomeDate"] = pd.to_datetime(incomeData["IncomeDate"])
    mask = (incomeData['IncomeDate'] <= currentMonthBeginning)
    filteredIncomeData = incomeData.loc[mask]

    expenseGraphTitle="Total for year until Today."
    # for each list you want plotted, just append a dataProcessor to dataListForPlotting
    dataListForPlotting.append(dataProcessor(expenseData=expenseData,
                                             incomeData=incomeData,
                                             expense_cats_data=expense_cats_data,
                                             graphTitle=expenseGraphTitle,
                                             printData=False))
    filteredExpenseGraphTitle = "Total for the year until %s" % (currentMonthBeginning)
    dataListForPlotting.append(dataProcessor(expenseData=filteredExpenseData,
                                             incomeData=filteredIncomeData,
                                             expense_cats_data=expense_cats_data,
                                             graphTitle=filteredExpenseGraphTitle,
                                             printData=False))
    # you must use list() so you dont create double reference to same object in memory.
    # used '1' here to make a copy of the yearly data excluding the current month
    dataListForPlotting.append(list(dataListForPlotting[1]))

    purchaseAverager = lambda data: round(data/numberOfMonthsPassed, 2)
    # replaces the data copied in above with averaged data
    dataListForPlotting[2][2] = list(map(purchaseAverager, dataListForPlotting[2][2])) # average the expenses
    dataListForPlotting[2][3] = list(map(purchaseAverager, dataListForPlotting[2][3])) # average the income

    avg_exp_per_month = (round(sum(dataListForPlotting[2][2], 2)))
    avg_inc_per_month = (round(sum(dataListForPlotting[2][3], 2)))

    averages_title = "Average for the year %s\n" %(currentYear)
    averages_title += "Average Expenses Per Month Thus Far: %s\n" % (avg_exp_per_month)
    averages_title += "Average Income Per Month Thus Far: %s\n" % (avg_inc_per_month)
    averages_title += "Avg. Net Income Thus Far: %s" % (avg_inc_per_month - avg_exp_per_month)
    dataListForPlotting[2][0] = averages_title

    plotter(numFigRows=len(dataListForPlotting),
            numFigCols=1,
            listOfData=dataListForPlotting,
            yLabel="Dollas",
            fullPlotTitle=plotTitle,
            fontSize=5,
            hspace=0.83,
            wspace=0.15,
            figSize=(20,9))

def main():
    # will be populated by command line arguments
    exp_postDetails = {
        "fname" : "",
        "lname" : "",
        "requestjson" : "Submit"
    }
    incomePostDetails = {
        "fname" : "",
        "lname" : "",
        "requestIncomeJson" : "Submit"
    }
    exp_cat_postDetails = {
        "fname" : "",
        "lname" : "",
        "getExpenses" : "Submit"
    }
    userDetails = settings.load_user_settings(os.path.join(os.path.dirname(__file__), 'secret.json'))
    postUrl = userDetails['url']
    exp_postDetails["fname"] = userDetails['userName']
    exp_postDetails["lname"] = userDetails['pword']
    incomePostDetails["fname"] = userDetails['userName']
    incomePostDetails["lname"] = userDetails['pword']
    exp_cat_postDetails["fname"] = userDetails['userName']
    exp_cat_postDetails["lname"] = userDetails['pword']

    # read in the json file
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    datesPath = pathToDirectory + "/dates.json"

    with open(datesPath) as jsonfile:
        dates = json.load(jsonfile)

    # get current day
    currentYear = str(input("Enter the year you wish to see data for: "))

    purchase_Response = fetchData(postDetails=exp_postDetails, postUrl=postUrl)
    expenseData = pd.DataFrame(json.loads(purchase_Response.text))

    # convert price to float
    expenseData = expenseData.astype({"TransactionPrice": float})
    expenseTotal = getTotalsOfIncome(expenseData, moneySelection="Expense")

    income_Response = fetchData(postDetails=incomePostDetails, postUrl=postUrl)
    incomeData = pd.DataFrame(json.loads(income_Response.text))
    incomeData = incomeData.astype({"Amount": float})
    incomeAmount = getTotalsOfIncome(incomeData, moneySelection="Income")

    expense_cats_response = fetchData(postDetails=exp_cat_postDetails, postUrl=postUrl)
    expense_cats_data = pd.DataFrame(json.loads(expense_cats_response.text))

    print(expense_cats_data)

    monthCounter = monthlyPlots(expenseData, incomeData, expense_cats_data, dates, incomeAmount, expenseTotal, currentYear)
    yearlyPlots(expenseData, incomeData, expense_cats_data, dates, incomeAmount, expenseTotal, currentYear, monthCounter - 1)
    plt.show()

if __name__=="__main__":

    main()
