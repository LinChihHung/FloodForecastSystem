import requests

def lineNotifyMessage(token, msg, img):

    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    files = {'imageFile': open(img, 'rb')}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files=files)
    if files:
        files['imageFile'].close()

    return r.status_code



if __name__ == "__main__":
    from linenotipy import Line
    line = Line(token='FRYsdxMysDd4pyL4cJ7a20QgPrtj2qARz7SCxBVxY6r')
    line.post(message="\n黃晶瑩小姐你真是人美心也美呢!!", imageFile=None)
#   token = 'UdJ1E3w3t41FjDGyY4qYSTPiBdKBUiiMFDbVLAuDtCA'
#   message = '\n鯉魚潭測站(C0T870), 24小時雨量已達大雨等級\n累積雨量 20 mm '
#   imgPath = r'C:\Users\User\Documents\test.jpg'
# #   lineNotifyMessage(token, message, imgPath)