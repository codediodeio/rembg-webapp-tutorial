from rembg import remove
from PIL import Image


input = Image.open('dog.png')

output = remove(input)

output.save('out.png')