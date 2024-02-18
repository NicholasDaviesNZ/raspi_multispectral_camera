from flask import Flask, request, jsonify, send_file
from picamera2 import Picamera2
import time
import os
import json
import PIL
import piexif
import io
from zipfile import ZipFile


app = Flask(__name__)
picam2 = Picamera2()
config = picam2.create_still_configuration(main={})
picam2.configure(config)


# helper function to get the metadata tag for the given label
#def get_tag_number(tag_name, tag_dict=piexif.TAGS):
#    for meta_type, meta_dict in tag_dict.items():
#        for number, details in meta_dict.items():
#            if details['name'] == tag_name:
#                return number
#    return None

#def replace_labels_with_numbers(data):
#    return {get_tag_number(key): value if not isinstance(value, tuple) else tuple(value) for key, value in data.items()}
 

if not os.path.exists('./captures/'):
    os.makedirs('./captures/')

@app.route('/capture', methods=['POST'])
def capture_photo():
    try:
        # recive input metadata
        print('enter')
        input_metadata = request.json or {}
        print(input_metadata) # print for debug
        filename = input_metadata.get('file_name') # get the file name to save everything as
        print(filename) #print it for debug - should put an if with a def filename here based on what is already int he captures folder

         # define the local directories for storing images
        captures_dir = f"/home/pi_zero_2/webserver/captures/"
        metafile_path = f"/home/pi_zero_2/webserver/captures/{filename}_metadata.json"

        # set camera parameters based on what is pasted in with the metadata
        picam2.set_controls({'AwbEnable':input_metadata['AWB'], 'AnalogueGain':input_metadata['analogue_gain'], 'ColourGains':input_metadata['colour_gains']})
        print('start capture')
        picam2.start()
        #capture metadata and image
        captured_metadata = picam2.capture_metadata('main')
        pil_image = picam2.capture_image('main')
       # captured_metadata['ExposureTime'] = int(1/(captured_metadata['ExposureTime']/1000000.0))
        #print(pil_image.getexif())
       # zeroth_ifd = {piexif.ImageIFD.Make: u"RaspberryPi",
        #      piexif.ImageIFD.DateTime: input_metadata['timestamp'],
        #      piexif.ImageIFD.XResolution: (96, 1),
         #     piexif.ImageIFD.YResolution: (96, 1),
          #    piexif.ImageIFD.Software: u"piexif"
          #    }
        #exif_ifd = {piexif.ExifIFD.DateTimeOriginal: input_metadata['timestamp'],
       #     piexif.ExifIFD.LensMake: u"LensMake",
       #     piexif.ExifIFD.Sharpness: 65535,
       #     piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
       #     piexif.ExifIFD.ExposureTime:(1, captured_metadata.pop('ExposureTime'))
       #     }
       # gps_ifd = {piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        #   piexif.GPSIFD.GPSAltitudeRef: 1
        #   }
       # first_ifd = {piexif.ImageIFD.Make: u"RaspberryPi",
            # piexif.ImageIFD.XResolution: (40, 1),
            # piexif.ImageIFD.YResolution: (40, 1),
            # piexif.ImageIFD.Software: u"piexif"
             #}

       # exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "GPS":gps_ifd, "1st":first_ifd}
       # exif_bytes = piexif.dump(exif_dict)        
       # labeled_metadata = {}
       # labeled_metadata['CalibrationIlluminant1'] = captured_metadata.pop('Lux')
       # labeled_metadata['FocalLength'] = captured_metadata.pop('FocusFoM')
       # labeled_metadata['DateTimeOriginal'] = captured_metadata.pop('SensorTimestamp')
       # labeled_metadata['ExposureTime'] = captured_metadata.pop('FrameDuration')

       # metadata = replace_labels_with_numbers(labeled_metadata)
        #metadata = json.dumps(metadata).encode('utf-8')
       # bytes_metadata = piexif.dump(metadata)
        picam2.stop()
        metadata = {**input_metadata, **captured_metadata}
        print(metadata)
        print('end capture')
        # save metadata as a json file
        with open(metafile_path, 'w') as json_file:
            json.dump(metadata, json_file)
        print('start split')
        # Split the RGB image into individual channels
        r, g, b = pil_image.split()
        print('start save')
        # Save each channel as a separate monochrome image
        r.save(f"{captures_dir}{filename}_rededge.jpg")
        g.save(f"{captures_dir}{filename}_midred.jpg")
        b.save(f"{captures_dir}{filename}_nir.jpg")
        print('start compression')
        # send everything to a zip file for transfer to main pi
        zip_data = io.BytesIO()
        with ZipFile(zip_data, 'w') as zipf:
            zipf.write(metafile_path, arcname=f'{filename}_noir_metadata.json')
            zipf.write(f'{captures_dir}{filename}_rededge.jpg', arcname=f'{filename}_rededge.jpg')
            zipf.write(f'{captures_dir}{filename}_midred.jpg', arcname=f'{filename}_midred.jpg')
            zipf.write(f'{captures_dir}{filename}_nir.jpg', arcname=f'{filename}_nir.jpg')
        zip_data.seek(0)
        print('image captured starting send')
        # Send the zip file as a response
        return send_file(zip_data, attachment_filename='image.zip', as_attachment=True, mimetype='application/zip')

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
