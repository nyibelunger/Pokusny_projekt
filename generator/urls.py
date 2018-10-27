from django.urls import path
from . import views

app_name = 'generator'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    #path('1/1/', views.detail_1, name='detail_1'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    #path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),
    #path('ais/', views.generator_ais, name='ais'),
    #path('usr_input/', views.usr_input, name='usr_input'),
    path('input_excel/', views.input_excel, name='input_excel'),
    #path('upload/', views.upload, name='upload'),
    path('upload_date/', views.upload_date, name='upload_date'),
    path('input_date/', views.input_date, name='input_date'),
    path('render_sel_us_ais/', views.render_sel_us_ais, name='render_sel_us_ais'),
    path('home/', views.home, name='home'),
    #path('usr_input/usr_input_add/', views.usr_input_add, name='usr_input_add'),
               ]
