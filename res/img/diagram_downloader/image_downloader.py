import urllib.request
import xlrd

book = xlrd.open_workbook("mols_all.xlsx")
sheet = book.sheet_by_index(0)

url_prefix = "https://cactus.nci.nih.gov/chemical/structure/"
url_suffix = "/image?width=500&height=500&linewidth=2&symbolfontsize=16"
path_prefix = ".\\structural_diagrams"
for i in range(sheet.nrows):
    if not i == 0 and not sheet.cell_value(i, 0) == "" and not sheet.cell_value(i, 6) == "":
        inchi = sheet.cell_value(i, 6)
        filenum = sheet.cell_value(i, 0)
        #print(inchi)
        #print(int(filenum))
        inchifixed = inchi.replace('(', '%28').replace(')', '%29')
        #print(inchifixed)
        url = url_prefix + inchifixed + url_suffix
        #print(url)
        filename = str(int(filenum)) + ".jpg"
        path = path_prefix + "\\" + filename
        urllib.request.urlretrieve(url, path)