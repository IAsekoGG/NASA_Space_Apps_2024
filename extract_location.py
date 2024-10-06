import json
from address2coords import get_coordinates
from tqdm import tqdm

soloma_info_path = "/home/hlak/PycharmProjects/NASA_Space_Apps_2024/data2/info/Солома_INFO_Солом'янський_район_7_locations.json"
los_solomas_path = '/home/hlak/PycharmProjects/NASA_Space_Apps_2024/data2/los_solomas/LOS SOLOMAS . КИЇВ_no_comments_1000_7_locations.json'

with open(soloma_info_path, 'r') as f:
    soloma_info = json.load(f)

with open(los_solomas_path, 'r') as f:
    los_solomas = json.load(f)

# location_types = set([f['location_type'][0] for f in los_solomas if 'location_type' in f.keys() and f['location_type']])
# location_types = {k: 0 for k in location_types}
# for f in los_solomas:
#     if 'location_type' in f.keys():
#         if f['location_type']:
#             location_types[f['location_type'][0]] += 1
#
# print(location_types)


# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = ' AIzaSyB3SbtDC6wCOv24kVzEiSQpDimvcG0yYrk'

# if coords:
#     print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
# else:
#     print("Could not geocode the address.")


res = []

for i, row in tqdm(enumerate(los_solomas), total=len(los_solomas)):

    if not ('location_type' in row.keys()):
        continue
    if not row['location_type']:
        continue
    if not any([lt in ['exact location', 'street'] for lt in row['location_type']]):
        continue

    for loc, tp in zip(row['location'], row['location_type']):
        if loc == 'Kyiv':
            continue
        coords = get_coordinates(loc, api_key)
        if coords is None:
            continue
        res_dict = {}
        for key in ['date', 'channel_name', 'message_id', 'text', 'sentiment', 'rephrased_news', 'title', 'topic', ]:
            res_dict[key] = row[key]
        res.append(res_dict | {'location_type': tp, 'location': loc, 'coords': coords})


with open("/home/hlak/PycharmProjects/NASA_Space_Apps_2024/data2/los_solomas/LOS_SOLOMAS_res.json", 'w') as f:
    json.dump(res, f, indent=4, ensure_ascii=False)
