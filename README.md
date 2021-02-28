# BalticLSC python module scheme
Package `balticlsc` is supposed to help with creating modules for the 
BalticLSC system in the python environment.

### Build your module
1. Create an implementation of the [ProcessingInterface](balticlsc/scheme/processing.py)*.
It should handle tokens according to the documentation.
2. Init in your code the BalticLSC api using yours implementation of processing*:
    ```
    from balticlsc.scheme.api import init_baltic_api
    
    app, rest_client = init_baltic_api(Processing)
    ```
3. Build the proper Dockerfile according to the documentation*.  

*Here you got some example modules on which you can base yours:
1. [Face recogniser](examples/face_recogniser)
