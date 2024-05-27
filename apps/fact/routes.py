from flask import Blueprint, render_template, request
from flask_login import login_required
from .db import get_db
from datetime import date
fact_bp=Blueprint("fact", __name__)

#might be wrong


@fact_bp.route("/")
def todays_fact():
    cursor,conn=get_db()
    year, month, day=date.today().year, date.today().month, date.today().day
    cursor.execute(f"SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}")
    fact=cursor.fetchone()
    tags=fact[1].split(",")
    conn.close()
    return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], tags=tags)
@fact_bp.route("/archive/<year:int>/<month:int>/<day:int>")
@login_required
def archived_fact(year:int, month:int, day:int):
    cursor, conn=get_db()
    fact=cursor.execute("SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}").fetchone()
    conn.close()
    tags=fact[1].split(",")
    return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], tags=tags)
@fact_bp.route("/search/")
@login_required
def search_by_tag():
    tags=request.args
    print(tags)
    cursor, conn = get_db()
    sql_build=[f"tags LIKE {tags[i]}" for i in tags.split(',')]
    facts=cursor.execute("SELECT * FROM facts WHERE {sql_build.join(' AND ')}").fetchall()
    return render_template("facts_list.html.jinja", facts=facts)



  
