# Face recogniser
Test the module in the following steps:
1. Prepare the config file that originally will be provided by BalticLSC system.
The listening below shows the example config:
    ```
    [
     {
     "PinName": "Input",
     "PinType": "input",
     "AccessType": "ftp",
     "DataMultiplicity": "single",
     "TokenMultiplicity": "single",
     "AccessCredential": {
        "User": "username",
        "Password": "password",
        "Host": "127.0.0.1",
        "Port": 21
      }
     },
     {
     "PinName": "Output",
     "PinType": "output",
     "AccessType": "ftp",
     "DataMultiplicity": "single",
     "TokenMultiplicity": "single"
    }]
    ```
2. Build and run the docker image. You can use [build_and_run](./build_and_run.sh) script. 
Make sure to provide proper config file directory using docker volume (see the script mentioned above).

3. Send an input token to the api.
The listening below shows the example token sending with the `curl` command:
    ```
    curl -X POST -d '{"MsgUid": "123", "PinName": "Input", "Values": "{\"dir\": \"/baltic_test/input_folder\"}"}' --header 'Content-Type: application/json' 0.0.0.0:56733/token
    ```
