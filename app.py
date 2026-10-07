from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import os

# ==========================================================
# VGPP DOCUMENT UPLOAD PROTOTYPE
# Version 1 - Single GP User
# ==========================================================

app = Flask(__name__)

# Secret key for login session
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "VGPP-PROTOTYPE-SECRET-2026"
)

# ==========================================================
# STORAGE
# ==========================================================

# For Internet prototype
# Files will be saved inside an "uploads" folder.
BASE_FOLDER = Path("uploads")

BASE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# DEMO GP USER
# ==========================================================

USERS = {

    "gp001": {

        "password": "test123",

        "gp_code": "TEST-GP-001",

        "gp_name": "Test Gram Panchayat",

        "block": "Test Block",

        "district": "Test District"

    }

}


# ==========================================================
# VGPP ACTIVITIES
# ==========================================================

ACTIVITIES = {

    "01_Gram_Sabha":
        "Gram Sabha Proceedings",

    "02_Attendance":
        "Attendance",

    "03_Photographs":
        "Photographs",

    "04_Water_Budget":
        "Water Budget",

    "05_PRA":
        "PRA Report",

    "06_Draft_VGPP":
        "Draft VGPP"

}


# ==========================================================
# ALLOWED FILE TYPES
# ==========================================================

ALLOWED_EXTENSIONS = {

    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "jpg",
    "jpeg",
    "png"

}


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================================
# LOGIN PAGE
# ==========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = USERS.get(username)

        if user and user["password"] == password:

            session["username"] = username

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid username or password."
        )

    return render_template(
        "login.html"
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    # Check login
    if "username" not in session:

        return redirect(
            url_for("login")
        )

    username = session["username"]

    user = USERS[username]

    # ------------------------------------------------------
    # GP folder
    # ------------------------------------------------------

    gp_folder = (

        BASE_FOLDER
        / user["district"]
        / user["block"]
        / user["gp_code"]

    )

    gp_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    activities = []


    # ------------------------------------------------------
    # Create activity folders
    # ------------------------------------------------------

    for folder, activity_name in ACTIVITIES.items():

        activity_folder = (
            gp_folder / folder
        )

        activity_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        files = [

            f for f in activity_folder.iterdir()

            if f.is_file()

        ]

        if len(files) > 0:

            status = "Submitted"

        else:

            status = "Pending"


        activities.append({

            "folder": folder,

            "name": activity_name,

            "count": len(files),

            "status": status

        })


    # ------------------------------------------------------
    # Calculate progress
    # ------------------------------------------------------

    total_activities = len(
        activities
    )

    completed_activities = sum(

        1

        for activity in activities

        if activity["status"] == "Submitted"

    )


    if total_activities > 0:

        progress = int(

            (
                completed_activities
                /
                total_activities
            )
            * 100

        )

    else:

        progress = 0


    return render_template(

        "dashboard.html",

        user=user,

        activities=activities,

        progress=progress

    )


# ==========================================================
# DOCUMENT UPLOAD
# ==========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    # Check login
    if "username" not in session:

        return redirect(
            url_for("login")
        )


    username = session["username"]

    user = USERS[username]


    # Get activity
    activity = request.form.get(
        "activity"
    )


    # Get uploaded file
    file = request.files.get(
        "file"
    )


    # ------------------------------------------------------
    # Validate activity
    # ------------------------------------------------------

    if (

        not activity

        or activity not in ACTIVITIES

    ):

        flash(
            "Invalid activity selected."
        )

        return redirect(
            url_for("dashboard")
        )


    # ------------------------------------------------------
    # Validate file
    # ------------------------------------------------------

    if (

        not file

        or file.filename == ""

    ):

        flash(
            "Please select a file."
        )

        return redirect(
            url_for("dashboard")
        )


    # ------------------------------------------------------
    # Check extension
    # ------------------------------------------------------

    if not allowed_file(
        file.filename
    ):

        flash(
            "File type not allowed. "
            "Allowed: PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG."
        )

        return redirect(
            url_for("dashboard")
        )


    # ------------------------------------------------------
    # Create GP folder
    # ------------------------------------------------------

    gp_folder = (

        BASE_FOLDER
        / user["district"]
        / user["block"]
        / user["gp_code"]

    )


    # ------------------------------------------------------
    # Activity folder
    # ------------------------------------------------------

    activity_folder = (

        gp_folder
        / activity

    )


    activity_folder.mkdir(

        parents=True,

        exist_ok=True

    )


    # ------------------------------------------------------
    # Secure original filename
    # ------------------------------------------------------

    original_filename = secure_filename(

        file.filename

    )


    # ------------------------------------------------------
    # Add timestamp
    # ------------------------------------------------------

    timestamp = datetime.now().strftime(

        "%Y%m%d_%H%M%S"

    )


    new_filename = (

        timestamp
        + "_"
        + original_filename

    )


    # ------------------------------------------------------
    # Save file
    # ------------------------------------------------------

    file_path = (

        activity_folder
        / new_filename

    )


    file.save(
        file_path
    )


    # ------------------------------------------------------
    # Success message
    # ------------------------------------------------------

    flash(

        "Document uploaded successfully: "
        + new_filename

    )


    return redirect(

        url_for("dashboard")

    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==========================================================
# HEALTH CHECK
# Useful when deploying to cloud
# ==========================================================

@app.route("/health")
def health():

    return {

        "status": "OK",

        "application":
            "VGPP Prototype",

        "version":
            "1.0"

    }


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )

    print(
        " VGPP DOCUMENT MANAGEMENT PROTOTYPE"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Login URL:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "Demo Username: gp001"
    )

    print(
        "Demo Password: test123"
    )

    print()

    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )

    )
