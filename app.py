from flask import Flask, render_template, redirect, request, url_for, session, flash
from forms import Post, RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "My-Secret-Key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- Models ---------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship("PostModel", backref="owner", lazy=True)


class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ---------------- Routes ---------------- #
@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        exisiting_user = User.query.filter_by(username=form.username.data).first()
        if exisiting_user:
            flash("Username already exists. Please try another one.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session["user"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/")
def home():
    posts = PostModel.query.all()
    return render_template("home.html", posts=posts)


@app.route("/add", methods=["POST", "GET"])
def add_post():
    if "user" not in session:
        flash("You must be logged in to add a post.", "warning")
        return redirect(url_for("login"))

    form = Post()
    if form.validate_on_submit():
        current_user = User.query.filter_by(username=session["user"]).first()
        new_post = PostModel(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Post added successfully!", "success")
        return redirect(url_for("home"))

    return render_template("add_post.html", form=form)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user" not in session:
        flash("You must be logged in to delete a post.", "warning")
        return redirect(url_for("login"))

    post = PostModel.query.get(post_id)
    current_user = User.query.filter_by(username=session["user"]).first()

    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for("home"))

    if post.owner != current_user:
        flash("You are not allowed to delete this post.", "danger")
        return redirect(url_for("home"))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for("home"))

@app.route("/edit/<int:post_id>", methods=["POST", "GET"])
def edit_blog(post_id):
    if "user" not in session:
        flash("You must be logged in to edit a post.", "warning")
        return redirect(url_for("login"))

    post = PostModel.query.get_or_404(post_id)
    current_user = User.query.filter_by(username=session["user"]).first()

    if post.owner != current_user:
        flash("You are not allowed to edit this post.", "danger")
        return redirect(url_for("home"))

    form = Post()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("home"))

    # Pre-fill form with current post data
    form.title.data = post.title
    form.content.data = post.content
    return render_template("edit_post.html", form=form, post=post)

    


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------- Run ---------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
