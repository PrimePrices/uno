from flask import Blueprint, render_template
from flask_login imort login_required
from time import date
#might be wrong
fact_bp=Blueprint()

@fact_bp.route("/")
def todays_fact():
  cursor,conn=get_db()
  fact=cursor.execute(f"SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}).selectone()
  tags=fact[1].split(",")
  conn.close()
  return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], tags=tags)
@fact_bp.route("/archive/<year:int>/<month:int>/<day:int>")
@login_required
def archived_fact(year:, month:int, day:int):
  cursor, conn=get_db()
  fact=cursor.execute("SELECT text, tags, sources FROM facts WHERE year={year} AND month={month} AND day={day}").selectone()
  conn.close()
  tags=fact[1].split(",")
  return render_template("fact.html.jinja", year=year, month=month, day=day, fact_text=fact[0], tags=tags)
@app.route("/search/limiting")
@login_required
def search_by_tag():
  tags=request.args("tags")
  cursor, conn = get_db()
  sql_build=[f"tags LIKE {tags[i]}" for i in tags.split(',')]
  facts=cursor.execute("SELECT * FROM facts WHERE {sql_build.join(" AND ")}").fetchall()
  return render_template("facts_list.html.jinja", facts=facts)

@app.route("/search/all")
@login_required
def search_by_tag():
  tags=request.args("tags")
  cursor, conn = get_db()
  sql_build=[f"tags LIKE {tags[i]}" for i in tags.split(',')]
  facts=cursor.execute("SELECT * FROM facts WHERE {sql_build.join(" OR ")}").fetchall()
  return render_template("facts_list.html.jinja", facts=facts)

  
