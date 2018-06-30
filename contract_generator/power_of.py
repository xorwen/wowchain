import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


class PowerOfGenerator(object):

    def __init__(self, image_file_in, image_file_out, font_file):

        self.font = ImageFont.truetype(font_file, 80)
        self.font_color = (225, 112, 66)

        self.image_file_in = image_file_in
        self.image_file_out = image_file_out

    def add_names(self, name_top, name_bottom):

        print("Generating Power Of Certificate to ", self.image_file_out)

        im1 = Image.open(self.image_file_in)

        draw = ImageDraw.Draw(im1)

        draw.text((200, 850), name_top, (136, 65, 156), font=self.font)
        draw.text((1250, 850), name_top, (61, 209, 212), font=self.font)

        draw.text((200, 1500), name_bottom, (61, 209, 212), font=self.font)
        draw.text((1250, 1500), name_bottom, (136, 65, 156), font=self.font)

        im1.save(self.image_file_out)

        im1.convert('RGB').save(self.image_file_out + ".jpeg", quality=100, optimize=True, progressive=True)

        im1.convert('RGB').save(self.image_file_out + ".50q.jpeg", quality=50, optimize=True, progressive=True)

        im1.thumbnail([512, 512], PIL.Image.ANTIALIAS)

        im1.save(self.image_file_out + ".small.png")

        im1.convert('RGB').save(self.image_file_out + ".small.jpeg", quality=100, optimize=True, progressive=True)

        im1.convert('RGB').save(self.image_file_out + ".small.50q.jpeg", quality=50, optimize=True, progressive=True)




