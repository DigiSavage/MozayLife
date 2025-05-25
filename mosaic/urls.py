from django.urls import path
from . import views

app_name = 'mosaic'

urlpatterns = [
    # 1) Root of your site shows the mosaic form immediately
    path('',          views.home,       name='home'),

    # 2) If you still want a Main‐Menu landing page, give it its own URL
    path('menu/',     views.main_menu,  name='main_menu'),

    # 3) Other actions
    path('remove/',   views.remove,     name='remove'),
    path('results/',  views.results,    name='results'),

    # 4) AJAX upload endpoints
    path('upload/',           views.PictureCreateView.as_view(), name='upload_new'),
    path('upload/<int:pk>/',  views.PictureDeleteView.as_view(), name='upload-delete'),
]
