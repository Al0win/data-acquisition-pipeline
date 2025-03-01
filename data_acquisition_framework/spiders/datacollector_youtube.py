import logging
import os

import scrapy
from scrapy import signals

from data_acquisition_framework.services.youtube_util import YoutubeUtil, is_youtube_api_mode
from ..items import YoutubeItem
from ..services.storage_util import StorageUtil


class DatacollectorYoutubeSpider(scrapy.Spider):
    name = 'datacollector_youtube'
    allowed_domains = ['youtube.com']
    start_urls = ['https://www.youtube.com']
    count = 0

    custom_settings = {
        'CONCURRENT_ITEMS': '1'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage_util = StorageUtil()
        self.storage_util.set_gcs_creds(str(kwargs["my_setting"]).replace("\'", ""))
        os.environ["youtube_api_key"] = str(kwargs["youtube_api_key"])
        self.youtube_util = YoutubeUtil()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(
            *args,
            my_setting=crawler.settings.get("GCS_CREDS") if "scrapinghub" in os.path.abspath("~") else open(
                "./credentials.json").read(),
            youtube_api_key=crawler.settings.get("YOUTUBE_API_KEY") if "scrapinghub" in os.path.abspath("~") else open(
                "./.youtube_api_key").read(),
            **kwargs
        )
        spider._set_crawler(crawler)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self):
        self.storage_util.clear_required_directories()
        if is_youtube_api_mode():
            self.storage_util.get_token_from_bucket()

    def spider_closed(self):
        if is_youtube_api_mode():
            self.storage_util.upload_token_to_bucket()

    def parse(self, response, **kwargs):
        for mode, channel_file_name, file_mode_data in self.youtube_util.validate_mode_and_get_result():
            channel_id = channel_file_name.split("__")[0]
            channel_name = channel_file_name.replace(channel_id + "__", "").replace('.txt', '')
            if mode == "file":
                channel_id = None
            logging.info(
                str("Channel {0}".format(channel_file_name)))
            yield YoutubeItem(
                channel_name=channel_name,
                channel_id=channel_id,
                filename=channel_file_name,
                filemode_data=file_mode_data)
