import os
from shutil import rmtree

dirPath = os.path.dirname(os.path.abspath(__file__))
cDataDir = dirPath+"/cosmeticData"

categoryLinks = [
    "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
    "https://www.rossmann.pl/kategoria/pielegnacja-i-higiena,12001",
    # "https://www.rossmann.pl/kategoria/wlosy,13174",
    # "https://www.rossmann.pl/kategoria/mezczyzna,13224",
    # "https://www.rossmann.pl/kategoria/perfumy,13264",
    # "https://www.rossmann.pl/kategoria/dziecko,13282"
]

def clean():
    print("cleaning directory")
    rmtree(cDataDir) # remove directory with content

def get_data(rescrap = False):
    if rescrap:
        clean()
    
    # print(dirPath, cDataDir)
    if os.path.exists(cDataDir):
        return # if data present, do not scrap again
    
    os.mkdir(cDataDir)

    productLink = [] # change to queue -> faster append

    for catLink in categoryLinks:
        name = catLink[catLink.find("kategoria/") + 10: catLink.find(",")]
        # print(name)