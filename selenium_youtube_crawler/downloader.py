import os

import pandas as pd
import requests

from gcs_helper import GCSHelper
from metadata_extractor import extract_metadata
from utilities import populate_local_archive
from youtube_util import YoutubeApiUtils


class Downloader:

    # file-dir is the directory where files get downloads
    def __init__(self, thread_local, bucket_name, bucket_path, language):
        self.thread_local = thread_local
        self.gcs_helper = GCSHelper(bucket_name, bucket_path)
        self.language = language
        self.file_dir = "downloads"

    def get_session(self):
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session

    def download(self, download_url, video_id, source):
        file_name = "file-id" + video_id + ".mp4"
        csv_name = "file-id" + video_id + ".csv"

        # download and extract metadata
        self.download_and_save(download_url, file_name)
        self.post_download_process(file_name, csv_name, source, video_id)

    def download_and_save(self, url, file_name):
        if not os.path.exists(self.file_dir):
            os.system("mkdir {0}".format(self.file_dir))
        session = self.get_session()
        with session.get(url, stream=True) as response:
            with open(self.file_dir + "/" + file_name, 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)

    def post_download_process(self, file_name, csv_name, source, video_id):
        youtube_url = "https://www.youtube.com/watch?v=" + video_id
        duration = extract_metadata(self.file_dir, file_name, youtube_url, source)
        print("Downloaded {0}".format(file_name))
        modified_file_name = str(duration) + file_name
        modified_csv_name = str(duration) + csv_name
        # change the title and filename in csv with duration prefixed
        self.update_metadata_fields(modified_file_name, csv_name, video_id)
        # upload media and metadata to bucket
        self.gcs_helper.upload_file_to_bucket(source, file_name, modified_file_name, self.file_dir)
        self.gcs_helper.upload_file_to_bucket(source, csv_name, modified_csv_name, self.file_dir)
        # remove files from local system
        self.clean_up_files(file_name, csv_name)
        # add to archive.txt here
        self.update_archive(source, video_id)

    def update_metadata_fields(self, modified_file_name, csv_name, video_id):
        meta_file = pd.read_csv(self.file_dir + "/" + csv_name)
        meta_file['raw_file_name'] = modified_file_name
        meta_file['title'] = modified_file_name
        meta_file['language'] = self.language.lower()
        meta_file['license'] = YoutubeApiUtils().get_license_info(video_id)
        meta_file.to_csv(self.file_dir + "/" + csv_name, index=False)

    def clean_up_files(self, file_name, csv_name):
        os.system('rm {0}/{1} {0}/{2}'.format(self.file_dir, file_name, csv_name))

    def update_archive(self, source, video_id):
        populate_local_archive(source, video_id)
        self.gcs_helper.upload_archive_to_bucket(source)
