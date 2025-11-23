from flask import Flask, render_template, request

app = Flask(__name__, static_folder='', static_url_path='')

@app.route("/")
def index():
    return render_template("index.html")

# --- 文字静态网页 ---
@app.route("/text")
def text_page():
    return render_template("text.html")

# --- 图片静态网页 ---
@app.route("/image")
def image_page():
    return render_template("image.html")

@app.get("/adder")
def get_adder():
    return render_template("adder.html")

# --- 动态加法器 ---
@app.post("/adder")
def post_adder():
    result, a, b = None, None, None
    a = float(request.form["a"])
    b = float(request.form["b"])
    result = a + b
    return render_template("adder.html",
                           result=result,
                           a_default=a,
                           b_default=b)

@app.errorhandler(404)
def errno_404(error):
    return "Oops! HTTP 404 Not Found!", 404

if __name__ == "__main__":
    app.run(debug=True)
