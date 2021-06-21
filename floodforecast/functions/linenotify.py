import requests

def lineNotifyMessage(token, msg, imgPath):

    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    files = {'imageFile': open(imgPath, 'rb')}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files=files)
    
    return r.status_code


if __name__ == "__main__":
  token = 'UdJ1E3w3t41FjDGyY4qYSTPiBdKBUiiMFDbVLAuDtCA'
  message = '\n鯉魚潭測站(C0T870), 24小時雨量已達大雨等級\n累積雨量 20 mm'
  imgPath = r'C:\Users\User\Documents\test.jpg'
  lineNotifyMessage(token, message, imgPath)