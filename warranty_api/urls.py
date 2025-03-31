from django.urls import path
from .views import home, calculate_warranty, warranty, repair, tradein, tradein_value, repair_locator

urlpatterns = [
    path('', home, name='home'),
    path('calculate/', calculate_warranty, name='calculate-warranty'),
    path('warranty/', warranty, name='warranty'),
    path('repair/', repair, name='repair'),
    path('tradein/', tradein, name='tradein'),
    path('tradein-value/', tradein_value, name='tradein-value'),
    path('repair-locator/', repair_locator, name='repair-locator'),# New API endpoint
]
