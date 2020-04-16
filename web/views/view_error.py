
from django.shortcuts import render_to_response



def PageNotFound(request):

    return render_to_response(request,'404.html')
