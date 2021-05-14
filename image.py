import pytesseract
from PIL import Image
from googletrans import Translator
import pyttsx3


def img(a):
    # opening an image from the source path
    img = Image.open(a)
    print(img)
    # path where the tesseract module is installed
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    # converts the image to result and saves it into result variable
    result = pytesseract.image_to_string(img)
    # write text in a text file and save it to source path
    print(result)
    for i in result:
        print(i, end=" ")
    engine = pyttsx3.init()

    rate = engine.getProperty('rate')
    engine.setProperty('rate', 125)

    x = result.split()
    t = len(x)
    engine.say("Your entered tokens are")
    for i in x:
        for b in i:
            engine.say(b)
        t = t - 1
        if t >= 1:
            engine.say("and")
    engine.runAndWait()
    if len(x) == 1:
        s = str(x[0])
        x = []
        for i in s:
            x.append(i)
    return x