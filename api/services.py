from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.dates import DateFormatter, MonthLocator
import datetime as dt
import pandas as pd
from django.db.models import Max, Min


class ServiceChart:
    @staticmethod
    def create_date(date):
        """Creates the date"""
        try:
            year, month, day = date.split('-')
            date = dt.datetime(int(year), int(month), int(day))
        except:
            pass
        finally:
            mdate = matplotlib.dates.date2num(date)
        return mdate

    @staticmethod
    def get_image():
        # create a bytes buffer for the image to save
        buffer = BytesIO()
        # create the plot with the use of BytesIO object as its 'file'
        plt.savefig(buffer, format='png')
        # set the cursor the begining of the stream
        buffer.seek(0)
        # retreive the entire content of the 'file'
        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png)
        graph = graph.decode('utf-8')
        # free the memory of the buffer
        buffer.close()
        return graph


class Service:
    @staticmethod
    def to_date(str_date):
        if type(str_date) != str:
            return str_date
        else:
            return dt.date(int(str_date[:4]), int(str_date[5:7]), int(str_date[8:10]))

    #### Funkcja wypełniająca puste elementy + convert
    @staticmethod
    def fill_none(df, list_col, wartosc=0, typ=int):
        for x in list_col:
            df[x].fillna(value=wartosc, inplace=True)
            df[x] = df.apply(lambda row: typ(row[x]) if type(row[x]) != typ else row[x], axis=1)
            if typ != int: df[x] = df[x].astype(typ)

    @staticmethod
    def to_str(date):
        return dt.datetime.strftime(date, '%Y-%m-%d')




