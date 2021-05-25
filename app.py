from flask import Flask, render_template
import os
import pymongo
app = Flask(__name__)

@app.route('/')
def index():
  SRV = os.environ['SRV']
  client = pymongo.MongoClient(SRV)
  user = client.game.user
  result = user.find({}, {"_id": 0, "password": 0})
  return render_template("index.html", data={"data": list(result)})

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)