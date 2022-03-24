filename = input("Write input's filename with extension : ")

try:
    with open(filename) as f:
        data = eval(f.read().replace('\n', ''))
except:
    print("There is no input file named", filename)
    exit()

vehicles = data["vehicles"]
jobs = data["jobs"]
matrix = data["matrix"]

def permutations(string):
    if len(string) == 0:
        return []
    result = []
    result.append(string[0])
    for i in range(1, len(string)):
        for j in reversed(range(len(result))):
            current = result.pop(j)
            for k in range(len(current) + 1):
                result.append(current[:k] + string[i] + current[k:])
    return result

def generate_all_routes():
    number_of_vehicles = len(vehicles)
    deliveries_list = [str(each["id"]) for each in jobs]
    initial_string = "".join(deliveries_list) + (number_of_vehicles-1) * ","
    routes = list(set(permutations(initial_string)))
    return routes

def filter_routes(routes):
    filtered_routes = []
    for eachRoute in routes:
        indexForVehicle = 0
        countOfComma = 0
        routeIndex = 0
        initial_capacities = [eachVehicle["capacity"] for eachVehicle in vehicles]
        flag = 0
        for eachElement in eachRoute:
            if(countOfComma == len(vehicles)-1):
                remainderTuple = eachRoute[routeIndex:]  
                for eachRemainderTuple in remainderTuple:
                    capacity_for_vehicle = vehicles[indexForVehicle]["capacity"]
                    for each in jobs:
                        if(str(each["id"]) == eachRemainderTuple):
                            delivered_carboy = each["delivery"]
                    vehicles[indexForVehicle]["capacity"] = [capacity_for_vehicle[0] - delivered_carboy[0]]
                    if(vehicles[indexForVehicle]["capacity"][0] < 0):
                        flag=1
                break
            if(eachElement == ","):
                countOfComma = countOfComma + 1
                indexForVehicle = indexForVehicle + 1
                routeIndex = routeIndex + 1
            else:
                capacity_for_vehicle = vehicles[indexForVehicle]["capacity"]
                for each in jobs:
                    if(str(each["id"]) == eachElement):
                        delivered_carboy = each["delivery"]
                vehicles[indexForVehicle]["capacity"] = [capacity_for_vehicle[0] - delivered_carboy[0]]
                if(vehicles[indexForVehicle]["capacity"][0] < 0):
                    flag = 1
                    break
                routeIndex = routeIndex + 1
        vehicle_index = 0
        for eachVehicle in vehicles:
            eachVehicle["capacity"] = initial_capacities[vehicle_index]
            vehicle_index = vehicle_index + 1
        if(flag == 0):
            filtered_routes.append(eachRoute)

    return filtered_routes

def calculate_durations_for_route(routeList, optional):
    calculations = []
    total_durationList = []
    for eachRoute in routeList:
        new_route_element = []
        index = 0
        duration = 0
        countOfComma = 0
        routeIndex = 0
        start_indexes = [eachVehicle["start_index"] for eachVehicle in vehicles]
        for eachElement in eachRoute:
            if(countOfComma == len(vehicles)-1):
                remainderTuple = eachRoute[routeIndex:]  
                for eachRemainderTuple in remainderTuple:
                    locationIndex = vehicles[index]["start_index"]
                    for each in jobs:
                        if(str(each["id"]) == eachRemainderTuple):
                            finishIndex = each["location_index"]
                            serviceTime = each["service"]
                    if(optional):
                        duration = duration + matrix[int(locationIndex)][int(finishIndex)] + int(serviceTime)
                    else:
                        duration = duration + matrix[int(locationIndex)][int(finishIndex)]
                    vehicles[index]["start_index"] = finishIndex
                new_route_element.append([vehicles[index]["id"], duration])
                break
            if(eachElement == ","):
                new_route_element.append([vehicles[index]["id"], duration])
                countOfComma = countOfComma + 1
                index = index + 1
                duration = 0
                routeIndex = routeIndex + 1
            else:
                locationIndex = vehicles[index]["start_index"]
                for each in jobs:
                    if(str(each["id"]) == eachElement):
                        finishIndex = each["location_index"]
                        serviceTime = each["service"]
                if(optional):
                    duration = duration + matrix[int(locationIndex)][int(finishIndex)] + int(serviceTime)
                else:
                    duration = duration + matrix[int(locationIndex)][int(finishIndex)]
                vehicles[index]["start_index"] = finishIndex
                routeIndex = routeIndex + 1
        if(len(new_route_element) == len(vehicles) - 1):
            new_route_element.append([vehicles[len(vehicles)-1]["id"],0])

        total_duration = 0

        for eachNewRoute in new_route_element:
            total_duration = total_duration + eachNewRoute[1]

        total_durationList.append(total_duration)

        calculations.append(new_route_element)

        vehicle_index = 0
        for eachVehicle in vehicles:
            eachVehicle["start_index"] = start_indexes[vehicle_index]
            vehicle_index = vehicle_index + 1

    return calculations, total_durationList

def helper_for_output(durationList, routes, calcs , minIndex):
    a = dict()
    a["total_delivery_duration"] = durationList[minIndex]
    a["routes"] = dict()
    bestRoute = routes[minIndex]
    index = 0
    indexForVehicle = 0
    for eachVehicle in vehicles:
        a["routes"][str(eachVehicle["id"])] = dict()
        a["routes"][str(eachVehicle["id"])]["jobs"] = list()
        for eachRoute in bestRoute[index:]:
            if(eachRoute != ","):
                index = index + 1
                a["routes"][str(eachVehicle["id"])]["jobs"].append(eachRoute)
            else:
                a["routes"][str(eachVehicle["id"])]["delivery_duration"] = calcs[minIndex][indexForVehicle][1]
                index = index + 1
                indexForVehicle = indexForVehicle + 1
                break
    a["routes"][str(eachVehicle["id"])]["delivery_duration"] = calcs[minIndex][indexForVehicle][1]
    #print(a)
    return a

def output_function(durationList, routes, calcs, optional):
    min_value = min(durationList)
    minIndexes = [i for i, x in enumerate(durationList) if x == min_value]
    index=0
    for eachMin in minIndexes:
        helper_for_output(durationList,routes,calcs,eachMin)
        if(not optional):
            with open("output"+str(index)+"_withoutServiceAndDelivery.json",'w') as data: 
                data.write(str(helper_for_output(durationList,routes,calcs,eachMin)))
        else:
            with open("output"+str(index)+"_withServiceAndDelivery.json",'w') as data:
                data.write(str(helper_for_output(durationList,routes,calcs,eachMin)))
        index = index + 1

### Naive Bayes Finding Minimum Total Delivery Time Without Service and Delivery Constraints

routes = generate_all_routes()
calcs , durationList = calculate_durations_for_route(routes, False) ## Optional False when there is no constraint
output_function(durationList, routes, calcs, False) 


### Naive Bayes Finding Minimum Total Delivery Time With Service and Delivery Constraints

filtered = filter_routes(routes)
calcsFiltered , durationListFiltered = calculate_durations_for_route(filtered, True) ## Optional True when there are constraint
output_function(durationListFiltered, filtered, calcsFiltered, True)