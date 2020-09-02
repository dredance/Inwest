from django.urls import path, include
from rest_framework import routers
from api import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'okresy/', views.OkresyView.as_view(), name='okresy'),
    path(r'obiekty/',views.ObiektyView.as_view(),name='obiekty'),
    path(r'analiza/', views.AnalizaProjektuView.as_view(), name='analiza'),
    path(r'sl/', views.SpawanieLinioweView.as_view(), name='sl'),
    path(r'sm/', views.SpawanieMontazoweView.as_view(), name='sm'),
    path(r'uk/', views.UkladkaView.as_view(), name='uk'),
    path(r'mb/', views.MetodyBezwykopoweView.as_view(), name='mb'),
    path(r'ob/', views.ObiektyView.as_view(), name='ob'),

    path(r'manager_data/', views.ManagerDataView.as_view(), name='manager-data'),
    path(r'new/<int:psp>/<slug:okres>/<slug:prev_data>/', views.CreateMultiFormView.as_view(), name='multiform-create'),
    path(r'update/<int:psp>/<slug:okres>/', views.UpdateMultiFormView.as_view(), name='multiform-update'),
    path(r'add_project/', views.AddProjektView.as_view(), name='add-project'),
    path(r'update_project/<int:pk>/', views.UpdateProjektView.as_view(), name='update-project'),
    path(r'delete_project/<int:pk>/', views.DeleteProjektView.as_view(), name='delete-project'),

]
