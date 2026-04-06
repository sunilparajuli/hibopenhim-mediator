from django.urls import path
from .views import NIDMappingView, NIDMediatorView

urlpatterns = [
    path('map/', NIDMappingView.as_view(), name='nid-mapping'),
    path('fetch/', NIDMediatorView.as_view(), name='nid-fetch-map'),
]
