import xlsxwriter
# from flask import url_for
from app.reports_sql import OrionReportAccessPoint, UnpackData

def SaveReport():
    workbook = xlsxwriter.Workbook('xlsx/report.xlsx')
    worksheet = workbook.add_worksheet()

    s = '20181022135500'
    e = '20181022135700'
    report = UnpackData(OrionReportAccessPoint(s, e))
    for row in range(len(report)):
        for col in range(len(report[row])):
            worksheet.write(row, col, report[row][col])
    workbook.close()
    return 'Saved'
