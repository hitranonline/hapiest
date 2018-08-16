import sys

class XscParser:

    @staticmethod
    def parse(datastr: str):
        lines = datastr.splitlines()
        header = lines[0]
        lines = lines[1:]
        molecule = header[0:20].strip(' ')
        min_wavenum = float(header[20:30].strip())
        max_wavenum = float(header[30:40].strip(' '))
        num_points = int(header[40:47].strip(' '))
        temperature = float(header[47:54].strip(' '))
        pressure = float(header[54:60].strip(' '))
        max_crossvalue = header[60:70].strip(' ')
        instrument_res = header[70:75].strip(' ')
        common_name = header[75:90].strip(' ')
        reserved = header[90:94].strip(' ')
        broadener = header[94:97].strip(' ')
        reference = header[97:100].strip(' ')

        y = []

        for line in lines:
            for yvalue in line.split():
                y.append(float(yvalue))
        step = (max_wavenum - min_wavenum) / float(num_points)
        x = list(map(lambda n: min_wavenum + float(n) * step, range(0, num_points)))

        return {
            'nu': x,
            'abscoef': y,
            'header': {
                'step': step,
                'numin': min_wavenum,
                'numax': max_wavenum,
                'molecule': molecule,
                'len': num_points,
                'pressure': pressure,
                'temp': temperature
            }
        }
