#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers

from beijing_flight_count.models import BeijingFlights
from beijing_flight_count.models import Ac_Number
from beijing_flight_count.models import ActualTimetable
from beijing_flight_count.models import Check_Option
from beijing_flight_count.models import Location
from beijing_flight_count.models import PlanTimetable

from datetime import datetime
from datetime import timedelta

import json

# Create your views here.
def home(request):
    ac_all = Ac_Number.objects.all()
    actual_all = ActualTimetable.objects.all()
    a_day = timedelta(days = 1)
    list_data = []
    for ac in ac_all:
        actual = ActualTimetable.objects.filter(actual_ac_number = ac).order_by('-actual_date')
        plan = PlanTimetable.objects.filter(plan_ac_number = ac).order_by('-plan_date')[0]
        print actual[0].actual_scheduled_check.name
        if actual[0].actual_scheduled_check.name == u"是" :
            begin_date = actual[0].actual_date
            print begin_date
        else:

            begin_date = actual[0].actual_date + a_day
            print begin_date
        beijing_flights = BeijingFlights.objects.filter(ac_number = ac.name,
                                                        date__gte = begin_date,
                                                        arrival_airfield = 'PEK').order_by('departure_datetime')
        total_count = len(beijing_flights)
        print len(beijing_flights)
        for flight in beijing_flights:
            print flight
        beijing_flights = BeijingFlights.objects.filter(ac_number = ac.name,
                                                        date__gte = begin_date)

        night_count = 0
        for index, item in enumerate(beijing_flights):
            print index, item
            if index > 0:
                if item.departure_airfield == 'PEK':
                    print item.departure_datetime
                    departure_time = item.departure_datetime.replace(hour = 5,
                                                               minute = 0,
                                                               second = 0)
                    if item.departure_datetime > departure_time:
                        arrival_time = item.departure_datetime - a_day
                        print "arrival_time:" + str(arrival_time)
                        arrival_time = arrival_time.replace(hour = 18,
                                                            minute = 0,
                                                            second = 0)
                        if beijing_flights[index-1].arrival_datetime > arrival_time and beijing_flights[index-1].arrival_datetime <departure_time:
                            night_count = night_count + 1
        print "count:%s,%s, %s" %(ac.name, total_count, night_count)
        dict_alone = {}
        dict_alone['ac_number'] = actual[0].actual_ac_number.name
        dict_alone['actual_date'] = actual[0].actual_date.strftime('%Y-%m-%d')
        dict_alone['actual_location'] = actual[0].actual_location.name
        dict_alone['actual_scheduled_check'] = actual[0].actual_scheduled_check.name
        dict_alone['total_count'] = total_count
        dict_alone['night_count'] = night_count
        dict_alone['all_count'] = total_count + night_count
        dict_alone['plan_date'] = plan.plan_date.strftime('%Y-%m-%d')
        dict_alone['plan_location'] = plan.plan_location.name
        dict_alone['plan_scheduled_check'] = plan.plan_scheduled_check.name
        list_data.append(dict_alone)

    upload_data = json.dumps(list_data)
    return render(request, 'home.html', {'json_data': upload_data})


def beijing_flights(request):
    query_data = BeijingFlights.objects.all()
    json_data = serializers.serialize("json", BeijingFlights.objects.all())
    list_data = json.loads(json_data)

    upload_data = []
    for item in list_data:
        upload_data.append(item['fields'])
    upload_data = json.dumps(upload_data)
    print upload_data
    return render(request, 'beijing_flights.html', {'json_data': upload_data})