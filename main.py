from MyMoney_UI import *
from new_balance_UI import *
from new_category_UI import *
from new_income_UI import *
from new_expense_UI import *
import datetime
import psycopg2
import sys

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

def DB_connect(DB_name,DB_user,DB_password,DB_host,DB_port):
    global DB
    try:
        DB = psycopg2.connect(
            database = DB_name,
            user = DB_user,
            password = DB_password,
            host = DB_host,
            port = DB_port
            )
        print('Успешное подключение к БД')
    except:
        print('Ошибка подключения к БД')
    return

DB_connect("MyMoneyDB","postgres","postgres","localhost","5432")


def get_all_balance():
    select_amount_all_balances = 'SELECT "Balance_amount" FROM "Balance";'
    with DB.cursor() as cursor:
        cursor.execute(select_amount_all_balances)
        amount_all_balances = cursor.fetchall()
        DB.commit()
    all_balances_amount = 0
    for i in range(len(amount_all_balances)):
        all_balances_amount += amount_all_balances[i][0]
    print(all_balances_amount)
    ui.label_2.setText(str(all_balances_amount) + ' руб.')

def show_balances():
    global all_balances
    select_balances = 'SELECT "Balance_name","Balance_amount" FROM "Balance";'
    with DB.cursor() as cursor:
        cursor.execute(select_balances)
        all_balances = cursor.fetchall()
        DB.commit()
    print(all_balances)
    for i in range(len(all_balances)):
        ui.listWidget_2.addItem(QtWidgets.QListWidgetItem(str(all_balances[i][0])))
        ui.listWidget_3.addItem(QtWidgets.QListWidgetItem(str(all_balances[i][1]) + ' руб.'))


def listwidget_balance_delete():
    balance_delete_index = ui.listWidget_2.currentRow()
    if balance_delete_index != -1:
        balance_delete_row = ui.listWidget_2.item(balance_delete_index).text()
        print(str(balance_delete_index) + ', ' + str(balance_delete_row))
        print(type(balance_delete_row))
        try:
            delete_selected_balance = f'DELETE FROM "Balance" WHERE "Balance_name" = \'{balance_delete_row}\''
            with DB.cursor() as cursor:
                cursor.execute(delete_selected_balance)
                DB.commit()
            update_balances()
        except:
            print('ошибка удаления строки')

def update_balances():
    ui.listWidget_2.clear()
    ui.listWidget_3.clear()
    show_balances()
    get_all_balance()

def show_incomes():
    select_incomes = '''
    SELECT "Income_ID","Income_name","Income_amount","Income_date","Category_name", "Balance_name"
    FROM "Income"
    JOIN "Categories" ON "Income"."Category_ID" = "Categories_ID"
    JOIN "Balance" ON "Income"."Balance_id" = "Balance_ID";
    '''
    with DB.cursor() as cursor:
        cursor.execute(select_incomes)
        all_incomes = cursor.fetchall()
        DB.commit()
    print(all_incomes)
    ui.tableWidget.setRowCount(len(all_incomes))
    for i in range(len(all_incomes)):
        for j in range(len(all_incomes[i])):
            ui.tableWidget.setItem(i,j, QtWidgets.QTableWidgetItem(str(all_incomes[i][j])))

def show_expenses():
    select_expenses = '''
    SELECT "Expenses_ID","Expenses_name","Expenses_amount","Expenses_date","Category_name","Balance_name"
    FROM "Expenses"
    JOIN "Categories" ON "Expenses"."Category_ID" = "Categories_ID"
    JOIN "Balance" ON "Expenses"."Balance_id" = "Balance_ID";
    '''
    with DB.cursor() as cursor:
        cursor.execute(select_expenses)
        all_expenses = cursor.fetchall()
        DB.commit()
    print('SHOW EXPENSES: ' + str(all_expenses))
    ui.tableWidget_2.setRowCount(len(all_expenses))
    for i in range(len(all_expenses)):
        for j in range(len(all_expenses[i])):
            ui.tableWidget_2.setItem(i, j, QtWidgets.QTableWidgetItem(str(all_expenses[i][j])))

def show_categories():
    select_categories = 'SELECT * FROM "Categories"'
    select_categories_names = 'SELECT "Category_name" FROM "Categories"'
    with DB.cursor() as cursor:
        cursor.execute(select_categories)
        all_categories = cursor.fetchall()
        cursor.execute(select_categories_names)
        categories_name = cursor.fetchall()
        DB.commit()
    print(categories_name)
    print(all_categories)
    for row in range(len(all_categories)):
        ui.listWidget_4.addItem(QtWidgets.QListWidgetItem(str(categories_name[row]).strip("(),'")))
    ui.listWidget_4.doubleClicked.connect(category_info)

def listwidget_categories_delete():
    categories_delete_index = ui.listWidget_4.currentRow()
    if categories_delete_index != -1:
        categories_delete_row = ui.listWidget_4.item(categories_delete_index).text()
        print(str(categories_delete_index) + ', ' + str(categories_delete_row))
        try:
            delete_selected_category = f'DELETE FROM "Categories" WHERE "Category_name" = \'{categories_delete_row}\''
            with DB.cursor() as cursor:
                cursor.execute(delete_selected_category)
                DB.commit()
            update_categories()
        except:
            print('ошибка удаления категории')

def new_categories_window():
    global New_Category, ui_New_Category
    New_Category = QtWidgets.QWidget()
    ui_New_Category = Ui_New_Category()
    ui_New_Category.setupUi(New_Category)
    New_Category.show()
    ui_New_Category.pushButton.clicked.connect(new_category)

def new_category():
    category_name = ui_New_Category.lineEdit.text()
    category_bool = ui_New_Category.checkBox.checkState()
    print(category_bool)
    try:
        if category_bool == 2:
            insert_new_category = f"INSERT INTO \"Categories\" VALUES (DEFAULT,'{category_name}','TRUE')"
        else:
            insert_new_category = f"INSERT INTO \"Categories\" VALUES (DEFAULT,'{category_name}','FALSE')"
        print(insert_new_category)
        with DB.cursor() as cursor:
            cursor.execute(insert_new_category)
            DB.commit()
            update_categories()
    except:
        print('Ошибка добавления новой категории')

def category_info():
    try:
        ui.plainTextEdit.clear()
        category_name = ui.listWidget_4.model().index(ui.listWidget_4.currentRow()).data()
        print('CATEGORY_INFO ' + str(category_name))
        select_get_category = f'SELECT "Categories_ID","Category_for_Income" FROM "Categories" WHERE "Category_name" = \'{category_name}\';'
        try:
            with DB.cursor() as cursor:
                cursor.execute(select_get_category)
                get_category = cursor.fetchall()
                DB.commit()
            category_id = str(get_category[0][0]).strip("(),'\"")
            category_id = int(category_id)
            category_bool = get_category[0][1]
            print('CATEGORY_INFO ' + 'ID категории ' + str(category_id))
            print('CATEGORY_INFO ' + 'BOOL ' + str(category_bool) + ' ' + str(type(category_bool)))
            if category_bool:
                select_category_amount = f'SELECT "Income_amount" FROM "Income" WHERE "Category_ID" = {category_id};'
                cout_category_number = f'SELECT count("Income_ID") FROM "Income" WHERE "Category_ID" = {category_id};'
            else:
                select_category_amount = f'SELECT "Expenses_amount" FROM "Expenses" WHERE "Category_ID" = {category_id};'
                cout_category_number = f'SELECT count("Expenses_ID") FROM "Expenses" WHERE "Category_ID" = {category_id};'
            with DB.cursor() as cursor:
                cursor.execute(cout_category_number)
                category_number = cursor.fetchall()
                cursor.execute(select_category_amount)
                category_amount_str = cursor.fetchall()
                DB.commit()
            category_amount = []
            category_amount_sum = 0
            for i in range(len(category_amount_str)):
                category_amount.append(float(category_amount_str[i][0]))
                category_amount_sum += category_amount[i]
            category_number = str(category_number[0]).strip("(),'\"")
            print('CATEGORY_INFO ' + 'траты по категории ' + str(category_amount_sum))
            print('CATEGORY_INFO ' + 'Количество записей с категорией ' + str(category_number))
            print('CATEGORY_INFO ' + 'Список трат по категории ' + str(category_amount_str))
            info_text = f"Количетсво транзакций по категории {category_name}:\n{category_number}\nСумма транзакций по категории {category_name}:\n{category_amount_sum}"
            ui.plainTextEdit.insertPlainText(info_text)
        except:
            print('Ошибка  вывода inf категории')
    except:
        print('Ошибка получения inf о категории')


def update_categories():
    ui.listWidget_4.clear()
    show_categories()

def new_balance_window():
    global New_Balance, ui_New_Balance
    New_Balance = QtWidgets.QWidget()
    ui_New_Balance = Ui_New_Balance()
    ui_New_Balance.setupUi(New_Balance)
    New_Balance.show()
    ui_New_Balance.pushButton.clicked.connect(new_balance)

def new_balance():
    balance_name = ui_New_Balance.lineEdit.text()
    balance_amount = ui_New_Balance.lineEdit_2.text()
    try:
        insert_new_balance = f"INSERT INTO \"Balance\" VALUES (DEFAULT,'{balance_name}',{float(balance_amount)})"
        print(insert_new_balance)
        with DB.cursor() as cursor:
            cursor.execute(insert_new_balance)
            DB.commit()
            update_balances()
    except:
        print('Ошибка добавления нового счёта')

def update_tables():
    for i in range(ui.tableWidget.rowCount()): ui.tableWidget.removeRow(i)
    for i in range(ui.tableWidget_2.rowCount()): ui.tableWidget_2.removeRow(i)
    show_incomes()
    show_expenses()

def new_expens_window():
    global Dialog_expense, Dialog_expense_ui
    Dialog_expense = QtWidgets.QDialog()
    Dialog_expense_ui = Ui_New_Expense()
    Dialog_expense_ui.setupUi(Dialog_expense)
    Dialog_expense.show()
    Dialog_expense_ui.pushButton_2.clicked.connect(add_new_expense)

    select_categories_expanse = 'SELECT "Categories_ID","Category_name" FROM "Categories" WHERE "Category_for_Income" = FALSE;'
    print(select_categories_expanse)
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_categories_expanse)
            categories_expense = cursor.fetchall()
            DB.commit()
        print(categories_expense)
        for i in range(len(categories_expense)):
            Dialog_expense_ui.comboBox.addItem(str(categories_expense[i]).strip("(),'1234567890"), int(categories_expense[i][0]))
        for i in range(len(all_balances)):
            Dialog_expense_ui.comboBox_2.addItem(str(all_balances[i][0]), int(all_balances[i][1]))
        Dialog_expense_ui.dateEdit.setDate((datetime.date).today())
    except:
        print("Не получилось запросить категории для расхода")

def new_income_window():
    global Dialog_income, Dialog_income_ui
    Dialog_income = QtWidgets.QDialog()
    Dialog_income_ui = Ui_New_Income()
    Dialog_income_ui.setupUi(Dialog_income)
    Dialog_income.show()
    Dialog_income_ui.pushButton_2.clicked.connect(add_new_income)

    select_categories_income = 'SELECT "Categories_ID", "Category_name" FROM "Categories" WHERE "Category_for_Income" = TRUE;'
    print(select_categories_income)
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_categories_income)
            categories_income = cursor.fetchall()
            DB.commit()
        print(categories_income)
        for i in range(len(categories_income)):
            Dialog_income_ui.comboBox.addItem(str(categories_income[i][1]).strip("(),''"), int(categories_income[i][0]))
        for i in range(len(all_balances)):
            Dialog_income_ui.comboBox_2.addItem(str(all_balances[i][0]), int(all_balances[i][1]))
        Dialog_income_ui.dateEdit.setDate((datetime.date).today())
    except:
        print("Не получилось запросить категории для дохода")

def add_new_income():
    income_description = Dialog_income_ui.lineEdit.text()
    income_amount = Dialog_income_ui.lineEdit_2.text()
    income_date = Dialog_income_ui.dateEdit.date().toPyDate()
    income_category_ID = Dialog_income_ui.comboBox.currentData()
    income_balance = Dialog_income_ui.comboBox_2.currentData()
    income_balance_name = Dialog_income_ui.comboBox_2.currentText()
    income_balance_name.strip("(),'\"1234567890")
    income_amount = int(income_amount)
    income_balance_plus = income_balance + income_amount
    select_get_balance_id = f'SELECT "Balance_ID" FROM "Balance" WHERE "Balance_name" = \'{income_balance_name}\';'
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_get_balance_id)
            get_balance_id = cursor.fetchall()
            DB.commit()
        print(get_balance_id)
        print(str(get_balance_id[0]).strip("(),'\""))
        get_balance_income_index = str(get_balance_id[0]).strip("(),'\"")
        get_balance_income_index = int(get_balance_income_index)

    except:
        print('Ошибка получения id баланса')
    print('----------------------------------------------------------------------------------------------------')
    print(income_date.strftime("%m-%d-%Y"))
    print(str(income_description) + ' ' +str(income_amount) + ' ' +str(income_date) + ' ' +str(income_category_ID) + ' ' + str(income_balance) + ' ' + str(income_balance_plus))
    update_balance = f'UPDATE "Balance" SET "Balance_amount" = {income_balance_plus} WHERE "Balance_name" = \'{income_balance_name}\''
    insert_new_income = f"""
    INSERT INTO \"Income\" (\"Income_ID\", \"Income_name\", \"Income_amount\", \"Income_date\", \"Category_ID\", \"Balance_id\") 
        VALUES (DEFAULT, '{income_description}', {income_amount}, '{income_date}', {income_category_ID}, {get_balance_income_index});"""
    try:
        with DB.cursor() as cursor:
            cursor.execute(insert_new_income)
            cursor.execute(update_balance)
            DB.commit()
        update_balances()
        update_tables()
    except:
        print('Ошибка при добалвении дохода или изменении баланса')

def add_new_expense():
    expense_description = Dialog_expense_ui.lineEdit.text()
    expense_amount = Dialog_expense_ui.lineEdit_2.text()
    expense_date = Dialog_expense_ui.dateEdit.date().toPyDate()
    expense_category_ID = Dialog_expense_ui.comboBox.currentData()
    expense_balance = Dialog_expense_ui.comboBox_2.currentData()
    expense_balance_name = Dialog_expense_ui.comboBox_2.currentText()
    expense_balance_name.strip("(),'\"1234567890")
    expense_amount = int(expense_amount)
    expense_balance_minus = expense_balance - expense_amount
    select_get_balance_id = f'SELECT "Balance_ID" FROM "Balance" WHERE "Balance_name" = \'{expense_balance_name}\';'
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_get_balance_id)
            get_balance_id = cursor.fetchall()
            DB.commit()
        print(get_balance_id)
        print(str(get_balance_id[0]).strip("(),'\""))
        get_balance_expense_index = str(get_balance_id[0]).strip("(),'\"")
        get_balance_expense_index = int(get_balance_expense_index)
    except:
        print('Ошибка получения id баланса')
    print('----------------------------------------------------------------------------------------------------')
    print(expense_date.strftime("%m-%d-%Y"))
    print(str(expense_description) + ' ' + str(expense_amount) + ' ' + str(expense_date) + ' ' + str(
        expense_category_ID) + ' ' + str(expense_balance) + ' ' + str(expense_balance_minus) + ' ' + str(get_balance_expense_index))
    update_balance = f'UPDATE "Balance" SET "Balance_amount" = {expense_balance_minus} WHERE "Balance_name" = \'{expense_balance_name}\''
    insert_new_expense = f"""
    INSERT INTO \"Expenses\" (\"Expenses_ID\", \"Expenses_name\", \"Expenses_amount\", \"Expenses_date\", \"Category_ID\", \"Balance_id\") 
        VALUES (DEFAULT, '{expense_description}', {expense_amount}, '{expense_date}', {expense_category_ID}, {get_balance_expense_index});"""
    try:
        with DB.cursor() as cursor:
            cursor.execute(insert_new_expense)
            cursor.execute(update_balance)
            DB.commit()
        update_balances()
        update_tables()
    except:
        print('Ошибка при добалвении расхода или изменении баланса')

def delete_income():
    row = ui.tableWidget.currentIndex().row()
    income_id = ui.tableWidget.model().index(row,0).data()
    balance_name = ui.tableWidget.model().index(row,5).data()
    income_amount = ui.tableWidget.model().index(row,2).data()
    income_amount = str(income_amount)
    income_amount = float(income_amount)
    print('================================')
    print(income_amount)
    print(balance_name)
    print(type(income_amount))
    print('=============================')
    select_get_balance = f'SELECT "Balance_amount" FROM "Balance" WHERE "Balance_name" = \'{balance_name}\''
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_get_balance)
            expense_balance = cursor.fetchall()
            DB.commit()
            balance_amount = str(expense_balance[0][0]).strip("(),'\"")
            balance_amount = int(balance_amount)
            print(income_amount)
            print(balance_amount)
            print(type(balance_amount))
    except:
        print('Ошибка получения баланса при удалении')
    balance_minus = balance_amount - income_amount
    print(balance_minus)
    delete_income = f'DELETE FROM "Income" WHERE "Income_ID" = {income_id}'
    update_balance = f'UPDATE "Balance" SET "Balance_amount" = {balance_minus} WHERE "Balance_name" = \'{balance_name}\''
    try:
        with DB.cursor() as cursor:
            cursor.execute(delete_income)
            cursor.execute(update_balance)
            DB.commit()
        update_tables()
        update_balances()
    except:
        print('Ошибка при удалении дохода')

def delete_expense():
    row = ui.tableWidget_2.currentIndex().row()
    expense_id = ui.tableWidget_2.model().index(row,0).data()
    balance_name = ui.tableWidget_2.model().index(row, 5).data()
    expense_amount = ui.tableWidget_2.model().index(row, 2).data()
    expense_amount = str(expense_amount)
    expense_amount = float(expense_amount)
    print('++++++++++++++++++++++++++++')
    print(balance_name)
    print('++++++++++++++++++++++++++')
    select_get_balance = f'SELECT "Balance_amount" FROM "Balance" WHERE "Balance_name" = \'{balance_name}\''
    try:
        with DB.cursor() as cursor:
            cursor.execute(select_get_balance)
            expense_balance = cursor.fetchall()
            DB.commit()
            balance_amount = str(expense_balance[0][0]).strip("(),'\"")
            balance_amount = int(balance_amount)
    except:
        print('Ошибка получения баланса при удалении')
    balance_plus = balance_amount + expense_amount
    update_balance = f'UPDATE "Balance" SET "Balance_amount" = {balance_plus} WHERE "Balance_name" = \'{balance_name}\''
    delete_expense = f'DELETE FROM "Expenses" WHERE "Expenses_ID" = {expense_id}'
    try:
        with DB.cursor() as cursor:
            cursor.execute(delete_expense)
            cursor.execute(update_balance)
            DB.commit()
        update_tables()
        update_balances()
    except:
        print('Ошибка при удалении расхода')

get_all_balance()
show_balances()
show_incomes()
show_expenses()
show_categories()

ui.pushButton_10.clicked.connect(listwidget_balance_delete)
ui.pushButton_9.clicked.connect(listwidget_categories_delete)
ui.pushButton.clicked.connect(new_balance_window)
ui.pushButton_4.clicked.connect(new_categories_window)
ui.pushButton_3.clicked.connect(new_expens_window)
ui.pushButton_2.clicked.connect(new_income_window)
ui.pushButton_6.clicked.connect(delete_income)
ui.pushButton_8.clicked.connect(delete_expense)

sys.exit(app.exec_())