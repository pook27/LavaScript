def b_and(a,b):
    out = ""
    for i in range(len(a)):
        out += str(int(a[i]) & int(b[i]))
    return out

def b_or(a,b):
    out = ""
    for i in range(len(a)):
        out += str(int(a[i]) | int(b[i]))
    return out

def b_not(a):
    out = ""
    for i in range(len(a)):
        out+= "1" if a[i]=="0" else "0"
    return out

def alu(x,y,zx,nx,zy,ny,f,no):
    if zx: x = "0"*len(x)

    if nx: x = b_not(x)

    if zy: y = "0"*len(y)

    if ny: y = b_not(y)

    if f: out = bin(int(x,2) + int(y,2))[2:].zfill(len(x))[-len(x):]

    else: out = b_and(x,y)

    if no: out = b_not(out)

    if len(out) > len(x): out = out[1:]

    zr = "1" if int(out,2) == 0 else "0"

    ng = "1" if out[0] == "1" else "0"

    return out,zr,ng
