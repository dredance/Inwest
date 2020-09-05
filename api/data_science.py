# WTYCZKA DO ODPALANIA W SPYDERZE
if __name__ == "__main__":
    import os, sys
    import django
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inwest.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()

from api.models import KamienieMilowe, SL, SM, MB, OB, UK
import pandas as pd
import datetime as dt
from api.services import Service
from django.db.models import Max, Min, Sum
from sqlalchemy import create_engine
from Inwest.settings import DATABASES


DAYS_IN_MONTH = 21


class RobotyPodstawowe:
    def __init__(self, model):
        self.model = model

    @property
    def df_teams(self):
        slm_df = pd.DataFrame(self.model.objects.all().values())
        return slm_df

    @property
    def df_group(self):
        slm_df = pd.DataFrame(self.model.objects.all().values('okres', 'projekt_id').annotate(
            ilosc=Sum('ilosc'), wykonanie_okres=Sum('wykonanie_okres'),
            wykonanie_all=Sum('wykonanie_all'),
            start_plan=Min('start_plan'), start_real=Min('start_real'),
            koniec_plan=Max('koniec_plan'), koniec_real=Max('koniec_real')))
        return slm_df

    def result(self, df_choice):
        # Wybór w podziale zespoły lub całej grupy robót
        if df_choice == 'df_group':
            df = self.df_group
        else:
            df = self.df_teams

        # Wypełenie pusych pól dla column wykonania
        Service.fill_none(df=df, list_col=['wykonanie_okres', 'wykonanie_all'])
        # Wykonanie nie moze przekroczyć ilosci
        df['ilosc'] = df.apply(
            lambda row: row['wykonanie_all'] if row['ilosc'] < row['wykonanie_all']
                                             else row['ilosc'], axis=1)
        # Obliczenie procentów Wykonania dla Okresu i Narastająco
        df['proc_okres'] = round(df['wykonanie_okres'] / df['ilosc'], 3)
        df[f'proc_all'] = round(df['wykonanie_all'] / df['ilosc'], 3)
        # Obliczenie srednie wykonanie w okresie miesiac_dni_robocze=21
        df['sr_wykonanie_okres'] = round(df['wykonanie_okres'] / DAYS_IN_MONTH, 1)
        # Obliczenie srednie wykonanie w okresie od początku spawania do dniaRaportu/koniec jak 1
        data_start = df.apply(
            lambda row: row['start_plan'] if row['start_real'] == None
                                          else row['start_real'], axis=1)
        data_koniec = df.apply(
            lambda row: row['koniec_real'] if row['koniec_real'] != None else row['okres'], axis=1)
        ilosc_dni = data_koniec - data_start
        ilosc_dni = ilosc_dni.apply(lambda row: row.days * 0.75)
        df['sr_wykonanie_all'] = round(df['wykonanie_all'] / ilosc_dni, 1)
        df['sr_wykonanie_all'] = df.apply(
            lambda row: 0 if row['sr_wykonanie_all'] <= 0 else row['sr_wykonanie_all'], axis=1)

        # Obliczenie wymaganego wykonania w następnych miesiącach w okresie aby spełnić KoniecPlan
        # po miesący dajemy tylko 5 dni na poprawe
        df['wym_wykonanie_okres'] = df.apply(
            lambda row: round((row['ilosc'] - row['wykonanie_all']) / max((row['koniec_plan']
                                - row['okres']).days, 5), 1), axis=1)
        # Różnica: ||-bufor||0||+opóźnienie||   max_opóxnienie = 180 dni ||| 0,1 x 21 =2,1 sp/mc
          # | Roznica = max(Dniwydajnosci-(KoniecPlan-Okres),180)
        df['roznica_dni'] = df.apply(
            lambda row: min(round((row['ilosc'] - row['wykonanie_all']) / max(row['sr_wykonanie_okres'], 0.1))
                            - (row['koniec_plan'] - row['okres']).days, 180)
                            if row['okres'] > (row['start_plan'] + dt.timedelta(days=31))  # miesiąc czasu na rozruch
                            else 0, axis=1)
        # jesli już wykonują to różnica 0
        warunek = df['ilosc'] == df['wykonanie_all']
        df.loc[warunek, 'roznica_dni'] = 0
        # Obliczenie daty przy srednim wykonaniu w okresie
        df['koniec_prognoza'] = df.apply(
            lambda row: row['koniec_plan'] + dt.timedelta(row['roznica_dni']), axis=1)
        ### Obliczenie Opisu
        jm = 'mb' if self.model == UK else 'sp'
        df['opis'] = df.apply(
            lambda row: f" Średnie wykonanie: {row['sr_wykonanie_all']} {jm}/dn"
                        if row[f'proc_all'] == 1
                        else f" {row['sr_wykonanie_okres']} {jm}/dn$\longrightarrow${row['wym_wykonanie_okres']} {jm}/dn"
                             f"\n {row['koniec_plan']}$\longrightarrow${row['koniec_prognoza']}" if row['roznica_dni'] > 0
                        else f" {row['sr_wykonanie_okres']} {jm}/dn | {row['wym_wykonanie_okres']} {jm}/dn"
                             f"\n bufor: {abs(row['roznica_dni'])} dn", axis=1)
        return df


class Obiekty:
    def __init__(self, model):
        self.model = model

    def proc_ob_item(self, df):
        wykonanie_procent = df.apply(
            lambda row: 0 if row['wykonanie_all'] == None
                          else row['wykonanie_all'] / row['ilosc'] * 0.85, axis=1)
        for kol in ['proba_real', 'spgw_real', 'oto_real']:
            wykonanie_procent += df.apply(lambda row: 0 if row[kol] == None
                                                        else 0.05, axis=1)
        return wykonanie_procent

    def opoznienie_dni(self, df):
        okres = df['okres']
        cal_start = df['cal_start_plan']
        cal_koniec = df['cal_koniec_plan']
        proc = min(1, df['wykonanie_all'] / df['ilosc'])
        opoznienie_lista = [0 if df[f'{skrot}_real'] else (okres - df[f'{skrot}_plan']).days
                            for skrot in ['oto', 'spgw', 'proba']]
        opoznienie_lista.append(0)
        cal_ilosc_dni = (cal_koniec - cal_start).days
        postep = cal_ilosc_dni * proc
        pozostalo = cal_ilosc_dni - postep
        opoznienie_lista.append(
            pozostalo if okres >= cal_koniec else (okres - (cal_start + dt.timedelta(days=postep))).days * 0.7)
        return max(opoznienie_lista)

    @property
    def result_df_ob(self):
        ### Stworzenie dataframe z zapytania sql
        df_ob = pd.DataFrame(self.model.objects.all().values())
        ### Wypełenie pusych pól dla column wykonania
        Service.fill_none(df=df_ob, list_col=['wykonanie_okres', 'wykonanie_all'])
        ### Obliczenie procentów Wykonania Narastająco dla poszczególnych obiektów
        df_ob['proc_all'] = round(self.proc_ob_item(df_ob), 3)
        ### Opóżnienie w dniach
        df_ob['opoznienie'] = df_ob.apply(lambda row: self.opoznienie_dni(row), axis=1)
        # Data prognozowana
        for skrot in ['cal_koniec', 'proba', 'spgw', 'oto']:
            df_ob[f'{skrot}_prognoza'] = df_ob.apply(
                lambda row: row[f'{skrot}_real'] if row[f'{skrot}_real']
                else row[f'{skrot}_plan'] + dt.timedelta(days=row['opoznienie']), axis=1)
        ### Dodanie do item obiektów kol: Wyswietlanie
        df_ob['wyswietlanie'] = df_ob.apply(lambda row: "{} {:.1%}".format(row['nazwa'], row['proc_all']), axis=1)
        return df_ob

    @property
    def result_df_ob_gr(self):
        df_group = self.result_df_ob.groupby(['projekt_id', 'okres'])
        
        ### Obliczenie dla obiektów ogólne w projekcie
        df_ob_gr = pd.DataFrame({'obiekty_liczba': df_group['projekt_id'].count(),
                                 'obiekty_liczba_opoznien': df_group['opoznienie'].apply(lambda x: x[x>0].count()),
                                 'start_plan': df_group['cal_start_plan'].min(),
                                 'koniec_plan': df_group['oto_plan'].max(), 'koniec_prognoza': df_group['oto_prognoza'].max(),
                                 'ilosc': df_group['ilosc'].sum(), 'wykonanie_all': df_group['wykonanie_all'].sum(),
                                 'proc_all': round(df_group['proc_all'].mean(), 3)}).reset_index()
        df_ob_gr['roznica'] = df_ob_gr.apply(lambda row: (row['koniec_prognoza']-row['koniec_plan']).days, axis=1)
        df_ob_gr['opis'] = df_ob_gr.apply(lambda row: f"Opóźnione {row['obiekty_liczba_opoznien']} z {row['obiekty_liczba']} obiektów"
                                                if row['roznica']>0 else "Zgodnie z planem",axis=1)
        df_ob_gr['okres'] = df_ob_gr['okres'].dt.date
        df_ob_gr.drop_duplicates(inplace=True)
        return df_ob_gr

class MetodyBezwykopowe:
    DATABASES_DEFAULT = DATABASES['default']
    ENGINE = create_engine(f'postgresql://{DATABASES_DEFAULT["USER"]}:{DATABASES_DEFAULT["PASSWORD"]}@localhost:5432/{DATABASES_DEFAULT["NAME"]}',
                           encoding="ISO-8859-2")

    def __init__(self, model):
        self.model = model

    @property
    def zakonczone_projekty(self):
        dane = self.model.objects.raw('SELECT max(id) AS id, max(okres) AS okres, projekt_id FROM api_mb GROUP BY projekt_id')
        dict = {}
        for i in dane:
            okres_str = dt.datetime.strftime(i.okres, '%Y-%m-%d')
            if okres_str in dict:
                list = dict.get(okres_str)
                list.append(i.projekt_id)
                dict[okres_str] = list
            else:
                dict[okres_str] = [i.projekt_id]
        dict = {key:tuple(value) for key, value in dict.items() if key != dt.datetime.strftime(self.data_stop, '%Y-%m-%d')}
        return dict

    def last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + dt.timedelta(days=4)
        return next_month - dt.timedelta(days=next_month.day)

    def range_ends_days(self, data_start, data_stop):
        rok = [rok for rok in range(data_start.year, data_stop.year + 1)]
        okres_list = []
        for r in rok:
            for m in list(range(1, 13)):
                end_day = self.last_day_of_month(any_day=dt.date(r, m, 1))
                if end_day <= data_stop and end_day >= data_start:
                    okres_list.append(dt.datetime.strftime(end_day, '%Y-%m-%d'))
        return okres_list

    @property
    def data_start(self):
        df_dane = pd.read_sql('SELECT min(okres) okres FROM api_mb', con=MetodyBezwykopowe.ENGINE)
        okres = min(df_dane['okres'])
        return okres

    @property
    def data_stop(self):
        df_dane = pd.read_sql('SELECT max(okres) okres FROM api_mb', con=MetodyBezwykopowe.ENGINE)
        okres = max(df_dane['okres'])
        return okres

    @property
    def warunki(self):
        
        if not self.zakonczone_projekty: warunek = f"NOT (projekt_id = 00001 AND okres > '2000-01-01')"
        i = 0
        for key, value in self.zakonczone_projekty.items():
            if i == 0 and len(value) == 1:
                warunek = f"NOT (projekt_id = {value[0]} AND okres > '{key}')"
            elif i == 0:
                warunek = f"NOT (projekt_id IN {value} AND okres > '{key}')"
            elif len(value) == 1:
                warunek += f" AND NOT (projekt_id = {value[0]} AND okres > '{key}')"
            elif isinstance(value, tuple):
                warunek += f" AND NOT (projekt_id IN {value} AND okres > '{key}')"
            else:
                warunek += f" AND NOT (projekt_id = {value} AND okres > '{key}')"
            i += 1
        return warunek


    def sql_dfmbi(self, okres):
        last_proj_okres= '''SELECT * FROM api_mb JOIN (SELECT max(okres) AS okres, projekt_id FROM api_mb
        GROUP BY projekt_id) as max_okres USING(projekt_id, okres)'''
        
        q_mb_ilosc = f'''SELECT projekt_id, max(okres), '{okres}' AS okres, Count(*) ilosc, sum(dlugosc) ilosc_mb, 
        min(start_plan) start_plan, min(start_real) start_real, max(koniec_plan) koniec_plan, max(koniec_real) koniec_real
        FROM ({last_proj_okres}) AS last_proj_okres
        GROUP BY projekt_id, okres
        '''
        q_mb_zak = f'''SELECT projekt_id, max(okres), '{okres}' AS okres, Count(*) ilosc_zak, sum(dlugosc) ilosc_mb_zak
        FROM ({last_proj_okres}) AS last_proj_okres
        WHERE koniec_real IS NOT NULL AND koniec_real <= '{okres}'
        GROUP BY projekt_id, okres
        '''
        q_mb_rozp = f'''SELECT projekt_id, max(okres),'{okres}' AS okres, Count(*) ilosc_rozp, sum(dlugosc) ilosc_mb_rozp
        FROM ({last_proj_okres}) AS last_proj_okres
        WHERE start_real IS NOT NULL AND koniec_real IS NULL AND start_real <='{okres}'
        GROUP BY projekt_id, okres
        '''
        q_mb_plan = f'''SELECT projekt_id, max(okres), '{okres}' AS okres, Count(*) ilosc_plan, sum(dlugosc) ilosc_mb_plan
        FROM ({last_proj_okres}) AS last_proj_okres
        WHERE koniec_plan <'{okres}'
        GROUP BY projekt_id, okres
        '''
        q_mb = f'''SELECT projekt_id, okres, min(start_plan) start_plan,min(start_real) start_real, 
        max(koniec_plan) koniec_plan,max(koniec_real) koniec_real,sum(ilosc) ilosc,
        sum(ilosc_zak) ilosc_zak,sum(ilosc_rozp) ilosc_rozp, sum(ilosc_plan) ilosc_plan,
        sum(ilosc_mb) ilosc_mb, sum(ilosc_mb_zak) ilosc_mb_zak, sum(ilosc_mb_rozp) ilosc_mb_rozp,
        sum(ilosc_mb_plan) ilosc_mb_plan, round((1.0*sum(ilosc_mb_zak))/(1.0*sum(ilosc_mb)),3) proc_all
        FROM ({q_mb_ilosc}) AS q_ilosc
        LEFT JOIN ({q_mb_zak}) AS q_zak
        USING(projekt_id, okres)
        LEFT JOIN ({q_mb_rozp}) AS q_rozp
        USING(projekt_id, okres)
        LEFT JOIN ({q_mb_plan}) AS q_plan
        USING(projekt_id, okres)
        WHERE {self.warunki}
        GROUP BY projekt_id, okres
        '''
        return pd.read_sql(q_mb, con=MetodyBezwykopowe.ENGINE)

    @property
    def lista_df_mbf(self):
        SQL_TAB = ["api_mb"]
        okres_list = self.range_ends_days(self.data_start, self.data_stop)
        lista_df_mb = [self.sql_dfmbi(okres) for okres in okres_list]
        return lista_df_mb

    @property
    def result(self):
        pol_tabele = pd.concat(self.lista_df_mbf)
        pol_tabele.fillna(value=0, inplace=True)
        pol_tabele['pozostale'] = pol_tabele['ilosc'] - pol_tabele['ilosc_zak'] - pol_tabele['ilosc_rozp']
        pol_tabele['roznica_exp'] = pol_tabele.apply(lambda row: round(0.4*(row['ilosc_mb_plan']-row['ilosc_mb_zak'])/row['ilosc_mb'], 4)
                                                        if row['ilosc_mb_plan']>row['ilosc_mb_zak'] else 0, axis=1)
        pol_tabele['roznica_dni'] = pol_tabele.apply(lambda row: round(row['roznica_exp'] * (row['koniec_plan'] - row['start_plan']).days), axis=1)
        pol_tabele['koniec_prognoza'] = pol_tabele.apply(lambda row: row['koniec_plan'] + dt.timedelta(days=row['roznica_dni']), axis=1)
        pol_tabele['opis'] = pol_tabele.apply(lambda row:f"Opóźnione: {int(row['ilosc_plan']-row['ilosc_zak'])} szt. metod"
                                                        if row['ilosc_plan'] > row['ilosc_zak'] else 'Zgodnie z bazą', axis=1)
        pol_tabele['okres'] = pd.to_datetime(pol_tabele['okres']).dt.date
        return pol_tabele


class Analiza:
    MIN_WARUNKI_KM = {'sl-sm': 1, 'sl-ot': 3, 'sm-ot': 1.2, 'uk-ot': 1, 
                       'mb-ot': 1.2, 'ob-ot': 0.1, 'ot-ok': 3,'ot-proba': -1,
                       'ot-rozruch': 0.15, 'ok-pnu': -0.4}
    
    def __init__(self, model, df_sl_gr, df_sm_gr, df_uk_gr, df_mb_gr, df_ob_gr):
        self.model = model
        self.df_sl_gr = df_sl_gr
        self.df_sm_gr = df_sm_gr
        self.df_uk_gr = df_uk_gr
        self.df_mb_gr = df_mb_gr
        self.df_ob_gr = df_ob_gr

    ### PROCENT WYKONANIA RZECZOWEGO PROJEKTU
    def procent(self, df):
        wyk_proc = 0
        wyk_proc = df.apply(lambda row: (row['proc_all_mb'] * 0.20 + row['proc_all_ob'] * 0.20
                                         + row['proc_all_uk'] * 0.10 + row['proc_all_sl'] * 0.25
                                         + row['proc_all_sm'] * 0.25) * 0.8, axis=1)
        for kol in ['ot_real', 'rozruch_real', 'pnu_real', 'ok_real']:
            wyk_proc += df.apply(lambda row: 0 if row[kol] == None else 0.05, axis=1)
        return round(wyk_proc, 3)

    @property
    def result(self):
        ### DOŁĄCZENIE KOLUMNY Z FAZĄ PROJEKTU
        df_dane = pd.DataFrame(self.model.objects.all().values())
        df_dane['faza'] = df_dane.apply(lambda row: "Eksploatacja" if row['ok_real'] else "Realizacja", axis=1)
        skroty = ['sl', 'sm', 'uk', 'mb', 'ob']
        #### 2.3.8 DOŁĄCZENIE DO DANYCH OGÓLNYCH DANE Z SL SM UK MB OB
        df_dane['proc_all'] = ''
        df_dane['koniec_prognoza'] = ''
        for prace, kol in zip([self.df_sl_gr, self.df_sm_gr, self.df_uk_gr, self.df_mb_gr, self.df_ob_gr], skroty):
            df_dane = pd.merge(df_dane, prace.loc[:, ['projekt_id', 'okres', 'proc_all', 'koniec_prognoza']], how='left',
                               on=['projekt_id', 'okres'], suffixes=('', f'_{kol}'))
        df_dane.drop(columns='proc_all', inplace=True)
        ### 2.4 OBLICZENIE PROCENTU ZAAWASOWANIA DANE
        df_dane['procent'] = self.procent(df_dane)
        # Obliczenie prognozowanych dat projektu
        df_dane['koniec_prognoza_sm'] = df_dane.apply(
            lambda row: max(row['koniec_prognoza_sl']+dt.timedelta(days=30*Analiza.MIN_WARUNKI_KM.get('sl-sm',0)),
                                                                      row['koniec_prognoza_sm']), axis=1)
        df_dane['ot_prognoza'] = df_dane.apply(
            lambda row: max([row[f'koniec_prognoza_{i}']+dt.timedelta(days=round(30*Analiza.MIN_WARUNKI_KM.get(f'{i}-ot',0),0))
                                                                for i in skroty]+[row['ot_plan']]), axis=1)
        df_dane['ok_prognoza'] = df_dane.apply(
            lambda row: max(row['ot_prognoza']+dt.timedelta(days=30*Analiza.MIN_WARUNKI_KM.get('ot-ok',0)),
                                                                      row['ok_plan']), axis=1)
        df_dane['proba_prognoza'] = df_dane.apply(
            lambda row: max(row['ot_prognoza']+dt.timedelta(days=30*Analiza.MIN_WARUNKI_KM.get('ot-proba',0)),
                                                                      row['proba_plan']), axis=1)
        df_dane['rozruch_prognoza'] = df_dane.apply(
            lambda row: max(row['ot_prognoza']+dt.timedelta(days=30*Analiza.MIN_WARUNKI_KM.get('ot-rozruch',0)),
                                                                      row['rozruch_plan']), axis=1)
        df_dane['pnu_prognoza'] = df_dane.apply(
            lambda row: max(row['ok_prognoza']+dt.timedelta(days=30*Analiza.MIN_WARUNKI_KM.get('ok-pnu',0)),
                                                                      row['pnu_plan']), axis=1)
        ### ZWROCENIE DATAFRAME
        return df_dane



try:
    sl_df = RobotyPodstawowe(SL).result('df_group')
except:
    sl_df = pd.DataFrame({'Test': []})

try:
    sm_df = RobotyPodstawowe(SM).result('df_group')
except:
    sm_df = pd.DataFrame({'Test': []})

try:
    uk_df = RobotyPodstawowe(UK).result('df_group')
except:
    uk_df = pd.DataFrame({'Test': []})

try:
    ob_df = Obiekty(OB).result_df_ob
except:
    ob_df = pd.DataFrame({'Test': []})

try:
    ob_df_gr = Obiekty(OB).result_df_ob_gr
except:
    ob_df_gr = pd.DataFrame({'Test': []})

try:
    mb_df = MetodyBezwykopowe(MB).result
except:
    mb_df = pd.DataFrame({'Test': []})

try:
    analiza_df = Analiza(KamienieMilowe, sl_df,sm_df,uk_df,mb_df,ob_df_gr).result
except:
    analiza_df = pd.DataFrame({'Test': []})
