""" Grocery List App. """

# Import web templating language
from jinja2 import StrictUndefined

# Import Flask web framework
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

# Import model.py table definitions
from model import connect_to_db, db, User, Recipe, Ingredient
from model import List, CategoryRecipe, CategoryIngredient, RecipeIngredient
from model import ListIngredient, Bookmark, RecipeCategory

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# So that undefined variables in Jinja2 will strike an error vs. failing silently
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """ Display homepage. """

    return render_template("homepage.html")


#################### REGISTRATION ####################

@app.route("/register")
def display_registration_form():
    """ Display registration form. """

    return render_template("register_form.html")


@app.route("/register", methods=['POST'])
def process_registration_form():
    """ Add user info to database. Redirects back to homepage. """

    # Get form data back from register_form.html
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    # Instantiate user
    # Refer to model.py for User table parameters
    # User_id will is autoincrementing, no need to specify it
    new_user = User(username=username, email=email, password=password)

    # Add user to database
    db.session.add(new_user)
    db.session.commit()

    flash("Thanks for registering {}!".format(username))  # same as new_user.username

    # Return to homepage. User now registered and can log in.
    return redirect("/")


#################### LOGIN/LOGOUT ####################

@app.route("/login")
def display_login_form():
    """ Display login form. """

    return render_template("login_form.html")


@app.route("/login", methods=['POST'])
def validate_login_info():
    """ Attempt to log the user in by crossmatching with database. """

    # Get form data back from login_form.html
    username = request.form["username"]
    password = request.form["password"]

    # Check if user in database
    # Use .first() --> gives back user object if exists. Nonetype if not.
    user = User.query.filter(User.username == username).first()

    # Error messages
    if not user:
        flash("{} does not exist!".format(username))
        return redirect("/login")
    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    # If successful, add user to session and go back to homepage.
    session["user_id"] = user.user_id
    session["username"] = user.username
    flash("{} has successfully logged in.".format(user.username))
    return redirect("/")


@app.route("/logout")
def logout_user():
    """ Log out user. """

    # Remove user from session (remember session info is user's PK not username!)
    del session["user_id"]
    del session["username"]
    flash("You have logged out.")
    return redirect("/")


#################### USER PROFILE ####################
@app.route("/user/<username>")
def display_profile(username):
    """ Show user profile. """

    # Access user info from session first, then refer to DB for rest of info
    username = session.get("username")
    user = User.query.filter(User.username == username).first()

    return render_template("user_profile.html", username=user.username, email=user.email)

# #GET - SHOW PROFILE
# # URL should be /users/<username>
# # implied that /users should be a page in itself?


# @app.route("/<username>/home")

# #LOGGED IN userpage with grocery list / recipe search bar
# FLASH MESSAGE login success
# #"Dashboard" of user
# #Or should I not do this and render '/' instead?

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
