from datetime import timedelta
import os

from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField, Select2Field
from flask_admin.contrib.sqla import ModelView
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    g,
    session,
)
from flask_htmx import HTMX

from models.models import Event, Gallery, Role, User, Vote, Feedback
from datetime import timedelta
from dotenv import load_dotenv
import random
from db import DATABASE_URL, db
from jinjax import Catalog
from flask_mail import Mail, Message

# if not load_dotenv(os.path.join(os.getcwd(), ".env")):
#     print("No .env file found")
#     exit()
load_dotenv()

app = Flask(__name__)
htmx = HTMX(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
app.config["MAIL_SERVER"] = MAIL_SERVER
app.config["MAIL_PORT"] = MAIL_PORT
# app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
app.config["MAIL_DEFAULT_SENDER"] = MAIL_USERNAME
mail = Mail(app)
COMPONENTS_DIR = "components"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"
ADMIN_NAME = os.getenv("ADMIN_NAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
catalog = Catalog(jinja_env=app.jinja_env)
catalog.add_folder(COMPONENTS_DIR)
catalog.add_folder(TEMPLATES_DIR)
app.jinja_env.globals["catalog"] = catalog
app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)

# Flask admin setup
admin = Admin(app, name="The Royal Highlanders", template_mode="bootstrap4")


def check_all_leadership_roles(names):
    if (
        "ra" in names
        or "president" in names
        or "vice_president" in names
        or "treasurer" in names
        or "secretary" in names
        or "grand_prix_rep" in names
        or "resident_satisfaction_committee_head" in names
        or "purchasing_committee_head" in names
        or "event_committee_head" in names
        or "hall_club_representation_committee_head" in names
    ):
        return True
    return False


def initialize_db():
    print("Creating database")
    db.create_all()
    Role.create(name="ra", is_electable=False)
    Role.create(name="president", is_electable=True)
    Role.create(name="vice_president", is_electable=True)
    Role.create(name="treasurer", is_electable=True)
    Role.create(name="secretary", is_electable=True)
    Role.create(name="grand_prix_rep", is_electable=True)
    Role.create(name="resident_satisfaction_committee_head", is_electable=True)
    Role.create(name="purchasing_committee_head", is_electable=True)
    Role.create(name="event_committee_head", is_electable=True)
    Role.create(name="hall_club_representation_committee_head", is_electable=True)
    Role.create(name="resident_satisfaction_committee", is_electable=False)
    Role.create(name="purchasing_committee", is_electable=False)
    Role.create(name="event_committee", is_electable=False)
    Role.create(name="hall_club_representation_committee", is_electable=False)
    Role.create(name="member", is_electable=False)

    User.create(
        full_name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        roles=[Role.query().filter(Role.name == "ra").first()],
        img="person.jpg",
    )

    # Make pretend candidates
    User.create(
        full_name="John Doe",
        email="jdoe@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "president").first().name,
        img="person.jpg",
        bio="president",
    )
    User.create(
        full_name="Alice Smith",
        email="asmith@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "vice_president").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="Bob Johnson",
        email="bjohnson@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "treasurer").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="Charlie Brown",
        email="cbrown@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "secretary").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="Lucy Goosey",
        email="lgoose@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "secretary").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="David Davis",
        email="ddavis@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "grand_prix_rep").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="Emma Thompson",
        email="ethompson@purdue.edu",
        password="password",
        running=Role.query()
        .filter(Role.name == "resident_satisfaction_committee_head")
        .first()
        .name,
        img="person.jpg",
    )
    User.create(
        full_name="Frank Wilson",
        email="fwilson@purdue.edu",
        password="password",
        running=Role.query()
        .filter(Role.name == "purchasing_committee_head")
        .first()
        .name,
        img="person.jpg",
    )
    User.create(
        full_name="John Smith",
        email="jsmith@purdue.edu",
        password="password",
        running=Role.query().filter(Role.name == "event_committee_head").first().name,
        img="person.jpg",
    )
    User.create(
        full_name="Josephy Krakowski",
        email="jkrack@purdue.edu",
        password="password",
        running=Role.query()
        .filter(Role.name == "hall_club_representation_committee_head")
        .first()
        .name,
        img="person.jpg",
    )

    Event.create(
        name="Hall Club Election",
        description="Vote for your Hall Club Representatives",
        start_time="2024-08-28 19:00:00",
        end_time="2024-09-04 19:00:00",
        img="election.jpeg",
    )


class EventView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "event_committee_head" in names
            or "secretary" in names
            or "vice_president" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=os.path.join(STATIC_DIR, "uploads", "images"),
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class GalleryView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if check_all_leadership_roles(names):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=os.path.join(STATIC_DIR, "uploads", "images"),
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class FeedbackView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "vice_president" in names
            or "secretary" in names
            or "resident_satisfaction_committee_head" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class RoleView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if "ra" in names or "president" in names or "secretary" in names:
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class UserView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "resident_satisfaction_committee_head" in names
            or "secretary" in names
            or "vice_president" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class VoteView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(
                User.email == session.get("email"),
                User.password == session.get("password"),
            )
            .first()
        )
        if user is None:
            return False

        names = [role.name for role in user.roles]
        if "ra" in names:
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


with app.app_context():
    admin.add_view(EventView(Event, db.session))
    admin.add_view(GalleryView(Gallery, db.session))
    admin.add_view(FeedbackView(Feedback, db.session))
    admin.add_view(RoleView(Role, db.session))
    admin.add_view(UserView(User, db.session))
    admin.add_view(VoteView(Vote, db.session))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    counter = 0
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = (
            User.query().filter(User.email == email, User.password == password).first()
        )

        names = [role.name for role in user.roles]

        if check_all_leadership_roles(names):
            session["email"] = email
            session["password"] = password
            print("Redirecting to admin")
            return redirect("/admin")
        else:
            counter += 1
            if counter == 3:
                return redirect("/")
            return catalog.render("admin_login")
    elif request.method == "GET":
        return catalog.render("admin_login")


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    session.pop("email", None)
    session.pop("password", None)
    return redirect("/")


# Configure session
@app.before_request
def make_session_permanent():
    session.permanent = True


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    gallery_imgs = Gallery.query(Gallery.img).all()
    users = User.query()
    execs = []
    for user in users:
        names = [role.name for role in user.roles]
        if (
            "president" in names
            or "vice_president" in names
            or "secretary" in names
            or "treasurer" in names
            or "resident_satisfaction_committee_head" in names
            or "purchasing_committee_head" in names
            or "event_committee_head" in names
            or "hall_club_representation_committee_head" in names
            and "ra" not in names
        ):
            execs.append(user)
    most_recent_event = (
        Event.query()
        .filter(Event.completed == False)
        .order_by(Event.start_time.asc())
        .first()
    )
    return catalog.render(
        "index", event=most_recent_event, gallery_imgs=gallery_imgs, execs=execs
    )


@app.route("/events")
def events():
    events = Event.query().all()
    return catalog.render("events", events=events)


@app.route("/events/<int:event_id>")
def event(event_id):
    event = Event.query().filter(Event.id == event_id).first()
    time = f"From {event.start_time.strftime('%B %d, %Y %H:%M')} to {event.end_time.strftime('%B %d, %Y %H:%M')}"
    return catalog.render("event", event=event, time=time)


@app.route("/sharktank")
def sharktank():
    return catalog.render("sharktank")


@app.route("/gallery")
def gallery():
    return catalog.render("gallery")


@app.route("/election", methods=["GET", "POST"])
def election():
    if request.method == "GET":
        email = session.get("email")
        if email is None:
            session["url"] = url_for("election")
            return redirect("/login")
        candidates = (
            User.query()
            .join(Role)
            .filter(User.running != None)
            .order_by(User.running.name)
            .all()
        )
        user = User.query().filter(User.email == email).first()
        votes = Vote.query(Vote.candidate_id).filter(Vote.voter_id == user.id).all()
        votes = [vote[0] for vote in votes]
        return catalog.render("election", candidates=candidates, user=user, votes=votes)
    elif request.method == "POST":
        return redirect(url_for("declare_candidacy"))


@app.route("/declare_candidacy", methods=["GET", "POST"])
def declare_candidacy():
    if request.method == "GET":
        positions = Role.query().filter(Role.is_electable == True).all()
        return catalog.render("declare_candidacy", positions=positions)
    elif request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["purdue_email"]
        password = request.form["password"]
        bio = request.form["bio"]
        img = request.files["image"]
        img.save(os.path.join(STATIC_DIR, "uploads", "images", img.filename))
        running = request.form["position"]
        platform = request.form["platform"]
        user = User.query().filter(User.email == email).first()
        if not user:
            user = User.create(
                full_name=full_name,
                email=email,
                password=password,
                img=img.filename,
                bio=bio,
                running=running,
                platform=platform,
            )
        else:
            if "ra" in [role.name for role in user.roles]:
                return redirect(url_for("/"))
            user.full_name = full_name
            user.password = password
            user.img = img.filename
            user.bio = bio
            user.running = running
            user.platform = platform
            user.save()
        return redirect("/election")


@app.route("/candidate/<int:candidate_id>", methods=["GET"])
def candidate(candidate_id):
    candidate = User.query().filter(User.id == candidate_id).first()
    return catalog.render("candidate", candidate=candidate)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = (
            User.query().filter(User.email == email, User.password == password).first()
        )
        url = session.get("url")
        print(url)
        if user is None:
            # User.create(email=email, password=password)
            # session["email"] = email
            session["password"] = password
            # Send a verification email
            code = random.randint(100000, 999999)
            session["code"] = str(code)
            msg = Message(
                "Verify your email",
                recipients=[email],
                body=f"Your verification code is {code}",
            )
            mail.send(msg)
            return redirect("/validate/{}".format(email))
        else:
            session["email"] = email
            session["password"] = password
        if url is None:
            return redirect("/")
        return redirect(url)
    else:
        return catalog.render("login")


@app.route("/validate/<email>", methods=["GET", "POST"])
def validate(email):
    if request.method == "POST":
        code = request.form.get("code")
        if code is None:
            return redirect(url_for("error"))
        elif code != session.get("code"):
            return redirect(url_for("error"))
        password = session.get("password")
        if password is None:
            return redirect(url_for("error"))
        User.create(email=email, password=password)
        session["email"] = email
        url = session.get("url")
        if url is None:
            return redirect("/")
        return redirect(url)
    else:
        return catalog.render("validate", email=email)


@app.route("/error", methods=["GET"])
def error(err):
    print(err)
    return catalog.render("error")


@app.errorhandler(Exception)
def handle_foo_exception(error):
    # response = jsonify(error.to_dict())
    # response.status_code = error.status_code
    # return response
    return redirect(url_for("error"))


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("email", None)
    session.pop("password", None)
    return redirect("/")


@app.route("/constitution")
def constitution():
    return catalog.render("constitution")


@app.route("/vote/<int:candidate_id>/<int:voter_id>", methods=["POST"])
def vote(candidate_id, voter_id):
    candidate = User.query().filter(User.id == candidate_id).first()
    user = User.query().filter(User.id == voter_id).first()
    votes = Vote.query().filter(Vote.voter_id == voter_id)
    # Check if the user has already for a candidate with the position
    for vote in votes:
        if vote.position == candidate.running:
            vote.update(candidate_id=candidate.id)
            # user.votes.append(vote)
            return redirect(url_for("election"))
    vote = Vote.create(
        candidate_id=candidate.id, position=candidate.running, voter_id=user.id
    )
    # user.votes.append(vote)
    return redirect(url_for("election"))


@app.route("/feedback")
def feedback():
    return catalog.render("feedback")


if __name__ == "__main__":
    try:
        initialize_db()
    except Exception as e:
        print(e)
        pass
    app.run(debug=True)
