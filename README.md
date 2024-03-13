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

- Python Environment: Ensure you have Python 3.9 or later installed. Install required dependencies, including OpenCV and PySpin, as well as any others needed by the scripts in this repository.

- Running the System: Use the Python scripts to control the system. The scripts will communicate with the Arduino through serial commands and control the cameras based on the settings specified in the TOML file.

### Usage
#### Data Acquisition

- Start the Python control script to initiate the data acquisition process. The script will interact with the Arduino to control the experimental setup and use the camera tools to acquire and save images or videos.

#### Hardware Control

- The Arduino sketches can be modified to add or change hardware control functionalities. Refer to the comments within each sketch for guidance on customization.

#### Commands available in cam_tools.py for building data aquisition scripts

##### Barcode Reading

-``` bcode_read(): Invoke this function to read barcodes using a handheld scanner. It prompts for a barcode scan and returns the scanned code.```

##### Camera Interaction

- detect_cams(n=None): Detects the number of connected cameras. Optionally, specify the number of expected cameras with n.
- set_resolution(cam, x_dim, y_dim): Sets the resolution of the specified camera. x_dim and y_dim should be in pixels.

##### Image Acquisition and Processing

- get_save(cam, wl, device, barcode, delay=None): Acquires an image from the camera after a specified delay and saves it. The function turns on specified illumination, captures the frame, and then turns the illumination off.
- grab_images(cam): Captures images from the specified camera and returns them along with timestamps.

##### Video Saving

- save_avi(images, frame_rate=None, barcode=None, prefix=None, path=None, is_color=None): Saves a sequence of images as an AVI file using OpenCV.
- save_video(images, frame_rate=None, barcode=None, prefix=None, path=None): Saves a list of images as a video file using the Spinnaker SDK.

### Description of the folder structure

TO DO ADD FOLDER STRUCTURE

### Compute Specifications

- Any system with a >=  USB 3.0 High Speed bus.  USB 3.0 Super Speed or better is preferred.

## Contributing

See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide-credit-for-contributions.md).


