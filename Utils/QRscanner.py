from pyzbar import pyzbar
import cv2
import numpy


def scanQR(content) -> str:
    nparr = numpy.frombuffer(content, numpy.uint8)
    all_data = []
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    qrcodes = pyzbar.decode(img)
    for qrcode in qrcodes:
        qrcodeData = qrcode.data.decode('utf-8')
        if qrcode.type == "QRCODE":
            all_data.append(qrcodeData.split('&')[0])
    return all_data[0]
