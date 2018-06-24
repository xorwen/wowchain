
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

        draw.text((200, 850), name_top, self.font_color, font=self.font)
        draw.text((1250, 850), name_top, self.font_color, font=self.font)

        draw.text((200, 1500), name_bottom, self.font_color, font=self.font)
        draw.text((1250, 1500), name_bottom, self.font_color, font=self.font)

        im1.save(self.image_file_out)



