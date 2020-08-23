from django.shortcuts import render,redirect
from database.models import CITY, CITYPREFERENCE, PREFERENCE, SPOTPREFERENCE, SPOT
from django.http import HttpResponse
from django.template import loader
from .distance import *
from .weather import *
import time
from datetime import date, timedelta
from RegLogin import views,urls

# Create your views here.
def display_cityChoice_page(request):
    template = loader.get_template('cityChoice.html')
    context = {}
    all_cities=CITY.objects.all()
    no_of_cities=all_cities.count()
    rows=int(no_of_cities/3)
    if (no_of_cities%3) != 0:
        rows=rows+1
    counter=0
    city_ids=[]
    city_names={}
    city_images={}
    city_descs={}
    for i in range(0,rows):
        ids=[]
        for j in range(0,3):
            if counter < no_of_cities:
                index=all_cities[counter].id
                ids.append(index)
                city_names[index]=all_cities[counter].cityName
                city_images[index]=str(all_cities[counter].image)
                city_descs[index]=all_cities[counter].description
                counter=counter+1
        city_ids.append(ids)

    context['city_ids']=city_ids
    context['city_names']=city_names
    context['city_descs']=city_descs
    context['city_images']=city_images

    if request.user.is_authenticated:
        context['logged_in']=True
    else:
        context['logged_in'] =False
    return HttpResponse(template.render(context, request))

def city_choice_page(request):

    context={}
    all_city = CITY.objects.all()
    city_names={}
    city_images={}
    city_ids={}
    count={}
    counter=0
    for a in all_city:
        city_names[a.pk] = a.cityName
        city_images[a.pk] = str(a.image)
        counter = counter + 1


    print(counter)
    rows=int(counter/3)

    if(counter%3!=0):
        rows=rows+1
    print(rows)
    context['rows']=rows

    context['city_names'] = city_names
    context['images']=city_images
    context['city_ids']=city_ids
    context['count']=count
    if request.user.is_authenticated:
        context['logged_in']=True
    else:
        context['logged_in'] =False
    return render(request, 'cityChoice.html', context)


def preference_page(request, city):
   # pref_ids = CITYPREFERENCE.objects.select_related('preferenceID').filter(cityId_id=city)
    print("City: " + str(city) )
    if request.method == 'POST':
       some_var = request.POST.getlist('selected_spot[]')
       print("some_var1: " + str(some_var) )

       print(some_var)
       chosen_spots=request.session.get('chosen_spots',default=None)
       chosen_cities=request.session.get('chosen_cities',default=None)
       print("previous_spots: " + str(chosen_spots) )
       print("previous_cities: " + str(chosen_cities) )
       if chosen_spots is None:
           #print("chosen_spots_None")
           chosen_spots = some_var
           request.session.__setitem__('chosen_spots',chosen_spots)
       else:
           #print("chosen_spots_Not_None")
           chosen_spots=chosen_spots+some_var
           #chosen_spots=[]
           #print("chosen_spots2:" + str(chosen_spots) )
           request.session.__setitem__('chosen_spots',chosen_spots)

       print("Current Spots: " + str(chosen_spots) )

       if chosen_cities is None:
           if len(some_var)!=0:
               chosen_cities=[]
               chosen_cities.append(city)
               request.session.__setitem__('chosen_cities',chosen_cities)
       else:
           if len(some_var)!=0:
               chosen_cities.append(city)
               request.session.__setitem__('chosen_cities',chosen_cities)

       print("Current City: " + str(chosen_cities) )


       #if request.user.id is None
           #return

       if 'next' in request.POST:
            return render(request,"extraDetailsForm.html",{})
       elif 'add_more_cities' in request.POST:
            return redirect('city')
       #return city_choice_page(request)

    else:
        preference_list={}
        pref_spotName_list={}
        pref_spotDescription_list = {}
        pref_spotImage_list={}
        pref_ids=CITYPREFERENCE.objects.filter(cityID=city)
        for p in pref_ids:
            pID = p.preferenceID
            pName=pID.prefName
            preference_list[pID.id]=pID.prefName
            spot_ids=SPOTPREFERENCE.objects.filter(preferenceID=pID)
            spots={}
            spotImages={}
            spotDescriptions={}
            for s in spot_ids:
                sID=s.spotID
                if sID.cityID.id == city:
                    spots[sID.id]=sID.spotName
                    spotImages[sID.id]=sID.image

                    spotDescriptions[sID.id]=sID.spotInfo
                    #print(sID.spotInfo)
                    #print(city, sID.spotName, pID.prefName)
            pref_spotName_list[pID.id]=spots
            pref_spotImage_list[pID.id]=spotImages
            pref_spotDescription_list[pID.id]=spotDescriptions
           # print(pref_spotDescription_list)


        all_city=CITY.objects.all()
        other_cities={}
        for c in all_city:
            #print(c.id)
            if c.id!=city:
                other_cities[c.id]=c.cityName

        return render(request, 'prefV2.html', {'preference_list':preference_list,
                                                   'pref_spotName_list':pref_spotName_list,
                                                   'pref_spotDescription_list': pref_spotDescription_list,
                                                   'pref_spotImage_list': pref_spotImage_list,
                                                    'other_cities':other_cities,
                                                   })

def data_form_view_page(request):
    template = loader.get_template('extraDetailsForm.html')
    context={}
    return HttpResponse(template.render(context,request))

def extra_data_fetching(request):
    template = loader.get_template('LoadingPage.html')
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    start_time=request.POST['start_time']
    end_time=request.POST['end_time']
    start_city=request.POST['start_location']
    budget=request.POST['budget']
    context = {}
    #context={'start_date':start_date, 'end_date':end_date, 'start_time':start_time, 'end_time':end_time,
    #         'start_location':start_city, 'budget':budget}

    chosen_spots = request.session.get('chosen_spots', default=None)
    chosen_cities = request.session.get('chosen_cities', default=None)

    start_city = CITY.objects.get(cityName=start_city).id
    end_city = start_city

    city_list, city_spot = generate_city_spot(chosen_spots, start_city,end_city)
    print(city_spot)
    print(city_list)


    temp = start_date.split('-')
    start_date = date( int( temp[0] ), int(temp[1]), int(temp[2]) )
    total_city = len(city_list)
    cur_date = start_date
    cityName_list = []
    desc_data = {}
    distance_data = {}
    time_data = {}
    weather_data = {}
    for i in range(total_city):
        if i == total_city - 1:
            continue
        cur_city = city_list[i]
        nxt_city = city_list[i+1]
        visit_by_day_description, visit_by_day_time, visit_by_day_distance, cur_date = generate_plan(cur_city, city_spot[cur_city], nxt_city, cur_date )

        print(visit_by_day_distance)
        print(visit_by_day_time)
        print(visit_by_day_description)
        cc = CITY.objects.get( id = cur_city )
        cityName = cc.cityName
        desc_data[ cityName ] = visit_by_day_description
        distance_data[ cityName ] = visit_by_day_distance
        time_data[cityName ] = visit_by_day_time
        weather_data[ cityName ], baad1, baad2 = getWeather(cc.latitude, cc.longitude)
        #print(cur_date)
        cityName_list.append( cityName )
    context['cityName'] = cityName_list
    context['description_data'] = desc_data
    context[ 'distance_data' ] = distance_data
    context[ 'time_data' ] = time_data
    context[ 'weather_data' ] = weather_data
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        request.session.__setitem__('plan_context_data',context)
        return  redirect('login',view_func_name="tour_plan")


def show_weather_information(request):
    template = loader.get_template('plan_weather.html')
    #city_list = get_city_from_spot(spotlist, start_city, end_city)
    city_list=[1,2,3,4,5,6,7]
    maximum={}
    minimum={}
    description={}
    context={}
    for c in city_list:
        obj=CITY.objects.get(id=c)
        d, mx, mn=getWeather(obj.longitude, obj.latitude )
        #descs=d[0:3]
        #max=mx[0:3]
        #min=mn[0:3]
        descs={}
        descs[0]=d[0]
        descs[1] = d[1]
        descs[2] = d[2]
        max={}
        max[0]= round( mx[0], 2 )
        max[1]= round( mx[1], 2 )
        max[2] = round( mx[2], 2 )

        min={}
        min[0] = round( mn[0], 2 )
        min[1] = round( mn[1], 2 )
        min[2] = round( mn[2], 2 )

        description[c]=descs
        maximum[c]=max
        minimum[c]=min

    context['cities']=city_list
    context['description']=description
    context['maximum']=maximum
    context['minimum']=minimum
    return HttpResponse(template.render(context, request))

def show_tour_plan(request):
    template = loader.get_template('plan_daywise.html')
    context={}
    day_list=[1,2,3]
    cities={}
    spots={}
    traveling_times={}
    for day in day_list:
        city_names=[1,2,3,4]
        cities[day]=city_names
        for c in city_names:
            spot_list=['am','rg','hd']
            spots[c]=spot_list
            time_list=[1,2]
            traveling_times[c]=time_list

    context['day_list']=day_list
    context['city']=cities
    context['spot']=spots
    context['traveling_times']=traveling_times

    return HttpResponse(template.render(context, request))