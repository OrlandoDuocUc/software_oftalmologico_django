from django.urls import path
from django.views.generic import TemplateView

app_name = "shared"

urlpatterns = [
    path("health/", TemplateView.as_view(template_name="core/health.html"), name="health"),
]
