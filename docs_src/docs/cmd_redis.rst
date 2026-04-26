.. -*- coding: utf-8 -*-

********************************
Command Reference ( redis mode )
********************************

List of redis mode commands.

redis ( docker_run ) : ``cmdbox -m redis -c docker_run <Option>``
=================================================================

- If you are running `iinfer -m install -c server` in install mode, use `docker-compose up -d`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--wsl_name <wsl_name>","","For Windows, specify the name of the WSL distribution."
    "--wsl_user <wsl_user>","","For Windows, specify the user name in WSL."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

redis ( docker_stop ) : ``cmdbox -m redis -c docker_stop <Option>``
===================================================================

- If you are running `iinfer -m install -c server` in install mode, use `docker-compose down`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--wsl_name <wsl_name>","","For Windows, specify the name of the WSL distribution."
    "--wsl_user <wsl_user>","","For Windows, specify the user name in WSL."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
