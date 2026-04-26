.. -*- coding: utf-8 -*-

*********************************
Command Reference ( client mode )
*********************************

List of client mode commands.

client ( capture ) : ``cmdbox -m client -c capture <Option>``
=============================================================

- Get a capture image on the client side.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--capture_device <capture_device>","required","Specify the capture device. The value passed to the first argument of `cv2.VideoCapture`."
    "--image_type <image_type>","required","Specify the type of image to output."
    "--capture_frame_width <capture_frame_width>","","Width px of the image to be captured. The value to be specified in the `cv2.CAP_PROP_FRAME_WIDTH` option of the `cv2.VideoCapture` object."
    "--capture_frame_height <capture_frame_height>","","Height px of the image to be captured. The value to be specified in the `cv2.CAP_PROP_FRAME_HEIGHT` option of the `cv2.VideoCapture` object."
    "--capture_fps <capture_fps>","","FPS of the image to be captured. If the capture is faster than the specified value, sleep for the remaining time."
    "--capture_count <capture_count>","","Number of captures."
    "--output_preview <output_preview>","","Display the inference result image with `cv2.imshow`."
    "--output_csv <output_csv>","","Saves the input as a csv file. If this is specified, no standard output is performed."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( deploy ) : ``cmdbox -m client -c deploy <Option>``
===========================================================

- Deploy AI model to server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model."
    "--model_file <model_file>","required","Specify the path or download URL of the trained model file."
    "--model_conf_file <model_conf_file>","","Specify the model configuration file. Multiple specifications are possible, but the file specified first is used at `start` time."
    "--model_img_width <model_img_width>","","Specify the INPUT size (width px) of the AI model."
    "--model_img_height <model_img_height>","","Specify the INPUT size (height px) of the AI model."
    "--predict_type <predict_type>","","Specify the inference type of the AI model."
    "--custom_predict_py <custom_predict_py>","","Specify when creating a custom inference type. In this case, specify `--predict_type Custom`."
    "--label_file <label_file>","","Specify the class label file of the inference result. A file specifying the label name (the row index matches the class) separated by line breaks."
    "--color_file <color_file>","","Specify the color file of the visualization image of the inference result. A file specifying the color (the row index matches the class) separated by line breaks."
    "--before_injection_type <before_injection_type>","","Specify when you want to execute preprocessing."
    "--before_injection_conf <before_injection_conf>","","Specify the setting file for preprocessing."
    "--before_injection_py <before_injection_py>","","Specify when creating a custom preprocessing."
    "--after_injection_type <after_injection_type>","","Specify when you want to create post-processing."
    "--after_injection_conf <after_injection_conf>","","Specify the setting file for post-processing."
    "--after_injection_py <after_injection_py>","","Specify when creating custom post-processing."
    "--overwrite <overwrite>","","Specify to overwrite even if it is already deployed."
    "--train_type <train_type>","","Specify the train type of the AI model."
    "--train_dataset <train_dataset>","","Specifies the data set directory."
    "--train_dataset_upload <train_dataset_upload>","","Upload the data set to the server."
    "--custom_train_py <custom_train_py>","","Specify when creating a custom train type. In this case, specify `--train_type Custom`."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( deploy_list ) : ``cmdbox -m client -c deploy_list <Option>``
=====================================================================

- Get a list of AI models deployed on the server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( predict ) : ``cmdbox -m client -c predict <Option>``
=============================================================

- Perform inference by specifying the AI model.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model to be deleted."
    "-i, --input_file <input_file>","","Specify the image to be inferred by file."
    "--stdin <stdin>","","Read the image to be inferred from standard input."
    "--nodraw <nodraw>","","Do not draw bboxes etc. on the inference result image."
    "--pred_input_type <pred_input_type>","required","Specifies the input type to be inferred."
    "--output_image <output_image>","","Specify the destination file for saving the inference result image."
    "-P, --output_preview <output_preview>","","Display the inference result image with `cv2.imshow`."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( predict_type_list ) : ``cmdbox -m client -c predict_type_list <Option>``
=================================================================================

- Get a list of inference types.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( read_dir ) : ``cmdbox -m client -c read_dir <Option>``
===============================================================

- Get image files in the directory on the client side.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--glob_str <glob_str>","required","Specifies the glob pattern of the file to be read."
    "--read_input_type <read_input_type>","required","Specifies the type of image to be loaded."
    "--image_type <image_type>","required","Specify the type of image to output."
    "--root_dir <root_dir>","required","Specifies the root directory on which to base the search."
    "--include_hidden <include_hidden>","","Specify whether to include hidden files in the types of files to be read."
    "--moveto <moveto>","","Specifies the destination directory to which loaded files are to be moved."
    "--polling <polling>","","Specifies whether to repeat reading in the directory periodically."
    "--polling_count <polling_count>","","Specifies the number of repeated readings in the directory.If it is less than or equal to 0, it repeats indefinitely."
    "--polling_interval <polling_interval>","","Specifies the repetition interval (in seconds) for reading in the directory."
    "--output_csv <output_csv>","","Saves the input as a csv file. If this is specified, no standard output is performed."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( start ) : ``cmdbox -m client -c start <Option>``
=========================================================

- Start the inference server by specifying the AI model.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model to be deleted."
    "--model_provider <model_provider>","","Specify when the model file is in ONNX format."
    "-T, --use_track <use_track>","","Specify when the task is ObjectDetection. Assign a tracking ID using motpy."
    "--gpuid <gpuid>","","Specify the device ID of the GPU."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( stop ) : ``cmdbox -m client -c stop <Option>``
=======================================================

- Stop the inference server by specifying the AI model.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model to be deleted."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( train ) : ``cmdbox -m client -c train <Option>``
=========================================================

- AI model training.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model."
    "--overwrite <overwrite>","","Specify to overwrite even if it is already trained."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( train_type_list ) : ``cmdbox -m client -c train_type_list <Option>``
=============================================================================

- Get a list of train types.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

client ( undeploy ) : ``cmdbox -m client -c undeploy <Option>``
===============================================================

- Delete AI models deployed on the server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "-n, --name <name>","required","Specify the registration name of the AI model to be deleted."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
