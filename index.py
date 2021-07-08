import plotly
import xlrd
import plotly.graph_objs as go


class tbData:
    rows = []

    def readData(self):
        book = xlrd.open_workbook(self.fileName)
        sheet1 = book.sheets()[0]
        sheet1_name = sheet1.name
        sheet1_cols = sheet1.ncols
        sheet1_nrows = sheet1.nrows
        for i in range(sheet1_nrows):  # 逐行打印sheet1数据
            print(sheet1.row_values(i))

    def __init__(self, fileName):
        self.fileName = fileName


c = tbData('tb.xls')
c.readData()

plotly.offline.plot({
    "data": [go.Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
    "layout": go.Layout(title="hello world")
}, auto_open=True)
