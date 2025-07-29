import json
import base64

def encode_obj_to_base64(obj):
    json_str = json.dumps(obj)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

def decode_base64_to_obj(base64_str):
    decoded_json_str = base64.b64decode(base64_str.encode('utf-8')).decode('utf-8')
    return json.loads(decoded_json_str)

def main():
    # obj = {
    #     "action": "trim",
    #     "inputs": "/Users/ofekfeller/Downloads/test.mp4",
    #     "start": 30,
    #     "duration": 10
    # }
    # base64_str = encode_obj_to_base64(obj)
    base64_str = "eyJhY3Rpb24iOiAiY29uY2F0IiwgImlucHV0IjogW3sicmVzdWx0X3N0cmVhbSI6ICJleUpoWTNScGIyNGlPaUFpZEhKcGJTSXNJQ0pwYm5CMWRDSTZJSHNpZFhKc0lqb2dJaTlWYzJWeWN5OXZabVZyWm1Wc2JHVnlMMFJ2ZDI1c2IyRmtjeTkwWlhOMExtMXdOQ0o5TENBaWMzUmhjblFpT2lBek1Dd2dJbVIxY21GMGFXOXVJam9nTVRCOSJ9LCB7InJlc3VsdF9zdHJlYW0iOiAiZXlKaFkzUnBiMjRpT2lGaWRISnBiU0lzSUNKcGJuQjFkQ0k2SUhzaWRYSnNJam9nSWk5VmMyVnljeTl2Wm1WclptVnNiR1Z5TDBSdmQyNXNiMkZrY3k5MFpYTjBNaTV0Y0RRaWZTd2dJbk4wWVhKMElqb2dOVEFzSUNKa2RYSmhkR2x2YmlJNklERXdmUT09In1dfQ=="
    print("Encoded base64:", base64_str)
    decoded_obj = decode_base64_to_obj(base64_str)
    print("Decoded object:", decoded_obj)

if __name__ == "__main__":
    main()

