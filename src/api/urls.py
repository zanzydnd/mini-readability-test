from django.urls import path

from api.views import HomePageView, ProcessUrlView, ApiView

urlpatterns_not_api = [
    path("", HomePageView.as_view(), name="home"),
    path("process_url/", ProcessUrlView.as_view(), name="process_url"),
]

urlpatterns_api = [path("process_url/", ApiView.as_view(), name="api_process_url")]
