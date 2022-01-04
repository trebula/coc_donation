from numpy import equal
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import sched, time
import os
from datetime import datetime
from IPython.display import display

url = "https://api.clashofclans.com/v1"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjdiYjhmMDZiLWYzZDAtNDI3Ny05ZjA2LTcyOTk1MThhMGIxMCIsImlhdCI6MTY0MDMyMjIxNiwic3ViIjoiZGV2ZWxvcGVyL2Y1N2UwNmI3LWM0NTQtZTNiZi1iMjVkLTdlY2I0NjcwMGQzYyIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjc1LjE4NS40NC40MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.OdLNJTOBMdAeo0kcB5xOrnOs7OFtGG1-3l6Lv4seWncmAIrPFRupEr-78w56eJUtd7JTYuuhcse-BGAcFv0X1Q"
hashtag = "%23"
my_player_tag = hashtag + "2000VCYUV"
stephanie_tag = hashtag + "2YVOYU9PQ"
my_clan_tag = hashtag + "2GPQLPPU"

path = "/clans/" + my_clan_tag + "/members"

# create dataframe from donations csv if csv not empty
if os.path.isfile("donations.csv"):
    donations_df = pd.read_csv("donations.csv")
else:
    donations_df = pd.DataFrame(columns=["name", "donations", "timestamp"])

def handle_response(response):
    global donations_df
    # check if the request was successful
    if response.status_code == 200:
        # parse the json response
        data = json.loads(response.text)

        # create a pandas dataframe
        df = pd.DataFrame(data["items"])

        # store only the player tag, name, trophies, donations, and donations received columns
        currDonos = df[["tag", "name", "trophies", "donations", "donationsReceived"]]

        # create scheduler
        s = sched.scheduler(time.time, time.sleep)

        # create a function to print dataframe only if donations changed
        def print_donations(sc, currDonos):
            global donations_df
            # get donations
            response = requests.get(url + path, headers={"Accept": "application/json", "Authorization": "Bearer " + token})
            
            # check if the request was successful
            if response.status_code != 200:
                print("Error: " + str(response.status_code))
                exit()
            
            # parse the json response
            data = json.loads(response.text)

            # create a pandas dataframe
            df = pd.DataFrame(data["items"])

            # store only the player tag, name, trophies, donations, and donations received columns
            newDonos = df[["tag", "name", "trophies", "donations", "donationsReceived"]]

            # if donations changed, print the difference
            for row in newDonos.itertuples():
                currDonation = currDonos.loc[currDonos["tag"] == row.tag, "donations"].values[0]
                if row.donations != currDonation:
                    amountDonated = row.donations - currDonation
                    print(f"{row.name} has donated {amountDonated}")

                    # add new donation entry to donations dataframe, name amount donated, and timestamp
                    donations_df = donations_df.append({"name": row.name, "donations": amountDonated, "timestamp": datetime.now()}, ignore_index=True)

            # schedule next call
            s.enter(5, 1, print_donations, (sc, newDonos))
            
        # call the scheduler
        s.enter(5, 1, print_donations, (s, currDonos))
        s.run()

    else:
        print("Request failed")
        print("Error: ", response.status_code)
        exit()

from atexit import register

def exit_handler():
    global donations_df
    # save donations dataframe to csv
    donations_df.to_csv("donations.csv", index=False)
    
    # print exiting
    print("Exiting")

def main():
    # register exit handler
    register(exit_handler)

    # set columns 
    pd.set_option('display.max_columns', None)

    # prevent pandas from text wrappping
    pd.set_option('display.width', None)

    response = requests.get(url + path, headers={"Accept": "application/json", "Authorization": "Bearer " + token})

    handle_response(response)

if __name__ == "__main__":
    main()
    # except KeyboardInterrupt:
    #     # save donations dataframe to csv
    #     donations_df.to_csv("donations.csv", index=False)
    #     exit()
    