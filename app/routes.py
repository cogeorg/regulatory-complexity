#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 16:10:43 2019

@author: jane

"""
from flask import Flask, Response
from flask import render_template, flash, redirect, request, url_for, send_file, session
from flask_login import current_user, login_user
from app.models import User, Submission, CorrectAnswer
from app import app, db
from app.forms import LoginForm, RegistrationForm, RulesForm, SubmissionForm, PracticeForm
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse
import csv
import pandas as pd  
import random
import numpy as np
from datetime import datetime

import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

# authorize the clientsheet 
client = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client.open('submissions')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)


sheet_instance.col_count
#print (sheet_instance.row_count)

# get all the records of the data
records_data = sheet_instance.get_all_records()

# view the data
#print(records_data)

records_df = pd.DataFrame.from_dict(records_data)

# view the top records
# print(records_df.head())

@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

@app.route('/')
@app.route('/index')
#@login_required
def index():
    return render_template('index.html')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accept_rules'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for("login"))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('accept_rules')
        return redirect(url_for('accept_rules'))
    return render_template('login.html', title = "Sign in", form = form)

@app.route('/register', methods=["GET", "POST"])

def register():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('accept_rules'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data, email=form.email.data, student_id = form.student_id.data, age=form.age.data, sex=form.sex.data, education=form.education.data, year=form.year.data, area=form.area.data, institution=form.institution.data, experience=form.experience.data, years_experience=form.years_experience.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for("login"))
    return render_template("register.html", title = "Register", form=form)

@app.route('/accept_rules', methods=["GET", "POST"])
def accept_rules():
    if not current_user.is_authenticated:
        return redirect(url_for("register"))
    form = RulesForm()
    if form.validate_on_submit():
        return redirect(url_for("experiment"))
    return render_template("accept_rules.html", title = "Rules", form=form)


@app.route('/return-excel/')
def return_excel():
    name = 'excel_template.xlsx'
    response = send_file('./static/excel_template.xlsx', as_attachment=True)
    # response.headers["x-filename"] = name
    # response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    # response.headers["Content-Disposition"] = "attachment; filename=" + name

    return response

@app.route("/rules/")
def rules():
    return render_template("rules.html")

@app.route('/experiment', methods=["GET", "POST"])
@app.route('/experiment/<int:n_reg>', methods=["GET", "POST"])
@login_required
def experiment(n_reg=1, Score=0):
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.id

    if n_reg == 1 :
        random_exp = 0
        with open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv", "w") as file:
            file.write(str(random_exp) + "\n")

    if n_reg == 2 :
        random_exp = (random.randint(0,9999))
        with open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv", "w") as file:
            file.write(str(random_exp) + "\n")

    for line in open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv"):
        random_user_num = (line.strip("\n"))
        user_experiments = []
        for line in open("./app/static/users/user_" + str(random_user_num) + "_experiments.csv"):
            user_experiments.append(line.strip("\n"))
    
    headers = ['question','answer']
    df = pd.read_csv("./app/static/correct_answers.csv", usecols=[0,1], names=headers, header=0)
    # correctanswer = (str(df.loc[df['question'] == n_reg]['answer'].values)[1:1])

    # print(n_reg)
    # print(user_experiments)
    answer_key = user_experiments[n_reg-1]
    # print(answer_key)
    answer_key = (int(answer_key))
    correctanswer = df.at[answer_key,'answer' ]
    # print(correctanswer)
    
    df = pd.read_csv("./app/static/table_template.csv") 
    df.to_html("./app/static/table.htm", na_rep="", index=False, index_names=False, col_space=60)
    df.style.set_properties(**{'text-align': 'right'})
    table = df.to_html()

    form = SubmissionForm()

    if n_reg == 1:
        form = PracticeForm()
    else: 
        form = SubmissionForm()
 
    if form.validate_on_submit():

        submission = Submission(answer = form.answer.data, correctanswer = correctanswer , verifyanswer = bool((correctanswer == form.answer.data)), regulation = user_experiments[n_reg-1], balance_sheet = user_experiments[n_reg-1], user_id = current_user.id)

        spenttime = ((datetime.utcnow() - session['start_time']))

        # headers = ['Index','Regulation','balance_sheet','answer','true','Correct Answer','User ID','Student ID', 'Username', 'Time Elapsed','Submission Full Time', 'Submission Date', 'Score', 'Set']
        
        service = build('sheets', 'v4', credentials=creds)
        spreadsheetId = "1gs3oq_1eCVSXdLhTfgcgv-iqkFqrChKySAZjAfrQMOQ"
        range = "submissions!M:M"
        
        if (n_reg == 1):
            if (bool(correctanswer == form.answer.data)):
                Score = 1
            else:
                Score = 0
        else:
            if (bool(correctanswer == form.answer.data)):
                rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range).execute().get('values')
                last_row = rows[-1] if rows else None
                last_row_id = len(rows)
                Score = int(last_row[0])
                Score = Score + 1 
            else:
                rows = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range).execute().get('values')
                last_row = rows[-1] if rows else None
                last_row_id = len(rows)
                Score = int(last_row[0])
                Score = Score
                
        row = [n_reg, user_experiments[n_reg-1], user_experiments[n_reg-1], submission.answer, submission.verifyanswer, int(submission.correctanswer), current_user.id, current_user.student_id, current_user.username, str(spenttime), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), datetime.utcnow().strftime("%Y-%m-%d"), int(float(Score)), random_user_num,current_user.age, current_user.sex, current_user.education, current_user.year, current_user.area, current_user.institution, current_user.experience, current_user.years_experience  ]
        
        
        service = build('sheets', 'v4', credentials=creds)
        list = [row]
        print (list)
        resource = {
            "majorDimension": "ROWS",
            "values": list
        }

        range = "submissions!A:Z"
        service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId,
        range=range,
        body=resource,
        valueInputOption="USER_ENTERED"
        ).execute()

        if n_reg<=9:
            return redirect(url_for("experiment", n_reg=n_reg+1)) #+1))
        else: 
            return redirect(url_for("endpage"))

    session['start_time'] = datetime.utcnow()
    
    return render_template('experiment.html', form = form, user_experiment_id = user_experiments[n_reg-1], n_reg = n_reg, table = table)



@app.route('/endpage')
def endpage():

    headers = ['Index','Regulation','balance_sheet','answer','true','Correct Answer','User ID','Student ID', 'Username', 'Time Elapsed','Submission Full Time', 'Submission Date', 'Score', 'Set']

    # get the instance of the Spreadsheet
    sheet = client.open('submissions')

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    records_data = sheet_instance.get_all_records()
    
    df = pd.DataFrame.from_dict(records_data)
    newdf = [df['User ID'] == current_user.id]
    bottom = df.tail(10)
    concatenated = pd.concat([bottom])
    print(concatenated)
    concatenated.reset_index(inplace=True, drop=True)

    concatenated.loc[concatenated['User ID'] == current_user.id].to_html("./app/static/useranswers.htm", index=None)
    table = concatenated.to_html()
    print(table)

    return render_template('endpage.html', table=table)

@app.route('/leaderboard')
def leaderboard():

    headers = ['Index','Regulation','balance_sheet','answer','true','Correct Answer','user_id','Student ID', 'Username', 'Time Elapsed','Submission Full Time', 'Submission Date', 'Score', 'Set']
    df = pd.read_csv("./app/static/submissions.csv", parse_dates=[9], names = headers)
    table = df.loc[df['Index'] == 10].sort_values(by='Score', ascending=False).to_html("./app/static/leaderboard.htm", index=None)

    return render_template('leaderboard.html', table=table)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/download-csv')
def downloadcsv():
    return '''
        <html><body>
        <a href="/getsubmissionscsv">Download Submissions</a>
        </body></html>
        '''

@app.route("/getsubmissionscsv")
def getPlotCSV():
    with open("./app/static/submissions.csv") as fp:
        csv = fp.read()

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=submissions.csv"})
