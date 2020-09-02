from django.contrib.auth.models import User
from rest_framework import viewsets, views
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from rest_framework.response import Response
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import datetime, timedelta
import pandas as pd
from .serializers import UserSerializer
from .models import Projekt, KamienieMilowe, MB, SL, SM, UK, OB
from .data_science import sl_df, sm_df, uk_df, mb_df, ob_df_gr, ob_df, analiza_df
from .forms import KamienieMiloweForm, SlFormSet, SmFormSet, UkFormSet, OBFormSet, MBFormSet, \
                   NewDataForm, UpdateDataForm, NewSlFormSet, NewSmFormSet, NewUkFormSet, NewOBFormSet, NewMBFormSet


class UserViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    permission_required = 'api.view_user'
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class OkresyView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        psp = self.request.query_params.get('psp')
        if psp:
            df = pd.DataFrame(KamienieMilowe.objects.filter(projekt_id=psp).values('projekt_id', 'okres'))
        else:
            df = pd.DataFrame(KamienieMilowe.objects.all().values('projekt_id', 'okres'))

        if df.empty:
            return Response([{'psp':psp, 'okresy': None}])

        df_group = df.groupby('projekt_id')
        result = []
        for i in df_group:
            result.append({'psp': i[0],
                           'okresy': i[1]['okres'].sort_values(ascending=False).tolist()})
        return Response(result)


class ObiektyView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_ob = ob_df.to_dict('records')
        return Response(dict_ob)


class AnalizaProjektuView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        df = analiza_df.where(pd.notnull(analiza_df), None)
        dict_km = df.to_dict('records')
        return Response(dict_km)


class SpawanieLinioweView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_sl = sl_df.to_dict('records')
        return Response(dict_sl)


class SpawanieMontazoweView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_sm = sm_df.to_dict('records')
        return Response(dict_sm)


class UkladkaView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_uk = uk_df.to_dict('records')
        return Response(dict_uk)


class MetodyBezwykopoweView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_mb = mb_df.to_dict('records')
        return Response(dict_mb)


class ObiektyGrupaView(LoginRequiredMixin, views.APIView):
    login_url = reverse_lazy('login')
    def get(self, request):
        dict_ob = ob_df_gr.to_dict('records')
        return Response(dict_ob)


class ManagerDataView(PermissionRequiredMixin, View):
    permission_required = 'api.add_km'

    def get(self, request):
        ctx = {'new_form': NewDataForm(initial={'download_data': True}, prefix='insert_form'),
             'update_form': UpdateDataForm(prefix='update_form'),
             'projects': Projekt.objects.all()}
        return render(request, 'manager_data.html', ctx)

    def post(self, request):
        if 'updateBtn' in request.POST:
            form_update = UpdateDataForm(request.POST, prefix='update_form')
            if form_update.is_valid():
                psp = form_update.cleaned_data['projekt']
                okres = form_update.cleaned_data['okres']
                return redirect('multiform-update', psp=psp.id, okres=okres.strftime('%Y-%m-%d'))
        elif 'deleteBtn' in request.POST:
            form_delete = UpdateDataForm(request.POST, prefix='update_form')
            if form_delete.is_valid():
                psp = form_delete.cleaned_data['projekt']
                okres = form_delete.cleaned_data['okres']
                for model in [KamienieMilowe, SL, SM, UK, OB, MB]:
                    model.objects.filter(okres=okres, projekt=psp).delete()
                messages.success(request, 'Usunięto poprawnie formularz.')
                return redirect('manager-data')
        elif 'insertBtn' in request.POST:
            form_insert = NewDataForm(request.POST, prefix='insert_form')
            if form_insert.is_valid():
                psp = form_insert.cleaned_data['projekt']
                okres = form_insert.cleaned_data['okres']
                download_data = form_insert.cleaned_data['download_data']
                return redirect('multiform-create', psp=psp.id, okres=okres.strftime('%Y-%m-%d'), prev_data=download_data)
        ctx = {'new_form': NewDataForm(request.POST, prefix='insert_form'),
                'update_form': UpdateDataForm(request.POST, prefix='update_form'),
                'projects': Projekt.objects.all()}
        return render(request, 'manager_data.html', ctx)


class CreateMultiFormView(PermissionRequiredMixin, View):
    permission_required = 'api.add_km'
    def get(self, request, psp, okres, prev_data):
        okres = datetime.strptime(okres, '%Y-%m-%d')
        if prev_data == 'True':
            prev_okres = okres.replace(day=1) - timedelta(days=1)
            ctx = {'okres': okres, 'psp':psp, 'new_okres': True}
            ctx['km_form'] = KamienieMiloweForm(initial=KamienieMilowe.objects.filter(projekt_id=psp, okres=prev_okres).values()[0])
            ctx['sl_form'] = SlFormSet(queryset=SL.objects.filter(projekt_id=psp, okres=prev_okres), prefix='sl_form')
            ctx['sm_form'] = SmFormSet(queryset=SM.objects.filter(projekt_id=psp, okres=prev_okres), prefix='sm_form')
            ctx['uk_form'] = UkFormSet(queryset=UK.objects.filter(projekt_id=psp, okres=prev_okres), prefix='uk_form')
            ctx['ob_form'] = OBFormSet(queryset=OB.objects.filter(projekt_id=psp, okres=prev_okres), prefix='ob_form')
            ctx['mb_form'] = MBFormSet(queryset=MB.objects.filter(projekt_id=psp, okres=prev_okres), prefix='mb_form')
        elif prev_data == 'False':
            ctx = {'okres': okres, 'psp':psp, 'new_okres': False}
            ctx['km_form'] = KamienieMiloweForm(initial={'okres':okres})
            ctx['sl_form'] = NewSlFormSet(queryset=SL.objects.none(), prefix='sl_form')
            ctx['sm_form'] = NewSmFormSet(queryset=SM.objects.none(), prefix='sm_form')
            ctx['uk_form'] = NewUkFormSet(queryset=UK.objects.none(), prefix='uk_form')
            ctx['ob_form'] = NewOBFormSet(queryset=OB.objects.none(), prefix='ob_form')
            ctx['mb_form'] = NewMBFormSet(queryset=MB.objects.none(), prefix='mb_form')
        return render(request, 'create_form.html', ctx)

    def post(self, request, psp, okres, prev_data):
        km_form = KamienieMiloweForm(request.POST)
        sl_form = SlFormSet(request.POST, prefix='sl_form')
        sm_form = SmFormSet(request.POST, prefix='sm_form')
        uk_form = UkFormSet(request.POST, prefix='uk_form')
        ob_form = OBFormSet(request.POST, prefix='ob_form')
        mb_form = MBFormSet(request.POST, prefix='mb_form')
        if sl_form.is_valid() and sm_form.is_valid() and uk_form.is_valid()\
                and ob_form.is_valid() and mb_form.is_valid() and km_form.is_valid():
            # SAVE NEW FORMS
            for Model, form in zip([KamienieMilowe], [km_form]):
                instance = form.save(commit=False)
                if Model.objects.count() > 0:
                    instance.pk = Model.objects.latest('pk').pk + 1
                else:
                    instance.pk = 1
                form.save()
            # SAVE NEW FORMSETS
            for Model, formset in zip([SL, SM, UK, OB, MB], [sl_form, sm_form, uk_form, ob_form, mb_form]):
                for form in formset:
                    instance = form.save(commit=False)
                    if Model.objects.count() > 0:
                        instance.pk = Model.objects.latest('pk').pk + 1
                    else:
                        instance.pk = 1
                    form.save()
            messages.success(request, 'Dodano poprawnie formularz.')
            return redirect('manager-data')
        else:
            messages.warning(request, 'Popraw formularz.')
        ctx = {'okres': datetime.strptime(okres, '%Y-%m-%d'), 'psp': psp, 'new_okres': True}
        ctx['km_form'] = km_form
        ctx['sl_form'] = sl_form
        ctx['sm_form'] = sm_form
        ctx['uk_form'] = uk_form
        ctx['mb_form'] = mb_form
        ctx['ob_form'] = ob_form
        return render(request, 'create_form.html', ctx)


class UpdateMultiFormView(PermissionRequiredMixin, View):
    permission_required = 'api.delete_km'
    def get(self, request, psp, okres):
        okres = datetime.strptime(okres, '%Y-%m-%d')
        ctx = {'okres': okres, 'psp':psp, 'new_okres': False}
        print(SlFormSet(queryset=SL.objects.filter(projekt_id=psp, okres=okres), prefix='sl_form'))
        ctx['km_form'] = KamienieMiloweForm(instance=KamienieMilowe.objects.filter(projekt_id=psp, okres=okres).first())
        ctx['sl_form'] = SlFormSet(queryset=SL.objects.filter(projekt_id=psp, okres=okres), prefix='sl_form')
        ctx['sm_form'] = SmFormSet(queryset=SM.objects.filter(projekt_id=psp, okres=okres), prefix='sm_form')
        ctx['uk_form'] = UkFormSet(queryset=UK.objects.filter(projekt_id=psp, okres=okres), prefix='uk_form')
        ctx['ob_form'] = OBFormSet(queryset=OB.objects.filter(projekt_id=psp, okres=okres), prefix='ob_form')
        ctx['mb_form'] = MBFormSet(queryset=MB.objects.filter(projekt_id=psp, okres=okres), prefix='mb_form')
        return render(request, 'create_form.html', ctx)

    def post(self, request, psp, okres):
        km_form = KamienieMiloweForm(request.POST, instance=KamienieMilowe.objects.filter(projekt_id=psp, okres=okres).first())
        sl_form = SlFormSet(request.POST, prefix='sl_form')
        sm_form = SmFormSet(request.POST, prefix='sm_form')
        uk_form = UkFormSet(request.POST, prefix='uk_form')
        ob_form = OBFormSet(request.POST, prefix='ob_form')
        mb_form = MBFormSet(request.POST, prefix='mb_form')
        if sl_form.is_valid() and sm_form.is_valid() and uk_form.is_valid()\
                and ob_form.is_valid() and mb_form.is_valid() and km_form.is_valid():
            # SAVE NEW FORMS
            for form in [km_form]:
                form.save()
            # SAVE NEW FORMSETS
            for Model, formset in zip([SL, SM, UK, OB, MB], [sl_form, sm_form, uk_form, ob_form, mb_form]):
                list_pk = []
                list_model = Model.objects.filter(projekt_id=psp, okres=okres)
                for form in formset:
                    instance = form.save(commit=False)
                    print(form)
                    if form.cleaned_data["id"]:
                        instance.pk = form.cleaned_data["id"].id
                    else:
                        instance.pk = Model.objects.latest('pk').pk + 1
                    list_pk.append(instance.pk)
                    form.save()
                for model in list_model:
                    if not model.pk in list_pk:
                        model.delete()
                # formset.save()
            messages.success(request, 'Dodano poprawnie formularz.')
            return redirect('manager-data')
        else:
            messages.warning(request, 'Popraw formularz.')
        ctx = {'okres': datetime.strptime(okres, '%Y-%m-%d'), 'psp': psp, 'new_okres': False}
        ctx['km_form'] = km_form
        ctx['sl_form'] = sl_form
        ctx['sm_form'] = sm_form
        ctx['uk_form'] = uk_form
        ctx['mb_form'] = mb_form
        ctx['ob_form'] = ob_form
        return render(request, 'create_form.html', ctx)


class AddProjektView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'api.add_projekt'
    template_name = 'forms.html'
    success_url = reverse_lazy('manager-data')
    success_message = "Dodano nowy Projekt"
    model = Projekt
    fields = '__all__'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.pk = instance.psp
        return super().form_valid(form)


class UpdateProjektView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'api.change_projekt'
    template_name = 'forms.html'
    success_url = reverse_lazy('manager-data')
    model = Projekt
    success_message = "Zaktualizowano Projekt"
    fields = '__all__'


class DeleteProjektView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'api.delete_projekt'
    # template_name = 'forms.html'
    success_url = reverse_lazy('manager-data')
    model = Projekt
    success_message = "Usunięto Projekt"
    fields = '__all__'

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('manager-data'))