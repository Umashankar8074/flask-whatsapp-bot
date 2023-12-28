from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "*"}})

def gsheet():
    import gspread

    # authentication path and connect
    credentials_file = "gsheetdbtest-407903-596ca589949f.json"
    google_connect = gspread.service_account(filename=credentials_file)

    # connecting to particular spread sheet
    gspreadsheet = google_connect.open("test-sheet")

    # connecting to particular worksheet
    worksheet1 = gspreadsheet.worksheet("worksheet1")

    worksheet1.update_cell(1, 1, 'user phone number')
    worksheet1.update_cell(1, 2, 'list of tasks of user')
    return worksheet1

worksheet1 = gsheet()
def command_list():
    commands = ("here is the format for input \n"
          "Add <task> \n"
          "Delete <task> \n"
          "Update <task1> ; <task2> \n"
          "View \n"
          )
    return commands

def user_check(from_number):
    col1 = worksheet1.col_values(1)
    n = len(col1)
    idx = -1
    flag = False
    for i in range(1,n):
        if from_number == col1[i]:
            idx = i+1
            flag = True
            break
    if flag == False:
        worksheet1.update_cell(n+1, 1, from_number)
        idx = n+1
    return idx


# ----------------------------------------------------------------
# opeation functionalities
# Adding a task operation
def add_task(task, idx):
    # assuming from_number is at a particular row
    # print(idx)
    row_idx = worksheet1.row_values(idx)
    worksheet1.update_cell(idx, len(row_idx)+1, task)
    return "Task added successfully"

# Deleting a task operation
def delete_task(task, idx):
    # assuming from_number is at a particular row
    # print(idx)
    flag = False
    row_idx = worksheet1.row_values(idx)
    for i in range(1, len(row_idx)):
        if row_idx[i] == task:
            flag = True
            cell_value = worksheet1.cell(idx, len(row_idx)).value
            worksheet1.update_cell(idx, i+1, cell_value)
            break
    if flag == False:
        return "Task not found please try again"
    else:
        worksheet1.update_cell(idx, len(row_idx), "")
        return "Task deleted successfully"
    
# updating a task operation
def update_task(task1, task2, idx):
    # assuming from_number is at a particular row
    # print(idx)
    flag = False
    row_idx = worksheet1.row_values(idx)
    for i in range(1, len(row_idx)):
        if row_idx[i] == str(task1):
            worksheet1.update_cell(idx, i+1, str(task2))
            flag = True
            break
    if flag == True:
        return "Task updated successfully"
    else:
        return "Task not updated please try again"
    
# viewing all tasks for a user
def view(idx):
    # print(idx)
    row_idx = worksheet1.row_values(idx)
    print(row_idx)
    if len(row_idx[1:]) == 0:
        return "You have no tasks in the TO-DO list"
    else:
        res = '\n'.join([i for i in row_idx[1:]])
        return res
    
# for processing the msg and calling the respective function
def process_msg(from_number,user_input):
    idx = user_check(from_number)
    # for old user case
    msg = user_input.split()
    print(msg)
    if idx < len(worksheet1.col_values(1)):
        # calling of other functions
        task = " ".join(msg[1:])
        if msg[0] == "Add":
            # task = " ".join(msg[1:])
            if len(task) == 0:
                return "Error : Invalid input"
            return add_task(task, idx)
        
        elif msg[0] == "Delete":
            # task = " ".join(msg[1:])
            if len(task) == 0:
                return "Error : Invalid input"
            return delete_task(task, idx)
        
        elif msg[0] == "Update":
            index = -1
            for i in range(len(msg)):
                if msg[i] == ";":
                    index = i
            # print(index)
            task1 = " ".join(msg[1:index])
            task2 = " ".join(msg[index+1:])
            print(task1,task2)
            if len(task1) == 0 or len(task2) == 0 or index == -1:
                return "Error : Invalid input"
            return update_task(task1, task2, idx)

        elif msg[0] == "View":
            return view(idx)
        
        else:
            return command_list()
    
    elif idx == len(worksheet1.col_values(1)):
        # call the command list function
        return command_list()

# ---------------------------------------------------------------- #
# check the working of all the functions propoerly #
# optimization and dealing with edge cases #
# ---------------------------------------------------------------- #

@app.route("/")
def hello():
    return "Hello, world!"


@app.route("/sms", methods=["GET", "POST"])
def sms_reply():
    "Respond to incoming calls with a simple text message"

    # Fetch the message
    print("request.form --")
    print(request.form)

    msg = request.form.get('Body')
    print("message received " + msg)

    from_number = request.form.get('From')
    print("from_number " + from_number)

    # calling the process message function
    message = process_msg(from_number, msg)
    # Create reply
    resp = MessagingResponse()
    # resp.message("You said: {}".format(msg))
    resp.message(message)

    # gsheet()
    return str(resp)

if __name__ == '__main__':
    app.run(debug = False, port = 5001)


