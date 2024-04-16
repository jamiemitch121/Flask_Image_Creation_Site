import os
import random
from flask import Flask, request , render_template, session, redirect, url_for
from waitress import serve
app = Flask(__name__)
from salesforcenew import process_image
from flask_mail import Mail, Message

mail = Mail(app)

app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = '09f5390ee001daa92a984cc29bbf3531'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app) 

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.secret_key = os.urandom(12)

@app.route('/', methods = ["GET","POST"])
def starterForm():
    if request.method =='POST':
         firstformdata = (request.form).to_dict(flat=True)
         repeatkey = True
         while repeatkey == True:
            userkey = str(random.randint(10**12, 10**13 - 1))
            filepath= os.path.join(APP_ROOT,'userinfo/',userkey+".txt")
            if os.path.exists(filepath) == False:
                session['userkey']=userkey
                repeatkey = False
         with open(filepath, 'w') as fp:
            fp.write(str(firstformdata))
            pass
         return redirect(url_for('upload'))
    return render_template("StarterForm.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")

@app.route("/loadingpage", methods=['POST'])
def loadingpage():
        target = os.path.join(APP_ROOT,'Static/images/')
        image = request.args.get('image')
        file = request.files.get("file")
        filename = file.filename
        destination = "/".join([target,filename])
        file.save(destination)
        session['sdestination'] = destination
        session['sfilename'] = filename
        return render_template("Loading.html")
        


@app.route("/processing", methods=['GET','POST'])
def processing():
    destination = session['sdestination']
    filename = session['sfilename']
    process_image(destination,(filename))

@app.route("/middleform", methods=['GET','POST'])
def middleform():
    filename = session['sfilename']
    originalroute = ("images/"+filename)
    generatedroute = ("generatedimages/"+filename)
    if request.method =='POST':
        userkey = session['userkey']
        MiddleFormdata = (request.form).to_dict(flat=True)
        filepath= os.path.join(APP_ROOT,'userinfo/',userkey+".txt")
        with open(filepath, 'a') as fp:
            fp.write("\n"+str(MiddleFormdata))
            session['50/50'] = 1
        return redirect(url_for('Form3'))

    return render_template("MiddleForm.html", originalroute=originalroute, generatedroute=generatedroute)


@app.route("/Form3", methods=['GET','POST'])
def Form3():
    print(str(session['50/50']) + "here!")
    if session['50/50']== 1:
        route1 = "images/humanlikeart3.jpg"
        route2 = "images/humanlikeart4.jpg"
        trueimage = "Second"
    else:
        route1 = "images/humanlikeart4.jpg"
        route2 = "images/humanlikeart3.jpg"
        trueimage = "First"
    if request.method =='POST':
        userkey = session['userkey']
        Form3data = (request.form).to_dict(flat=True)
        Form3data["trueimage"] = trueimage
        filepath= os.path.join(APP_ROOT,'userinfo/',userkey+".txt")
        with open(filepath, 'a') as fp:
            fp.write("\n"+str(Form3data))
            session['50/50'] = random.randrange(1, 3) 
        return redirect(url_for('finalform'))

    return render_template("Form3.html", route1=route1, route2=route2)


@app.route("/finalform", methods=['GET','POST'])
def finalform():
    if session['50/50']== 1:
        route1 = "images/humanlikeart.jpg"
        route2 = "images/humanlikeart2.jpg"
        trueimage = "Second"
    else:
        route1 = "images/humanlikeart2.jpg"
        route2 = "images/humanlikeart.jpg"
        trueimage = "First"
        
    if request.method =='POST':
        render_template("complete.html")
        userkey = session['userkey']
        filename =session['sfilename']
        FinalFormdata = (request.form).to_dict(flat=True)
        FinalFormdata["trueimage"] = trueimage
        filepath= os.path.join(APP_ROOT,'userinfo/',userkey+".txt")
        with open(filepath, 'a') as fp:
            fp.write("\n"+str(FinalFormdata))

        message = Message( 
                subject ='not real Results', 
                sender ='Tester@demomailtrap.com', 
                recipients = ['r98269299@gmail.com'] 
               ) 
        with app.open_resource(filepath) as file:

            message.attach(filepath,"application/txt",file.read())
        message.body = 'Hello Flask message sent from Flask-Mail'
        print (message)
        mail.send(message) 
        if os.path.exists("static/images/"+filename):
            os.remove("static/images/"+filename)
        if os.path.exists("static/generatedimages/"+filename):
            os.remove("static/generatedimages/"+filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        return render_template("complete.html")
    return render_template("FinalForm.html", route1=route1, route2=route2)

if __name__=="__main__":
    serve(app, host ='0.0.0.0',port=50100,threads=4)
