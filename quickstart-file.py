import asyncio, io, glob, os, sys, time, uuid, requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

# https://docs.microsoft.com/en-us/azure/cognitive-services/face/overview
# https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236
# https://docs.microsoft.com/en-us/azure/cognitive-services/face/quickstarts/python-sdk#find-similar-faces
# Add environmental variables (Mac OS): "export COGNITIVE_SERVICE_KEY=your-key"

# Create an authenticated FaceClient.
(KEY, ENDPOINT) = (os.environ['FACE_SUBSCRIPTION_KEY'], os.environ['FACE_ENDPOINT'])
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Urls to sample images
single_face_img_url="https://www.biography.com/.image/t_share/MTQ1MzAyNzYzOTgxNTE0NTEz/john-f-kennedy---mini-biography.jpg"
multi_face_image_url = "http://www.historyplace.com/kennedy/president-family-portrait-closeup.jpg"


def detect_faces_from_img_url(url):
    # Detect faces in an image that contains faces; returns list of detectedFaces object
    face_img_name = os.path.basename(url)
    detected_faces = face_client.face.detect_with_url(url=url)
    if not detected_faces:
        raise Exception('No face detected from image {}'.format(face_img_name))
    return detected_faces

def extract_face_ids(detectedFaces):
    # returns a list of face ids from a list of detectedFaces objects
    return [face.face_id for face in detected_faces]

def find_similar_faces(face_id,face_ids):
    # Given query face's faceId, to search the similar-looking faces from a faceId array
    similar_faces = face_client.face.find_similar(face_id=face_id, face_ids=face_ids)
    if not similar_faces[0]:
        raise Exception('No similar faces found detected')
    return similar_faces


def get_rectangle(faceObject):
    # Convert width height to a point in a rectangle; returns a tuple of rectangle coordinates
    rect = faceObject.face_rectangle
    left = rect.left
    top = rect.top
    bottom = left + rect.height
    right = top + rect.width
    return ((left, top), (bottom, right))

def get_img_from_url(url):
    # download an image from the image url
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def draw_rect_on_face(img,faceObject):
    # draw rectangle on face and return new image with rectangles
    draw = ImageDraw.Draw(img)
    draw.rectangle(get_rectangle(faceObject), outline='red')
    return img


def show_detected_faces(img_url):
    # show preview of detected faces in an image
    detected_faces=detect_faces_from_img_url(img_url)
    img = get_img_from_url(img_url)
    for face in detected_faces:
        rect = get_rectangle(face)
        draw_rect_on_face(rect,img,face)
    img.show()
