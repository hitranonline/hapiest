from random import shuffle

class Colors:
    ## Some handsome hex colors taken from this stack overflow thread:
    # https://graphicdesign.stackexchange.com/questions/3682/where-can-i-find-a-large-palette-set-of-contrasting-colors-for-coloring-many-d
    # It seems like it may be a good future resource as well.
    __colors = [0xff0000, 0xb00000, 0x870000, 0x550000, 0xe4e400, 0xbaba00, 0x878700, 0x545400, 0x00ff00, 0x00b000,
          0x008700, 0x005500, 0x00ffff, 0x00b0b0, 0x008787, 0x005555, 0xb0b0ff, 0x8484ff, 0x4949ff, 0x0000ff,
          0xff00ff, 0xb000b0, 0x870087, 0x550055, 0xe4e4e4, 0xbababa, 0x878787, 0x545454]
    __trash = shuffle(__colors)
    __color_index = -1

    def __init__(self):
        self.index = 0

    def next(self):
        color = Colors.__colors[self.index % len(Colors.__colors)]
        self.index += 1
        return color