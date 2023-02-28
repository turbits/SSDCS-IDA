from django.shortcuts import render
# from django.http import HttpResponse

# Create your views here.


def index(request):
    # data can be put here that the page might need
    
    # if there were data to pass, you would write this like this
    # context = {
    #     'test_context': 'testvalue'
    # }
    # return render(request, 'index.html', context=context)
    # then the page would have access to
    # the value of: context.test_context
    # more here: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Home_page
    return render(request, 'index.html')


def dataview(request):
    return render(request, 'dataview.html')
