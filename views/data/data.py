import base64

class stringcrafter:
    
    def string(string1):
        string2 = string1.encode("ascii")
        string3 = base64.b64decode(string2)
        string4 = string3.decode("ascii")
        return(string4)