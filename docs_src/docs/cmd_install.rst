.. -*- coding: utf-8 -*-

**********************************
Command Reference ( install mode )
**********************************

List of install mode commands.

install ( insightface ) : ``cmdbox -m install -c insightface <Option>``
=======================================================================

- Install `insightface`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

install ( mmcv ) : ``cmdbox -m install -c mmcv <Option>``
=========================================================

- Install `mmcv`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

install ( mmdet ) : ``cmdbox -m install -c mmdet <Option>``
===========================================================

- Install `mmdetection`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
    "--data <data>","required","When omitted, `$HONE/.iinfer` is used."

install ( mmpretrain ) : ``cmdbox -m install -c mmpretrain <Option>``
=====================================================================

- Install `mmpretrain`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
    "--data <data>","required","When omitted, `$HONE/.iinfer` is used."

install ( mmseg ) : ``cmdbox -m install -c mmseg <Option>``
===========================================================

- Install `mmsegmentation`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
    "--data <data>","required","When omitted, `$HONE/.iinfer` is used."

install ( onnx ) : ``cmdbox -m install -c onnx <Option>``
=========================================================

- Install `onnxruntime`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

install ( server ) : ``cmdbox -m install -c server <Option>``
=============================================================

- `Build` the docker image of the `inference server`.
- If the `build` is successful, a `docker-compose.yml` file is generated in the execution directory.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.iinfer` is used."
    "--install_cmdbox <install_cmdbox>","","When omitted, `cmdbox==0.7.9` is used."
    "--install_from <install_from>","","Specify the FROM image that will be the source of the docker image to be created."
    "--install_no_python <install_no_python>","","Do not install python."
    "--install_compile_python <install_compile_python>","","Compile and install python3; if install_no_python is specified, it is preferred."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
    "--voicevox_ver <voicevox_ver>","","Specify the version of VOICEVOX to use."
    "--voicevox_whl <voicevox_whl>","","Specify the VOICEVOX wheel file to use."
    "--init_extra <init_extra>","","Specify the command to be executed immediately after “from”."
    "--run_extra_pre <run_extra_pre>","","Specify additional commands to run before install_extra execution."
    "--run_extra_post <run_extra_post>","","Specify additional commands to run after install_extra execution."
    "--install_extra <install_extra>","","Specify additional packages to install."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
    "--install_iinfer <install_iinfer>","","When omitted, `iinfer` is used. You can also specify `iinfer==0.13.4`."
    "--install_onnx <install_onnx>","","Install `onnxruntime` in the docker image."
    "--install_mmdet <install_mmdet>","","Install `mmdetection` in the docker image."
    "--install_mmseg <install_mmseg>","","Install `mmsegmentation` in the docker image."
    "--install_mmpretrain <install_mmpretrain>","","Install `mmpretrain` in the docker image."
    "--install_insightface <install_insightface>","","Install `insightface` in the docker image."
