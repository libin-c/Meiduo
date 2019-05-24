from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponse
# Create your views here.
class RegisterView(View):
    def get(self, request):

        return render(request, 'register.html')