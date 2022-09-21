from crypt import methods
from flask import Flask, jsonify,render_template,request,redirect
from flask_mysqldb import MySQL
import yaml

import mysql.connector
from mysql.connector import Error

app=Flask(__name__)

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] =db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB'] =db['mysql_db']

mysql=MySQL(app)

@app.route('/',methods=['GET','POST'])
def index():
    # Get data from the form
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['userName']
        address=userDetails['address']
        phoneNo=userDetails['phoneNo']
        slotName=userDetails['slotName']
        cur=mysql.connection.cursor()
        slotQuery="SELECT slot_entries FROM slot where slot_name = %s"
        cur.execute(slotQuery,(slotName,))
        slotNames=cur.fetchone()
        slotCount=slotNames[0]        

        # Checking if maximum entry limit is reached
        if slotCount>=20:
            slotId= int(slotName[-1])
            query="SELECT slot_entries from slot"
            cur.execute(query)
            cur.fetchall()
            c=slotId
            # Allocating delivery request to next available slot
            for i in range (0,4):
                if c==4 and slotCount>=20:
                    c=1
                availableSlot='Slot '+ (str(c+1))
                slotQuery2="SELECT slot_entries FROM slot where slot_name = %s"
                cur.execute(slotQuery2,(availableSlot,))
                slotNames1=cur.fetchone()
                if slotNames1[0]<20:
                    cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,availableSlot))
                    slotCount=slotCount+1
                    updatedSlotCount=slotNames1[0]+1
                    cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(updatedSlotCount,availableSlot))
                    mysql.connection.commit()
                    cur.close()
                    break
                elif c<5:
                    c=c+1
                else:
                    return 'NO AVAILABLE SLOTS'
            return ('Alloted to ' + availableSlot)
        # Updating data to the database when slot limit is not reached
        else:
            cur.execute("INSERT INTO user (user_name,address,phone_no,slot_name) VALUES(%s,%s,%s,%s)",(name,address,phoneNo,slotName))
            slotCount=slotCount+1
            cur.execute("UPDATE slot SET slot_entries = %s WHERE slot_name = %s",(slotCount,slotName))
            mysql.connection.commit()
            cur.close()
            return 'success'
    return render_template('index.html')


if __name__==("__main__"):
    app.run(debug=True)