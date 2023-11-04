import json

json_out = '{"type": "FeatureCollection",  "features": ['
coords_vect = []

# Open the text file
with open('ais_1.txt', 'r') as file:
    # Read the entire file content
    content = file.read()

    # Split the content by the b' characters
    json_strings = content.split("b'")[1:]
    json_strings[-1] = json_strings[-1].rstrip("'\non_close() takes 1 positional argument but 3 were given")

    # Iterate through the JSON strings
    for json_str in json_strings:
        # Remove the trailing single quote and newline characters
        json_str = json_str.rstrip("'\n")

        # Try to parse the JSON string
        try:
            data = json.loads(json_str)
            # Extract the longitude and latitude
            long = data['Message']['PositionReport']['Longitude']
            lat = data['Message']['PositionReport']['Latitude']
            
            json_out += '{"type": "Feature","properties": {},"geometry": {"coordinates": ['+str(long)+','+str(lat)+'],"type": "Point"}},'
            coords_vect.append((long,lat))

        except json.JSONDecodeError:
            # If the JSON string cannot be parsed, skip it
            continue
        
json_out += ']}'
print(coords_vect)

with open('coordinates_list.json', 'w') as f:
  json.dump(json_out, f, ensure_ascii=False)