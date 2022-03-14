from alive_progress import alive_bar
import requests
import concurrent.futures
import json
import os
import time

#Edit these two lines to match your file locations.
downloadPath = '/your/path/to/save/location'
dataPath = '/path/to/data/downloaded/from/snapchat'

# Variables below can remain as is
# Advanced Users - Set Max request retries and Max Threads
maxRetries = 10
maxWorkers = 100


def getSnapData(dataStruct):
    link = dataStruct['Link']
    if dataStruct['Type'] == "Image":
        filePath = os.path.join(imageFolder, dataStruct['FileName'])
    elif dataStruct['Type'] == "Video":
        filePath = os.path.join(videoFolder, dataStruct['FileName'])
    link.split('?')
    url = link[0]
    snapRequest = link[1]

    done = False
    attempt = 0
    
    while not done:
        response = requests.post(link, data = snapRequest, headers = {"Content-type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            r = requests.get(response.text)
            open(filePath,'wb').write(r.content)
            done = True
        elif attempt < maxRetries:
            print("Retrying got response code "+str(response.status_code))
            attempt += 1
            time.sleep(5)
        else:
            print("Too many retries. Giving up on file "+str(dataStruct['FileName']))
            return 0
    
    

if __name__ == "__main__":
    f = open(dataPath+"json/memories_history.json")
    data = json.load(f)
    snap = 'SnapchatBackup'
    image = 'Images'
    video = 'Videos'

     # make Snapchat Memories folder, Photos, and videos folder
    snapFolder = os.path.join(downloadPath, snap)
    # Make photos subfolder
    imageFolder = os.path.join(snapFolder, image)
    # Make videos subfolder
    videoFolder = os.path.join(snapFolder, video)

    os.makedirs(imageFolder, exist_ok=True)
    os.makedirs(videoFolder, exist_ok=True)

    imageLinks = []
    videoLinks = []

    imageCnt = 0
    videoCnt = 0


    for i in data['Saved Media']:
        if i["Media Type"] == "Image":
            imageCnt+=1
            dateParts=i["Date"].split()
            timeParts=dateParts[1].split(':')
            filename = dateParts[0] + "_" + timeParts[0] + "-" + timeParts[1] + "-" + timeParts[2] + ".jpg"
            imageLinks.append({ "Link":i["Download Link"],"FileName" : filename, "Type" : "Image"})
            
        elif i["Media Type"] == "Video":
            videoCnt+=1
            dateParts=i["Date"].split()
            timeParts=dateParts[1].split(':')
            filename = dateParts[0] + "_" + timeParts[0] + "-" + timeParts[1] + "-" + timeParts[2] + ".mp4"
            videoLinks.append({ "Link":i["Download Link"],"FileName" : filename, "Type" : "Video"})
            
    # Save Images and Display progress
    with alive_bar(imageCnt) as bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
            print("Now downloading all photos from Snapchat!")
            future_to_url = {executor.submit(getSnapData, data): data for data in imageLinks}
            for future in concurrent.futures.as_completed(future_to_url):
                data = future_to_url[future]
                try:
                    result = future.result()
                except Exception as exc:
                    print("Error??")
                else:
                    bar()

    # Save Images and Display progress
    with alive_bar(videoCnt) as bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
            print("Now downloading all Videos from Snapchat!")
            future_to_url = {executor.submit(getSnapData, data): data for data in videoLinks}
            for future in concurrent.futures.as_completed(future_to_url):
                data = future_to_url[future]
                try:
                    result = future.result()
                except Exception as exc:
                    print("Error??")
                else:
                    bar()
    