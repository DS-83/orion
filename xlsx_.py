import xlsxwriter
from flask import g, current_app
from datetime import datetime

def SaveReport(date_start, date_end, data):
    filename = f"{current_app.config['DWNLD_FOLDER']}/{str(g.user['username'])}_{date_end}_{date_start}.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss', 'align': 'left'})

    for row in range(len(data)):
        for col in range(len(data[row])):
            if row != 0 and col == 7:
                print(data[row][col])
                worksheet.write_datetime(row, col, data[row][col], date_format)
            else:
                worksheet.write(row, col, data[row][col])
    workbook.close()
    return f"{str(g.user['username'])}_{date_end}_{date_start}.xlsx"
