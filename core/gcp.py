from google.cloud import vision
from google.cloud import firestore

vision_client = vision.ImageAnnotatorClient()


def extract_text_from_image(content):
    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    return_text = ""
    for text in texts:
        return_text += text.description
    return return_text


db = firestore.Client()
