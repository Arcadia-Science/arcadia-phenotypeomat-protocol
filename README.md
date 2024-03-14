# Arcadia-phenotypeomat-protocol

## Purpose

This repository contains the firmware and software necessary to aquire data with the Arcadia Phenotype-o-mat.

## Installation and Setup

This repository uses conda to manage software environments and installations. You can find operating system-specific instructions for installing miniconda [here](https://docs.conda.io/projects/miniconda/en/latest/). After installing conda and [mamba](https://mamba.readthedocs.io/en/latest/), run the following command to create the pipeline run environment.

```{bash}
mamba env create -n phenotypeomat --file phenotypeomat.yml
conda activate phenotypeomat
```

This code also requires the Spinnaker SDK from Flir/Teledyne. The SDK and installation instructure are available [here](https://www.flir.com/products/spinnaker-sdk/?vertical=machine+vision&segment=iis).
Note, you must also install the Spinnaker python wheel appropriate for your version of Python and Spinnaker. These are also available through the link above.

## Overview
### Phenotype-o-Mat Control and Data Acquisition System

The Phenotype-o-Mat system is an integrated solution for controlling experimental hardware and acquiring data, particularly designed for use with Blackfly cameras and Arduino-based control systems. This repository includes Arduino sketches for serial communication, a TOML configuration file for system settings, and Python modules for camera control and initialization.
Components
### Arduino Sketches

- serial_io.ino: Implements basic serial I/O operations for Arduino, facilitating communication between the Arduino and a connected computer.

- arduino_control_through_serial.ino: An advanced sketch for controlling various Arduino outputs (e.g., LEDs, motors) through serial commands sent from a computer. This sketch is designed to work in tandem with the Python control scripts, allowing for automated hardware control during data acquisition.

### Configuration File

-  phenotypeomat.toml: A TOML file used to configure system parameters, such as device identifiers and operational settings. This file ensures that the system can be easily customized without modifying the source code.

### Python Modules

- cam_tools.py: Provides a suite of tools for acquiring images from Blackfly cameras using the Spinnaker SDK. It includes functions for barcode scanning, camera detection, image acquisition, resolution setting, and video saving.

### Setup

- Arduino Setup: Upload the appropriate .ino sketch to your Arduino device. Ensure that the Arduino is connected to your computer and that the correct port and baud rate are set.

- System Configuration: Edit the phenotypeomat.toml file to match your system's configuration. Specify device identifiers, operational parameters, and any other necessary settings.

- Python Environment: Ensure you have Python 3.9 or later installed. Install required dependencies, including OpenCV and PySpin (PySpin is part of the python wheel associated with the Spinnaker SDK), as well as any others needed by the scripts in this repository.

- Running the System: Use the Python scripts to control the system. The scripts will communicate with the Arduino through serial commands and control the cameras based on the settings specified in the TOML file.

### Usage
#### Data Acquisition

- Start the Python assay script (e.g., test_assay_growth_curve_chlamy.py) to initiate the data acquisition process. The script will interact with the Arduino to control the experimental setup and use the camera tools to acquire and save images or videos.

### Tools for writing data aquisition scripts
#### Illumination hardware Control
##### Currently, the Arduino code allows control of 5 illumination sources: white lite trans-illumination and incident light at 4 wavelengths: 460nm, 535nm, 590nm, and 670nm. Control of the Arduino is meddiated by a generic serial communication system to facilitate the addition of other functionality. The assay scripts communicate with the arduino through use of the [pySerial](https://pyserial.readthedocs.io/en/latest/shortintro.html) module. The Arduino sketches can be modified to add or change hardware control functionalities. Refer to the comments within each sketch for guidance on customization. The current usage is outlined below.

 After initializing a serial connection with the arduino (see example assay or pySerial documentation to accomplish this) commands can be sent in the following format:

-```GET LED_[WAVELENGTH]_STATUS;``` where wavelength is 460, 535, 590, 670, or TRANS.  e.g. GET LED_460_STATUS; will return a 0 (LED is on) or a 1 (LED is off).
-```SET LED_[WAVELENGTH]_STATUS [desired numerical status];``` Where wavelength is 460, 535, 590, 670, or TRANS. And 'desired numerical statis is either 0 (turn on LED) or 1 (turn off LED  e.g. SET LED_460_STATUS 0; will turn on the 460nm LED.
-```GET_AND_SET LED_[WAVELENGTH]_STATUS [desired numerical status];``` Where wavelength is 460, 535, 590, 670, or TRANS. And 'desired numerical statis is either 0 (turn on LED) or 1 (turn off LED  e.g. GET_AND_SET LED_460_STATUS 1;``` Will attempt to turn off the 460 LED and then check the LED status and return the current status.  This is helpful to be sure the SET command changed the LED status.

##### Barcode Reading

-``` bcode_read()```: Invoke this function to read barcodes using a USB handheld scanner. It prompts for a barcode scan and returns the scanned code.

##### Camera control
###### Several of these functions are part of the Spinnaker SDK and we direct you to the SDK documentation for more information.  They are provided here because these are the minimum functions required to interface with the camera.  For example usage see the provded 'test_assay.'

- ```detect_cams(n=None)```: Detects the number of connected cameras. Optionally, specify the number of expected cameras with n.
- ```ps.System.GetInstance()```: Initializes an object to interface between the computer system and the PySpin SDK.
- ```system.GetCameras()```: Property of a system object that queries the computer system USB and GigE interfaces for Blackfly cameras and returns handles for those cameras in a list.
- ```system.ReleaseInstance()```: Property of a system object that stops that instance.
- ```cam_list.Clear()```: Property of a camera list that ends the handlers for those cameras and returns the cameras to a idle state.
- ```camera.Init()```: Initializes a camera object. Camera objects can be de-initialized and returned to idle state by calling '''del camera'''

##### Image Acquisition and Processing

- ```get_save(cam, wl, device, barcode, delay=None)```: Acquires an image from the camera after a specified delay and saves it. The function turns on specified illumination, captures the frame, and then turns the illumination off.
- ```grab_images(cam)```: Captures images from the specified camera and returns them along with timestamps.
- ```set_resolution(cam, x_dim, y_dim)```: Sets the dimensions of the acquired image. X and Y dim should be in pixels. 'cam' is a camera object.
- ```set_binning(can, x_dim, y_dim)```: Sets the dimensions of binning. X and Y dim should be in pixels. 'cam' is a camera object.
- ```set_gain_mode(cam, mode="once")```: Sets the automatic gain mode of the camera.  Mode should be 'once', 'continuous', or 'off'.
- ```get_gain_mode(cam)```: Returns the current automatic gain mode setting from the camera.
- ```set_expos_mode(cam, mode="once")```: Sets the automatic exposure mode of the camera.  Mode should be once, continuous, or off.
- ```set_expos_time(cam, time)```: Sets a custom exposure time.  Expects values in micro seconds.
- ```get_auto_exposure(cam)```: Returns the current autoexposure value determined by the camera in micro seconds.
- ```set_framerate(cam, frame_rate=None)```: sets the framerate set on the camera. 'frame_rate' should be in hz.
- ```get_framerate(cam)```: Returns the current framerate on the camera.

##### Video Saving

- ```save_avi(images, frame_rate=None, barcode=None, prefix=None, path=None, is_color=None)```: Saves a sequence of images as an AVI file using OpenCV.
- ```save_video(images, frame_rate=None, barcode=None, prefix=None, path=None)```: Saves a list of images as a video file using the Spinnaker SDK.

### Description of the folder structure

[design_files/](design_files/) Contains design files for the components of the phenotype-o-mat including the printed circuit board. \
[flir_camera_tools/](flir_camera_tools/) Contains the python module to interact with the phenotype-o-mat. \
[firmware_src/](firmware_src/) Contains the firmware to be uploaded to the Arduino which operates the illumination system. \
[test_assay_growth_curve_chlamy.py](test_assay_growth_curve_chlamy.py) Is an example assay for aquiring data from the phenotype-o-mat.  It uses much of the currently implemented functionality. 

### Compute Specifications

- Any system with a >=  USB 3.0 High Speed bus.  USB 3.0 Super Speed or better is preferred.

## Contributing

See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide-credit-for-contributions.md).


