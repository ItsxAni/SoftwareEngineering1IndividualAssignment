from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Define a many-to-many relationship table between Student and Course with an additional 'grade' field
student_course_association = db.Table(
    'student_course_association',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('grade', db.Integer)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Changed the primary key column to 'id'
    name = db.Column(db.String(100), nullable=False)
    credits_earned = db.Column(db.Integer, nullable=False)
    courses = db.relationship('Course', secondary=student_course_association, back_populates='students')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))  # Updated the foreign key reference
    instructor = db.relationship('Instructor', back_populates='courses')
    students = db.relationship('Student', secondary=student_course_association, back_populates='courses')

class Instructor(db.Model):
    name = db.Column(db.String(100), nullable=False)
    id = db.Column(db.Integer, primary_key=True)  # Changed the primary key column to 'id'
    department = db.Column(db.String(100), nullable=False)
    courses = db.relationship('Course', back_populates='instructor')




@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    credits_earned = request.form['credits_earned']
    student_id = request.form['student_id']
    courses_input = request.form.getlist('courses')


    new_student = Student(name=name, credits_earned=credits_earned, id=student_id)
    # new_student.courses = courses

    db.session.add(new_student)
    db.session.commit()
    return redirect('/')

@app.route('/update_student/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    student = Student.query.get(id)
    if student:
        if request.method == 'POST':
            student.name = request.form['name']
            student.credits_earned = request.form['credits_earned']
            db.session.commit()
            return redirect('/students')
        return render_template('update_student.html', student=student)
    return 'Student not found', 404

@app.route('/delete_student/<int:id>')
def delete_student(id):
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect('/students')




@app.route('/add_course', methods=['POST'])
def add_course():
    name = request.form['name']
    department = request.form['department']
    
    new_instructor = Instructor(name=name, department=department)
    db.session.add(new_instructor)
    db.session.commit()

@app.route('/update_course/<int:id>', methods=['GET', 'POST'])
def update_course(id):
    course = Course.query.get(id)
    if course:
        if request.method == 'POST':
            course.title = request.form['title']
            db.session.commit()
            return redirect('/courses')
        return render_template('update_course.html', course=course)
    return 'Course not found', 404

@app.route('/delete_course/<int:id>')
def delete_course(id):
    course = Course.query.get(id)
    if course:
        db.session.delete(course)
        db.session.commit()
    return redirect('/courses')

@app.route('/update_instructor/<int:id>', methods=['GET', 'POST'])
def update_instructor(id):
    instructor = Instructor.query.get(id)
    if instructor:
        if request.method == 'POST':
            instructor.name = request.form['name']
            instructor.department = request.form['department']
            db.session.commit()
            return redirect('/instructors')
        return render_template('update_instructor.html', instructor=instructor)
    return 'Instructor not found', 404

@app.route('/delete_instructor/<int:id>')
def delete_instructor(id):
    instructor = Instructor.query.get(id)
    if instructor:
        db.session.delete(instructor)
        db.session.commit()
    return redirect('/instructors')


@app.route('/add_instructor', methods=['POST'])
def add_instructor():
    name = request.form['name']
    department = request.form['department']
    id = int(request.form['instructor_id'])
    new_instructor = Instructor(name=name, department=department)
    db.session.add(new_instructor)
    db.session.commit()
    return redirect('/')

@app.route('/enter_grades', methods=['POST'])
def enter_grades():
    student_id = request.form['student_id']
    course_id = request.form['course_id']
    grade = request.form['grade']

    # Query the student and course based on their IDs
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if student and course:
        # Create or update the student's grade for the course
        student_course_association = db.session.query(student_course_association).filter_by(student_id=student_id, course_id=course_id)
        if student_course_association.count() > 0:
            student_course_association.update({'grade': grade})
        else:
            db.session.execute(student_course_association.insert().values(student_id=student_id, course_id=course_id, grade=grade))

        db.session.commit()
    else:
        # Handle the case where the student or course doesn't exist
        # You can add error handling or validation here
        pass

    return redirect('/')

# Routes for displaying data
@app.route('/students', methods=['GET'])
def show_students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/courses', methods=['GET'])
def show_courses():
    courses = Course.query.all()
    instructors = Instructor.query.all()
    return render_template('courses.html', courses=courses, instructors=instructors)

@app.route('/instructors', methods=['GET'])
def show_instructors():
    instructors = Instructor.query.all()
    return render_template('instructors.html', instructors=instructors)

@app.route('/', methods=['GET'])
def show_all_info():
    # we want to create each table
    students = Student.query.all()
    courses = Course.query.all()
    # error present here. need help displaying data. 
    instructors = Instructor.query.all()
    return render_template('homepage.html', students=students, courses=courses, instructors=instructors)


if __name__ == "__main__":

    app.run(debug=True)


