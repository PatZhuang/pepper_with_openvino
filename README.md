## run

```bash
python2 cam.py
```

```bash
# set openvino environment
source ~/intel/openvino/bin/setupvars.sh

python3 detection.py
```

`cam.py` runs on `python2` with naoqi python SDK installed.

`detection.py` runs on `python3` with openvino SDK installed.

Then you'll see a openCV window showing person detection results of pepper's front camera.

Other files are for testing only.

Press any key on OpenCV window to exit client which would accordingly exit server.

If not correctly stopping server would cause a subscriber registration error. One resolution is to reboot Pepper itself, or just change `get_image` to another name for `video_service.subscribe("get_image", resolution, colorSpace, 5)` line for convenience.

The `detection.py` only detects person by default. To enable face detect just modify `DETECT_FACE` to `True` in code.