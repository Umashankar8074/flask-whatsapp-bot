from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# sample code for sending response to our incoming whatsapp message

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

    # fetch all worksheets
    # worksheets = gspreadsheet.worksheets()
    # print(worksheets)

    # add new worksheet from code
    # gspreadsheet.add_worksheet("worksheet3", 4, 5)

    # getting url of the gsheet
    # print(gspreadsheet.url)

    # fetch all values in the worksheets
    # data = worksheet1.get_all_values()
    # print(data)

    # data1 = worksheet1.get_all_records()
    # get_all_records commands prints everything in a worksheet even if the cells are empty
    # print(data1)

    # To check a particular key/word present in the entire worksheet
    # cell = worksheet1.find("erg")
    # print(cell)
    # print(cell.row, cell.col)


    # To fetch a particular value from a particular cell using row and column
    # cell_value = worksheet1.cell(4, 2).value
    # # cell_value = worksheet1.cell(4, 2)
    # print(cell_value)


    # To fetch all row values
    # row3 = worksheet1.row_values(3)
    # print(row3)

    # # To fetch all column values
    # col3 = worksheet1.col_values(3)
    # print(len(col3))
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
            idx = i
            flag = True
            break
    if flag == False:
        worksheet1.update_cell(n+1, 1, from_number)
        idx = n+1
        # here we need to call other function display the menu.
        # is it required to call this function here below ????
        # command_list()
    return idx


# ----------------------------------------------------------------
# opeation functionalities
# Adding a task operation
def add_task(from_number,task):
    # assuming from_number is at a particular row
    idx = user_check(from_number)
    idx = idx + 1
    print(idx)
    row_idx = worksheet1.row_values(idx)
    flag = False
    for i in range(1,len(row_idx)):
        if row_idx[i] == "":
            # row_idx[i] = task
            worksheet1.update_cell(idx, i+1, str(task))
            flag = True
            break
    if flag == False:
        worksheet1.update_cell(idx, len(row_idx)+1, task)
    return "Task added successfully"

# Deleting a task operation
def delete_task(from_number,task):
    # assuming from_number is at a particular row
    idx = user_check(from_number)
    idx = idx + 1
    print(idx)
    flag = False
    row_idx = worksheet1.row_values(idx)
    for i in range(1, len(row_idx)):
        if row_idx[i] == task:
            flag = True
            cell_value = worksheet1.cell(idx, len(row_idx)).value
            worksheet1.update_cell(idx, i+1, cell_value)
            break
        # row_idx[len(row_idx)-1] = ""
    if flag == False:
        return "Task not found please try again"
    else:
        worksheet1.update_cell(idx, len(row_idx), "")
        return "Task deleted successfully"
    
# updating a task operation
def update_task(from_number, task1, task2):
    # assuming from_number is at a particular row
    idx = user_check(from_number)
    idx = idx + 1
    print(idx)
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
def view(from_number):
    idx = user_check(from_number)
    idx = idx + 1
    print(idx)
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
    # idx = idx + 1
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
            return add_task(from_number, task)
        
        elif msg[0] == "Delete":
            # task = " ".join(msg[1:])
            if len(task) == 0:
                return "Error : Invalid input"
            return delete_task(from_number, task)
        
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
            return update_task(from_number, task1, task2)

        elif msg[0] == "View":
            return view(from_number)
        
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


