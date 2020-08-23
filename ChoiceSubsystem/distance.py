import random
import time
from datetime import date, timedelta
import requests
from database.models import *
import math
ALL_VISITED = None

def getDistance( latitude1, longitude1, latitude2, longitude2 ):
    time.sleep(1.2)
    s = ('https://api.mapbox.com/directions/v5/mapbox/driving/%s,%s;%s,%s?access_token=pk.eyJ1IjoidG11dHRhcXVlZW4iLCJhIjoiY2p4eWM3b2NuMDBmbjNub2J1ejZ3ZXZkbSJ9.cmOI397iM8GxEdwpfpfnKA')%( longitude1, latitude1, longitude2, latitude2)
    v = requests.get(s).json()
    return round(v['routes'][0]['distance'],2)

def getDuration( latitude1, longitude1, latitude2, longitude2 ):
    time.sleep(1.2)
    s = ('https://api.mapbox.com/directions/v5/mapbox/driving/%s,%s;%s,%s?access_token=pk.eyJ1IjoidG11dHRhcXVlZW4iLCJhIjoiY2p4eWM3b2NuMDBmbjNub2J1ejZ3ZXZkbSJ9.cmOI397iM8GxEdwpfpfnKA')%( longitude1, latitude1, longitude2, latitude2)
    v = requests.get(s).json()
    return round(v['routes'][0]['duration'],2)

def dateToString( date_in ):
    return date_in.strftime("%A, %d %B, %Y")

def tsp( mask, last, dp, to, dist, n):
    if mask == ALL_VISITED:
        return dp[mask][last]

    if to[mask][last] != -1:
        return dp[mask][last]


    v = 1000*1000*1000
    nxt = -1
    for i in range(n):
        if mask&(1<<i) != 0:
            continue

        val = dist[last][i] + tsp(mask|(1<<i), i, dp, to, dist, n)

        if val < v:
            nxt = i
            v = val

    to[mask][last] = nxt
    dp[mask][last] = v

    #print( "dp: "+ str(dp) )
    #print( str(mask) + " " + str(last) + " " + str(v) )
    return dp[mask][last]


def get_city_sequence(citylist):
    random.seed(61)
    n = len(citylist) - 1
    print(citylist)
    print(n)
    INF = 1000*1000*1000

    dist = [ [0 for x in range(n+1)] for y in range(n+1) ]

    for i in range(n+1):
        xx = CITY.objects.get( id = citylist[i] )
        #print(xx.cityName)

    for x in range(n+1):
        for y in range(n+1):
            xx = CITY.objects.get( id = citylist[x] )
            yy = CITY.objects.get( id = citylist[y] )
            #print( str(citylist[x]) + " " + str( citylist[y] )  )
            dist[x][y] = getDistance( xx.latitude, xx.longitude, yy.latitude, yy.longitude )

    '''dist = [ [random.randint(1, 10) for x in range(n+1)] for y in range(n+1) ]
    for i in range(n+1):
        for j in range(n+1):
            if i == j:
                dist[i][j] = 0'''
    #print(dist)
    dp = [ [INF]*n for x in range(1<<n)]
    to = [ [-1]*n for x in range(1<<n)]
    ALL_VISITED = (1<<n) - 1
    for x in range(n):
        dp[ALL_VISITED][x] = dist[x][n]
        to[ALL_VISITED][x] = n

    print(tsp(1,0, dp, to, dist, n))
    seq = []
    seq.append(0)
    mask = 1
    for i in range(n):
        nxt = to[mask][ seq[i] ]
        mask = mask|(1<<nxt)
        seq.append(nxt)
    #print(seq)
    for i in range(n+1):
        seq[i] = citylist[ seq[i] ]
    #print(seq)
    return seq


'''ct = [1,3,4,5,6,1]
get_city_sequence(ct)'''

def get_city_from_spot( spotlist, start_city, end_city  ):
    city = set()
    for s in spotlist:
        spot = SPOT.objects.get(id=s)
        city.add(spot.cityID.id)

    city.discard(start_city)
    city.discard(end_city)
    citylist = []
    citylist.append(start_city)
    for v in city:
        citylist.append(v)

    citylist.append(end_city)
    citylist = get_city_sequence(citylist)
    return citylist

def generate_city_spot( spotlist, start_city, end_city ):
    citylist = get_city_from_spot(spotlist, start_city, end_city)
    #print(citylist)
    city_spot = {}
    for v in citylist:
        city_spot[v] = []

    for s in spotlist:
        spot = SPOT.objects.get(id = s)
        city_spot[spot.cityID.id].append(s)
    #print(city_spot)
    return (citylist, city_spot)


'''spot = [7,8,9,10,11,12,13]
start_city = 1
end_city = 1
generate_city_spot(spot, start_city, end_city)'''



def generate_plan( cur_city, spot_list, nxt_city, cur_date  ):
    #print( "cur city: " + str(cur_city))
    #print( "spot_list: " + str(spot_list) )
    #print("nxt_city: "  + str(nxt_city) )
    total_time = 0
    spot_visit_time = []
    for s in spot_list:
        dbs = SPOT.objects.get( id = s )
        spot_visit_time.append( float(dbs.totalVisitTime.split()[0]) )
        total_time = total_time + float(dbs.totalVisitTime.split()[0])

    daily_travel_time = 7.0
    spot_day = math.ceil( total_time/daily_travel_time )
    src = CITY.objects.get( id = cur_city )
    dst = CITY.objects.get( id = nxt_city )
    #tm.append( getDuration( src.latitude, src.longitude, dst.latitude, dst.longitude )/3600.0 )
    tot_spot = len(spot_list)
    spot_it = 0
    visit_by_day_description = {}
    visit_by_day_time = {}
    visit_by_day_distance = {}

    #print( "spot day: " + str(spot_day))

    for i in range(spot_day):
        new_date = cur_date + timedelta(days = i)
        spots = []
        temp_daily_travel_time = daily_travel_time
        while (spot_it < tot_spot and spot_visit_time[spot_it] < temp_daily_travel_time ):
            spots.append( spot_list[spot_it] )
            temp_daily_travel_time -= spot_visit_time[spot_it]
            spot_it = spot_it+1

        #print( "spot: " + str(spots) )

        s = dateToString(new_date)
        #print(s)
        visit_by_day_description[s] = []
        visit_by_day_time[s] = []
        visit_by_day_distance[s] = []
        n = len(spots)
        for j in range(n):
            x = spots[j]
            xx = SPOT.objects.get(id = x)
            visit_by_day_description[s].append( ("Visit Spot: %s")%(xx.spotName) )
            visit_by_day_time[s].append(  str(float(dbs.totalVisitTime.split()[0])*60) + " Minutes"  )
            visit_by_day_distance[s].append( "-" )
            if j+1 < n:
                yy = SPOT.objects.get(id = spots[j+1])
                visit_by_day_description[s].append( ("Travel from spot %s to spot %s")%(xx.spotName, yy.spotName) )
                visit_by_day_distance[s].append( str( round(getDistance( xx.latitude, xx.longitude, yy.latitude, yy.longitude )/1000.0, 2)) + " Kilometers" )
                visit_by_day_time[s].append( str(round(getDuration(xx.latitude, xx.longitude, yy.latitude, yy.longitude)/60.0,2)) + " Minutes" )
    new_date = cur_date + timedelta(days = spot_day)
    s = dateToString(new_date)
    #print(s)
    visit_by_day_description[s] = []
    visit_by_day_distance[s] = []
    visit_by_day_time[s] = []
    visit_by_day_description[s].append( ("Travel from city %s to city %s")%(src.cityName, dst.cityName) )
    visit_by_day_distance[s].append( str(round(getDistance( src.latitude, src.longitude, dst.latitude, dst.longitude )/1000.0, 2)) + " Kilometers" )
    visit_by_day_time[s].append( str(round(getDuration(src.latitude, src.longitude, dst.latitude, dst.longitude)/60.0,2)) + " Minutes" )
    #print( visit_by_day_description )
    #print( visit_by_day_time )
    #print( visit_by_day_distance )
    cur_date = cur_date + timedelta( days= spot_day + 1 )
    return ( visit_by_day_description, visit_by_day_time, visit_by_day_distance, cur_date )



