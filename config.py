token = ""
vk_tokens = ["",
             '',
             '',
             '',
             '',
             '']
my_vk_token = ""
ver = 5.101
count = 3
offset = 0

client_id = ""
client_secret = ""
reg_vk = r'(?P<url>https?://[^\s]+)'  # регулярка для обрезки вк
reg_tg = r'###(.*)\n(.*)'  # регулярка для обрезки сообщения перед отправкой в канал
reg_ali = r'https?://aliexpress\.ru/item/.*.html|https?://www.aliexpress\.com/item/.*.html' # регулярка для обрезки али
reg_ali_kot = [r'#(.*)', r'⚡(.*)⚡', r'\n\n']
reg_ali_kupon = r'✈(.*)✈'
chat_id = '@wektnwrjntwei234'
time_post = [0, 0, 0, 0, 0, 0, 0]
chat_id_to_post = '-'
chat_id_to_post2 = '-'
cloud_name=''
api_key=''
api_secret=''

DEFAULT_TAG = "python_sample_basic"
