from flask import Flask, render_template, request, escape, session, copy_current_request_context
from flask import copy_current_request_context
from vsearch import search_letters

from checker import check_logged_in
"""DBcm文件代码中包import mysql.connector"""
from DBcm import UseDatabase, ConnectionError, CredentialsError,SQLError

from threading import Thread
from time import sleep

app = Flask(__name__)

"""将连接属性字典增加到web应用的配置中(Flask内置的配置机制)"""
app.config['dbconfig'] = {'host':'35.173.69.207',
                          'user':'vsearch',
                          'password':'vsearchpasswd',
                          'database':'vsearchlogDB',}

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'

@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are now logged out.'

@app.route('/search', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """log details of the web request and the results"""
        sleep(15)
        with UseDatabase(app.config['dbconfig']) as cursor:

            _SQL = """insert into log
                      (phrase, letters, ip, browser_string, results)
                      values
                      (%s,%s,%s,%s,%s)"""
            cursor.execute(_SQL, (req.form['phrase'],
                                  req.form['letters'],
                                  req.user_agent.browser,
                                  res,))

    phrase=request.form['phrase']
    letters=request.form['letters']
    title='Here are your result'
    results=str(search_letters(phrase,letters))
    try:
        t = Thread(target=log_request, args=(request,results))
        r.start()
    except Exception as err:
        print('*****Logging failed with this err:', str(err))
    return render_template('results.html',
                          the_phrase=phrase,
                          the_letters=letters,
                          the_title=title,
                          the_results=results,)

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to search_letters on the web!')

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:    
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('Phrase', 'Letters', 'ip', 'Remote_addr', 'User_agent', 'Results')
            return render_template('viewlog.html',
                                   the_title='View Log',
                                   the_row_titles=titles,
                                   the_data=contents,)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))
    return 'Error'

app.secret_key = 'YouWillNeverGuessMyScrectKey'

if __name__ == '__main__':
    app.run(debug = True)
