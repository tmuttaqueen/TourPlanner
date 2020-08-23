from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse
from .search import *

def show_search_page(request):
    template = loader.get_template('searchPage.html')
    context = {}
    return HttpResponse(template.render(context, request))

def show_search_results(request):
    template = loader.get_template('searchPage.html')

    if request.method == 'POST':
        context = {}
        context['placeholder']="What are you looking for?"
        search_text = request.POST['search_text']
        print(search_text)
        caption=[]
        data=[]
        image=[]
        caption,data,image = getDetailsFromSearchKey(search_text)
        #print(caption)
        #print(data)
        #print(image)
        if len(caption)==0:
            print("No results found")
            context['error']="No results found"
            context['caption']=[]
            context['data']=[]
            context['image']=[]
            context['placeholder'] = search_text
        else:
            context['caption']=caption
            context['data']=data
            context['image']=image
            context['placeholder'] = search_text
    else:
            context = {}
            context['placeholder']="What are you looking for?"
        

    return HttpResponse(template.render(context, request))

