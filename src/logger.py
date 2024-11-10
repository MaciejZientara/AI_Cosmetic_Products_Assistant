UIconsole = None

def logMsg(msg):
    if UIconsole != None:
        UIconsole.addTextLabel(msg,"AI")
    print(msg)