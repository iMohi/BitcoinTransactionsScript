#this script is using explorer.btc.com API
import requests
import json
from datetime import datetime
import math
import pandas as pd
import openpyxl
import xlsxwriter
import xlrd
import os.path


def getAddressInfo(walletadd):
    url = requests.get(f"https://chain.api.btc.com/v3/address/{walletadd}")
    getAddDetails = url.json()["data"]
    address = getAddDetails["address"]
    received = float(getAddDetails["received"]) * float(satoshi)
    sent = float(getAddDetails["sent"]) * float(satoshi)
    balance = float(getAddDetails["balance"]) * float(satoshi)
    txCount = getAddDetails["tx_count"]

    layout = {
        "Address": address,
        "Total_Received": received,
        "Total_Sent": sent,
        "Transactions": txCount,
        "Final_Balance": balance
    }
    return layout

#get transactions for the given wallet address
def getAddressTransactions(walletadd,pagenum):
    url = requests.get(f"https://chain.api.btc.com/v3/address/{walletadd}/tx?page={pagenum}")
    getTransDetails = url.json()["data"]["list"]

    totalResult = []

    #Check for all transaction
    for tnum, content in enumerate(getTransDetails):

        #print(json.dumps(getTransDetails[tnum], indent=4))
        txHash = getTransDetails[tnum]["hash"]
        txTime = datetime.fromtimestamp(int(getTransDetails[tnum]["block_time"]))
        inputsCount = getTransDetails[tnum]["inputs_count"]
        inputsValue = float(getTransDetails[tnum]["inputs_value"]) * float(satoshi)
        outputsCount = getTransDetails[tnum]["outputs_count"]
        outputValue = float(getTransDetails[tnum]["outputs_value"]) * float(satoshi)
        coinbase = getTransDetails[tnum]["is_coinbase"]
        fees = inputsValue - outputValue


        if inputsCount == 1:
            fromAddress = getTransDetails[tnum]["inputs"][0]["prev_addresses"]
            if fromAddress != walletadd:
                transType = "Received"
            else:
                transType = "Sent"
        else:
            fromAddress = getTransDetails[tnum]["inputs"]
            transType = "Received"
            for i in range(inputsCount):
                transType = "Received"
                if str(fromAddress[i]["prev_addresses"][0]) == str(walletadd):
                    transType = "Sent"
                    break

        if coinbase == "true":
            exchange = "Coinbase"
        else:
            exchange = "Unknown"

        if transType == "Sent":
            outputAddressList = []
            outputAddress = getTransDetails[tnum]["outputs"]

            for index, outadd in enumerate(outputAddress):
                outputAddressList.append({"address": outadd["addresses"][0],"Value": float(outadd["value"]) * float(satoshi) })

            layout = {
                "Address": walletadd,
                "Transaction_Hash": txHash,
                "Date_and_Time": str(txTime),
                "Transaction_Type": transType,
                "Output_Address": outputAddressList,
                "Input_Count": inputsCount,
                "Output_Count": outputsCount,
                "Input_Value": inputsValue,
                "Output_Value": outputValue,
                "Exchange": exchange,
            }
            totalResult.append(layout)

        elif transType == "Received":
            inputAddressList = []
            inputAddress = getTransDetails[tnum]["inputs"]
            outputAddress = getTransDetails[tnum]["outputs"]


            # get the amount received
            for index, outadd in enumerate(outputAddress):
                if str(walletadd) == str(outadd["addresses"][0]):
                    amountReceived = float(outadd["value"]) * float(satoshi)
                    break

            #get the input addresses and its value
            for index, inadd in enumerate(inputAddress):
                inputAddressList.append({"Address": inadd["prev_addresses"][0],
                                         "Value": float(inadd["prev_value"]) * float(satoshi)})

            layout = {
                "Address": walletadd,
                "Transaction_Hash": txHash,
                "Date_and_Time": str(txTime),
                "Transaction_Type": transType,
                "Input_Address": inputAddressList,
                "Input_Count": inputsCount,
                "Output_Count": outputsCount,
                "Input_Value": inputsValue,
                "Output_Value": outputValue,
                "Amount_Received": amountReceived,
                "Exchange": exchange,
            }
            totalResult.append(layout)

    return totalResult


def walletDataframe(totalList):
    tier = []
    ransomWallet = []
    waladdress = []
    txHash = []
    txType = []
    inputAdd = []
    inputAmount = []
    outputAdd = []
    outputAmount = []
    dateTime = []
    relation = []
    ransomFam = []
    source = []

    for data in totalList:
        #if transaction is from the sender get the senders wallet info
        if data["Transaction_Type"] == "Received":
            for num in range(data["Input_Count"]):
                tier.append("Base")
                ransomWallet.append(data["Address"])
                waladdress.append(data["Address"])
                txHash.append(data["Transaction_Hash"])
                txType.append(data["Transaction_Type"])
                inputAdd.append(data["Input_Address"][num]["Address"])
                inputAmount.append(data["Amount_Received"])
                outputAdd.append(data["Address"])
                outputAmount.append(data["Input_Value"])
                dateTime.append(data["Date_and_Time"])
                relation.append(data["Address"])
                ransomFam.append("Netwalker")
                source.append("https://zenodo.org/record/6512123#.YwXH0XZBy5d")
                print(data)


        elif data["Transaction_Type"] == "Sent":
            for num in range(data["Output_Count"]):
                tier.append("Base")
                ransomWallet.append(data["Address"])
                waladdress.append(data["Address"])
                txHash.append(data["Transaction_Hash"])
                txType.append(data["Transaction_Type"])
                inputAdd.append(data["Address"])
                inputAmount.append(data["Input_Value"])
                outputAdd.append(data["Output_Address"][num]["address"])
                outputAmount.append(data["Output_Address"][num]["Value"])
                dateTime.append(data["Date_and_Time"])
                relation.append(data["Address"])
                ransomFam.append("Netwalker")
                source.append("https://zenodo.org/record/6512123#.YwXH0XZBy5d")

    layout = {"Tier (I,II, III, IV)": tier,
              "Ransomware related Address": ransomWallet,
              "Wallet Address": waladdress,
              "Transaction Hash": txHash,
              "Transation Type": txType,
              "Senders Address": inputAdd,
              "Sent Amount(BTC)": inputAmount,
              "Receivers Address": outputAdd,
              "Received Amount(BTC)": outputAmount,
              "Date and Time": dateTime,
              "Relationship Address": relation,
              "Ransomware Family": ransomFam,
              "Source": source}

    return layout

def convertToExcel(dataframe):
    if os.path.exists("Ransomware_Dataset.xlsx"):
        print("it exist")
        df = pd.DataFrame(dataframe)
        with pd.ExcelWriter("Ransomware_Dataset.xlsx", mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            df.to_excel(writer, sheet_name="Wallet Address", header=None, startrow=writer.sheets["Wallet Address"].max_row, index=False)
    else:
        print("Converted Successfully")
        df = pd.DataFrame(dataframe)
        writer = pd.ExcelWriter("Ransomware_Dataset.xlsx", engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Wallet Address", index=False)
        writer.save()


def tierRange(whole, tier):
    wholeTier = []
    inAddress = []
    OutAddress = []
    dictionary = {}

    for data in whole:
        if data["Transaction_Type"] == "Received":
            for num in range(data["Input_Count"]):
                dictionary["address"] = data["Input_Address"][num]["Address"]
                dictionary["type"] = "Received"
                OutAddress.append(dictionary)



whole = []

#walletAddress = "12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw"
walletAddress = "17TMc2UkVRSga2yYvuxSD9Q1XyB2EPRjTF"
satoshi = float(1.0) * float(10 ** -8)
transactionId = "55cde36a456e5fa90d23e34a0c8d83a12e46e83a07f171f69057ba4dbaac48fe"


#Request to get all of the transactions

totaltrans = getAddressInfo(walletAddress)["Transactions"]

if totaltrans > 10:
    calc = math.ceil(totaltrans / 10)
    for i in range(calc):
        get = getAddressTransactions(walletAddress, i + 1)
        whole.extend(get)

else:
    whole.extend(getAddressTransactions(walletAddress, 1))

print(json.dumps(whole, indent=4))

#print(json.dumps(walletDataframe(whole), indent=4))

#convertToExcel(walletDataframe(whole))

#print(json.dumps(getAddressTransactions(walletAddress), indent=4))
#getAddress2 = requests.get(f"https://chain.api.btc.com/v3/address/{walletAddress}/tx?pagesize=10")
#getTransactionInputOutput = requests.get(f"https://chain.api.btc.com/v3/tx/{transactionId}?verbose=3")

#print(json.dumps(getTransactionInputOutput.json(), indent=4 ))
#print(json.dumps(getAddress2.json(), indent=4))