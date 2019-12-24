from flask import Flask,render_template,request,jsonify
import requests #to send req over internet
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
from bs4 import BeautifulSoup as bs # for html parsing, create structure from html for our app to understand
from urllib.request import urlopen as uReq #to send req over internet
import pymongo

app = Flask(__name__) # initialize flask app with name app

@app.route("/",methods=['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content']
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['dbcrawlerDB']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html',reviews = reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q="+searchString
                uClient =uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage,"html.parser")
                bigboxes = flipkart_html.find_all("div", {"class": "bhgxx2 col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prod_html = bs(prodRes.text,'html.parser')
                commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})
                table = db[searchString]
                filename = searchString+".csv"
                fw = open(filename,"w")
                headers = "Product, Customer Name, Rating, Heading, Comment \n"
                fw.write(headers)
                reviews = []
                for comment in commentboxes:
                    try:
                        name = commentboxes.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except Exception as e:
                        print(e)
                        name = e
                    try:
                        rating = commentboxes.div.div.div.div.text
                    except:
                        rating = "Not available"
                    try:
                        commentHead = commentboxes.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentboxes.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'
                    fw.write(searchString + "," + name.replace(",", ":") + "," + rating + "," + commentHead.replace(",",
                                                                                                                    ":") + "," + custComment.replace(
                        ",", ":") + "\n")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}
                    x = table.insert_one(mydict)
                    reviews.append(mydict)
                return render_template('results.html', reviews=reviews)
        except:
            return "something went wrong"
    else:
        return render_template('index.html')






if __name__  == "__main__":
    app.run(port = 8000,debug=True)




