from flask import Flask, render_template, redirect, url_for, flash, session, request
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, PostModel
from forms import RegistrationForm, LoginForm, Post

app = Flask(__name__)
app.config["SECRET_KEY"] = "My-Secret-Key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ---------- Helper Decorator ---------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("You must be logged in.", "warning")
            return redirect(url_for("login"))
        current_user = User.query.filter_by(username=session.get("user")).first()
        if not current_user:
            flash("User not found. Please log in again.", "warning")
            session.pop("user", None)
            return redirect(url_for("login"))
        return f(current_user, *args, **kwargs)  # pass current_user to route
    return decorated_function

# ---------- Routes ---------- #

@app.route("/")
def home():
    posts = PostModel.query.all()
    return render_template("home.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session["user"] = user.username
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials.", "danger")
        return redirect(url_for("login"))
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_post(current_user):
    form = Post()
    if form.validate_on_submit():
        new_post = PostModel(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash("Post added successfully!", "success")
        return redirect(url_for("home"))
    return render_template("add_post.html", form=form)

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(current_user, post_id):
    post = PostModel.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("Not allowed to edit.", "danger")
        return redirect(url_for("home"))
    form = Post()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("home"))
    form.title.data = post.title
    form.content.data = post.content
    return render_template("edit_post.html", form=form)

@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(current_user, post_id):
    post = PostModel.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("Not allowed to delete.", "danger")
        return redirect(url_for("home"))
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for("home"))

# ---------- Run App ---------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
