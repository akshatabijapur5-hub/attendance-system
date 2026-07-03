from flask import Flask, request
import pandas as pd
import qrcode
from datetime import datetime

students = pd.read_excel("class_students.xlsx")
app = Flask(__name__)

selected_subject = ""
present_students = []
attendance_count = []
total_classes = 0

@app.route('/')
def home():
    return '''
    <h2>Select Subject</h2>
    <form action="/set_subject" method="POST">
        <select name="subject">
            <option value="Python">Python</option>
            <option value="DBMS">DBMS</option>
            <option value="Java">Java</option>
        </select>
        <button type="submit">Generate QR</button>
    </form>
    '''
@app.route('/set_subject', methods=['POST'])
def set_subject():
    global selected_subject
    global present_students
    selected_subject = request.form['subject']
    present_students = []

    return generate_qr()


@app.route('/generate_qr')
def generate_qr():
    data = "http:// 192.168.56.1:5000/mark_attendance"
    qr = qrcode.make(data)   
    qr.save("attendance_qr.png")
    return f"QR Generated {selected_subject}"

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    global present_students
    global attendance_count

    if request.method == 'POST':
        reg_no = request.form['reg_no']

        student = students[students['Register No'].astype(str) == str(reg_no)]

        if student.empty:
            return "Invalid Register Number"

        name = student.iloc[0]['Student Name']
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        present_students.append(reg_no)

        if reg_no not in attendance_count:
            attendance_count[reg_no] = 0
        attendance_count[reg_no] += 1    

        record = f"{reg_no} | {name} | {selected_subject} | {date} | Present\n"

        with open("attendance.txt", "a") as file:
            file.write(record)

        return f"Attendance marked for {name} in {selected_subject}"

    return '''
    <h2>Attendance Form</h2>
    <form method="POST">
        Register Number:
        <input type="text" name="reg_no">
        <button type="submit">Submit</button>
    </form>
    '''

@app.route('/close_session')
def close_session():
    global present_students
    global total_classes

    total_classes += 1

    for index, row in students.iterrows():
        reg_no = str(row['Register No'])
        name = row['Student Name']

        if reg_no not in present_students:
            record = f"{reg_no} | {name} | {selected_subject} | Absent\n"

            with open("attendance.txt", "a") as file:
                file.write(record)

    return "Session Closed. Absent students marked."

@app.route('/percentage/<reg_no>')
def percentage(reg_no):
    global attendance_count
    global total_classes

    present = attendance_count.get(reg_no, 0)

    if total_classes == 0:
        return "No classes conducted"

    percent = (present / total_classes) * 100

    return f"Attendance Percentage of {reg_no}: {percent:.2f}%"

@app.route('/reset')
def reset():
    global present_students
    global selected_subject

    present_students = []
    selected_subject = ""

    open("attendance.txt", "w").close()

    return "System Reset Successful"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)




