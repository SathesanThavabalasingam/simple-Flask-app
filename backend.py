from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


#--------------- Settings--------------------------------------------------------
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/phrase_holder'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# ---------------Declare model for PostGres---------------------------------------
class phrases(db.Model):
    """Declares model for integration with phrase_holder database.
    
    Within database there is a table phrases with two columns:
    id: refers to index in storage.txt or the phrase number
    phrase: refers to actual phrase sent as post request 
    
    """
    id = db.Column(db.Integer(), primary_key=True)
    phrase = db.Column(db.String, unique=True)

    def __repr__(self, phrase):
        self.phrase = phrase

#--------------Write end-point-------------------------------------------------------
@app.route('/write', methods=['GET', 'POST']) #allow both GET and POST requests
def postToWrite():
    if request.method == 'POST':  
        language = request.get_json() 
        result = language['phrase']
        num = sum(1 for line in open('storage.txt')) #I do this to get the line number of new phrase  
        
        try:
            #---write to database-----------------
            pf = phrases(id = num, phrase = result)
            db.session.add(pf)
            db.session.commit()
            #-------------------------------------
            with open('storage.txt', 'a+') as f: 
                f.write(result + "\n") 
                f.flush()
            result_return = jsonify({'phrase' : result,'id' : num}) # return json object with line number
            result_return.status_code=200
            return result_return; 
        except:
            return "Error while connecting to PostgreSQL database."       
    #return 'OK'

#--------------Read end-point-------------------------------------------------------
@app.route('/read', methods=['GET', 'POST'])
def getToPrint():
	if request.method == 'GET':
	    data=[]
	    with open('storage.txt', "r") as test:
	        for cnt, line in enumerate(test):
	            data.append({'id' : cnt, 'phrase' : line})
	        return jsonify({'phrases' : data})  #note must be in debug to have prettified JSON
	        test.flush()

#--------------Delete end-point-------------------------------------------------------
@app.route('/delete/<int:id_req>', methods=['GET','DELETE'])
def deleteFromStore(id_req):
    if request.method =='DELETE':
        lines=[]
        num = sum(1 for line in open('storage.txt'))
        if id_req <= num:
            try:
                #----Delete from database---------------------------    
                qr = phrases.query.filter_by(id="%s" % id_req).one()
                db.session.delete(qr)
                db.session.commit()
                #---------------------------------------------------
                with open('storage.txt', "r") as file:
                    for cnt, line in enumerate(file):
                        if cnt != id_req | cnt != num: #NOTE: added this for if id == list length for some reason didnt delete before.
                            lines.append(line)
                with open('storage.txt', "w") as file2:
                    file2.writelines(lines)
                    file2.close()
                return "id %d deleted"% id_req
            except:
                return "Error while connecting to PostgreSQL database."
        else:
            return "id %d is not in direcory" % id_req
            
if __name__ == "__main__":
    app.run(debug=True, port=8080) # to run on port 8080

