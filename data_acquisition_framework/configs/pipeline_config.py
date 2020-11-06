mode = 'channel'  # [channel,file]

# Common configurations
bucket = 'ekstepspeechrecognition-dev'
channel_blob_path = 'scrapydump/refactor_test'#'data/audiotospeech/raw/download/downloaded/gujarati/audio'
archive_blob_path = 'archive'
source_name = 'DEMO'  # Scraped Data file name(CSV)
batch_num = 1  # keep batch small on free tier
scraped_data_blob_path = "scraped"

# Channel mode configurations
channel_url_dict = {"https://www.youtube.com/channel/UCZlp89ioAcju3Va7ADa1B-Q": "Tamil"}  # eg {"https://www.youtube.com/channel/UCQvdU25Eqk3YS9-QnILhKKQ" : "ABCD"}
match_title_string = ''
reject_title_string = ''

# File Mode configurations
file_speaker_gender_column = 'speaker_gender'
file_speaker_name_column = "speaker_name"
file_url_name_column = "video_url"
