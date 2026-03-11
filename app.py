import math
from flask import request, render_template, redirect, url_for

import math
from flask import Flask, request, render_template, redirect, url_for
# from db import get_connection          # uncomment when using real DB
from calculations import calculate_metrics
from database import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------
# PORTAL SELECTION
# --------------------------

@app.route("/portal", methods=["POST"])
def portal():

    role = request.form["role"]

    if role == "student":
        return render_template("student_login.html")

    return render_template("teacher_login.html")




CLASS_HOURS = 1.5


# -------------------------------------------------
# HELPER: FETCH STUDENT ATTENDANCE DATA
# -------------------------------------------------

def get_student_dashboard_data(roll, medical=0, extra=0):
    """
    Fetches student + per-subject attendance from DB,
    computes per-subject and overall metrics.

    medical / extra – claim counts that reduce the overall
    conducted denominator (excused absences).
    """

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ---- Student info ----
    cursor.execute("""
        SELECT roll_number, student_name
        FROM Students
        WHERE roll_number = %s
    """, (roll,))
    student = cursor.fetchone()

    # ---- Per-subject attendance ----
    cursor.execute("""
        SELECT
            s.subject_id,
            s.subject_name,
            t.teacher_name,
            a.classes_conducted,
            a.classes_attended
        FROM Attendance a
        JOIN Subjects s ON a.subject_id = s.subject_id
        JOIN Teachers t ON s.teacher_id = t.teacher_id
        WHERE a.roll_number = %s
    """, (roll,))
    records = cursor.fetchall()
    conn.close()

    # ---- Per-subject calculations (no claims applied at subject level) ----
    for r in records:
        attended  = r["classes_attended"]
        conducted = r["classes_conducted"]

        pct = 0 if conducted == 0 else round((attended / conducted) * 100, 2)

        r["percentage"]     = pct
        r["hours_attended"] = round(attended  * CLASS_HOURS, 1)
        r["total_hours"]    = round(conducted * CLASS_HOURS, 1)

    # ---- Overall totals ----
    total_attended  = sum(r["classes_attended"]  for r in records)
    total_conducted = sum(r["classes_conducted"] for r in records)

    # ---- Apply claims to overall metrics only ----
    metrics = calculate_metrics(
        attended  = total_attended,
        conducted = total_conducted,
        medical   = medical,
        extra     = extra,
        remaining = 0       # set if you track remaining classes
    )

    overall_percentage    = metrics["percentage"]
    display_percentage    = metrics["display_percentage"]
    progress              = metrics["display_percentage"]
    classes_needed        = metrics["needed"]
    effective_conducted   = metrics["effective_conducted"]

    return (
        student,
        records,
        total_attended,
        total_conducted,       # raw conducted (shown in table)
        effective_conducted,   # after claims (used for overall stats)
        overall_percentage,
        display_percentage,
        progress,
        classes_needed,
    )


# -------------------------------------------------
# STUDENT DASHBOARD
# -------------------------------------------------

@app.route("/student", methods=["POST"])
def student():

    roll = request.form["roll"]

    (
        student,
        records,
        total_attended,
        total_conducted,
        effective_conducted,
        overall_percentage,
        display_percentage,
        progress,
        classes_needed,
    ) = get_student_dashboard_data(roll)

    if not student:
        return "Invalid Roll Number", 404

    return render_template(
        "student_dashboard.html",
        student             = student,
        records             = records,
        total_attended      = total_attended,
        total_conducted     = total_conducted,
        effective_conducted = effective_conducted,
        overall_percentage  = overall_percentage,
        display_percentage  = display_percentage,
        progress            = progress,
        classes_needed      = classes_needed,
        simulated           = False,
        medical_claim       = 0,
        extra_claim         = 0,
    )


# -------------------------------------------------
# CLAIM SIMULATOR
# -------------------------------------------------

@app.route("/simulate_claim", methods=["POST"])
def simulate_claim():

    roll    = request.form["roll"]
    medical = int(request.form.get("medical_claim") or 0)
    extra   = int(request.form.get("extra_claim")   or 0)

    (
        student,
        records,
        total_attended,
        total_conducted,
        effective_conducted,
        overall_percentage,
        display_percentage,
        progress,
        classes_needed,
    ) = get_student_dashboard_data(roll, medical=medical, extra=extra)

    if not student:
        return "Invalid Roll Number", 404

    return render_template(
        "student_dashboard.html",
        student             = student,
        records             = records,
        total_attended      = total_attended,
        total_conducted     = total_conducted,
        effective_conducted = effective_conducted,
        overall_percentage  = overall_percentage,
        display_percentage  = display_percentage,
        progress            = progress,
        classes_needed      = classes_needed,
        simulated           = True,
        medical_claim       = medical,
        extra_claim         = extra,
    )


# -------------------------------------------------
# RESET DASHBOARD
# -------------------------------------------------

@app.route("/reset_dashboard", methods=["POST"])
def reset_dashboard():
    roll = request.form["roll"]
    return redirect(url_for("student"), code=307)



# --------------------------
# TEACHER LOGIN / DASHBOARD
# --------------------------

@app.route("/teacher", methods=["GET", "POST"])
def teacher():

    if request.method == "POST":
        teacher_id = request.form["teacher_id"]
    else:
        teacher_id = request.args.get("teacher_id")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
        a.attendance_id,
        st.roll_number,
        st.student_name,
        s.subject_id,
        s.subject_name,
        a.classes_attended,
        a.classes_conducted
        FROM Attendance a
        JOIN Students st ON a.roll_number = st.roll_number
        JOIN Subjects s ON a.subject_id = s.subject_id
        WHERE s.teacher_id=%s
    """, (teacher_id,))

    records = cursor.fetchall()
    conn.close()

    return render_template(
        "teacher_dashboard.html",
        records=records,
        teacher_id=teacher_id
    )


# --------------------------
# MARK PRESENT
# --------------------------

@app.route("/mark_present", methods=["POST"])
def mark_present():

    attendance_id = request.form["attendance_id"]
    teacher_id = request.form["teacher_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Attendance
        SET classes_attended = classes_attended + 1,
            classes_conducted = classes_conducted + 1
        WHERE attendance_id=%s
    """,(attendance_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("teacher", teacher_id=teacher_id))


# --------------------------
# MARK ABSENT
# --------------------------

@app.route("/mark_absent", methods=["POST"])
def mark_absent():

    attendance_id = request.form["attendance_id"]
    teacher_id = request.form["teacher_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Attendance
        SET classes_conducted = classes_conducted + 1
        WHERE attendance_id=%s
    """,(attendance_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("teacher", teacher_id=teacher_id))


# --------------------------
# EDIT ATTENDANCE
# --------------------------

@app.route("/edit_attendance", methods=["POST"])
def edit_attendance():

    attendance_id = request.form["attendance_id"]
    new_attended = request.form["new_attended"]
    teacher_id = request.form["teacher_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Attendance
        SET classes_attended=%s
        WHERE attendance_id=%s
    """,(new_attended,attendance_id))

    conn.commit()
    conn.close()

    return redirect(url_for("teacher", teacher_id=teacher_id))

@app.route("/edit_conducted", methods=["POST"])
def edit_conducted():

    attendance_id = request.form["attendance_id"]
    new_conducted = request.form["new_conducted"]
    teacher_id = request.form["teacher_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Attendance
        SET classes_conducted=%s
        WHERE attendance_id=%s
    """, (new_conducted, attendance_id))

    conn.commit()
    conn.close()

    return redirect(url_for("teacher", teacher_id=teacher_id))


if __name__ == "__main__":
    app.run(debug=True)