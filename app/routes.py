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
from app.forms import LoginForm, StudentRegistrationForm,  InstitutionRegistrationForm, RulesForm, SubmissionForm, PracticeForm
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse
import csv
import pandas as pd
import random
from datetime import datetime
from sqlalchemy import column


import numpy

from psycopg2.extensions import register_adapter, AsIs


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)


@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


@app.route('/')
@app.route('/index')
# @login_required
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accept_rules'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('accept_rules')
        return redirect(url_for('accept_rules'))
    return render_template('login.html', title="Sign in", form=form)

@app.route('/register-student', methods=["GET", "POST"])
def registerstudent():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('accept_rules'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            student_id=form.student_id.data,
            age=form.age.data,
            sex=form.sex.data,
            education=form.education.data,
            year=form.year.data,
            area=form.area.data,
            institution=form.institution.data,
            experience=form.experience.data,
            years_experience=form.years_experience.data,
            usertype=form.usertype.data
            )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for("login"))
    return render_template("student-registration.html", title="Register", form=form)


@app.route('/register-institution', methods=["GET", "POST"])
def registerinstitution():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('accept_rules'))
    form = InstitutionRegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            businessemail=form.businessemail.data,
            affiliation=form.affiliation.data,
            age=form.age.data,
            sex=form.sex.data,
            education=form.education.data,
            year=form.year.data,
            area=form.area.data,
            institution=form.institution.data,
            experience=form.experience.data,
            years_experience=form.years_experience.data,
            usertype=form.usertype.data
            )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for("login"))
    return render_template("institution-registration.html", title="Register", form=form)


@app.route('/accept_rules', methods=["GET", "POST"])
def accept_rules():
    if not current_user.is_authenticated:
        return redirect(url_for("registerstudent"))
    form = RulesForm()
    if form.validate_on_submit():
        return redirect(url_for("experiment"))
    return render_template("accept_rules.html", title="Rules", form=form)


@app.route('/return-excel/')
def return_excel():
    name = 'excel_template.xlsx'
    response = send_file('./static/excel_template.xlsx', as_attachment=True)

    return response

@app.route("/rules/")
def rules():
    return render_template("rules.html")

@app.route('/experiment', methods=["GET", "POST"])
@app.route('/experiment/<int:n_reg>', methods=["GET", "POST"])
@login_required
def experiment(n_reg=1):
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    user_id = current_user.id
    user_experiments = []

    if n_reg == 1:
        random_exp = 1
        with open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv", "w") as file:
            file.write(str(random_exp) + "\n")

    for line in open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv"):
        random_user_num = (line.strip("\n"))
        for line in open("./app/static/users/user_" + str(random_user_num) + "_experiments.csv"):
            user_experiments.append(line.strip("\n"))

    headers = ['question', 'answer']
    df = pd.read_csv("./app/static/correct_answers.csv", usecols=[0, 1], names=headers, header=0)

    answer_key = user_experiments[n_reg - 1]
    answer_key = (int(answer_key))
    correctanswer = df.at[answer_key, 'answer']

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

        if n_reg == 1:
            random_exp = (random.randint(0, 9999))
            with open("./app/static/question-sets/user_" + str(user_id) + "_question_set.csv", "w") as file:
                file.write(str(random_exp) + "\n")

        if n_reg == 1:
            answer = str(form.answer.data)
        else:
            answer = int(form.answer.data)

        if n_reg == 1:
            if bool((int(correctanswer) == answer)):
                Score = 1
                print(Score)
            else:
                Score = 0
                print(Score)
        else:
            if bool((int(correctanswer) == answer)):
                Score = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("score"))]
                Score = int(Score[-1]) + 1
                print(Score)
            else:
                Score = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("score"))]
                Score = int(Score[-1])
                print(Score)

        db.session.add(Submission(
            question=n_reg,
            answer=form.answer.data,
            correctanswer=correctanswer,
            verifyanswer=bool((int(correctanswer) == answer)),
            totaltime=(str(datetime.utcnow() - session['start_time'])),
            regulation=user_experiments[n_reg - 1],
            balance_sheet=user_experiments[n_reg - 1],
            score=Score,
            user_id=current_user.id,
            student_id=current_user.student_id,
            affiliation=current_user.affiliation,
            usertype=current_user.usertype)),
        db.session.commit()
        db.session.expire_all()

        if n_reg <= 9:
            return redirect(url_for("experiment", n_reg=n_reg + 1))  # +1))
        else:
            return redirect(url_for("endpage"))

    session['start_time'] = datetime.utcnow()

    return render_template('experiment.html', form=form, user_experiment_id=user_experiments[n_reg - 1], n_reg=n_reg,
                           table=table)


@app.route('/endpage')
def endpage():

    id = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("id"))]
    question = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("question"))]
    answer = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("answer"))]
    correct_answer = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("correctanswer"))]
    regulation = [r[0] for r in Submission.query.filter_by(user_id=current_user.id).values(column("regulation"))]

    dummy_data1 = {
        'ID': id,
        'question': question,
        'regulation': regulation,
        'answer': answer,
        'correct answer': correct_answer,
    }

    df = pd.DataFrame(dummy_data1, columns=['ID', 'question', 'regulation', 'answer', 'correct answer'])

    pd.to_numeric(df.question)

    df["question"] = pd.to_numeric(df["question"])

    df.sort_index()

    df = df.sort_values(by='ID', axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')

    print(df.dtypes)

    bottom = df.tail(10)

    print(bottom)

    bottom.to_html("./app/static/useranswers-" + str(current_user.id) + ".htm", index=None)
    table = bottom.to_html()

    print(table)

    return render_template('endpage.html', table=table)


@app.route('/leaderboard')
def leaderboard():
    score = [r[0] for r in Submission.query.filter_by(question='10').values((column("score")))]
    username = [r[0] for r in Submission.query.filter_by(question='10').values((column("student_id")))]

    dummy_data3 = {
        'user': username,
        'score': score
    }

    df = pd.DataFrame(dummy_data3)
    pd.set_option('precision', 0)
    df = df.sort_values(by='score', ascending=False)
    df.to_html("./app/static/leaderboard.htm", index=None)
    table = df.to_html()

    print(table)

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

@app.route('/download-user-csv')
def downloadusercsv():
    return '''
        <html><body>
        <a href="/getusercsv">Download Users</a>
        </body></html>
        '''


@app.route("/getsubmissionscsv")
def getPlotCSV():

    score = [r[0] for r in Submission.query.filter((Submission.user_id.between('1', '400 '))).values((column("score")))]
    username = [r[0] for r in Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("student_id")))]
    answer = [r[0] for r in
                Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("answer")))]
    correct_answer = [r[0] for r in
              Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("correctanswer")))]
    regulation = [r[0] for r in
              Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("regulation")))]
    question = [r[0] for r in
              Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("question")))]
    student_id = [r[0] for r in
                Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("student_id")))]
    totaltime = [r[0] for r in
                Submission.query.filter((Submission.user_id.between('1', '400'))).values((column("totaltime")))]

    dummy_data3 = {
        'question': question,
        'regulation': regulation,
        'user': username,
        'answer': answer,
        'correct answer': correct_answer,
        'score': score,
        'student id': student_id,
        'time taken': totaltime
    }

    df = pd.DataFrame(dummy_data3)

    df.to_csv(r'./app/static/submissions.csv', header=True)

    with open("./app/static/submissions.csv") as fp:
        csv = fp.read()

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=submissions.csv"})


@app.route("/getusercsv")
def getUserCSV():

    username = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("username")))]
    email = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("email")))]
    student_id = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("student_id")))]
    sex = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("sex")))]
    education = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("education")))]
    year = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("year")))]
    area = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("area")))]
    institution = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("institution")))]
    experience = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("experience")))]
    years_experience = [r[0] for r in User.query.filter((User.id.between('1', '400'))).values((column("years_experience")))]

    dummy_data3 = {
        'username': username,
        'email': email,
        'student_id': student_id,
        'sex': sex,
        'education': education,
        'year': year,
        'area': area,
        'institution': institution,
        'experience': experience,
        'years_experience': years_experience
    }

    df = pd.DataFrame(dummy_data3)

    df.to_csv(r'./app/static/users.csv', header=True)

    with open("./app/static/users.csv") as fp:
        csv = fp.read()

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=users.csv"})
