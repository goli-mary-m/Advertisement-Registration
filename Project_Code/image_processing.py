
import requests
import config

IMAGGA_API_KEY = config.IMAGGA_API_KEY
IMAGGA_API_SECRET = config.IMAGGA_API_SECRET

def image_tagging(ad_id):

    image_path = 'static/downloads/' + str(ad_id) +'.png'

    response = requests.post(
        'https://api.imagga.com/v2/tags',
        auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET),
        files={'image': open(image_path, 'rb')})
    
    return response.json()

def check_tags(response_json):
 
    flag_have_vehicle_tag = False

    all_tags_dict = {}
    for json_dict in list(dict(dict(response_json).get('result')).get('tags')):
        confidence = json_dict.get('confidence')
        tag = json_dict.get('tag').get('en')
        all_tags_dict[tag] = confidence

    if('vehicle' in all_tags_dict.keys()):
        flag_have_vehicle_tag = True
        vehicle_confidence = all_tags_dict['vehicle']

    if(flag_have_vehicle_tag == True and vehicle_confidence >= 50):
        state = "accepted"
        category = list(all_tags_dict.keys())[0]
    else:
        state = "failed"   
        category = None

    return state, category