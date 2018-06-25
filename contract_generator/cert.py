
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import datetime


class CertGenerator(object):

    def __init__(self, image_file_in, image_file_out, font_file):

        self.font = ImageFont.truetype(font_file, 80)
        self.font_small = ImageFont.truetype(font_file, 40)


        self.font_color = (136, 65, 156)

        self.image_file_in = image_file_in
        self.image_file_out = image_file_out

        self.im1 = Image.open(self.image_file_in)
        self.draw = ImageDraw.Draw(self.im1)

    def add_names(self, name_top, name_bottom, name_top_id, name_bottom_id):

        self.draw.text((200, 1000), name_top, (136, 65, 156), font=self.font)
        self.draw.text((1250, 1000), name_bottom, (136, 65, 156), font=self.font)

        self.draw.text((200, 1150), name_top_id, (61, 209, 212), font=self.font_small)
        self.draw.text((1250, 1150), name_bottom_id, (61, 209, 212), font=self.font_small)

    def add_contract_id(self, contract_id):

        self.draw.text((200, 2050), contract_id, (136, 65, 156), font=self.font)

    def add_expiration_date(self, months):

        end_date = datetime.datetime.now() + datetime.timedelta(months*365/12)

        cnt_text = "Both parties promised each other that relationship ends "+end_date.strftime("%-d. %-m. %Y")

        self.draw.text((200, 1500), cnt_text, (70, 70, 70), font=self.font_small)

    def save(self):

        print("Saving Certificate to ",self.image_file_out)

        self.im1.save(self.image_file_out)






