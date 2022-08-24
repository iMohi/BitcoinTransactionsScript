#this script is using explorer.btc.com API
import requests
import json
from datetime import datetime


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

def getAddressTransactions(walletadd):
    url = requests.get(f"https://chain.api.btc.com/v3/address/{walletadd}/tx")
    getTransDetails = url.json()["data"]["list"]

    totalResult = []

    #Check for all transaction
    for tnum, content in enumerate(getTransDetails):

        print(getTransDetails[tnum])
        txHash = getTransDetails[tnum]["hash"]
        txTime = datetime.fromtimestamp(int(getTransDetails[tnum]["block_time"]))
        inputsCount = getTransDetails[tnum]["inputs_count"]
        inputsValue = float(getTransDetails[tnum]["inputs_value"]) * float(satoshi)
        outputsCount = getTransDetails[tnum]["outputs_count"]
        outputValue = float(getTransDetails[tnum]["outputs_value"]) * float(satoshi)
        coinbase = getTransDetails[tnum]["is_coinbase"]
        fees = inputsValue - outputValue
        inputsList = []

        if inputsCount == 1:
            fromAddress = getTransDetails[tnum]["inputs"][0]["prev_addresses"]
            inputsList.append(fromAddress)
            if fromAddress != walletadd:
                transType = "Received"
            else:
                transType = "Sent"
        else:
            fromAddress = getTransDetails[tnum]["inputs"][0]
            for address in fromAddress["prev_addresses"]:
                transType = "Received"
                if address == str(walletadd):
                    transType = "Sent"
                    break

        if coinbase == "true":
            exchange = "Coinbase"
        else:
            exchange = "Unknown"

        layout = {
            "Address": walletadd,
            "Transaction_Hash": txHash,
            "Date_and_Time": str(txTime),
            "Transaction_Type": transType,
            "Input_Count": inputsCount,
            "Output_Count": outputsCount,
            "Input_Value" : inputsValue,
            "Output_Value": outputValue,
            "Exchange": exchange,
        }

        totalResult.append(layout)
    return totalResult


#walletAddress = "12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw"
walletAddress = "17TMc2UkVRSga2yYvuxSD9Q1XyB2EPRjTF"
satoshi = float(1.0) * float(10 ** -8)
transactionId = "55cde36a456e5fa90d23e34a0c8d83a12e46e83a07f171f69057ba4dbaac48fe"

print(json.dumps(getAddressTransactions(walletAddress), indent=4))
#getAddress2 = requests.get(f"https://chain.api.btc.com/v3/address/{walletAddress}/tx?pagesize=10")
#getTransactionInputOutput = requests.get(f"https://chain.api.btc.com/v3/tx/{transactionId}?verbose=3")

#print(json.dumps(getTransactionInputOutput.json(), indent=4 ))
#print(json.dumps(getAddress2.json(), indent=4))