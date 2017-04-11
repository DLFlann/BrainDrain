import os
import jinja2
import webapp2
import re
import hashlib
import hmac
import random
import string
import time
from google.appengine.ext import db


# Create template directory for jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Crate jinja environment for rendering html templates
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# - - - Datastore Kind Definitions - - - - - - - - - - - - - - - - - - -

# User kind to store user profiles
class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)


# Blog post kind to store blog post
class Post(db.Model):
    subject = db.StringProperty(required=True)
    entry = db.TextProperty(required=True)
    likes = db.IntegerProperty(default=0)
    comments = db.StringListProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


# Comment kind to store comments on blog post
class Comment(db.Model):
    creator = db.StringProperty(required=True)
    entry = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


# Like kind to store and track user likes
class Like(db.Model):
    creator = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


# - - - Registration Input Verification - - - - - - - - - - - - - - - - - - -

"""Compare username passed to regular expression"""
def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and USER_RE.match(username)

"""Compare password passed to regular expression"""
def valid_password(password):
    PASS_RE = re.compile(r"^.{3,20}$")
    return password and PASS_RE.match(password)

"""Compare email passed to regular expression"""
def valid_email(email):
    EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return not email or EMAIL_RE.match(email)


# - - - Cookie Hashing and Validation - - - - - - - - - - - - - - - - - - -

SECRET = "imsosecret"

"""Creates a secure hash out of the userId and secret to prevent cookie
    manipulation of client side"""
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


"""Makes a secure cookie to track user on site consisting of
    userId and secure hash"""
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


"""Verifies cookie received from browser is authentic and matches its hash"""
def check_secure_val(h):
    val = h.split("|")[0]
    if h == make_secure_val(val):
        return val


# - - - Password Hashing and Validation - - - - - - - - - - - - - - - - - - -

"""Generate salt for hashing user password"""
def make_salt():
    return "".join(random.choice(string.letters) for x in xrange(5))


"""Create hashed password and salt for DB storage"""
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (hashed, salt)


"""Validate password from login page"""
def val_pw(name, pw, h):
    salt = h.split(",")[1]
    if h == make_pw_hash(name, pw, salt):
        return True


# - - - Base Handler - - - - - - - - - - - - - - - - - - -

class Handler(webapp2.RequestHandler):
    """Class implemented to help make writing and rendering templates easier"""

    """Simplified self.response.write method, reduces typing"""
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    """Template rendering method grabs the template passed to it from the
        templates directory above and passes parameters to be filled in to it
    """
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    """Uses simplified write method to respond with chosen template, passing
        along parameters"""
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    """Sets user_id cookie"""
    def set_user_cookie(self, user_entity):
        user_id = str(user_entity.key().id())
        cookie = make_secure_val(user_id)
        self.response.headers.add_header("Set-Cookie", "user_id=%s" % cookie)

    """Verifies user_id cookie in browser"""
    def check_cookie(self):
        # Get cookie from browser
        cookie = self.request.cookies.get("user_id")

        # Check cookie is found and valid
        if cookie:
            if check_secure_val(cookie):
                return True
            else:
                return False

    """Return user datastore key"""
    def get_user_key(self):
        cookie = self.request.cookies.get("user_id")
        if cookie.split("|")[0].isdigit():
            user_id = int(cookie.split("|")[0])
            user_key = db.Key.from_path("User", user_id)
            return user_key

    """Retrieve the 10 most recent entries and render home page with error if
        necessary"""
    def render_home(self, error=""):
        # Retrieve 10 most recent blog post from datastore
        entries = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT "
                              "10")

        # Render home page with error message
        self.render("home.html", entries=entries, error=error, db=db)


# - - - Main Page Handler - - - - - - - - - - - - - - - - - - -

class MainPage(Handler):
    """Home page where users browse blog post, leave comments, and like
        blog post by others
    """

    def get(self):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Render home page
            self.render_home()


# - - - Signup Page Handler - - - - - - - - - - - - - - - - - - -

class SignupPage(Handler):
    """Signup page for registering new user"""

    def get(self):
        # Render signup page with form for new users
        self.render("signup.html")

    def post(self):
        # Create error variable and set initial value to false
        have_error = False

        # Get information passed in from user
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        # Create a dictionary called params to store user values
        # and errors in order to re-render the page with information if needed
        params = dict(username=username,
                      email=email)

        # Check that username is valid
        if not valid_username(username):
            params["usernameError"] = "Invalid Username"
            have_error = True

        # Check that password is valid and matches
        if not valid_password(password):
            params["passwordError"] = "Invalid Password"
            have_error = True
        elif password != verify:
            params["verifyError"] = "Passwords Don't Match"
            have_error = True

        # If email is present, check that it's valid
        if not valid_email(email):
            params["emailError"] = "Invalid Email Address"

        # If error variable True, re-render page with values and error message
        if have_error:
            self.render("signup.html", **params)
        else:
            # Make sure user doesn't already exist
            user_exist = db.GqlQuery("SELECT * FROM User WHERE username =:1",
                                     username).get()
            if user_exist:
                # If user exist, set error message and re-render page
                params["usernameError"] = "Username not available"
                self.render("signup.html", **params)
            else:
                # Create password hash
                hpw = make_pw_hash(username, password)

                # Store new user in database
                new_user = User(username=username, password=hpw, email=email)
                new_user.put()

                #Create and set user_id cookie
                self.set_user_cookie(new_user)

                # Redirect to welcome page
                self.redirect("/success")


# - - - Login Page Handler - - - - - - - - - - - - - - - - - - -

class LoginPage(Handler):
    """Login page for existing users to sign into their account"""

    def get(self):
        # Render initial login page for user
        self.render("login.html")

    def post(self):
        # Get credentials from user
        username = self.request.get('username')
        password = self.request.get('password')

        # Get user entity from datastore
        user = db.GqlQuery("SELECT * FROM User WHERE username =:1",
                           username).get()

        # Valid user exist and password is correct
        if user and val_pw(username, password, user.password):
            # Set user_id cookie
            self.set_user_cookie(user)
            # Redirect to welcome page
            self.redirect("/success")
        else:
            # If not both valid user and correct password, return login form
            # with error
            self.render("login.html", username=username, error="Invalid Login")


# - - - Welcome Page Handler - - - - - - - - - - - - - - - - - - -

class WelcomePage(Handler):
    """Welcome page displaying welcome message and username after successful
        login.  Automatically redirects to homepage after 3 seconds."""

    def get(self):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Retrieve cookie and entity from datastore using id value in
            # cookie
            user_key = self.get_user_key()
            user = db.get(user_key)

            # Render welcome page
            self.render("welcome.html", user=user)


# - - - Logout Page Handler - - - - - - - - - - - - - - - - - - -

class LogoutPage(Handler):
    """Logout handler, sets user_id cookie to empty and redirects to login"""

    def get(self):
        # Set user_id cookie to empty and redirect to login page
        self.response.headers.add_header("Set-Cookie", "user_id=''")
        self.redirect("/login")


# - - - New Post Page Handler - - - - - - - - - - - - - - - - - - -

class NewPostPage(Handler):
    """Create newpost handler for adding new blog post"""

    def get(self):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Render form to enter new blog post
            self.render("newpost.html")

    def post(self):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get subject and content from user
            subject = self.request.get("subject")
            content = self.request.get("content")

            # Verify both subject and content are filled out
            if subject and content:
                # Get key of current user
                prof_key = self.get_user_key()

                # Create post entity for new blog post, setting current user
                # as parent relationship
                post = Post(subject=subject, entry=content, parent=prof_key)

                # Commit post to datastore
                post.put()

                # Redirect to blog post permalink
                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                # Subject and content not present, re-render page with error
                error = "Subject and content, please!"
                self.render("newpost.html", subject=subject,
                            content=content, error=error)


# - - - Post Permalink Page Handler - - - - - - - - - - - - - - - - - - -

class PostPage(Handler):
    """Blog post permalink page"""

    def get(self, post_id):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key
            prof_key = self.get_user_key()

            # Use user key to generate blog post key and retrieve blog post
            key = db.Key.from_path("Post", int(post_id), parent=prof_key)
            post = db.get(key)

            # If post is not in datastore, return 404
            if not post:
                self.error(404)
                return

            # Render permalink page with blog post
            self.render("permalink.html", entry=post)


# - - - Edit Post Page Handler - - - - - - - - - - - - - - - - - - -

class EditPage(Handler):
    """Edit handler allows author of blog post to edit and update"""

    def get(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key
            user_key = self.get_user_key()

            # Get encoded key from url and convert to entity key
            post_key = db.Key(web_safe_post_key)

            if post_key.parent() != user_key:
                # If user is not author of post, re-render home page with error
                error = "Sorry, only the author may edit that post."

                self.render_home(error)
            else:
                # Get blog post from datastore
                post = db.get(post_key)

                # If post is not in datastore, return 404
                if not post:
                    self.error(404)
                    return

                # Render edit post page with blog post
                self.render("newpost.html", subject=post.subject,
                            content=post.entry)

    def post(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key
            user_key = self.get_user_key()

            # Get encoded key from url and convert to entity key
            post_key = db.Key(web_safe_post_key)

            if post_key.parent() != user_key:
                # If user is not author of post, re-render home page with error
                error = "Sorry, only the author may edit that post."

                self.render_home(error)
            else:
                # Get subject and content from user
                subject = self.request.get("subject")
                content = self.request.get("content")

                # Verify both subject and content are filled out
                if subject and content:
                    # Get post entity from key
                    post = db.get(post_key)

                    # If post is not in datastore, return 404
                    if not post:
                        self.error(404)
                        return

                    # Set blog post subject and content to user input
                    post.subject = subject
                    post.entry = content

                    # Commit update to datastore
                    post.put()

                    # Redirect to blog post permalink
                    self.redirect('/blog/%s' % str(post.key().id()))
                else:
                    # If subject and content not present,
                    # re-render page with error
                    error = "Subject and content, please!"
                    self.render("newpost.html", subject=subject,
                                content=content, error=error)


# - - - Delete Post Page Handler - - - - - - - - - - - - - - - - - - -

class DeletePage(Handler):
    """Delete handler, deletes blog post after author confirms"""

    def get(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key
            user_key = self.get_user_key()

            # Get encoded key from url and convert to entity key
            post_key = db.Key(web_safe_post_key)

            # If user is not the author of blog post,
            # re-render home page with error
            if post_key.parent() != user_key:
                error = "Sorry, only the author may remove that post."

                self.render_home(error)
            else:
                # Get blog post entity from datastore
                post = db.get(post_key)

                # If post is not in datastore, return 404
                if not post:
                    self.error(404)
                    return

                # Render delete confirmation page with blog post
                self.render("deletepost.html", entry=post)

    def post(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key
            user_key = self.get_user_key()

            # Get encoded key from url and convert to entity key
            post_key = db.Key(web_safe_post_key)

            # If user is not the author of blog post,
            # re-render home page with error
            if post_key.parent() != user_key:
                error = "Sorry, only the author may remove that post."

                self.render_home(error)
            else:
                # Get post entity from key
                post = db.get(post_key)

                # If post is not in datastore, return 404
                if not post:
                    self.error(404)
                    return

                # Delete related comments from datastore
                comments = post.comments
                for comment in comments:
                    c_key = db.Key(comment)
                    c_entity = db.get(c_key)
                    c_entity.delete()

                # Delete post from datastore
                post.delete()

                # Delay before redirect to that home page, so
                # delete action can remove entity from datastore
                # Without this, the redirect happens before the
                # datastore has time to remove the object and update
                time.sleep(0.5)
                self.redirect("/")


# - - - Like Handler - - - - - - - - - - - - - - - - - - -

class LikeHandler(Handler):
    """Like handler increments the number of like
    for a post when clicked by a user"""

    def post(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key and entity from key
            user_key = self.get_user_key()
            creator = db.get(user_key)

            # Get encoded key from url and post entity from key
            post_key = db.Key(web_safe_post_key)
            post = db.get(post_key)

            # If post is not in datastore, return 404
            if not post:
                self.error(404)
                return

            # See if user has already like this post
            user_already_liked = db.GqlQuery("SELECT * FROM Like WHERE creator =:1 "
                               "AND ANCESTOR IS :2 ", creator.username,
                               post_key).get()

            if post_key.parent() == user_key:
                # If user is author of post, re-render page with error
                error = "Sorry, you cannot like your own post."

                self.render_home(error)
            elif user_already_liked:
                # Delete like from Like table
                user_already_liked.delete()

                # Decrease post likes by 1
                post.likes -= 1
                post.put()

                # Delay before redirecting so datastore
                # can update before page render
                time.sleep(0.5)

                # Redirect to home page
                self.redirect("/")
            else:
                # Create like entity for new like, setting blog post as parent
                like = Like(creator=creator.username, parent=post_key)

                # Add like to Like table
                like.put()

                # Increase like count by 1
                post.likes += 1
                post.put()
                time.sleep(0.5)

                # Redirect to home page
                self.redirect("/")


# - - - Comment Page Handler - - - - - - - - - - - - - - - - - - -

class CommentPage(Handler):
    """Create new comment handler for adding comments to a blog post"""

    def get(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Render comment page
            self.render("comment.html")

    def post(self, web_safe_post_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile
            user_key = self.get_user_key()
            creator = db.get(user_key)

            # Get encoded key from url and post entity from key
            post_key = db.Key(web_safe_post_key)
            post = db.get(post_key)

            # If post is not in datastore, return 404
            if not post:
                self.error(404)
                return

            # Get comment text from user
            content = self.request.get("content")

            if content:
                # Create comment entity with post as parent
                comment = Comment(creator=creator.username,
                                  entry=content, parent=post_key)

                # Add comment to datastore comment kind
                comment.put()

                # Get comment key
                com_key = comment.key()

                # Add comment key to blog post entity
                post.comments.append(str(com_key))
                post.put()

                # Redirect to home page after delay,
                # allowing time for datastore update
                time.sleep(0.5)
                self.redirect("/")

            else:
                # If no comment entered, re-render page with error
                error = "Please enter a comment"
                self.render("comment.html", error=error)


# - - - Edit Comment Page Handler - - - - - - - - - - - - - - - - - - -

class EditComment(Handler):
    """Edit comment handler allows author of comment to edit and update"""

    def get(self, web_safe_comment_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key and profile
            user_key = self.get_user_key()
            user = db.get(user_key)

            # Get encoded key from url and post entity
            c_key = db.Key(web_safe_comment_key)
            comment = db.get(c_key)

            # If comment is not in datastore, return 404
            if not comment:
                self.error(404)
                return

            # If user is not comment author, re-render page with error
            if comment.creator != user.username:
                error = "Sorry, only the author may edit that comment."

                self.render_home(error)
            else:
                # Render page for edit
                self.render("comment.html", content=comment.entry)

    def post(self, web_safe_comment_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key and profile
            user_key = self.get_user_key()
            user = db.get(user_key)

            # Get encoded key from url and post entity
            c_key = db.Key(web_safe_comment_key)
            comment = db.get(c_key)

            # If comment is not in datastore, return 404
            if not comment:
                self.error(404)
                return

            # If user is not comment author, re-render page with error
            if comment.creator != user.username:
                error = "Sorry, only the author may edit that comment."

                self.render_home(error)
            else:
                # Get comment text from user
                content = self.request.get("content")

                if content:
                    # Get post entity from key
                    comment = db.get(c_key)

                    # If post is not in datastore, return 404
                    if not comment:
                        self.error(404)
                        return

                    # Set comment content to user input
                    comment.entry = content

                    # Commit update to datastore
                    comment.put()

                    # Redirect to home page with delay so
                    # datastore can update before page render
                    time.sleep(0.5)
                    self.redirect("/")
                else:
                    # If no comment, re-render page with error
                    error = "Please enter a comment"
                    self.render("comment.html", error=error)


# - - - Delete Comment Page Handler - - - - - - - - - - - - - - - - - - -

class DeleteComment(Handler):
    """Delete comment handler, deletes comment after author confirms"""

    def get(self, web_safe_comment_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key and profile
            user_key = self.get_user_key()
            user = db.get(user_key)

            # Get encoded key from url and comment entity
            c_key = db.Key(web_safe_comment_key)
            comment = db.get(c_key)

            # If post is not in datastore, return 404
            if not comment:
                self.error(404)
                return

            # If user is not the author of comment, re-render page with error
            if comment.creator != user.username:
                error = "Sorry, only the author may remove that comment."

                self.render_home(error)
            else:
                # Render delete confirmation page
                self.render("deletecomment.html", comment=comment)

    def post(self, web_safe_comment_key):
        # Verify cookie
        if not self.check_cookie():
            self.redirect("/login")
        else:
            # Get user profile key and profile
            user_key = self.get_user_key()
            user = db.get(user_key)

            # Get encoded key from url and comment entity
            c_key = db.Key(web_safe_comment_key)
            comment = db.get(c_key)

            # If post is not in datastore, return 404
            if not comment:
                self.error(404)
                return

            # If user is not the author of comment, re-render page with error
            if comment.creator != user.username:
                error = "Sorry, only the author may remove that comment."

                self.render_home(error)
            else:
                # Get comment parent
                p_key = c_key.parent()
                post = db.get(p_key)
                # If post is not in datastore, return 404
                if not comment:
                    self.error(404)
                    return

                # # Remove comment from blog post comments list
                post.comments.remove(web_safe_comment_key)
                post.put()

                # Delete post from datastore
                comment.delete()

                # Delay before redirect so that home delete
                # action can remove entity from datastore
                # Without this, the redirect happens before
                # the datastore has time to remove the object and update
                time.sleep(0.5)
                self.redirect("/")


# - - - URL Mapping - - - - - - - - - - - - - - - - - - -

app = webapp2.WSGIApplication(
    [("/", MainPage),
     ("/signup", SignupPage),
     ("/login", LoginPage),
     ("/success", WelcomePage),
     ("/logout", LogoutPage),
     ("/newpost", NewPostPage),
     ("/blog/([0-9]+)", PostPage),
     ("/edit/([\S]+)", EditPage),
     ("/delete/([\S]+)", DeletePage),
     ("/like/([\S]+)", LikeHandler),
     ("/comment/([\S]+)", CommentPage),
     ("/editcomment/([\S]+)", EditComment),
     ("/deletecomment/([\S]+)", DeleteComment)
     ], debug=True)