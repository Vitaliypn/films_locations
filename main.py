#! /usr/bin/env python
# -*- coding: utf-8 -*-
"Lab 1 task 2"
import argparse
# import geopy
# from geopy import geocoders
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from haversine import haversine
import folium


parser = argparse.ArgumentParser()
parser.add_argument("year", type = int,  help = "year of the film")
parser.add_argument("coord1", type = int , help = "latitude")
parser.add_argument("coord2", type = int,help = "longtitude")
parser.add_argument("path", type = str, help = "path to file")
args = parser.parse_args()


def main(year, coord1, coord2, path):
    """Main function

    Args:
        year(int): year of the film
        coord1(int): latitude
        coord2(int): longtitude
        path (str): path to file

    Returns:
        html: file with marked locations
    """
    years = []
    with open(path, 'rb') as file:
        geolocator = Nominatim(user_agent="movie")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.0001)
        cont = file.readlines()
        for line in cont:
            line = str(line)
            line = line[1:].strip().replace("'b",'').replace("'",'').replace('\\t',' ')
            if '(' in line:
                if line[line.index('(')+1:line.index(')')] == str(year):
                    film_name = line[:line.index('(') - 1]
                    location =  line[line.index(')') + 1:].strip()[:-2].replace('\\','')\
                    .replace('(V)','').replace('(TV)','').replace('xefxbfxbd','').strip()
                    if '}' in location:
                        continue
                    if '(' in location:
                        location = location[:location.index('(')].strip()
                    adress = geocode(location)
                    print(location)
                    if adress is not None:
                        distance = haversine((coord1, coord2), (adress.latitude,adress.longitude))
                        print(distance)
                        years.append([distance,adress.latitude,adress.longitude,\
                            location, film_name.replace('\\','').replace('\\x','').replace('"','')])
    return markers(dictionary(years), coord1, coord2, year)


def dictionary(lst):
    """This function helps me to prevent certain
    films be in the same location and count as a 
    different location. Also the same movie will 
    only be at the one location

    Args:
        lst (list): This is the list of 
        films that were shooted at this year

    Returns:
        dict: key is coordinates of location and item 
        is a film names
    """
    all_films = {}
    names = []
    for element in sorted(lst, key = lambda x: x[0]):
        if (element[1],element[2]) in all_films:
            new = all_films.get((element[1],element[2]))
            new.append(element[4])
        else:
            if len(all_films) > 9:
                return all_films
            if element[4] not in names:
                all_films.update({(element[1],element[2]): [element[4]]})
        names.append(element[4])
    return all_films


def markers(places, coord1, coord2, year):
    """
    This function creates an map with marked
    top 10 nearest films]
    top 3 is red, from 4 to 6 is green and else is blue
    
    Args:
        places (dict): key is coordinates of location and item 
        is a film names
        coord1: latitude
        coord2: langtitude
        year: year of the film

    Returns:
        html: map with marked locations
    """
    map = folium.Map(location=[coord1, coord2], zoom_start=5)
    map.add_child(folium.CircleMarker(location=[coord1, coord2],
                                  radius=10,
                                  popup=year,
                                  fill_color='yellow',
                                  color='blue',
                                  fill_opacity=0.5))
    html = """<h4>Location information:</h4>
    Year: {},<br>
    Films names: {}
    """
    i = 1
    rgb = 'red'
    fg_list = []
    for elem in places:
        if i > 3:
            if i > 6:
                rgb = 'green'
            else:
                rgb = 'blue'
        fg = folium.FeatureGroup(name = i)
        films = places.get(elem)
        iframe = folium.IFrame(html=html.format(year,films),
                            width=300,
                            height=100)
        fg.add_child(folium.Marker(location=list(elem),
                    popup=folium.Popup(iframe),
                    icon=folium.Icon(color = rgb)))
        i +=1
        fg_list.append(fg)
    for fg in fg_list:
        map.add_child(fg)
    map.add_child(folium.LayerControl())
    name = 'Films location in '+ str(year) + '.html'
    return map.save(name)



if __name__=="__main__":
    main(args.year, args.coord1, args.coord2, args.path)
