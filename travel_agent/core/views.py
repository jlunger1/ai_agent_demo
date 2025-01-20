from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def ask(request):
    # the user is asking a question, this provides the response
    return HttpResponse("This is the response to your question.")
