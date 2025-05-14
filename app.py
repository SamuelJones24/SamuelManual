from flask import Flask, render_template
from scraper import scrape_all_products

app = Flask(__name__)

@app.route("/")
def home():
    products = scrape_all_products()
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
