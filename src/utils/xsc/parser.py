import sys

class a_cross_parser:

    with open(sys.argv[1], 'r') as data:
        header = data.readline()
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

    def a_cross_parse(file):
        with open(file, 'r') as datafile:
            x = []
            y = []
            count = 0
            header = datafile.readline()
            for line in datafile:
                for yvalue in line.split():
                    count = count + 1
                    x.append(count)
                    y.append(yvalue)
            return (x, y)

    x, y = a_cross_parse(sys.argv[1])