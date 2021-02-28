import os
from typing import List, Tuple, Dict

import face_recognition

from matplotlib import pyplot, patches

from PIL import Image

import numpy as np

from balticlsc.access.ftp import upload_file, get_connection
from balticlsc.configs.credential.ftp import FTPCredential
from balticlsc.scheme.api import init_baltic_api
from balticlsc.scheme.logger import logger
from balticlsc.scheme.pin import Pin, MissingPin, PinAttribute, ValuesAttribute
from balticlsc.scheme.processing import ProcessingInterface
from balticlsc.scheme.utils import camel_to_snake, get_random_output_folder

MODULE_VERSION = 'latest'


class Processing(ProcessingInterface):
    def process(self, msg_uid: str, input_pin: Pin,  output_pin_name_to_value: Dict[str, Pin]) -> None:
        logger.info('module version = ' + MODULE_VERSION)
        logger.info('starting processing for input pin="' + str(input_pin) + '"')
        input_access_credential = input_pin.getattr(PinAttribute.ACCESS_CREDENTIAL)
        input_folder = input_pin.getattr(PinAttribute.ACCESS_PATH)

        if input_access_credential is None:
            raise ValueError(f'missing access credential in the input pin={str(input_pin)}')

        if input_folder is None:
            raise ValueError(f'missing access path in the input pin={str(input_pin)}')

        input_ftp_credential = FTPCredential(**input_access_credential)
        # START # Establish the output access credential and folder # START #
        output_pin_name: str = 'Output'

        if output_pin_name not in output_pin_name_to_value:
            error_msg = 'missing pin with name="' + output_pin_name + '" in output pins config'
            logger.error(error_msg)
            raise MissingPin([pin for pin in output_pin_name_to_value.values()], error_msg)

        output_pin = output_pin_name_to_value[output_pin_name]
        logger.info('loading output pin=' + str(output_pin))
        output_access_credential = output_pin.getattr(PinAttribute.ACCESS_CREDENTIAL)

        if output_access_credential is None:
            logger.info('output pin access credentials is None, using input access credentials')
            output_ftp_credential = input_ftp_credential
        else:
            output_access_credential = {camel_to_snake(key): value for key, value in output_access_credential.items()}

            if str(output_access_credential) == str(input_access_credential):
                logger.info('input and output access credential are the same')
                output_ftp_credential = input_ftp_credential
            else:
                output_ftp_credential = FTPCredential(**output_access_credential)

        output_access_path = output_pin.getattr(PinAttribute.ACCESS_PATH)

        if output_access_path is None:
            logger.info('access path is not provided in output config')
            logger.info('setting random generated string as output folder name')
            output_folder = get_random_output_folder(input_folder)
        else:
            output_access_path = {camel_to_snake(key): value for key, value in output_access_path.items()}

            if 'resource_path' not in output_access_path:
                logger.info('missing "resource_path" value in output access path')
                logger.info('setting random generated string as output folder name')
                output_folder = get_random_output_folder(input_folder)
            else:
                output_folder = output_access_path['resource_path']
                logger.info('setting output folder based on output pin config "resource_path"=' + output_folder)
        # STOP # Establish output credentials and folder # STOP #
        logger.info('connecting to input ftp server: ' + input_ftp_credential.host)
        input_ftp = get_connection(input_ftp_credential)

        if output_ftp_credential != input_ftp_credential:
            logger.info('connecting to output ftp server: ' + output_ftp_credential.host)
            output_ftp = get_connection(output_ftp_credential)
        else:
            logger.info('using the same connection as output ftp')
            output_ftp = input_ftp
        # START # process and send files # START #
        logger.info('changing ftp working directory to "' + input_folder + '"')
        input_ftp.cwd(input_folder)
        logger.info('working directory changed')
        logger.info('listing files in the working directory ...')
        filenames: List[str] = input_ftp.nlst()
        logger.info('handling ' + str(len(filenames)) + ' files')
        os.makedirs('tmp', exist_ok=True)

        for filename in filenames:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                logger.warning('wrong format of the file "' + filename + '", omitting')
                continue

            logger.info('downloading file "' + filename + '"')
            filepath = 'tmp/' + filename
            # Save the image locally
            with open(filepath, 'wb') as file:
                input_ftp.retrbinary("RETR " + filename, file.write)
            # Mark faces and save the image
            image = np.array(Image.open(filepath))
            im = Image.fromarray(image)
            im.save(filepath)
            height: int = image.shape[0]
            width: int = image.shape[1]
            dpi: int = 100
            faces_coords: List[Tuple[int]] = face_recognition.face_locations(image)
            figure = pyplot.figure(frameon=False, dpi=dpi)
            figure.set_size_inches(width / dpi, height / dpi)
            ax = pyplot.Axes(figure, [0., 0., 1., 1.])
            ax.set_axis_off()
            figure.add_axes(ax)
            ax.imshow(image)
            logger.info('adding ' + str(len(faces_coords)) + ' faces to image "' + filename + '"')
            fig = pyplot.gcf()
            fig.savefig(fname=filepath, dpi=dpi, bbox_inches='tight')

            for index in range(len(faces_coords)):
                x_start = faces_coords[index][3]
                y_start = faces_coords[index][0]
                x_width = (faces_coords[index][1] - faces_coords[index][3])
                y_height = (faces_coords[index][2] - faces_coords[index][0])
                rect = patches.Rectangle((x_start, y_start), x_width, y_height,
                                         edgecolor='r', facecolor="none")
                ax.add_patch(rect)

            pyplot.savefig(fname=filepath, dpi=dpi, bbox_inches='tight')
            pyplot.close()
            # Send file to ftp
            with open(filepath, 'rb') as file:
                logger.info('uploading file "' + filename + '" into ' + output_folder)
                upload_file(filename, output_folder, output_ftp, file)
                file.close()  # close file and FTP

            input_ftp.cwd(input_folder)
        # STOP # process and send files # STOP #
        input_ftp.quit()

        if output_ftp_credential != input_ftp_credential:
            output_ftp.quit()

        rest_client.send_output_token(
            base_msg_uid=msg_uid,
            values={
                ValuesAttribute.RESOURCE_PATH: output_folder
            },
            output_pin_name=output_pin.getattr(PinAttribute.NAME))
        rest_client.send_ack_token(
            msg_uids=[msg_uid],
            is_final=True,
            is_failed=False,
        )


app, rest_client = init_baltic_api(Processing)
