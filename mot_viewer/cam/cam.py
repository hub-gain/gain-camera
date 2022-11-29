import ctypes
from typing import Optional

import tisgrabber as tis


class ImageControlLibrary:
    def __init__(self, dll: str = "./tisgrabber_x64.dll"):
        self._ic = ctypes.cdll.LoadLibrary(dll)
        tis.declareFunctions(self._ic)
        self._ic.IC_InitLibrary(0)

    def get_device_count(self, i: int) -> int:
        return self._ic.IC_GetDeviceCount(i)

    def get_unique_name_from_list(self, i: int) -> str:
        return self._ic.IC_GetUniqueNamefromList(i)

    def open_message_box(self, message: str, title: str) -> None:
        self._ic.IC_MsgBox(tis.T(message), tis.T(title))

    def create_grabber(self):
        return self._ic.IC_CreateGrabber()

    def show_device_selection_dialog(self):
        return self._ic.IC_ShowDeviceSelectionDialog(None)


class Camera:
    def __init__(
        self, device: Optional[str] = None, dll: str = "./tisgrabber_x64.dll"
    ) -> None:
        self._ic = ImageControlLibrary(dll=dll)._ic

        if device:
            self._grabber = self._ic.create_grabber()
            if str(device).endswith(".xml"):
                self.load_device_state_from_file(device)
            else:
                self.open_video_capture_device(device)
        else:
            self._grabber = self._ic.show_device_selection_dialog()

        if not self.is_valid_device:
            raise RuntimeError("No device opened.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_grabber()

    def release_grabber(self):
        self._ic.IC_ReleaseGrabber(self._grabber)

    def open_video_capture_device(self, device: str):
        return self._ic.IC_OpenVideoCaptureDevice(self._grabber, tis.T(device))

    def save_device_state_to_file(self, filename: str):
        self._ic.IC_SaveDeviceStateToFile(self._grabber, tis.T(filename))

    def load_device_state_from_file(self, filename: str):
        self._ic.IC_LoadDeviceStateFromFile(self._grabber, tis.T(filename))

    def open_device_by_unique_name(self, unique_name: str):
        self._ic.IC_OpenDeviceByUniqueName(self._grabber, tis.T(unique_name))

    @property
    def is_valid_device(self) -> bool:
        return self._ic.IC_IsDevValid(self._grabber)

    def print_properties(self) -> None:
        self._ic.IC_printItemandElementNames(self._grabber)

    @property
    def frame_rate(self) -> float:
        return self._ic.IC_GetFrameRate(self._grabber)

    @frame_rate.setter
    def frame_rate(self, value: float) -> None:
        self._ic.IC_SetFrameRate(self._grabber, ctypes.c_float(value))

    @property
    def video_format(self) -> str:
        return self._ic.IC_GetVideoFormat(self._grabber)

    @video_format.setter
    def video_format(self, value: str) -> None:
        self._ic.IC_SetVideoFormat(self._grabber, tis.T(value))

    def start_live(self) -> None:
        self._ic.IC_StartLive(self._grabber, 1)

    def stop_live(self) -> None:
        self._ic.IC_StopLive(self._grabber)

    def snap_image(self, timeout: int = 1000) -> int:
        return self._ic.IC_SnapImage(self._grabber, timeout)

    def save_image(
        self, filename: str, format: str = "JPG", quality: int = 100
    ) -> None:
        self._ic.IC_SaveImage(
            self._grabber, tis.T(filename), tis.ImageFileTypes(format, quality)
        )
