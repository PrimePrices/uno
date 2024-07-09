from flask import Blueprint, render_template, request, send_from_directory, abort
from flask_login import login_required
from get_db import get_db
from datetime import date
fact_bp=Blueprint("fact", __name__, template_folder="templates", url_prefix="/fact", static_folder="static")




@fact_bp.route("/")
def todays_fact():
    print("Todays fact accessed")
    conn=get_db()
    year, month, day=date.today().year, date.today().month, date.today().day
    fact=conn.execute(f"SELECT fact, tags, sources FROM facts WHERE date_written='{year}-{month}-{day}'").fetchone()
    if fact is None:
        print("No fact found for today")
        return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text="No fact found for today", tags=[])
    tags=fact[1].split(",")
    conn.close()
    return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], sources=fact[2], tags=tags)

@fact_bp.route("/archive/<int:year>/<int:month>/<int:day>")
@login_required
def archived_fact(year:int, month:int, day:int):
    conn=get_db()
    fact=conn.execute("SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}").fetchone()
    conn.close()
    tags=fact[1].split(",")
    return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], tags=tags)
@fact_bp.route("/search/")
@login_required
def search_by_tag():
    raise NotImplementedError()
    tags=request.args
    print(tags)
    conn = get_db()
    facts=conn.execute(f"SELECT * FROM facts WHERE ").fetchall()
    conn.close()
    return render_template("facts_list.html.jinja", facts=facts)
@fact_bp.route("/static/<folder>/<anything>")
def get_static(folder, anything):
    if folder == "script":
        return send_from_directory("apps/fact/static/script", anything)
    elif folder == "style":
        return send_from_directory("apps/fact/static/style", anything)
    elif folder == "image":
        return send_from_directory("static/image", anything)
    else: 
        abort(404)

  
