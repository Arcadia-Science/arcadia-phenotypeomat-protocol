"""This is a set of tools for acquiring images from blackfly cameras.  It uses the
 the spinnaker 2.3 SDK and python 3.9.
Dave Mets 10_5_22"""

import time as tm

import cv2 as cv
import PySpin as ps


def bcode_read():
    """function to simplify collecting barcode information using a handheld barcode reader"""
    bcode = input("Scan barcode now or press enter for no barcode ")
    if len(bcode) > 0:
        return bcode
    else:
        return "000000"


def wl_to_ser(wl, device, status=None):
    if status is None:
        status = 1
    if status == "on":
        status = 0
    elif status == "off":
        status = 1
    ser_command = "SET LED_" + str(wl) + "_STATUS " + str(status) + ";"
    device.write(bytes(ser_command, "UTF-8"))


def get_save(cam, wl, device, barcode, delay=None):
    """a function to wait for some delay, turn on an illumination wavelength,
    grab a frame from the camera, save the image and turn off the illumination"""
    if delay is None:
        delay = 5
    wl_to_ser(wl, device, status="on")
    tm.sleep(delay)
    image, timestamps = grab_images(cam)
    save_avi(image, prefix=str(wl), barcode=barcode)
    wl_to_ser(wl, device, status="off")


def detect_cams(n=None):
    if n is None:
        n = 1
    """detects cameras.  Helpful to do before trying to change anything!"""
    sys = ps.System.GetInstance()
    cam_list = sys.GetCameras()
    n_cams = cam_list.GetSize()
    if n_cams < n:
        print("Not enough cameras detected!")
        cam_list.Clear()
        sys.ReleaseInstance()
        return False
    else:
        cam_list.Clear()
        sys.ReleaseInstance()
        return True


def set_resolution(cam, x_dim, y_dim):
    """sets the dimensions of the acquired image. X and Y dim should be in pixels"""
    try:
        cam.Height.SetValue(y_dim)
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False
    try:
        cam.Width.SetValue(x_dim)
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False
    return True


def set_binning(cam, x_dim, y_dim):
    """sets the dimensions of binning. X and Y dim should be in pixels"""
    try:
        cam.BinningVertical.SetValue(y_dim)
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False
    try:
        cam.BinningHorizontal.SetValue(x_dim)
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False
    return True


def set_gain_mode(cam, mode="once"):
    """sets the exposure mode of the camera.  Mode should be once, continuous, or off."""
    if mode == "once":
        try:
            cam.GainAuto.SetValue(ps.GainAuto_Once)
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    elif mode == "continuous":
        try:
            cam.GainAuto.SetValue(ps.GainAuto_Continuous)
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    elif mode == "off":
        try:
            cam.GainAuto.SetValue(ps.GainAuto_Off)  # turn off auto gain
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    else:
        print("Invalid gain mode.  It should be once, continuous, or off.")
        return False


def get_gain_mode(cam):
    """gets the gain mode from the camera"""
    mode_dct = {1: "Once", 2: "Continuous", 0: "Off"}
    try:
        mode = mode_dct[cam.GainAuto.GetValue()]
        return mode
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_expos_mode(cam, mode="once"):
    """sets the exposure mode of the camera.  Mode should be once, continuous, or off."""
    if mode == "once":
        try:
            cam.ExposureAuto.SetValue(ps.ExposureAuto_Once)
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    elif mode == "continuous":
        try:
            cam.ExposureAuto.SetValue(ps.ExposureAuto_Continuous)
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    elif mode == "off":
        try:
            cam.ExposureAuto.SetValue(ps.ExposureAuto_Off)  # turn off auto exposure
            return True
        except ps.SpinnakerException as ex:
            print("Error: %s" % ex)
            return False
    else:
        print("Invalid exposure mode.  It should be once, continuous, or off.")
        return False


def get_expos_mode(cam):
    """gets the exposure mode from the camera"""
    mode_dct = {1: "Once", 2: "Continuous", 0: "Off"}
    try:
        mode = mode_dct[cam.ExposureAuto.GetValue()]
        return mode
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_expos_cont(cam):
    """sets the exposure to automatic for each frame of a video independently"""
    try:
        cam.ExposureAuto.SetValue(ps.ExposureAuto_Continuous)
        return True
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_expos_once(cam):
    """sets the exposure to automatic for the first frame of a video then uses those exposure
    parameters for subsequent frames"""
    try:
        cam.ExposureAuto.SetValue(ps.ExposureAuto_Once)
        return True
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_expos_time(cam, time):
    """sets a custom exposure time.  Expects values in us"""
    try:
        cam.ExposureAuto.SetValue(ps.ExposureAuto_Off)  # turn off auto exposure
        time = min(
            cam.ExposureTime.GetMax(), time
        )  # checks to be sure 'time' isn't longer than max possible
        cam.ExposureTime.SetValue(time)  # set the exposure time on the camera
        return True
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_acq_cont(cam):
    """sets the acquisition mode on the camera to continuous"""
    try:
        cam.AcquisitionMode.SetValue(ps.AcquisitionMode_Continuous)
        return True
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def print_cam_info(cam):
    """prints variables pulled from the camera"""
    try:
        nodemap = cam.GetTLDeviceNodeMap()
        node_device_info = ps.CategoryPtr(nodemap.GetNode("DeviceInformation"))
        if ps.IsAvailable(node_device_info) and ps.IsReadable(node_device_info):
            features = node_device_info.GetFeatures()
            for feature in features:
                node_feat = ps.CValuePtr(feature)
                print(f"{node_feat.GetName()}: {node_feat.ToString()}")
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def get_auto_exposure(cam):
    """Initializes a cam, grabs the auto exposure time.  Can be useful for when you want to
    get an autoexposure but you don't want to change exposure over the course of a video"""
    try:
        cam.AcquisitionMode.SetValue(ps.AcquisitionMode_Continuous)  # set Acq mode to continuous
        cam.BeginAcquisition()
        expose_time = cam.ExposureTime.GetValue()
        cam.EndAcquisition()
        return expose_time
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def get_framerate(cam):
    """gets the framerate set on the camera"""
    try:
        frame_rate = cam.AcquisitionFrameRate.GetValue()
        return frame_rate
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def set_framerate(cam, frame_rate=None):
    """sets the framerate set on the camera. Frame_rate should be in hz"""
    if frame_rate is None:
        frame_rate = 158.0
    try:
        cam.AcquisitionFrameRateEnable.SetValue(True)
        cam.AcquisitionFrameRate.SetValue(frame_rate)
        return True
    except ps.SpinnakerException as ex:
        print("Error: %s" % ex)
        return False


def grab_images(cam, length=None, n_frames=None):
    """this grabs a set of images from a camera.  It assumes the camera has been initialized and
    all desired changes to acquisition have been made on the camera. Expects 'length' to be in
    seconds"""
    if length is None and n_frames is None:
        n_frames = 1
    elif length is not None and n_frames is None:
        frame_rate = get_framerate(cam)
        exposure_time = cam.ExposureTime()
        if 1000**2 / exposure_time < frame_rate:
            frame_rate = 1000**2 / exposure_time
        n_frames = int(float(length) * frame_rate)
    elif length is not None and n_frames is not None:
        print("plese specify either the number of frames or the length of the acquisition not both")
        return
    timestamps = []
    try:
        cam.BeginAcquisition()
        images = list()
        timeout = 1000
        for _i in range(n_frames):
            curr_time = tm.time()
            image = cam.GetNextImage(timeout)
            images.append(image.GetNDArray())
            image.Release()
            timestamps.append(curr_time)
        cam.EndAcquisition()
        return images, timestamps
    except ps.SpinnakerException as ex:
        cam.EndAcquisition()
        print("Error: %s" % ex)
        return False


def save_avi(images, frame_rate=None, barcode=None, prefix=None, path=None, is_color=None):
    """OpenCV utility to save a video.  It expects 'images' to be a numpy array"""
    if frame_rate is None:
        frame_rate = 160.0
    if barcode is None:
        barcode = "00000"
    if prefix is None:
        prefix = "videofile"
    if path is None:
        path = "./"
    if is_color is None:
        is_color = False
    fourcc_code = 0  # this is a fourcc compression codec code. 0 is uncompressed
    tme = int(tm.time())
    im_height = len(images[0])
    im_width = len(images[0][0])
    filename = path + prefix + "_" + str(barcode) + "_" + str(tme) + ".avi"
    avi_handler = cv.VideoWriter(filename, fourcc_code, frame_rate, (im_width, im_height), is_color)
    for image in images:
        avi_handler.write(image)
    cv.destroyAllWindows()
    avi_handler.release()


def save_video(images, frame_rate=None, barcode=None, prefix=None, path=None):
    """Saves a list of images as a video.  This uses the spinnnaker SDK.
    This expects 'images' to be a list of pointers to pySpin images. Could
    be done with opencv or other..."""
    if frame_rate is None:
        frame_rate = 160.0
    if barcode is None:
        barcode = "00000"
    if prefix is None:
        prefix = "videofile"
    if path is None:
        path = "./"
    tme = int(tm.time())
    filename = path + prefix + "_" + str(barcode) + "_" + str(tme) + ".avi"
    avi_handler = ps.SpinVideo()
    avi_header_settings = ps.AVIOption()
    avi_header_settings.frameRate = frame_rate
    avi_header_settings.height = len(images[0])
    avi_header_settings.width = len(images[0][0])
    avi_handler.Open(filename, avi_header_settings)
    for i in range(len(images)):
        avi_handler.Append(images[i])
    avi_handler.close()
