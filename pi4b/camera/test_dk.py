from dronekit import connect, VehicleMode
import RPi.GPIO as GPIO
import busio
import board
import adafruit_mlx90640
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from PIL import Image
import numpy as np
import time
import requests
import json
import zipfile
import os
import concurrent.futures
from fractions import Fraction
import math
import pyexiv2
from scipy.ndimage import zoom
pyexiv2.xmp.register_namespace('/drone-dji/', 'drone-dji')
pyexiv2.xmp.register_namespace('/Camera/', 'Camera')

file_colour_names_list = ('red', 'green', 'blue', 'rededge', 'midred', 'nir', 'rgb', 'lwir')

gpio_pin = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# setting up i2c for the thermal camera
# Specify the correct I2C address for your MLX90640 sensor
mlx_address = 0x33  # Change this to the actual I2C address of your sensor
i2c = busio.I2C(board.SCL, board.SDA)  # setup I2C
# Create the MLX90640 object with the specified I2C address
mlx = adafruit_mlx90640.MLX90640(i2c, address=mlx_address)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ  # set refresh rate

# define the static urls for each pi zero running a web server
pi_zero_1_api_url = "http://10.0.1.11:5000/capture" # vis image capture
pi_zero_2_api_url = "http://10.0.1.12:5000/capture" # noir image capture
pi_zero_3_api_url = "http://10.0.1.13:5000/capture" # vis upfacing
pi_zero_4_api_url = "http://10.0.1.14:5000/capture" # noir upfacing

# base metadata for all cameras
metadata_base = {
    "AWB":False,
    "colour_gains": (1.0,1.0),
    "analogue_gain": 30.0,
}

# should consider using a single metadata obj and do a call to the verious pi zeros at the start, 
# telling them to start streaming the cameras with the given properties, this sould speed up the capture process
logger.info('connecting')
print('connecting')
# Connect to the Vehicle (modify the connection string accordingly)
vehicle = connect('/dev/serial0', wait_ready=True, baud=57600)
logger.info('connected')
print('connected')


# function to check that the required directorys exist
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# function to ask the pi zero to take an image and pass it back, takes in the url of the web server on the desired pi, and the metadata dict
# passes back a zip file (over writen with each call to that pi zero) and saves the unique images and meta data to the assocated sub directory
def call_pi_zero(api_url, metadata):
    """
    Function to call the downward facing pi zero cameras and instruct them to take and image and retrieve it. 
    It takes in the url for the particular pi zero, and the metadata required for the image to be taken
    """
    # Send a POST request with metadata
    response = requests.post(api_url, json=metadata, stream=True)
    # Save the received image file
    with open(f"received_{metadata['image_type']}.zip", "wb") as f:
        for chunk in response.iter_content(chunk_size=512*1024):# Make a POST request to the server
            f.write(chunk)

    ensure_directory_exists(f"images")     
    with zipfile.ZipFile(f"received_{metadata['image_type']}.zip", 'r') as zip_ref:
        # Extract all contents to the specified directory
        zip_ref.extractall(f"images")

    # Print the server's response
    logger.info(f'image capature complete {api_url}')
    print(f'done image capture {api_url}')
    print(response)

def call_pi_zero_upfacing(api_url, metadata):
    """
    Function to call the upward facing pi zero cameras and instruct them to take an image and process it, 
    returning only the required data, band wise intensity and camera exposure settings 
    """
    try:
        # Send a POST request with metadata
        response = requests.post(api_url, json=metadata)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON data from the response
        returned_upfacing_data = response.json()

        # Return the data as a Python dictionary
        print(f'upfacing done {api_url}')
        return(returned_upfacing_data)

    except requests.exceptions.RequestException as e:
        logger.info("Error: {str(e)}")
        print(f"Error: {str(e)}")
        return {"error": str(e)}

def print_gps_status():
    # Print GPS status
    print("GPS Status:")
    print("Fix Type: {}".format(vehicle.gps_0.fix_type))
    print("Number of Satellites: {}".format(vehicle.gps_0.satellites_visible))
    print("Latitude: {}".format(vehicle.location.global_frame.lat))
    print("Longitude: {}".format(vehicle.location.global_frame.lon))
    print("Altitude: {} meters".format(vehicle.location.global_frame.alt))
    print("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
    print("Altitude relative to home_location: %s" % vehicle.location.global_relative_frame.alt)
    print('Battery level: %s' % vehicle.battery.level)
    print('Battery voltage: %s' % vehicle.battery.voltage)
    print('Battery current: %s' % vehicle.battery.current) 



def do_band_removals(noir_upfacing, vis_upfacing, noir_exposure, vis_exposure, vis_to_noir_upfacing_ratio, noir_upfacing_exposure, vis_upfacing_exposure, cur_time):
    """
    this is the main camera function which takes all of the retrieved raw images and does the required manipulations to get them 
    to a standardized level of exposures etc. based on the exposures, gains etc. and the upfacing cameras it does band wise corrections and saves them 
    as band wise gray scale images
    """
    
    # load all of the images we need as arrays
    #vis_to_noir_ratio = noir_exposure/vis_exposure # add check that the raio is below 1 - converting vis into the noir exposire
    #vis_to_noir_upfacing_ratio = noir_upfacing_exposure/vis_upfacing_exposure
    # the above two convert into the noir exposure, below converts the downfacing into the upfacing exposure
    #down_to_upfacing_ratio = noir_upfacing_exposure/noir_exposure 

    down_vis_to_up_noir = noir_upfacing_exposure/vis_exposure
    down_noir_to_up_noir = noir_upfacing_exposure/noir_exposure
    up_vis_to_up_noir = noir_upfacing_exposure/vis_upfacing_exposure

    vis_red = (np.array(Image.open(f'images/PiMS_{cur_time}_red.jpg')))*down_vis_to_up_noir
    vis_green = (np.array(Image.open(f'images/PiMS_{cur_time}_green.jpg')))*down_vis_to_up_noir
    vis_blue = (np.array(Image.open(f'images/PiMS_{cur_time}_blue.jpg')))*down_vis_to_up_noir
    noir_red = (np.array(Image.open(f'images/PiMS_{cur_time}_rededge.jpg')))*down_noir_to_up_noir
    noir_green = (np.array(Image.open(f'images/PiMS_{cur_time}_midred.jpg')))*down_noir_to_up_noir
    noir_blue = (np.array(Image.open(f'images/PiMS_{cur_time}_nir.jpg')))*down_noir_to_up_noir

#    vis_red = (np.array(Image.open(f'images/PiMS_{cur_time}_red.jpg'))*vis_to_noir_ratio)*down_to_upfacing_ratio
#    vis_green = (np.array(Image.open(f'images/PiMS_{cur_time}_green.jpg'))*vis_to_noir_ratio)*down_to_upfacing_ratio
#    vis_blue = (np.array(Image.open(f'images/PiMS_{cur_time}_blue.jpg'))*vis_to_noir_ratio)*down_to_upfacing_ratio
#    noir_red = (np.array(Image.open(f'images/PiMS_{cur_time}_rededge.jpg')))*down_to_upfacing_ratio
#    noir_green = (np.array(Image.open(f'images/PiMS_{cur_time}_midred.jpg')))*down_to_upfacing_ratio
#    noir_blue = (np.array(Image.open(f'images/PiMS_{cur_time}_nir.jpg')))*down_to_upfacing_ratio
    # subtract the vis pixels from the noir pixels to get only wavelengths larger than 700nm
    noir_red = noir_red-vis_red
    noir_green = noir_green-vis_green
    noir_blue = noir_blue-vis_blue
    # subtract the blue channel from the red and green channels to remove the wavelengths over 800nm
    noir_red = noir_red-noir_blue
    noir_green = noir_green-noir_blue

    # now how to get the return intensity
    vis_red_upfacing = vis_upfacing['RedMean']*up_vis_to_up_noir 
    vis_green_upfacing = vis_upfacing['GreenMean']*up_vis_to_up_noir 
    vis_blue_upfacing = vis_upfacing['BlueMean']*up_vis_to_up_noir 
    noir_red_upfacing = noir_upfacing['RedMean'] - vis_red_upfacing
    noir_green_upfacing = noir_upfacing['GreenMean'] - vis_green_upfacing
    noir_blue_upfacing = noir_upfacing['BlueMean'] - vis_blue_upfacing
    
    noir_red_upfacing = noir_red_upfacing - noir_blue_upfacing
    noir_green_upfacing = noir_green_upfacing - noir_blue_upfacing

    # calculate the ratio to go from upfacing to downfacing exposure for each band
    # should check all of these are below 255
    red = (vis_red/vis_red_upfacing)*255
    green = (vis_green/vis_green_upfacing)*255
    blue = (vis_blue/vis_blue_upfacing)*255
    rededge = (noir_red/noir_red_upfacing)*255
    midred = (noir_green/noir_green_upfacing)*255
    nir = (noir_blue/noir_blue_upfacing)*255

    Image.fromarray(red.astype(np.uint8)).save(f'images/PiMS_{cur_time}_red.jpg')
    Image.fromarray(green.astype(np.uint8)).save(f'images/PiMS_{cur_time}_green.jpg')
    Image.fromarray(blue.astype(np.uint8)).save(f'images/PiMS_{cur_time}_blue.jpg')
    Image.fromarray(rededge.astype(np.uint8)).save(f'images/PiMS_{cur_time}_rededge.jpg')
    Image.fromarray(midred.astype(np.uint8)).save(f'images/PiMS_{cur_time}_midred.jpg')
    Image.fromarray(nir.astype(np.uint8)).save(f'images/PiMS_{cur_time}_nir.jpg')

    
#    Image.fromarray(vis_red.astype(np.uint8)).save(f'images/PiMS_{cur_time}_red.jpg')
#    Image.fromarray(vis_green.astype(np.uint8)).save(f'images/PiMS_{cur_time}_green.jpg')
#    Image.fromarray(vis_blue.astype(np.uint8)).save(f'images/PiMS_{cur_time}_blue.jpg')
#    Image.fromarray(noir_red.astype(np.uint8)).save(f'images/PiMS_{cur_time}_rededge.jpg')
#    Image.fromarray(noir_green.astype(np.uint8)).save(f'images/PiMS_{cur_time}_midred.jpg')
#    Image.fromarray(noir_blue.astype(np.uint8)).save(f'images/PiMS_{cur_time}_nir.jpg')

def do_upfacing_band_removals(vis_to_noir_upfacing_ratio, vis_upfacing, noir_upfacing):
    """
    processing of the upfacing cameras, it normalizes the values form each band in the cameras. This data is used to normalize
    reflectance from the downward facing cameras to make them more stable from image to image. 
    """
    #convert the vis to the same exposure level as the noir
    vis_upfacing['RedMean'] = vis_upfacing['RedMean']*vis_to_noir_upfacing_ratio
    vis_upfacing['GreenMean'] = vis_upfacing['GreenMean']*vis_to_noir_upfacing_ratio
    vis_upfacing['BlueMean'] = vis_upfacing['BlueMean']*vis_to_noir_upfacing_ratio

    noir_red = noir_upfacing['RedMean']-vis_upfacing['RedMean']
    noir_green = noir_upfacing['GreenMean']-vis_upfacing['GreenMean']
    noir_blue = noir_upfacing['BlueMean']-vis_upfacing['BlueMean']
    # subtract the blue channel from the red and green channels to remove the wavelengths over 800nm
    noir_red = noir_red-noir_blue
    noir_green = noir_green-noir_blue

    upfacing_band_intensities = {
        'red':vis_upfacing['RedMean'],
        'green':vis_upfacing['GreenMean'],
        'blue': vis_upfacing['BlueMean'],
        'rededge': noir_red,
        'midred': noir_green,
        'nir': noir_blue,
    }

    return(upfacing_band_intensities)


# these functions convert the pixhawk lats and longs to a from a decinmal degree forma
def dec_to_deg(value):
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return ((Fraction((deg), 1), Fraction((min), 1), Fraction((round(sec * 100000)), 100000)))

def ref_long(value):
    if value < 0:
        loc_value = 'W'
    else:
        loc_value = 'E'
    return (loc_value)

def ref_lat(value):
    if value < 0:
        loc_value = 'S'
    else:
        loc_value = 'N'
    return (loc_value)

def radians_to_degrees(radians):
    degrees = math.degrees(radians)
    return (degrees + 360) % 360

def get_FC_data():
    """
    connect to pixhawk and get the current location and vehicle orientation
    """
    time.sleep(0.5) # wait to line up the call to the FC with the camera exposure times more correctly, may need to change later
    FC_data_dict = {
        'GPSLatitude':vehicle.location.global_frame.lat,
        'GPSLatitudeRef':vehicle.location.global_frame.lat,
        'GPSLongitude':vehicle.location.global_frame.lon,
        'GPSLongitudeRef': vehicle.location.global_frame.lon,
        'GPSAltitude':vehicle.location.global_frame.alt,
        'GPSRelativeAltitude':vehicle.location.global_relative_frame.alt,
        'Yaw':vehicle.attitude.yaw,
        'Pitch':vehicle.attitude.pitch,
        'Roll':vehicle.attitude.roll,
        }
    logger.info("got FC data")
    print('got FC data')
    return(FC_data_dict)

def alt_to_alt(alt):
    """
    converting altitude from the pixhawk format to readable 
    """
    if alt is None or alt <= 0:
        return Fraction(0, 1000)
    else:
        return Fraction(round(alt * 1000), 1000)

def capture_thermal(cur_time):
    """
    function which is called to get the thermal image - note this is causing some issues still
    """
    logger.info("capturing thermal image")
    print("capturing thermal image")

    frame = np.zeros((24*32,))  # setup array for storing all 768 temperatures

    try:
        mlx.getFrame(frame)  # read MLX temperatures into frame var
        # Create a 2D array to represent the temperature grid
        temperature_grid = np.reshape(frame, (24, 32))
        # potentually do upscaling here
        upsampled_grid = temperature_grid #zoom(temperature_grid, (10, 10), order=1)
        # do conversion to uint16 so it can be saved as a tif and so that it reproduces upsampled_grid when run though:
        #   image = image.astype("float32")
        #    image -= (273.15 * 100.0) # Convert Kelvin to Celsius
        #    image *= 0.01
        upsampled_grid_kelvin = (upsampled_grid+273.15)*100 
        
        upsampled_grid_kelvin_uint16 = upsampled_grid_kelvin.astype(np.uint16)

        # Create a PIL Image object from the NumPy array
        thermal_image = Image.fromarray(upsampled_grid_kelvin_uint16)

        thermal_image.save(f"images/PiMS_{cur_time}_lwir.tif")
        logger.info('saved thermal image')
        print('saved thermal image')
        # Leaving this bit for now until the above is completed
        # Create a colormap and normalize to map temperatures to colors
        #norm = Normalize(vmin=np.min(frame), vmax=np.max(frame))
        #colormap = cm.viridis
        # Apply colormap to the temperature grid
        #colorized_image = colormap(norm(temperature_grid))

        # Save the image as a JPG file
        #plt.imsave(f"images/PiMS_{cur_time}_lwir.jpg", colorized_image)
        return()

    except Exception as e:
        logger.info(f'Error: {e}')
        print(f'Error: {e}')

def add_metadata(cur_time, cur_time_string, FC_data_dict):
    """
    for each image this file adds the metadata of where the image was taken from, along with bands etc
    """
    logger.info('adding metadata')
    print('adding metadata')
    for image_colour in file_colour_names_list:
        if image_colour == 'lwir':
            metadata = pyexiv2.ImageMetadata(f'images/PiMS_{cur_time}_{image_colour}.tif')
            metadata.read()
            metadata['Exif.Image.Make'] = "MicaSense" 
            metadata['Exif.Image.Model'] = "Altum"
        else:
            metadata = pyexiv2.ImageMetadata(f'images/PiMS_{cur_time}_{image_colour}.jpg')
            metadata.read()
        metadata['Exif.Photo.DateTimeOriginal'] = cur_time_string
        metadata['Exif.GPSInfo.GPSLatitudeRef'] = ref_lat(FC_data_dict['GPSLatitudeRef'])
        metadata['Exif.GPSInfo.GPSLatitude'] = dec_to_deg(FC_data_dict['GPSLatitude'])
        metadata['Exif.GPSInfo.GPSLongitudeRef'] = ref_long(FC_data_dict['GPSLongitudeRef'])
        metadata['Exif.GPSInfo.GPSLongitude'] = dec_to_deg(FC_data_dict['GPSLongitude'])
        metadata['Exif.GPSInfo.GPSAltitude'] = alt_to_alt(FC_data_dict['GPSAltitude']),
        metadata['Exif.GPSInfo.GPSAltitudeRef'] = '0'

        metadata['Xmp.drone-dji.GpsLatitude'] = str(FC_data_dict['GPSLatitude'])
        metadata['Xmp.drone-dji.GpsLongitude'] = str(FC_data_dict['GPSLongitude'])
        metadata['Xmp.drone-dji.AbsoluteAltitude'] = str(FC_data_dict['GPSAltitude'])
        metadata['Xmp.drone-dji.RelativeAltitude'] = str(FC_data_dict['GPSRelativeAltitude'])

        metadata['Xmp.Camera.BandName'] = image_colour
        metadata['Xmp.Camera.Yaw'] = radians_to_degrees(FC_data_dict['Yaw'])
        metadata['Xmp.Camera.Pitch'] = radians_to_degrees(FC_data_dict['Pitch'])
        metadata['Xmp.Camera.Roll'] = radians_to_degrees(FC_data_dict['Roll'])
        metadata.write()

def catpure_images():
    """
    Main function which is run continuously and coordinates everything based on the GPIO input from the pixhawk
    """
    while True:
        input_state = GPIO.input(gpio_pin)
        #voltage = GPIO.input(gpio_pin)
        #print(f"Input State: {input_state}, Voltage: {voltage}")

        if input_state > 0:
            start_time = time.time()
            cur_time = int(time.time())
            cur_time_string = time.strftime("%Y:%m:%d %H:%M:%S")
            logger.info(cur_time_string)
            logger.info("print_gps_status")
            print_gps_status()
            metadata_vis_test = {
                "file_name": f"PiMS_{cur_time}",
                "AWB":False,
                "image_type":'visual',
                "colour_gains": (1.0,1.0),
                "analogue_gain": 30.0,
                "timestamp": cur_time_string  # note can get number of secs since unix epoch like this: int(time.time())
                }
            metadata_noir_test = {
                "file_name": f"PiMS_{cur_time}",
                "AWB":False,
                "image_type":'noir',
                "colour_gains": (1.0,1.0),
                "analogue_gain": 30.0,
                "timestamp": cur_time_string  # note can get number of secs since unix epoch like this: int(time.time())
                }
            logger.info('sending capture request')
            print('sending capture request')
            # Create a ThreadPoolExecutor with 2 worker threads to call the two pi zeros at the same time
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
                # Define the tasks for each Pi Zero
                task1 = executor.submit(call_pi_zero, pi_zero_1_api_url, metadata_vis_test)
                task2 = executor.submit(call_pi_zero, pi_zero_2_api_url, metadata_noir_test)
                task3 = executor.submit(get_FC_data)
                task4 = executor.submit(capture_thermal, cur_time)
                task5 = executor.submit(call_pi_zero_upfacing, pi_zero_3_api_url, metadata_base)
                task6 = executor.submit(call_pi_zero_upfacing, pi_zero_4_api_url, metadata_base)
                
                # Wait for both tasks to complete
                concurrent.futures.wait([task1, task2, task3, task4, task5, task6])
            # get the location info dict from task3
            FC_data_dict = task3.result()
            logger.info(FC_data_dict)
            print(FC_data_dict)
            vis_upfacing = task5.result()
            print(vis_upfacing)
            noir_upfacing = task6.result()
            print(noir_upfacing)
            # get each image and to the calcs that need to be done on it
            # load noir metadata and get and calculate teh exposure value
            with open((f'images/PiMS_{cur_time}_noir_metadata.json'), 'r') as file_noir:
                metadata_noir = json.load(file_noir)
            noir_exposure = metadata_noir["AnalogueGain"]*(metadata_noir["ExposureTime"])

            # load vis metadata and work out the exposure correction factor
            with open((f'images/PiMS_{cur_time}_vis_metadata.json'), 'r') as file_vis:
                metadata_vis = json.load(file_vis)
            vis_exposure = metadata_vis["AnalogueGain"]*(metadata_vis["ExposureTime"])

            # get the difference in exposure for the upfacing cameras
            noir_upfacing_exposure = noir_upfacing["AnalogueGain"]*noir_upfacing["ExposureTime"]
            vis_upfacing_exposure = vis_upfacing["AnalogueGain"]*vis_upfacing["ExposureTime"]

            # get the value to multiply the noir image by to get it 
            vis_to_noir_ratio = noir_exposure/vis_exposure # add check that the raio is below 1

            # get the ratio for the upfacing cameras
            vis_to_noir_upfacing_ratio = noir_upfacing_exposure/vis_upfacing_exposure

            #metadata_vis["ExposureTime"] = metadata_vis["ExposureTime"]*vis_to_noir_ratio
            # Save the updated metadata back to the JSON file
            #with open(f'images/vis_{cur_time}_metadata.json', 'w') as file_vis:
            #    json.dump(metadata_vis, file_vis)  # Use indent for pretty formatting, adjust as needed
            # convert the vis data to the same exposure value as the noir data
            # load up the 3 vis images and multiply the arrays by vis_to_noir_ratio
            # pixelwise subtract the vis channels from the noir channels
            # subtract the remaining blue chanel of teh noir image from the red and green channels
            do_band_removals(noir_upfacing, vis_upfacing, noir_exposure, vis_exposure, vis_to_noir_upfacing_ratio, noir_upfacing_exposure, vis_upfacing_exposure, cur_time)
            # do the equivilent for upfacing
            #upfacing_band_intensities = do_upfacing_band_removals(vis_to_noir_upfacing_ratio, vis_upfacing, noir_upfacing)

            # create new metadata
            # save all images with metadata
            add_metadata(cur_time, cur_time_string, FC_data_dict)



            # Wait until the input state changes back to low
            while GPIO.input(gpio_pin) > 0:
                time.sleep(0.01)

            logger.info('finished capture')
            print('finished capture')

            end_time = time.time()

            # Calculate and print the execution time
            execution_time = end_time - start_time
            logger.info(f'recived capture, time take: {execution_time}')
            print(f'recived capture, time take: {execution_time}')
        time.sleep(0.01)
    


try:
    logger.info("Starting image capture script")
    capture_images()
except KeyboardInterrupt:
    logger.info("Script interrupted by user")
finally:
    GPIO.cleanup()
    logger.info("GPIO cleanup done")
    if vehicle:
        vehicle.close()
    logger.info("Vehicle connection closed")
