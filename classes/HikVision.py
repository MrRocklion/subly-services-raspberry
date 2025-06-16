import requests
from classes.logger_config import logger
from requests.auth import HTTPDigestAuth
from datetime import datetime, timezone
import json
import os
class HikVision():
    def __init__(self, api_url,username, password):
        self.user = username
        self.password = password
        self.api_url = api_url

    
    def enroll_user(self,user):
        userData = self.format_user_data(user)
        url_enroll = f"{self.api_url}/ISAPI/AccessControl/UserInfo/Record?format=json"
        try:
            response_enroller = requests.post(
                url_enroll,
                headers={},
                data= json.dumps(userData),
                auth=HTTPDigestAuth(self.user, self.password),
                verify=False
            )
            if response_enroller.status_code == 200:
                return True
            else:
                logger.error(f"Error al enviar solicitud de inscripcion: {response_enroller.status_code} - {response_enroller.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar solicitud de inscripcion: {e}")
            return False
    def enroll_face(self, user_id):
        url_face_id = f"{self.api_url}/ISAPI/Intelligent/FDLib/FDSetUp?format=json"
        image_name = str(user_id) +".jpg"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(base_dir, ".."))
        data_dir = os.path.join(src_dir, "dataset")
        total_path = os.path.join(data_dir, image_name)
        files= [('img',(image_name,open(total_path,'rb'),'image/jpeg'))]
        try:
            requests.put(
                    url_face_id,
                    headers={},
                    files=files,
                    data = self.format_image_data(user_id),
                    auth=HTTPDigestAuth(self.user, self.password),
                    verify=False
                )
            logger.info(f"Exito Solicitud de inscripcion de cara enviada para el usuario {user_id}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar solicitud de inscripcion de cara: {e}")
            return False
    
    def update_days(self,user):
        userData = self.format_user_data(user)
        url_enroll = f"{self.api_url}/ISAPI/AccessControl/UserInfo/Modify?format=json"
        try:
            response_enroller = requests.put(
                url_enroll,
                headers={},
                data= json.dumps(userData),
                auth=HTTPDigestAuth(self.user, self.password),
                verify=False
            )
            if response_enroller.status_code == 200:
                return True
            else:
                logger.error(f"Error al enviar solicitud de inscripcion: {response_enroller.status_code} - {response_enroller.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar solicitud de inscripcion: {e}")
            return False
    
    def format_user_data(self, user):
        name = user['name']+' '+user['lastname']
        start_date = datetime.strptime(user['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(user['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        user_data = {
                "UserInfo": {
                    "employeeNo": str(user['user_id']),
                    "name": name,
                    "userType": "normal",
                    "Valid": {
                        "enable": True,
                        "beginTime": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "endTime": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "timeType": "local"
                    },
                    "doorRight": "1",
                    "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                    "gender": 'male',
                    "localUIRight": False,
                    "maxOpenDoorTime": 0,
                    "userVerifyMode": "",
                    "groupId": 1,
                    "userLevel": "Employee",
                    "localPassword": ""
                }
            }
        return user_data
    
    def format_image_data(self, id):
        image_data =  {
                "FaceDataRecord": f'{{"faceLibType":"blackFD","FDID":"1","FPID":"{id}"}}'
            }
            
        return image_data

