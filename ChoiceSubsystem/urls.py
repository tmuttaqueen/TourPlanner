from django.urls import path
from . import views
urlpatterns = [
    path('detailsForm',views.data_form_view_page,name="dataFormDisplay"),
    path('planTour/',views.extra_data_fetching,name="plan"),
    path('preference/<int:city>', views.preference_page, name="preference"),
    path('', views.display_cityChoice_page, name="city"),
    path('test/',views.show_weather_information),


]