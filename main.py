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
import time
import gui

#This function gets all the wallet address information. eg. How much bitcoin is being sent or recieved, transactions, etc
def getAddressInfo(walletadd):
    url = requests.get(f"https://chain.api.btc.com/v3/address/{walletadd}") #Get request to extract data from chain.api.btc.com
    getAddDetails = url.json()["data"] #convert data into json format and store into getAddDetails
    address = getAddDetails["address"] #select the value of "address" key
    received = float(getAddDetails["received"]) * float(satoshi) #select the value of "received" and convert it to nearest whole number
    sent = float(getAddDetails["sent"]) * float(satoshi) #select the value of "sent" and convert it to nearest whole number
    balance = float(getAddDetails["balance"]) * float(satoshi) #select the value of "balance" and convert it to nearest whole number
    txCount = getAddDetails["tx_count"] #select the value of "received" to check the all transaction count

    #Laying out necessary information
    layout = {
        "Address": address,
        "Total_Received": received,
        "Total_Sent": sent,
        "Transactions": txCount,
        "Final_Balance": balance
    }
    return layout

#get transactions for the given wallet address. eg. just the particular wallet address
def getAddressTransactions(walletadd,pagenum):
    url = requests.get(f"https://chain.api.btc.com/v3/address/{walletadd}/tx?page={pagenum}") #Get request to extract data from chain.api.btc.com
    getTransDetails = url.json()["data"]["list"]  # Convert the data into readable json

    totalResult = [] # List all the items in layout filter all the stuffs that is needed and store in this array

    #Loop to Check for all transaction
    for tnum, content in enumerate(getTransDetails):
        #set variables for each value that has been extracted from the Json list
        txHash = getTransDetails[tnum]["hash"]
        txTime = datetime.fromtimestamp(int(getTransDetails[tnum]["block_time"]))
        inputsCount = getTransDetails[tnum]["inputs_count"]
        inputsValue = float(getTransDetails[tnum]["inputs_value"]) * float(satoshi)
        outputsCount = getTransDetails[tnum]["outputs_count"]
        outputValue = float(getTransDetails[tnum]["outputs_value"]) * float(satoshi)
        coinbase = getTransDetails[tnum]["is_coinbase"]

        #Suspicious Flag
        trans = getAddressInfo(walletadd)["Transactions"]
        if trans == 2:
            stats = "Suspicious"
        else:
            stats = "Normal"

        #if input count only contains 1 wallet address then run this block
        if inputsCount == 1:
            fromAddress = getTransDetails[tnum]["inputs"][0]["prev_addresses"]
            #if the current input address matches with the walletadd variable then flag the transtype to be Recieved or else flag as sent
            if fromAddress[0] != walletadd:
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
        #if the walletadd variable belongs to coinbase exchange then create a variable which has a value of "Coinbase" or else store the value as "Unknown"
        if coinbase == "true":
            exchange = "Coinbase"
        else:
            exchange = "Unknown"
        if transType == "Sent": #If the transaction type value is "Sent" then get the details of the output value and store in outputAddressList
            outputAddressList = []
            outputAddress = getTransDetails[tnum]["outputs"]

            for index, outadd in enumerate(outputAddress):
                outputAddressList.append({"address": outadd["addresses"][0],"Value": float(outadd["value"]) * float(satoshi) })

            #create a layout to make the data readable and easy to manipulate
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
                "Flag": stats,
            }
            totalResult.append(layout)

        elif transType == "Received": #If the transaction type value is "Received" then get the details of the Input value and store in inputAddressList
            inputAddressList = []
            inputAddress = getTransDetails[tnum]["inputs"]
            outputAddress = getTransDetails[tnum]["outputs"]

            # get the input addresses and its value
            for index, inadd in enumerate(inputAddress):
                inputAddressList.append({"Address": inadd["prev_addresses"][0],
                                         "Value": float(inadd["prev_value"]) * float(satoshi)})

            # get the amount received
            for index, outadd in enumerate(outputAddress):
                if str(walletadd) == str(outadd["addresses"][0]):
                    amountReceived = float(outadd["value"]) * float(satoshi)
                    break
            #Layout and filter the data into readable format
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
                "Flag": stats,
            }

            totalResult.append(layout)

    return totalResult


# This converts the data into a list so in can be written in excel. Basically a data manipulation
def walletDataframe(ransomWall, totalList, tierLvl, relationship, ranFam, Src):
    #set an empty lists based on their data name
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
    stats = []

    for data in totalList:
        #if transaction is from the sender get the senders wallet info
        if data["Transaction_Type"] == "Received":
            for num in range(data["Input_Count"]):
                tier.append(tierLvl)
                ransomWallet.append(ransomWall)
                waladdress.append(data["Address"])
                txHash.append(data["Transaction_Hash"])
                txType.append(data["Transaction_Type"])
                inputAdd.append(data["Input_Address"][num]["Address"])
                inputAmount.append(data["Input_Address"][num]["Value"])
                outputAdd.append(data["Address"])
                outputAmount.append(data["Amount_Received"])
                dateTime.append(data["Date_and_Time"])
                relation.append(relationship)
                ransomFam.append(ranFam)
                source.append(Src)
                if tierLvl == "Base":
                    stats.append("Suspicious")
                else:
                    stats.append(data["Flag"])

        elif data["Transaction_Type"] == "Sent":
            for num in range(data["Output_Count"]):
                tier.append(tierLvl)
                ransomWallet.append(ransomWall)
                waladdress.append(data["Address"])
                txHash.append(data["Transaction_Hash"])
                txType.append(data["Transaction_Type"])
                inputAdd.append(data["Address"])
                inputAmount.append(data["Input_Value"])
                outputAdd.append(data["Output_Address"][num]["address"])
                outputAmount.append(data["Output_Address"][num]["Value"])
                dateTime.append(data["Date_and_Time"])
                relation.append(relationship)
                ransomFam.append(ranFam)
                source.append(Src)
                if tierLvl == "Base":
                    stats.append("Suspicious")
                else:
                    stats.append(data["Flag"])

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
              "Source": source,
              "Transaction Flag": stats}

    return layout # return the layout data to be written

#this function writes tha data that has been stored on Walletdatafram function onto excel
def convertToExcel(dataframe, loc):
    if os.path.exists(loc + "/Ransomware_Dataset.xlsx"):
        print("it exist")
        df = pd.DataFrame(dataframe)
        with pd.ExcelWriter(loc + "/Ransomware_Dataset.xlsx", mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            df.to_excel(writer, sheet_name="Wallet Address", header=None, startrow=writer.sheets["Wallet Address"].max_row, index=False)
    else:
        print("Converted Successfully")
        df = pd.DataFrame(dataframe)
        writer = pd.ExcelWriter(loc + "/Ransomware_Dataset.xlsx", engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Wallet Address", index=False)
        writer.save()

def calculateWholeTx(wallet): #gets all the transaction in wallet
    wholeCalc = [] #set an empty list to temporarily store the layouted transaction
    # Request to get all of the transactions
    totaltrans = getAddressInfo(wallet)["Transactions"]
    if totaltrans > 10:
        calc = math.ceil(totaltrans / 10)
        for i in range(calc):
            get = getAddressTransactions(wallet, i + 1)
            wholeCalc.extend(get)
            print(f"Get all transaction in page {i}")
    else:
        wholeCalc.extend(getAddressTransactions(wallet, 1))
    return wholeCalc


def tierRange(whole, tier):
    wholeTier = []
    totalAddress = []
    OutAddress = []


    for i in range(tier):
        totalAddress.clear()
        tempInAddress = []

        for data in whole:
            #print(dictionary)
            if data["Transaction_Type"] == "Received":
                for num in range(data["Input_Count"]):
                    dictionary = {}
                    dictionary["address"] = data["Input_Address"][num]["Address"]
                    dictionary["type"] = "Received"
                    tempInAddress.append(dictionary)

            if data["Transaction_Type"] == "Sent":
                for num in range(data["Output_Count"]):
                    dictionary = {}
                    dictionary["address"] = data["Output_Address"][num]["address"]
                    dictionary["type"] = "Sent"
                    tempInAddress.append(dictionary)
        totalAddress.extend(tempInAddress)
    return totalAddress

def tempInOut(whole, type):
    tempInAddress = []
    dic = {}
    transList = []

    if type == "Sent":
        for data in whole:
            if data["Transaction_Type"] == "Sent":
                for num in range(data["Output_Count"]):
                    transList.append(data["Output_Address"][num]["address"])
                    # tempInAddress.append(data["Output_Address"][num]["address"])

    if type == "Received":
        for data in whole:
            if data["Transaction_Type"] == "Received":
                for num in range(data["Input_Count"]):
                    transList.append(data["Input_Address"][num]["Address"])
                    #tempInAddress.append(data["Input_Address"][num]["Address"])



    dic["MainAdd"] = whole[0]["Address"]
    dic["Trans"] = transList
    tempInAddress.append(dic)
    return tempInAddress



satoshi = float(1.0) * float(10 ** -8)


#************************************************************************************************************************************

#this function is to test the code and can be runnable
def initialised(wallet, fam, source, type, tiers, loca):
    print("Initial called")
    placeholder = {}
    gui.App.message = "Ransomware Payment Dataset Gen"
    wall = "1HZHhdJ6VdwBLCFhdu7kDVZN9pb3BWeUED"
    transType = "Sent"
    ransomfam = "Qlocker"
    src = "https://www.pcrisk.com/removal-guides/20704-qlocker-ransomware"
    loc = "C:/"
    tr = 9


    if len(placeholder) == 0:
        walletAddress = wall
        address = wall
        relation = wall
        tier = "Base"


        whole = calculateWholeTx(address)
        temporaryAdd = tempInOut(whole, transType)
        dataframe = walletDataframe(walletAddress, whole, tier, relation, ransomfam, src)
        convertToExcel(dataframe, loc)
        #print(json.dumps(temporaryAdd, indent=4))
        #print(len(temporaryAdd[0]["Trans"]))

        placeholder["1"] = temporaryAdd[0]
        print(placeholder)



    hit = tr
    add = 1
    while add != hit:
        tierPicker = {"1": "Tier One",
                      "2": "Tier Two",
                      "3": "Tier Three",
                      "4": "Tier Four",
                      "5": "Tier Five",
                      "6": "Tier Six",
                      "7": "Tier Seven",
                      "8": "Tier Eight",
                      "9": "Tier Nine",
                      "10": "Tier Ten"}
        print("counter", add)
        gui.app.progressUpdate("counter" + str(add))
        if int(len(placeholder[str(add)]["Trans"])) != 0:
            print("Yes")

            walletAddress = wall
            address = placeholder[str(add)]["Trans"][0]
            relation = placeholder[str(add)]["MainAdd"]
            tier = tierPicker[str(add)]

            if walletAddress == address:
                pass

            temp = placeholder[str(add)]["Trans"]
            temp.remove(address)
            placeholder[str(add)]["Trans"] = temp


            whole = calculateWholeTx(address)
            print(f"Pass whole: {add}")
            temporaryAdd = tempInOut(whole, transType)
            print(f"Pass temporaryAdd: {add}")
            dataframe = walletDataframe(walletAddress, whole, tier, relation, ransomfam, src)
            print(f"Pass Dataframe: {add}")
            gui.app.progressUpdate(f"Writing Data for Tier" + str(add))
            print("************************WRITING DATA*********************************")
            convertToExcel(dataframe, loc)
            print("************************WRITING FINISHED*********************************")
            gui.app.progressUpdate(f"Writing Finished for Tier" + str(add))
            #print(json.dumps(temporaryAdd, indent=4))
            #print(len(temporaryAdd[0]["Trans"]))

            if getAddressInfo(address)["Transactions"] >= 50:
                pass
            else:
                placeholder[str(add+1)] = temporaryAdd[0]

            print(f"Address: {address} \n Relations: {relation} \n Tier: {tier}")
            print(placeholder)

        else:
            add += 1

