from flask import Flask,redirect, request, url_for, render_template
import sqlite3 as sql
import os.path
import pickle
import cv2
from skimage import feature
import requests
import csv 
import numpy as np

items = []
with open('parkinson_test_input.csv', newline='') as csvfile:
    data = list(csv.reader(csvfile))

print(len(data))
# file = open("parkinson_test_input.csv")
# items = np.loadtxt(file, delimiter=",")
# print(items)
# with open('parkinson_test_input.csv') as csvfile:    
# 	csvReader = csv.reader(csvfile)    
# 	for row in csvReader:        
# 		items.append(row[0])        
# print(items)
API_KEY = "y78YjqQtl67p9cXH197lt6YsP3Fu1w7EZdGs1llpfxEv"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
app=Flask(__name__)

class DB:
    def _init_(self, name = 0):
         self._name = name
         self._lid = 0
         self._tot=0

    # getter method
    def get_name(self):
        return self._name

    # setter method
    def set_name(self, x):
        self._name = x
    def get_lid(self):
        return self._lid

    # setter method
    def set_lid(self, x):
        self._lid = x

    def get_tot(self):
        return self._tot

    # setter method
    def set_tot(self, x):
        self._tot = x
obj=DB()
@app.route('/')
def home():
    try:
        lid=obj.get_lid()
        print(lid)
        return render_template('login.html',data=lid)
    except Exception as e:
        return render_template('login.html')
@app.route('/index')
def index():
    # obj._lid=0
    return render_template('index.html')
@app.route('/info')
def info():
    # obj._lid=0
    return render_template('info.html')

@app.route('/login')
def login():
    # obj._lid=0
    return render_template('login.html')
@app.route('/predict',methods=["GET","POST"])
def predict():
    if request.method == 'POST':
        f=request.files['file'] #requesting the file
        f.save(f.filename)  
        # basepath=os.path.dirname(__file__)#storing the file directory 
        # filepath=os.path.join(basepath, "uploads", f.filename)#storing the
        # f.save(filepath)#saving the file #Loading the saved model
        print("[INFO] Loading model...") 
        model = pickle.loads (open('model.pkl', "rb").read()) #pre-process the image in the same manner we did earlier
        image=cv2.imread(f.filename)
        output = image.copy() # load the input image, convert it to grayscale, and resize
        output = cv2.resize(output, (128, 128))
        image= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (200, 200))
        image = cv2.threshold(image, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) [1]

        # quantify the image and make predictions based on the extracted #features using the last trained Random Forest
        print('hi')
        features = feature.hog(image, orientations=9,  pixels_per_cell=(10, 10), cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")
        print(features.shape)
        list = features.tolist()
        payload_scoring = {"input_data": [{"fields": data, "values": [list]}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/246e322f-c88b-4818-a537-7ab7463bce8b/predictions?version=2022-11-18', json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        print(response_scoring.json())
        preds=model.predict([features])

        print("dsa",preds) 
        
        pred=response_scoring.json()
        print(pred)
        result=pred['predictions'][0]['values'][0][0]
        print(result)
        # ls=["healthy","parkinson"]

        # result=ls[preds[0]]
        ls=["healthy","parkinson"]

        res=ls[result]
    # obj._lid=0
    return render_template('predict.html',d=res)
@app.route("/login", methods = ["GET","POST"])
def Login():

    l_id = request.form["logname"]
    l_pass  = request.form["logpass"]

    tab=l_id+l_pass
    #print("name")
    if request.method == 'POST':
        print("name")
        l_id = request.form["logname"]
        l_pass  = request.form["logpass"]

        tab=l_id+l_pass
        print(tab)
        obj.set_name(tab)
        obj.set_lid(l_id)
        return redirect(f"/check")

    return render_template('invalid.html',invalid='Please enter a valid data')

@app.route('/sign')
def sign():
    return render_template('signup.html')

@app.route("/regis",methods=["GET","POST"])
def regis():
    u_id = request.values.get("signu_id")
    s_pass  = request.values.get("sign_pass")
    print(u_id)
    print(s_pass)
    table_name=u_id+s_pass
    print(table_name)
    try:
        conn=sql.connect('main.db')

        print("Opened database successfully")
        create="CREATE TABLE "+table_name+" (detail TEXT, cred TEXT)"
        conn.execute(create)
        #conn.execute("select * from credential")

        print("Table created successfully")
        conn.close()
        return render_template("success.html")
    except:
        # print("dsa")
        return render_template("invalid.html", a="Username and password are already taken. Try another.")
@app.route("/check",methods = ["GET","POST"])
def cart():
    tab=obj.get_name()
    lid=obj.get_lid()
    print(lid)
    if request.method == 'GET':
        print(f"Your name is {tab}")
        try:
            con = sql.connect("main.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            a=f"select * from {tab}"
            print(a)
            cur.execute(a)
            return render_template('index.html',data=lid)
        except :
            return render_template('invalid.html',a='Please enter a valid data')

     
if __name__=="__main__":
    app.run(debug=True)
