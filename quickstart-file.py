import asyncio, io, glob, os, sys, time, uuid, requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

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

def get_rectangle(faceDictionary):
    # Convert width height to a point in a rectangle
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    bottom = left + rect.height
    right = top + rect.width
    return ((left, top), (bottom, right))

def get_img_from_url(url):
    # Download the image from the url
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def draw_rect_on_face(rect,img,face):
    #draw rectangle on face and return new image with rectangles
    draw = ImageDraw.Draw(img)
    draw.rectangle(get_rectangle(face), outline='red')
    return img

def show_detected_faces(img_url):
    detected_faces=detect_faces_from_img_url(img_url)
    img = get_img_from_url(img_url)
    for face in detected_faces:
        rect = get_rectangle(face)
        draw_rect_on_face(rect,img,face)
    img.show()

show_detected_faces(single_face_img_url)

# # Detect the faces in an image that contains multiple faces
# # Each detected face gets assigned a new ID
# multi_face_image_url = "http://www.historyplace.com/kennedy/president-family-portrait-closeup.jpg"
# multi_face_image_name = os.path.basename(multi_face_image_url)
# detected_faces2 = face_client.face.detect_with_url(url=multi_face_image_url)
#
# # Search through faces detected in group image for the single face from first image.
# # First, create a list of the face IDs found in the second image.
# second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
# # Next, find similar face IDs like the one detected in the first image.
# similar_faces = face_client.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)
# if not similar_faces[0]:
#     print('No similar faces found in', multi_face_image_name, '.')
#
# # Print the details of the similar faces detected
# print('Similar faces found in', multi_face_image_name + ':')
# for face in similar_faces:
#     first_image_face_ID = face.face_id
#     # The similar face IDs of the single face image and the group image do not need to match,
#     # they are only used for identification purposes in each image.
#     # The similar faces are matched using the Cognitive Services algorithm in find_similar().
#     face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
#     if face_info:
#         print('  Face ID: ', first_image_face_ID)
#         print('  Face rectangle:')
#         print('    Left: ', str(face_info.face_rectangle.left))
#         print('    Top: ', str(face_info.face_rectangle.top))
#         print('    Width: ', str(face_info.face_rectangle.width))
#         print('    Height: ', str(face_info.face_rectangle.height))
#
# # Download the image from the url
# response2 = requests.get(multi_face_image_url)
# img2 = Image.open(BytesIO(response2.content))
#
# # For each face returned use the face rectangle and draw a red box.
# draw2 = ImageDraw.Draw(img2)
# if face_info:
#     draw2.rectangle(get_rectangle(face_info), outline='red')
#
# # Display the image in the users default image browser.
# img2.show()
