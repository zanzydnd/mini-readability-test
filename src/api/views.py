import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from api.forms import UrlForm
from core.extractor import UsefulTextFromHtmlExtractor


class HomePageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProcessUrlView(View):
    def post(self, request, *args, **kwargs):
        form = UrlForm(request.POST)
        if not form.is_valid():
            return render(request, "error.html", context={"form": form})

        extractor = UsefulTextFromHtmlExtractor()

        try:
            article = extractor.process(form.cleaned_data["url"])
        except Exception:
            return render(
                request,
                "error.html",
                context={"my_error": "Ошибка На сервере, что-то не так"},
            )

        return render(request, "response.html", context={"result": article})


@method_decorator(csrf_exempt, name="dispatch")
class ApiView(View):
    def post(self, request, *args, **kwargs):
        json_body = json.loads(request.body)

        form = UrlForm(data={"url": json_body.get("url")})

        if not form.is_valid():
            return JsonResponse(status=400, data={"errors": {"url": "Невалидный."}})

        extractor = UsefulTextFromHtmlExtractor()

        try:
            article = extractor.process(form.cleaned_data["url"])
        except Exception:
            return JsonResponse(
                status=500, data={"errors": {"server": "Ошибка сервера"}}
            )

        return JsonResponse(status=200, data={"article": article})
