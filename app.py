from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL


app = Flask(__name__)


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "11vedang11"
app.config["MYSQL_DB"] = "skillloop"

mysql = MySQL(app)

app.secret_key = "skillloop_secret_key"

# HOME


@app.route("/")
def home():

    return render_template("index.html")



# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        teach_skill = request.form["teach_skill"]
        learn_skill = request.form["learn_skill"]
        skill_level = request.form["skill_level"]


        # Password check

        if password != confirm_password:

            return "Passwords do not match!"


        # Database connection

        cur = mysql.connection.cursor()


        # Check email already exists

        cur.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cur.fetchone()


        if existing_user:

            cur.close()

            return "Email already registered!"


        # Insert new user

        cur.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                teach_skill,
                learn_skill,
                skill_level
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (
                name,
                email,
                password,
                teach_skill,
                learn_skill,
                skill_level
            )
        )


        mysql.connection.commit()

        cur.close()


        # Registration ke baad Login page

        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )

# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]


        cur = mysql.connection.cursor()


        cur.execute(
            """
            SELECT *
            FROM users

            WHERE email = %s
            AND password = %s
            """,

            (
                email,
                password
            )
        )


        user = cur.fetchone()

        cur.close()


        if user:

            # User ki ID session mein save

            session["user_id"] = user[0]

            session["user_name"] = user[1]


            return redirect(
                url_for("dashboard")
            )


        else:

            return "Invalid email or password!"


    return render_template(
        "login.html"
    )


# DASHBOARD

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    cur.execute(
        """
        SELECT *
        FROM users

        WHERE id = %s
        """,

        (
            session["user_id"],
        )
    )


    user = cur.fetchone()

    cur.close()


    return render_template(
        "dashboard.html",
        user=user
    )


# PROFILE


@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    cur.execute(
        """
        SELECT *
        FROM users

        WHERE id = %s
        """,

        (
            session["user_id"],
        )
    )


    user = cur.fetchone()

    cur.close()


    return render_template(
        "profile.html",
        user=user
    )



# EDIT PROFILE

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    # UPDATE PROFILE


    if request.method == "POST":

        teach_skill = request.form["teach_skill"]

        learn_skill = request.form["learn_skill"]

        skill_level = request.form["skill_level"]


        cur.execute(
            """
            UPDATE users

            SET
                teach_skill = %s,
                learn_skill = %s,
                skill_level = %s

            WHERE id = %s
            """,

            (
                teach_skill,
                learn_skill,
                skill_level,
                session["user_id"]
            )
        )


        mysql.connection.commit()

        cur.close()


        return redirect(
            url_for("profile")
        )



    # GET CURRENT USER


    cur.execute(
        """
        SELECT *
        FROM users

        WHERE id = %s
        """,

        (
            session["user_id"],
        )
    )


    user = cur.fetchone()

    cur.close()


    return render_template(
        "edit-profile.html",
        user=user
    )


# PROGRESS

@app.route("/progress")
def progress():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    cur.execute(
        """
        SELECT *
        FROM users

        WHERE id = %s
        """,

        (
            session["user_id"],
        )
    )


    user = cur.fetchone()

    cur.close()


    return render_template(
        "progress.html",
        user=user
    )



# MATCHES


@app.route("/matches")
def matches():

    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user_id = session["user_id"]

    cur = mysql.connection.cursor()

    # CURRENT USER


    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (current_user_id,)
    )

    user = cur.fetchone()


    # ALL OTHER USERS
 

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id != %s
        """,
        (current_user_id,)
    )

    users = cur.fetchall()

    matches = []



    # CHECK EACH USER


    for match in users:

        other_user_id = match[0]


        # Check request sent by current user


        cur.execute(
            """
            SELECT id, status
            FROM connection_requests

            WHERE sender_id = %s
            AND receiver_id = %s
            """,
            (
                current_user_id,
                other_user_id
            )
        )

        request_data = cur.fetchone()


 
        # Agar current user ne request nahi bheji,
        # to check karo saamne wale ne request bheji hai


        if request_data is None:

            cur.execute(
                """
                SELECT id, status
                FROM connection_requests

                WHERE sender_id = %s
                AND receiver_id = %s
                """,
                (
                    other_user_id,
                    current_user_id
                )
            )

            request_data = cur.fetchone()


        # CHECK SKILL MATCH

        skill_match = (

            match[4] == user[5]

            and

            match[5] == user[4]

        )


        # ACCEPTED CONNECTION
    

        if request_data and request_data[1] == "accepted":

            matches.append({
                "user": match,
                "request": request_data
            })


        # NORMAL SKILL MATCH
       
        elif skill_match:

            matches.append({
                "user": match,
                "request": request_data
            })


    cur.close()


    return render_template(
        "matches.html",
        user=user,
        matches=matches
    )

# SEND CONNECTION REQUEST


@app.route("/send-request/<int:receiver_id>")
def send_request(receiver_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    sender_id = session["user_id"]


    # USER KHUD KO REQUEST NAHI BHEJ SAKTA
   

    if sender_id == receiver_id:

        return redirect(
            url_for("matches")
        )


    cur = mysql.connection.cursor()


    # CHECK EXISTING REQUEST


    cur.execute(
        """
        SELECT *

        FROM connection_requests

        WHERE
            sender_id = %s

        AND
            receiver_id = %s
        """,

        (
            sender_id,
            receiver_id
        )
    )


    existing_request = cur.fetchone()


    if existing_request:

        cur.close()

        return redirect(
            url_for("matches")
        )



    # CREATE REQUEST
    

    cur.execute(
        """
        INSERT INTO connection_requests
        (
            sender_id,
            receiver_id,
            status
        )

        VALUES
        (
            %s,
            %s,
            %s
        )
        """,

        (
            sender_id,
            receiver_id,
            "pending"
        )
    )


    mysql.connection.commit()

    cur.close()


    flash(
        "Connection request sent! 🤝",
        "success"
    )


    return redirect(
        url_for("matches")
    )


# CONNECTION REQUESTS

@app.route("/requests")
def requests():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()


    # CURRENT USER KO AAYI REQUESTS
 

    cur.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.teach_skill,
            users.learn_skill,
            connection_requests.id,
            connection_requests.status

        FROM connection_requests

        JOIN users
        ON connection_requests.sender_id = users.id

        WHERE connection_requests.receiver_id = %s

        ORDER BY connection_requests.created_at DESC
        """,
        (
            session["user_id"],
        )
    )

    requests = cur.fetchall()

    cur.close()

    return render_template(
        "requests.html",
        requests=requests
    )



# ACCEPT REQUEST

@app.route("/accept-request/<int:request_id>")
def accept_request(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    cur.execute(
        """
        UPDATE connection_requests

        SET status = 'accepted'

        WHERE
            id = %s

        AND
            receiver_id = %s

        AND
            status = 'pending'
        """,

        (
            request_id,
            session["user_id"]
        )
    )


    mysql.connection.commit()


    # Check ki actual mein row update hui ya nahi

    updated_rows = cur.rowcount


    cur.close()


    if updated_rows > 0:

        flash(
            "Connection request accepted! 🤝",
            "success"
        )

    else:

        flash(
            "Request could not be accepted.",
            "error"
        )


    return redirect(
        url_for("requests")
    )



# REJECT REQUEST


@app.route("/reject-request/<int:request_id>")
def reject_request(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    cur = mysql.connection.cursor()


    cur.execute(
        """
        UPDATE connection_requests

        SET status = 'rejected'

        WHERE
            id = %s

        AND
            receiver_id = %s

        AND
            status = 'pending'
        """,

        (
            request_id,
            session["user_id"]
        )
    )


    mysql.connection.commit()


    updated_rows = cur.rowcount


    cur.close()


    if updated_rows > 0:

        flash(
            "Connection request rejected.",
            "error"
        )

    else:

        flash(
            "Request could not be rejected.",
            "error"
        )


    return redirect(
        url_for("requests")
    )



# LOGOUT


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )



# RUN APPLICATION


if __name__ == "__main__":

    app.run(
        debug=True
    )