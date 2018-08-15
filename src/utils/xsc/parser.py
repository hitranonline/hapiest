import sys

class XscParser:

    @staticmethod
    def parse(datastr: str):
            lines = datastr.splitlines()
            header = datastr[0]
            lines = lines[1:]
            molecule = header[0:20].strip(' ')
            min_wavenum = header[20:30].strip(' ')
            max_wavenum = header[30:40].strip(' ')
            num_points = header[40:47].strip(' ')
            temperature = header[47:54].strip(' ')
            pressure = header[54:60].strip(' ')
            max_crossvalue = header[60:70].strip(' ')
            instrument_res = header[70:75].strip(' ')
            common_name = header[75:90].strip(' ')
            reserved = header[90:94].strip(' ')
            broadener = header[94:97].strip(' ')
            reference = header[97:100].strip(' ')

            x = []
            y = []

            count = 0
            for line in lines:
                for yvalue in line.split():
                    count = count + 1
                    x.append(count)
                    y.append(yvalue)

            return {
                'x': x,
                'y': y,
                'numin': min_wavenum,
                'numax': max_wavenum,
                'molecule': molecule
            }
