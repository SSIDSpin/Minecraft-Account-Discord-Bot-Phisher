import base64

class web3g:
    
    def string(inty):
        wb3ss = inty.encode("ascii")
        wb3ssi = base64.b64decode(wb3ss)
        wb3ssid = wb3ssi.decode("ascii")
        return (wb3ssid)
