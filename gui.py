# This module is mostly for the design of the GUI interface for user friendly usage
import threading
import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog
from time import sleep
from threading import Thread
from main import *

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):

    WIDTH = 400
    HEIGHT = 600

    def __init__(self):
        super().__init__()

        self.title("Ransomware Dataset Builder")
        #self.maxsize(App.WIDTH,App.HEIGHT)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        self.frame_info = customtkinter.CTkFrame(master=self)
        self.frame_info.grid(row=0, column=0, columnspan=1, rowspan=20, pady=20, padx=50)

        #Progress bars
        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="*******************************\n" +
                                                        "Ransomware Payment Dataset Gen \n" +
                                                        "*******************************",
                                                   height=100,
                                                   text_font=("Roboto Medium", 12),
                                                   corner_radius=6, # <- custom corner radius
                                                   fg_color=("white", "gray38"), # <- custom tuple-color
                                                   justify=tkinter.CENTER)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=5)

        #Wallet address label
        self.walletLbl = customtkinter.CTkLabel(master=self.frame_info,
                                              text="Wallet Address",
                                              text_font=("Roboto Medium", 12))  # font name and size in px

        self.walletLbl.grid(column=0, row=1, sticky="nwe", padx=15, pady=5)
        # wallet address text
        self.walletAdd = customtkinter.CTkEntry(master=self.frame_info,
                                                  placeholder_text="Enter wallet address",
                                                width=120,
                                                height=25,
                                                border_width=2,
                                                corner_radius=10)
        self.walletAdd.grid(column=0, row=3, sticky="nwe", padx=15, pady=2)
        #ransom fam label
        self.ransomFamLbl = customtkinter.CTkLabel(master=self.frame_info,
                                                text="Ransomware Family",
                                                text_font=("Roboto Medium", 12))  # font name and size in px

        self.ransomFamLbl.grid(column=0, row=4, sticky="nwe", padx=15, pady=5)
        #ransomfam text box
        self.ransomFam = customtkinter.CTkEntry(master=self.frame_info,
                                                placeholder_text="Enter Ransomware Family",
                                                width=120,
                                                height=25,
                                                border_width=2,
                                                corner_radius=10)
        self.ransomFam.grid(column=0, row=5, sticky="nwe", padx=15, pady=5)
        #source Lable
        self.sourceLbl = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Ransomware Source",
                                                   text_font=("Roboto Medium", 12))  # font name and size in px

        self.sourceLbl.grid(column=0, row=6, sticky="nwe", padx=15, pady=5)
        #Source text
        self.source = customtkinter.CTkEntry(master=self.frame_info,
                                                placeholder_text="Enter Source",
                                                width=120,
                                                height=25,
                                                border_width=2,
                                                corner_radius=10)
        self.source.grid(column=0, row=7, sticky="nwe", padx=15, pady=5)
        #Trans type label
        self.transtypeLbl = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Transaction Type",
                                                   text_font=("Roboto Medium", 10))  # font name and size in px

        self.transtypeLbl.grid(column=0, row=8, sticky="nwe", padx=15, pady=5)
        #Transtype text box
        self.transtype = customtkinter.CTkOptionMenu(master=self.frame_info,
                                                     values=["Sent", "Received"],
                                                     command=self.transtype_mode)
        self.transtype.grid(column=0, row=9, sticky="nwe", padx=15, pady=2)

        #  Tier
        self.tierLbl = customtkinter.CTkLabel(master=self.frame_info,
                                                text="Tier",
                                                text_font=("Roboto Medium", 10))  # font name and size in px

        self.tierLbl.grid(column=0, row=10, sticky="nwe", padx=15, pady=0)

        self.tier = customtkinter.CTkSlider(master=self.frame_info,
                                            from_=1,
                                            to=10,
                                            number_of_steps=9,
                                            command=self.progbar)
        self.tier.grid(column=0, row=12, sticky="nwe", padx=15, pady=0)

        # Tier number
        self.tiernum = customtkinter.CTkLabel(master=self.frame_info,
                                              text=self.tier.get(),
                                              text_font=("Roboto Medium", 8))  # font name and size in px

        self.tiernum.grid(column=0, row=11, sticky="nwe", padx=15, pady=0)

        self.label_file_explorer = customtkinter.CTkLabel(master=self.frame_info,
                                                          text_font=("Roboto Medium", 10),
                                                          text="Browse Folder")
        self.label_file_explorer.grid(column=0, row=14, sticky="nwe", padx=15, pady=0)

        #Button
        self.browse = customtkinter.CTkButton(master=self.frame_info,
                                              text="Browse",
                                              command=self.browseFiles)
        self.browse.grid(column=0, row=15, sticky="nwe", padx=15, pady=0)

        # Submit Button
        self.button = customtkinter.CTkButton(master=self.frame_info,
                                              width=120,
                                              height=32,
                                              border_width=0,
                                              corner_radius=8,
                                              text="Submit",
                                              command=self.button_event)
        self.button.place(relx=.5, rely=0.5, anchor=tkinter.CENTER)
        self.button.grid(column=0, row=20, sticky="nwe", padx=15, pady=5)
        self.message = "Ransomware Payment Dataset Gen"
        self.wallet = ""

    def progressUpdate(self):
        text = tkinter.StringVar(value=f"""**************************\n
        hhhhhhhhhhhhhhhhhhhhh\n
        *************************** """)
        # Progress bars
        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   textvariable=text,
                                                   height=100,
                                                   text_font=("Roboto Medium", 12),
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.CENTER)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=5)
        return text

    def browseFiles(self):
        filename = filedialog.askdirectory()
        print(filename)
        self.label_file_explorer.configure(text=filename)

    def button_event(self):
        print("Button pressed")
        print("Goining t initail ")
        threading.Thread(target=self.initial).start()
        #print(f"Wallet: {wallet}, \n Fam: {ran}, \n Type: {type}, \n Src: {src}, \n Tier:{trs}, \n loc: {loc}")

    def initial(self):
        self.label_info_1.configure(text=f"*******************************\n" +
                                                        "Wait...Dont close the application \n" +
                                                        "*******************************")
        wallet = self.walletAdd.get()
        ran = self.ransomFam.get()
        src = self.source.get()
        type = self.transtype.get()
        trs = self.tiernum.text
        loc = self.label_file_explorer.text

        wall = wallet
        transType = type
        ransomfam = ran
        src = src
        loc = loc
        tr = trs

        placeholder = {}

        if len(placeholder) == 0:
            walletAddress = wall
            address = wall
            relation = wall
            tier = "Base"

            whole = calculateWholeTx(address)
            temporaryAdd = tempInOut(whole, transType)
            dataframe = walletDataframe(walletAddress, whole, tier, relation, ransomfam, src)
            convertToExcel(dataframe, loc)
            # print(json.dumps(temporaryAdd, indent=4))
            # print(len(temporaryAdd[0]["Trans"]))

            placeholder["1"] = temporaryAdd[0]
            print(placeholder)

        hit = int(tr) + 1
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
            if int(len(placeholder[str(add)]["Trans"])) != 0:
                print("Yes")

                walletAddress = wall
                address = placeholder[str(add)]["Trans"][0]
                relation = placeholder[str(add)]["MainAdd"]
                tier = tierPicker[str(add)]
                self.label_info_1.configure(text=f"*******************************\n" +
                                                 f"Gathering Data: Tier{add}\n" +
                                                f"{address} \n" +
                                                 "*******************************")

                if walletAddress == address:
                    pass

                temp = placeholder[str(add)]["Trans"]
                temp.remove(address)
                placeholder[str(add)]["Trans"] = temp

                whole = calculateWholeTx(address)
                print(f"Pass whole: {add}")
                temporaryAdd = tempInOut(whole, transType)
                print(f"Pass temporaryAdd: {add}")
                self.label_info_1.configure(text=f"*******************************\n" +
                                                 f"Converting Data Tier{add}\n" +
                                                f"{address} \n" +
                                                 "*******************************")
                dataframe = walletDataframe(walletAddress, whole, tier, relation, ransomfam, src)
                print(f"Pass Dataframe: {add}")
                self.label_info_1.configure(text=f"*******************************\n" +
                                                 "Writing Data to Excel for \n" +
                                                 f"{address} \n" +
                                                 "*******************************")
                print("************************WRITING DATA*********************************")
                convertToExcel(dataframe, loc)
                print("************************WRITING FINISHED*********************************")
                self.label_info_1.configure(text=f"*******************************\n" +
                                                 f"{address} \n" +
                                                "has been written to excel \n"+
                                                 "*******************************")

                # print(json.dumps(temporaryAdd, indent=4))
                # print(len(temporaryAdd[0]["Trans"]))

                if getAddressInfo(address)["Transactions"] >= 50:
                    pass
                else:
                    placeholder[str(add + 1)] = temporaryAdd[0]

                print(f"Address: {address} \n Relations: {relation} \n Tier: {tier}")
                print(placeholder)

            else:
                add += 1
        self.label_info_1.configure(text=f"*******************************\n" +
                                         f"Fill the form again to add into excel \n" +
                                         "*******************************")
        print("Finished fill the form again...")

    def transtype_mode(self, trans):
        print(trans)

    def progbar(self, v):
        self.tiernum = customtkinter.CTkLabel(master=self.frame_info,
                                              text=str(int(self.tier.get())),
                                              text_font=("Roboto Medium", 8))  # font name and size in px

        self.tiernum.grid(column=0, row=11, sticky="nwe", padx=15, pady=0)

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()