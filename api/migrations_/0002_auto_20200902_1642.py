# Generated by Django 3.1 on 2020-09-02 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='nagazowanie_koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Nagazowanie zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='nagazowanie_start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Nagazowanie rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='ok_real',
            field=models.DateField(blank=True, null=True, verbose_name='Odbiór Końcowy Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='ot_real',
            field=models.DateField(blank=True, null=True, verbose_name='Odbiór Techniczny Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='pnu_real',
            field=models.DateField(blank=True, null=True, verbose_name='Pozwolenie na użytkowanie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='proba_real',
            field=models.DateField(blank=True, null=True, verbose_name='Próba szczelności Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='rozruch_real',
            field=models.DateField(blank=True, null=True, verbose_name='Rozruch Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='sl_koniec_baza',
            field=models.DateField(blank=True, null=True, verbose_name='Spawanie Liniowe zakończenie Harm. Bazowy'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='sl_start_baza',
            field=models.DateField(blank=True, null=True, verbose_name='Spawanie Liniowe rozpoczęcie Harm. Bazowy'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='sm_koniec_baza',
            field=models.DateField(blank=True, null=True, verbose_name='Spawanie Montaż zakończenie Harm. Bazowy'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='sm_start_baza',
            field=models.DateField(blank=True, null=True, verbose_name='Spawanie Montaż rozpoczęcie Harm. Bazowy'),
        ),
        migrations.AlterField(
            model_name='kamieniemilowe',
            name='umowa_wrb_real',
            field=models.DateField(blank=True, null=True, verbose_name='Umowa WRB Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='mb',
            name='firma',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='mb',
            name='koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='mb',
            name='nazwa',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nazwa przejścia'),
        ),
        migrations.AlterField(
            model_name='mb',
            name='rodzaj',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='Rodzaj metody'),
        ),
        migrations.AlterField(
            model_name='mb',
            name='start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='cal_koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Calostyki zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='cal_start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Calostyki rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='firma',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='oto_real',
            field=models.DateField(blank=True, null=True, verbose_name='Odbiór Techniczny Obiektu Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='proba_real',
            field=models.DateField(blank=True, null=True, verbose_name='Próba szczelności Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='sm_start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Spawanie Montaż rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='spgw_real',
            field=models.DateField(blank=True, null=True, verbose_name='Spoiny Gwarantowane Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='umowa_real',
            field=models.DateField(blank=True, null=True, verbose_name='Umowa o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='ob',
            name='wniosek_real',
            field=models.DateField(blank=True, null=True, verbose_name='Wnioski o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='dlugosc',
            field=models.IntegerField(blank=True, null=True, verbose_name='Długość gazociągu [mb]'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='dlugosc_rur',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Długości rur [mb]'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='kierownik_gs',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Kierownik Projektu'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='odcinki',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ilość odcinków próbnych'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='srednica',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Średnica gazociągu [mm]'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='wni',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Wykonawca Nadzoru Inwestorskiego'),
        ),
        migrations.AlterField(
            model_name='projekt',
            name='wrb',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Wykonawca Robót Budowlanych'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='firma',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='sily_wlasne',
            field=models.BooleanField(blank=True, max_length=6, null=True, verbose_name='Siły własne'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='umowa_real',
            field=models.DateField(blank=True, null=True, verbose_name='Umowa o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sl',
            name='wniosek_real',
            field=models.DateField(blank=True, null=True, verbose_name='Wnioski o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='firma',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='sily_wlasne',
            field=models.BooleanField(blank=True, max_length=6, null=True, verbose_name='Siły własne'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Rozpoczęcie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='umowa_real',
            field=models.DateField(blank=True, null=True, verbose_name='Umowa o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='sm',
            name='wniosek_real',
            field=models.DateField(blank=True, null=True, verbose_name='Wnioski o podwykonawcę Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='uk',
            name='firma',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Firma'),
        ),
        migrations.AlterField(
            model_name='uk',
            name='koniec_real',
            field=models.DateField(blank=True, null=True, verbose_name='Zakończenie Rzeczywiste'),
        ),
        migrations.AlterField(
            model_name='uk',
            name='start_real',
            field=models.DateField(blank=True, null=True, verbose_name='Rozpoczęcie Rzeczywiste'),
        ),
    ]
