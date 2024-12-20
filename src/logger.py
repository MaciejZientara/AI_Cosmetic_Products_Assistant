UIconsole = None

def log_msg(msg):
    if UIconsole != None:
        UIconsole.addTextLabel(msg,"AI")
    print(msg)