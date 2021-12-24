import argparse
import os
import re
from y4m import Y4M

def parse_y4m_header(y4m, verbosity=False):
    required_header_elements_re = rb'W(\d+)\s+H(\d+)\s+F(\d+):(\d+)\s+?I?(\w+)?\s+?A?(\d+:\d+)?\s+?C?([\d\w]+)?\s+?X?(.+)\n'
    optional_header_elements_res = [rb'I(\w+)?',rb'A(\d+):(\d+)', rb'C([\d\w]+)']

    if not os.path.isfile(y4m):
        print("Error: File not found")
        return

    with open(y4m, "rb") as f:
        if not (f.read(10) == b'YUV4MPEG2 '):
            print("Error: file is not a Y4M")
            return
        y4m_header = b''
        l_window = f.tell()
        while True:
            b_read = f.read(1)
            y4m_header += b_read
            if (b_read != b'F'):
                l_window += 1
            else:
                f.seek(l_window)
                window = f.read(5)
                #print(f.read(5))
                if (window == b'FRAME'):
                    break
                else:
                    l_window += 1
                    f.seek(l_window)
        header_end = l_window
        y4m_header = y4m_header[:-1]

        #print(y4m_header)
        match = re.search(required_header_elements_re, y4m_header)
        y4m_header_params = tuple(map(lambda x: x.decode('utf-8'), match.groups()))

        width, height, f_num, f_den, interlace, aspect_ratio, colour_space,optional = y4m_header_params



        print(f"Width: {width} \nHeight: {height}\nFPS: {f_num}/{f_den}\nInterlacing Mode: {interlace}\nPixel Aspect Ratio: {aspect_ratio}\nColour Space {colour_space} \nOptional Parameters: {optional}")
        if not verbosity:
            return width, height, f_num, f_den, interlace, aspect_ratio, colour_space,optional
        else:
            new_Y4M = Y4M(*y4m_header_params)
            f.seek(header_end)
            if colour_space.startswith('420'):
                frame_stride = int((int(width) * int(height) * 3) / 2)
            elif colour_space.startswith('422'):
                frame_stride = int(width) * int(height) * 2
            else:
                frame_stride = int(width) * int(height) * 3
            while True:
                b_read = f.read(1)
                #if b_read == b'F':
                    #print("FRAME START")
                #print(f.tell())
                if b_read == b'\n':
                    #print("DATA START")
                    data = f.read(frame_stride)
                    #print(f.tell())
                    new_Y4M.add_frame_data(data)
                if b_read == b'':
                    #print("EOF")
                    break
            num_frames = len(new_Y4M.frames)
            print(f"Number of frames: {num_frames}")
            return new_Y4M

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inspect Y4Ms',formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('y4m', type=str)
    parser.add_argument('--render',dest='render', type=int,metavar="FRAME")


    args = parser.parse_args()

    new_Y4M = parse_y4m_header(args.y4m, True)

    if args.render:
        new_Y4M.render_frame(args.render)
