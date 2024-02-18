from flask import Flask, request, jsonify, send_file
from picamera2 import Picamera2
import time
import os
import json
import io

app = Flask(__name__)
picam2 = Picamera2()
config = picam2.create_still_configuration(main={})
picam2.configure(config)

@app.route('/capture', methods=['POST'])
def capture_photo():
    try:
        # recive input metadata
        print('enter')
        input_metadata = request.json or {}
        print(input_metadata) # print for debug

        # set camera parameters based on what is pasted in with the metadata
        picam2.set_controls({'AwbEnable':input_metadata['AWB'], 'AnalogueGain':input_metadata['analogue_gain'], 'ColourGains':input_metadata['colour_gains']})
        picam2.start()
        #capture metadata and image
        captured_metadata = picam2.capture_metadata('main')
        image_array = picam2.capture_array('main')

        picam2.stop()

        # Split the RGB image into individual channels
        r = image_array[:, :, 0]
        g = image_array[:, :, 1]
        b = image_array[:, :, 2]

        return(jsonify({
           "AnalogueGain": captured_metadata["AnalogueGain"],
           "ExposureTime": captured_metadata["ExposureTime"],
           "RedMean": r.mean(),
           "GreenMean": g.mean(),
           "BlueMean": b.mean()
        }))

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

