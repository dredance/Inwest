import datetime as dt

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




