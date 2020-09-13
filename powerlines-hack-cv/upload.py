import requests
import json


# '[{"TaskId":0,"Link":"http://89.223.95.49:8888/790890846_139488894_no_insulator.JPG"}]'

def upload_one_image(local_img_path):
    files = {'file': (local_img_path, open(local_img_path, 'rb'))}
    response = requests.post('http://89.223.95.49:8886/upload', files=files) # only upload!

    res_text = json.loads(response.text)
    uploaded_link = res_text[0]['Link']
    return uploaded_link