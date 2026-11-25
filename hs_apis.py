import time
import requests
import json

# Bounds on every HTTP call below, so a stuck backend can't hang a worker
# thread (and therefore the whole ThreadPoolExecutor run) forever.
DEFAULT_TIMEOUT = 30   # seconds; generic HTTP request timeout
UPLOAD_TIMEOUT = 120   # app binaries can be large
INSTALL_TIMEOUT = 60   # device install/uninstall can be slow
ANALYSIS_TIMEOUT = 150 # waitOnAnalysis's own ?timeout=120 already waits server-side

class HS_API():

    #INTIALIZATION OF APIs WITH HS API TOKEN
    def __init__(self, api_token, device_address=None):
        self.api_token = api_token
        self.url_root = 'https://api-dev.headspin.io/v0/'
        self.url_rootV1 = 'https://api-dev.headspin.io/v1/'
        self.headers = {}
        self.headers["Authorization"] = "Bearer {}".format(api_token)
        self.device_address= device_address
        self.session_id = ""
    
    def setSessionID(self, session_id):
        self.session_id = session_id

    def start_capture(self, device_address):
        request_url = self.url_root + "sessions"
        payload = {}
        payload['device_address'] = device_address
        payload['session_type'] = "capture"
        payload = json.dumps(payload)
        response = requests.post(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        json_data = json.loads(response.text)
        if response.status_code == 200:
            print("Sesssion Capture Started")
            session_id = json_data['session_id']
            self.setSessionID(session_id)
        else:
            print("Error creating session....\n")

    def stop_capture(self):
        request_url = self.url_root + "sessions/" + self.session_id
        payload = {}
        payload['active'] = False
        payload = json.dumps(payload)
        response = requests.patch(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        json_data = json.loads(response.text)
        if response.status_code == 200:
            print("Session capture stopped")
        else:
            print("Error stopping session....\n")

    def lock_device(self, device_address):
        request_url = self.url_root + f'devices/lock?idleTimeout=54000'
        device_id = device_address.split('@')[0]
        payload = {}
        payload['device_id'] = device_id
        payload = json.dumps(payload)
        response = requests.post(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Device Locked")
            return True
        else:
            print("Error locking device....\n")
            return False

    def unlock_device(self, device_address):
        request_url = self.url_root + f'devices/unlock'
        device_id = device_address.split('@')[0]
        payload = {}
        payload['device_id'] = device_id
        payload = json.dumps(payload)
        response = requests.post(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Device Unlocked")
        else:
            print("Error unlocking device....\n")

    
    def get_timestamps(self):
        request_url = self.url_root + f'sessions/{self.session_id}/timestamps'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        json_data = json.loads(response.text)
        if response.status_code == 200:
            print("Got Timestamps from sessions")
            return json_data
        else:
            print("Error getting timestamps from session....\n")

    ###improve this function 
    def get_stats(self, kpi_track):
        #https://api-dev.headspin.io/v0/sessions/timeseries/a07665e6-038d-11f1-9890-22b18d70df98/download?key=memory_used'
        request_url = self.url_root + f'sessions/timeseries/{self.session_id}/download?key={kpi_track}'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        #json_data = json.loads(response.text)
        if response.status_code == 200:
            print("Complete")
            return response.text
        else:
            print("Error injecting audio....\n")
    
    def run_xcuiTest(self, device_address, app_id):
        device_id = device_address.split('@')[0]
        payload = {}
        payload['device_id'] = device_id
        payload = json.dumps(payload)
        request_url = f'https://api-dev.headspin.io/v1/app/{app_id}/test/{device_id}/execute/LaunchTests/testExample'
        response = requests.post(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Complete")
            print(response.text)
        else:
            print("Error locking device....\n")

    def waitForAnalysis(self):
        request_url = self.url_root + f'sessions/analysis/status/{self.session_id}'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Waiting for analysis")
        else:
            print("Error waiting for analysis....\n")
        
    
    def run_audio_match(self, session_id, audio_ids, audio_start, audio_end):
        request_url = self.url_root + f'sessions/{session_id}/label/add'
        payload = {}
        session_data = {}
        session_data = [{"name": "audio match", "label_type": "audio-match-request", 
              "start_time": str(audio_start), "end_time": str(audio_end),
              "data": {"ref_audio_media_id": audio_ids}}]
        payload['labels'] = session_data
        payload = json.dumps(payload)
        response = requests.post(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Complete")
        else:
            print("Error injecting audio....\n")

    def fetch_timestamps(self, session_id):
        request_url = self.url_root + f'sessions/{session_id}/timestamps'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        json_data = json.loads(response.text)
        if response.status_code == 200:
            print("Fetching timestmaps")
            return json_data
        else:
            print("Failure to fetch timestamps.\n")
        
    def fetch_devices(self, selector=None):
        """selector examples: 'device_id:<id>', 'hostname:<host>', 'device_type:ios'."""
        if selector:
            request_url = self.url_root + f'devices/{selector}/information'
        else:
            request_url = self.url_root + 'devices'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        json_data = json.loads(response.text)
        if response.status_code == 200:
            return json_data['devices']
        else:
            print("Error gathering devices....\n")
            return []



    def add_computed_label(self, kpi_track, startTime, endTime):
        data_payload = {}
        data_payload['label_type'] = "time-series-request"
        data_payload['name'] = "Memory Used Compute stats"
        #data_payload['video_box'] = video_box
        data_payload['ts_start'] = str(startTime)
        data_payload['ts_end'] = str(endTime)
        data= {}
        data['method'] = "stats"
        data['time_series_key']= kpi_track
        data['parameters']= {"metrics": ["mean", "percentile 10", "percentile 90", 'max']}
        data_payload['data']= data
        request_url = self.url_root + f'sessions/{self.session_id}/label/add'
        response = requests.post(request_url, headers=self.headers, json=data_payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("Complete")
            #return json_data['capture-started']
        else:
            print("Error creating label....\n")
        response = json.loads(response.text)
        label_id = response['label_id']
        return label_id
    
    def get_group_label(self, label_id):
        request_url = self.url_root + f'sessions/label/{label_id}'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        response = json.loads(response.text)
        label_group_id = response['label_group_id']
        return label_group_id

    def get_computed_stats(self, kpi_track, startTime, endTime):
        label_id = self.add_computed_label(kpi_track, startTime, endTime)
        label_group_id = self.get_group_label(label_id)
        self.waitForAnalysis()
        request_url = self.url_root + f'sessions/analysis/timeseries/stats/{self.session_id}?label_group_id={label_group_id}'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        response = json.loads(response.text)
        data = []
        for stat in response['summary_statistics']:
            info = {}
            info[stat['metric']] = stat['value']
            data.append(info)
        return data

    def checkHar(self):
        request_url = self.url_root + f'sessions/{self.session_id}.har'
        response = requests.get(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        if "https://fake-json-api.mock.beeceptor.com/users" in response.text:
            
            return True
        else:
            return False
        
    def waitOnAnalysis(self):
        #300
        request_url = self.url_root + f'sessions/analysis/status/{self.session_id}?timeout=120'
        response = requests.get(request_url, headers=self.headers, timeout=ANALYSIS_TIMEOUT)
        json_data = json.loads(response.text)
        # print(json_data)
        if json_data['status'] == "done":
            return True
        return False

    def uploadApp(self, files):
        request_url = self.url_rootV1 + f'app/upload'
        response = requests.post(request_url, headers=self.headers, files=files, timeout=UPLOAD_TIMEOUT)
        # print(json_data)
        if response.status_code == 200:
            response = json.loads(response.text)
            return response['app_id']
        return ''

    def deleteApp(self, appID):
        request_url = self.url_rootV1 + f'app/{appID}/delete'
        response = requests.delete(request_url, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            print("App deleted")
            return True
        #not sure on the actual failed response
        return False

    def installApp(self, app_id, device_id):
        request_url = self.url_rootV1 + f'app/{app_id}/install/{device_id}'
        response = requests.post(request_url, headers=self.headers, timeout=INSTALL_TIMEOUT)
        if response.status_code != 200:
            return False, None
        response = json.loads(response.text)
        print(response)
        # HTTP 200 only means the install command ran, not that it succeeded —
        # the actual result is the adb-style returncode/stdout in the body
        # (e.g. returncode=1, stdout="Failure [INSTALL_FAILED_USER_RESTRICTED...]").
        if isinstance(response, dict) and 'returncode' in response:
            return response['returncode'] == 0, response.get('stdout')
        return True, response.get('stdout') if isinstance(response, dict) else None

    def uninstallApp(self, app_id, device_id):
        request_url = self.url_rootV1 + f'app/{app_id}/uninstall/{device_id}'
        response = requests.post(request_url, headers=self.headers, timeout=INSTALL_TIMEOUT)
        if response.status_code != 200:
            return False, None
        response = json.loads(response.text)
        print(response)
        if isinstance(response, dict) and 'returncode' in response:
            return response['returncode'] == 0, response.get('stdout')
        return True, response.get('stdout') if isinstance(response, dict) else None

    def runADBCommand(self, device_id, command):
        request_url = self.url_root + f'adb/{device_id}/shell'
        payload = command
        response = requests.post(request_url, headers=self.headers, data=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            response = json.loads(response.text)
            print(f"ADB command {command} ran successfully")
            return response
        return False


    