from PIL import Image

class Y4M():

    def __init__(self, width, height, f_num, f_den, interlace, aspect_ratio, colour_space, optional=None):
        self.width = int(width)
        self.height = int(height)
        self.f_num = int(f_num)
        self.f_den = int(f_den)
        self.interlace = interlace
        self.aspect_ratio = aspect_ratio
        self.colour_space = colour_space
        self.optional = optional
        self.frames = []

    def add_frame_data(self, data):
        self.frames.append(data)

    def render_frame(self, frame_number):
        selected_frame = self.frames[frame_number]
        pixel_grid = []

        if self.colour_space.startswith("420"):
            width, height = self.width, self.height
            #print(len(selected_frame))
            y_block = selected_frame[:width*height]
            u_block = selected_frame[width*height:int(width*height+width*height/4)]
            v_block = selected_frame[int(width*height+width*height/4):]
            #print(len(y_block), len(u_block), len(v_block))


            img = Image.new( 'RGB', (self.width,self.height), "black") # create a new black image
            pixels = img.load()

            for j in range(height):
                column = []
                for i in range(width):
                    #print(i,j)
                    k = j*self.width+i
                    y = y_block[k]
                    block_num = int(int(j/2)*self.width/2) + int(i/2)
                    # if block_num == 1:
                    #     print(i,j,block_num)
                    u = u_block[block_num]
                    v = v_block[block_num]

                    #print(y,u,v)
                    column.append(self.yuvToRGB(y,u,v))
                    colour = column[i]
                    pixels[i,j] = (colour[0], colour[1], colour[2])

                pixel_grid.append(column)

            img.show()

    def yuvToRGB(self, y,u,v):
        rTmp = y + (1.370705 * (v-128));
        gTmp = y - (0.698001 * (v-128)) - (0.337633 * (u-128));
        bTmp = y + (1.732446 * (u-128));

        clamp = lambda x: 0 if x < 0 else (255 if x>255 else int(x))

        return clamp(rTmp),clamp(gTmp), clamp(bTmp)
