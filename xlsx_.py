import xlsxwriter
from flask import g, current_app
from datetime import datetime
import os
from app.reports_sql import dt

def SaveReport(date_start, date_end, data, report_name):
    if g:
        filename = f"{current_app.config['DWNLD_FOLDER']}/{str(g.user['username'])}_{date_start}_{date_end}.xlsx"
    else:
        filename = f"{os.path.join('./instance', 'xlsx')}/{str(report_name)}_{date_start}_{date_end}.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    # Protect worksheet
    worksheet.protect()

    # Sheet heading
    # Merge format
    merge_format = workbook.add_format({'align': 'left', 'bold': True, 'font_size': 12})

    if isinstance(date_start, str):
        heading = f"Report name: {report_name}\nTime range: from: {dt(date_start)} to: {dt(date_end)}"
    else:
        heading = f"Report name: {report_name}\nTime range: from: {date_start} to: {date_end}"

    worksheet.merge_range(1, 4, 2, 8, heading, merge_format)

    # Insert logo
    # Merge format
    merge_format = workbook.add_format({'align': 'center'})
    if g:
        im_path = os.path.join(current_app.static_folder, 'logo.png')
    else:
        im_path = os.path.join('./app/static', 'logo.png')
    image = worksheet.insert_image(0, 0, im_path,
                            {'x_scale': 0.6, 'y_scale': 0.6,}
                            )
    worksheet.merge_range(0, 0, 5, 1, image, merge_format)

    # Keep track columns width
    col_width = list(range(len(data[0])))

    indent = 6
    old = None
    # Find time column
    time_col = [data[0].index(x) for x in data[0] if x == 'Time']

    # Write data
    for row in range(indent, len(data) + indent):

        # Head format
        if row == indent:
            cell_format = workbook.add_format({'bold': True, 'font_size': 11,
                            'border': True, 'align': 'center', 'bg_color': '#3b3a30',
                            'font_color': 'white'})
        # Highlight every new record in first column
        elif data[row - indent][0] != old:
            cell_format = workbook.add_format({'top': True,
                          'bg_color': '#b2b2b2', 'bold': True,
                          'align': 'left'})
            cell_format_t = workbook.add_format({'top': True,
                          'num_format': 'DD-MM-YYYY HH:MM:SS',
                          'bg_color': '#b2b2b2', 'bold': True,
                          'align': 'left'})

            old = data[row - indent][0]
        # cell
        else:
            cell_format = workbook.add_format({
                            'align': 'left', 'right': True,
                            'left': True, 'bg_color': '#e0e2e4'})
            cell_format_t = workbook.add_format({
                            'align': 'left', 'right': True,
                            'num_format': 'DD-MM-YYYY HH:MM:SS',
                            'left': True, 'bg_color': '#e0e2e4'})

        for col in range(len(data[row - indent])):
            if col_width[col] < len(str(data[row - indent][col])):
                col_width[col] = len(str(data[row - indent][col]))

            if col == time_col[0] and row > indent:
                worksheet.write(row, col, data[row - indent][col], cell_format_t)
            else:
                worksheet.write(row, col, data[row - indent][col], cell_format)

    # Set columns width
    for col in range(len(col_width)):
        worksheet.set_column(col, col, col_width[col])



    workbook.close()

    if g:
        return f"{str(g.user['username'])}_{date_start}_{date_end}.xlsx"
    else:
        return filename
