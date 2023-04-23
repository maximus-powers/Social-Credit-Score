from flask import Flask
from flask import render_template
from flask import request,session, redirect, url_for, escape,send_from_directory,make_response 
from flask_session import Session
from datetime import timedelta
from user import user
from student import student
from ratings import ratings

#create Flask app instance
app = Flask(__name__,static_url_path='')

#Configure serverside sessions 
app.config['SECRET_KEY'] = '56hdtryhRTg'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
sess = Session()
sess.init_app(app)

@app.route('/')
def home():
    student_obj = student()

    # query the scores for the leaderboard, adds them all up before subtracting to calc score, comes in order of score desc
    sql = """
        SELECT s.studentID, s.fname, s.lname, 
            COALESCE(SUM(CASE WHEN r.love = 1 THEN 1 ELSE 0 END), 0) AS total_love, 
            COALESCE(SUM(CASE WHEN r.hate = 1 THEN 1 ELSE 0 END), 0) AS total_hate
        FROM `student` s
        LEFT JOIN `ratings` r ON s.studentID = r.studentID
        GROUP BY s.studentID, s.fname, s.lname
        ORDER BY (COALESCE(SUM(r.love), 0) - COALESCE(SUM(r.hate), 0)) DESC;
        """

    student_obj.cur.execute(sql)
    lb_results = student_obj.cur.fetchall()

    # make list of dictionaries from the results
    lb_results_list = []

    # parse the results
    rank = 1
    for row in lb_results:
        new_row = {}
        new_row['rank'] = rank
        new_row['name'] = row['fname'] + ' ' + row['lname']
        new_row['score'] = row['total_love'] - row['total_hate'] if row['total_love'] is not None and row['total_hate'] is not None else 0 # don't forget they might not have any
        new_row['studentID'] = row['studentID']
        lb_results_list.append(new_row)
        rank += 1

    return render_template('home.html',lb_results=lb_results_list)

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        student_obj = student()

        # search for the search term in 3 relevant fields
        sql = f"""SELECT s.studentID, s.fname, s.lname, s.grad_year,
                    COALESCE(SUM(CASE WHEN r.love = 1 THEN 1 ELSE 0 END), 0) AS total_love,
                    COALESCE(SUM(CASE WHEN r.hate = 1 THEN 1 ELSE 0 END), 0) AS total_hate,
                    COALESCE(SUM(r.love), 0) - COALESCE(SUM(r.hate), 0) AS score
                FROM student s
                LEFT JOIN ratings r ON s.studentID = r.studentID
                WHERE s.fname LIKE %s OR s.lname LIKE %s OR s.grad_year LIKE %s
                GROUP BY s.studentID, s.fname, s.lname
                ORDER BY score DESC;
                """

        search_pattern = f"%{search_term}%"  # Adding '%' for pattern matching
        student_obj.cur.execute(sql, (search_pattern, search_pattern, search_pattern))
        search_results = student_obj.cur.fetchall()

        # creates a list of dictionaries from the results
        search_results_list = []
        rank = 1
        for row in search_results:
            new_row = {}
            new_row['rank'] = rank
            new_row['name'] = row['fname'] + ' ' + row['lname']
            new_row['score'] = row['score'] if row['score'] is not None else 0
            new_row['class'] = row['grad_year']
            new_row['studentID'] = row['studentID']
            search_results_list.append(new_row)
            rank += 1

        return render_template('searchResults.html',results=search_results_list)
    else:
        # render the search form for GET requests (before search button is clicked)
        return render_template('home.html')

@app.route('/rate', methods=['POST'])
def rate():
    # get data from the request
    rating_type = request.form.get('rating_type') # Should be 'love' or 'hate'
    student_id = request.form.get('student_id') # Should be the studentID of the parent card

    # create a ratings object and establish a database connection
    ratings_obj = ratings()

    try:
        # insert a new rating entry into the ratings table
        sql = """
        INSERT INTO `ratings` (`love`, `hate`, `userID`, `studentID`)
        VALUES (%s, %s, NULL, %s);
        """
        # set the love and hate values based on the rating_type
        love = 1 if rating_type == 'love' else 0
        hate = 1 if rating_type == 'hate' else 0
        # execute the SQL query
        ratings_obj.cur.execute(sql, (love, hate, student_id))
        ratings_obj.conn.commit()

        # return success response
        return 'Rating added successfully!', 200
    except Exception as e:
        # handle any errors
        ratings_obj.conn.rollback()
        return 'Error adding rating: {}'.format(str(e)), 500

@app.route('/new-student', methods=['POST'])
def newStudent():
    student_obj = student()

    # Get data from the request
    fname = request.form['fname']
    lname = request.form['lname']
    class_name = request.form['class']

    # Convert names to lowercase for case-insensitive check
    fname_lower = fname.lower()
    lname_lower = lname.lower()

    # Check if student already exists in the table, case-insensitive
    student_obj.cur.execute("SELECT * FROM student WHERE LOWER(fname) = %s AND LOWER(lname) = %s", (fname_lower, lname_lower))
    existing_student = student_obj.cur.fetchone()

    if existing_student:
        # Student already exists, return a response indicating duplicate record
        return "Error: Student already exists in the database."

    else:
        # Insert form data into the 'student' table
        student_obj.cur.execute("INSERT INTO student (fname, lname, grad_year) VALUES (%s, %s, %s)", (fname, lname, class_name))

        # Commit the transaction and close the database connection
        student_obj.conn.commit()

        # Redirect to a success page or return a response indicating successful insertion
        return "Record added successfully!"


@app.route('/confirm',methods=['GET','POST'])
def confirm():
    #product = request.form.get('product')
    product = session['product']
    ship = request.form.get('ship')
    return render_template('confirm.html',product=product,ship=ship)

#test setting a session:
@app.route('/set')
def set():
    session['key'] = 'value'
    return 'ok'

#test getting a session:
@app.route('/get')
def get():
    return session.get('key', 'not set')

@app.route('/test')
def test():
    user = 'Tommy'
    return render_template('test.html',username = user)

@app.route('/list_users')
def list_users():
    o = user()
    o.getAll()
    return render_template('list_users.html',objs = o)

@app.route('/users/manage',methods=['GET','POST'])
def manage_user():
    o = user()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    if action is not None and action == 'insert':
        d = {}
        d['name'] = request.form.get('name')
        d['email'] = request.form.get('email')
        d['role'] = request.form.get('role')
        d['password'] = request.form.get('password')
        o.set(d)
        o.insert()
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['name'] = request.form.get('name')
        o.data[0]['email'] = request.form.get('email')
        o.data[0]['role'] = request.form.get('role')
        o.data[0]['password'] = request.form.get('password')
        o.update()
        
    if pkval is None:
        o.getAll()
        return render_template('users/list.html',objs = o)
    if pkval == 'new':
        o.createBlank()
        return render_template('users/add.html',obj = o)
    else:
        o.getById(pkval)
        return render_template('users/manage.html',obj = o)

#display form   
@app.route('/enterName')
def enterName():
    return render_template('nameForm.html')

#process form   
@app.route('/submitName',methods=['GET','POST'])
def submitName():
    username = request.form.get('myname')
    othername = request.form.get('othername')
    print(othername)
    print(username)
    #At this point we would INSERT the user's name to the mysql table
    return render_template('message.html',msg='name '+str(username)+' added!')

@app.route('/elements')
def elements():
    return render_template('formelements.html')

# endpoint route for static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
      
  
if __name__ == '__main__':
   app.run(host='127.0.0.1',debug=True)   