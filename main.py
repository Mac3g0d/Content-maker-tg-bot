import telebot
from threading import *
import time
import requests
import json
import re
from PIL import Image
from io import BytesIO
from telebot import types
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.api import delete_resources_by_tag, resources_by_tag
import cloudinary
from config import *
import top.api

bot = telebot.TeleBot(token)
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret)

class Img:
    def get_image_in_html(self,url):
        r = requests.get(url)
        x = re.findall(r"imagePathList\":(\[.*?\])", r.text)
        x = re.sub(r'\"|\[|\]', '', x[0])
        image = x.split(',')
        return image[0]
    def get_product_id_from_link(self,link):
        """Returns the product id from a regular AliExpress link"""
        link = re.findall(r'/item/(.*).html', link)
        return link[0]

    def get_main_image(self,link):
        r = top.api.AliexpressAffiliateProductdetailGetRequest()
        r.product_ids = self.get_product_id_from_link(link)
        #r.fields = "commission_rate,sale_price"
        product_info = r.getResponse()
        try:
            image = product_info['aliexpress_affiliate_productdetail_get_response']['resp_result']['result']['products']['product'][0]['product_main_image_url']
            return image
        except Exception as e:
            print(e)
            return self.get_image_in_html(link)


    def upload_files(self,width, height):
        response = upload("out.jpg", tags=DEFAULT_TAG)
        url_pic, options = cloudinary_url(response["public_id"], format=response["format"], width=width, height=height,
                                          crop="fill")
        print(f'img done! {url_pic}')
        return url_pic


    def cleanup(self):
        response = resources_by_tag(DEFAULT_TAG)
        resources = response.get("resources", [])
        if not resources:
            print("No images found")
            return
        print("Deleting {0:d} images...".format(len(resources)))
        delete_resources_by_tag(DEFAULT_TAG)
        print("Done!")


    # def ali_parse(self,base_url):
    #     headers = {'accept': '*/*',
    #                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 YaBrowser/19.10.1.238 Yowser/2.5 Safari/537.36'}
    #     session = requests.session()
    #     request = session.get(base_url, headers=headers)
    #     if request.status_code == 200:
    #         soup = bs(request.content, 'html.parser')
    #         root = soup.find('link', attrs={'as': "image"})
    #         try:
    #             href = root.attrs['href']
    #         except Exception as e:
    #             print(f'error {e} root = {root}')
    #     return href



    def collage(self,img_urls):
        global img_count, img, imgcanvasw, imgcanvash
        # for i, img in enumerate( images ):
        #     x = img_size * (i % 3)
        #     y = img_size * (i // 3)
        #     original_image.paste( img, x, y )

        # print('img count= ' + str(lenimg))
        img_size = int(1000)
        newsize = 1000, 1000
        r = []
        img = []

        if len(img_urls) == 1:
            imgcanvasw = img_size
            imgcanvash = img_size
        elif len(img_urls) == 2:
            imgcanvasw = img_size * 2
            imgcanvash = img_size
        elif len(img_urls) <= 3:
            imgcanvasw = img_size * 3
            imgcanvash = img_size
        elif len(img_urls) <= 6:
            imgcanvasw = img_size * 3
            imgcanvash = img_size * 2
        elif len(img_urls) > 6:
            imgcanvasw = img_size * 3
            imgcanvash = img_size * 3
        original_Image = Image.new('RGB', (imgcanvasw, imgcanvash), 'WHITE')
        for i in range(len(img_urls)):
            r.append(requests.get(img_urls[i]))
            im = Image.open(BytesIO(r[i].content))
            if len(img_urls) > 1:
                img.append(im.resize(newsize))
            else:
                img.append(im)
                width, height = im.size
                original_Image = Image.new('RGB', (width, height), 'WHITE')
            i += 1
        if len(img_urls) >= 1:
            original_Image.paste(img[0], (0, 0))
            if len(img_urls) > 1:
                original_Image.paste(img[1], (img_size, 0))
                if len(img_urls) > 2:
                    original_Image.paste(img[2], (img_size * 2, 0))
                    if len(img_urls) > 3:
                        original_Image.paste(img[3], (0, img_size))
                        if len(img_urls) > 4:
                            original_Image.paste(img[4], (img_size, img_size))
                            if len(img_urls) > 5:
                                original_Image.paste(img[5], (img_size * 2, img_size))
                                if len(img_urls) > 6:
                                    original_Image.paste(img[6], (0, img_size * 2))
                                    if len(img_urls) > 7:
                                        original_Image.paste(img[7], (img_size, img_size * 2))
                                        if len(img_urls) > 8:
                                            original_Image.paste(img[8], (img_size * 2, img_size * 2))
        else:
            img_count = 0

        original_Image.save("out.jpg")
        img_count = 1
        img = self.upload_files(imgcanvasw, imgcanvash)
        return img

    def take_ali_img(self,media_text):
        ali_goods_links = Data().get_aliexpress_links(media_text)
        ali_img_urls = []
        if len(ali_goods_links) > 9:
            ali_goods_links = ali_goods_links[:9]
        if len(ali_goods_links) != 1:
            for link in ali_goods_links:
                ali_img_urls.append(self.get_main_image(link))
        else:
            ali_img_urls.append(self.get_main_image(ali_goods_links[0]))
        return self.collage(ali_img_urls)


class Epn:
    def create_creative(self,link):
        url_tc = "https://app.epn.bz/creative/create"
        payload_tc = "link=" + link + "&offerId=1&description=test&type=link"
        headers_tc = {
            'Content-Type': "application/x-www-form-urlencoded",
            'X-ACCESS-TOKEN': epn_token}
        response = requests.request("POST", url_tc, data=payload_tc, headers=headers_tc)
        time.sleep(0.5)
        code = json.loads(response._content.decode("utf-8"))
        fshort_link = code['data']['attributes']['code']
        url_ts = "https://app.epn.bz/link-reduction"
        payload_ts = "urlContainer=" + fshort_link + "&domainCutter=ali.pub"
        headers_ts = {
            'Content-Type': "application/x-www-form-urlencoded",
            'X-ACCESS-TOKEN': epn_token}
        r_link = requests.request("POST", url_ts, data=payload_ts, headers=headers_ts)
        time.sleep(0.5)
        code_link = json.loads(r_link._content.decode("utf-8"))
        short_link = code_link['data']['attributes'][0]['result']
        return short_link

    def get_ssid(self):
        try:
            url = "http://oauth2.epn.bz/ssid"
            querystring = {"client_id": client_id}
            headers = {
                'X-API-VERSION': "2"}
            response = requests.request("POST", url, headers=headers, params=querystring)
            code = json.loads(response._content.decode("utf-8"))

            ssid = code['data']['attributes']['ssid_token']
            # print( 'ssid is ' + str( ssid ) )
        except Exception as e:
            print("\033[31m {} ssid".format(e))
        return ssid

    def get_token(self,ssid):
        global epn_token
        try:
            url = "https://oauth2.epn.bz/token"
            payload = "grant_type=client_credential&client_id=" + client_id + "&client_secret=" + client_secret
            headers = {
                'X-API-VERSION': "2",
                'X-SSID': ssid,
                'Content-Type': "application/x-www-form-urlencoded"
            }
            r_token = requests.request("POST", url, data=payload, headers=headers)
            decode = json.loads(r_token._content.decode("utf-8"))
            epn_token = decode['data']['attributes']['access_token']

        except Exception as e:
            print("\033[31m {} token".format(e))

        return epn_token

    def refresh_token(self):
        ssid = self.get_ssid()
        self.get_token(ssid)

    def timer_refresh_token(self):
        self.refresh_token()
        Timer(7200.0, self.refresh_token).start()
        return print('refresh token\nnew token is \n' + epn_token)

    def change_links(self,media_text):
        try:
            changed_media_text = media_text
            allurl = Data().get_aliexpress_links(media_text)

            b = 0
            L = len(allurl)
            print(f'ссылок всего {L}')
            for i in range(L):
                try:
                    link = self.create_creative(allurl[i])
                    changed_media_text = re.sub(allurl[i], link, changed_media_text)
                    b += 1
                    print(f'Без ошибок сделано {b} ссылок из {L}')
                except Exception as e:
                    print(f'in change links error {e}')
        except Exception as e:
            print(f'change links error {e}')

        return changed_media_text

class Data:
    def get_aliexpress_links(self,text):
        return re.findall(reg_ali,text)
    def get_aliexpress_links_from_vk(self,text):
        return re.findall(reg_vk,text)
    def last_url(self,l_url):
        #ressp = requests.get(l_url)
        # history = len(ressp.history)
        # try:
        #     for i in range(history):
        #         res = ressp.history[i].url
        #         i += 1
        #         if re.findall(reg_ali,res):
        #             break
        #     resp = re.findall(reg_ali, res)
        #     resp = resp[0]
        # except Exception as e:
        #     print(f'lasturl error {e} ')
        #     resp = re.findall(reg_ali, ressp.url)
        #     try:
        #         resp = resp[0]
        #     except:
        #         pass
        # return resp
        return requests.get(l_url).url
    def last_urls(self,text):
        links = self.get_aliexpress_links_from_vk(text)
        lasturls = []
        for link in links:

            r = self.last_url(link)
            r = Data().get_aliexpress_links(r)[0]
            try:
                r = r.replace('m.', '')
            except:
                print('нет ссылки с мобильной весией')
            lasturls.append(r)
        return lasturls

    def take_posts(self,domain, my_vk_token):
        wall = requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'access_token': my_vk_token,
                                'v': ver,
                                'domain': domain,
                                'offset': offset,
                                'count': count
                            })
        time.sleep(1)
        all_posts = wall.json()['response']['items']
        # print(f'{all_posts} {domain}')
        try:
            if all_posts[0]['is_pinned'] == 1:
                all_posts = all_posts[1:]

        except:
            pass
        return all_posts



    @staticmethod
    def send_post(media_text):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Oпубликовать в SUPERCOUPONS', callback_data='but1 '),
               types.InlineKeyboardButton(text='Опубликовать в AliKupon', callback_data='but2 '))
        return bot.send_message(chat_id, media_text, parse_mode="HTML", reply_markup=kb)



    @staticmethod
    def publish(chat_id, media_text):

        media_text = re.sub(reg_tg, '', media_text)
        ali_img = Img().take_ali_img(media_text)
        changed_media_text = Epn().change_links(media_text)
        changed_media_text = f"<a href='{ali_img}'>&#8203; </a>{changed_media_text}"
        return bot.send_message(chat_id, changed_media_text, parse_mode="HTML")



    @staticmethod
    def delete_watermark(domain, media_text):
        if domain == 'alikot_sale':
            media_text = re.sub(reg_ali_kot[0], '', media_text)
            media_text = re.sub(reg_ali_kot[1], '', media_text)
            media_text = re.sub(reg_ali_kot[2], '', media_text)
        if domain == 'alikupon2018':
            media_text = re.sub(reg_ali_kupon, '', media_text)
        return media_text
    def take_media_post(self,domain, vktoken, index):
        global time_post, media_text
        img_urls = []
        all_posts = self.take_posts(domain, vktoken)
        timelast = all_posts[0]['date']
        if timelast > time_post[index]:
            media_text = all_posts[0]['text']
            if self.get_aliexpress_links_from_vk(media_text):
                print(f'получил пост от {domain}')
                time_post[index] = timelast
                owner_id = all_posts[0]['owner_id']
                idown = all_posts[0]['id']
                debug_info = f'\n\n### _______DEBUG INFO\n Источник : vk.com/{domain}?w=wall{owner_id}_{idown}'
                len_text = 4096 - int(len(debug_info))
                media_text = media_text[:len_text]
                media_text = self.delete_watermark(domain,media_text)
                if all_posts[0]['attachments']:
                    if len(img_urls) <= 0:
                        img = all_posts[0]['attachments'][0]['photo']['sizes'][-1]['url']
                    m_text = self.get_aliexpress_links_from_vk(media_text)
                    for url in m_text:
                        try:
                            link = self.last_url(url)
                            link = self.get_aliexpress_links(link)
                            media_text = re.sub(url, link[0], media_text)
                        except:
                            pass
                    media_text = f"<a href='{img}'>&#8203; </a>{media_text} {debug_info}"
                    self.send_post(media_text)








class Main(Thread):
    def run(self):
        while True:

            try:
                Data().take_media_post('alikot_sale', vk_tokens[0], 0)
            except Exception as e:
                bot.send_message(chat_id, f' {e}')
            try:
                Data().take_media_post('kitayposilka', vk_tokens[1], 1)
            except Exception as e:
                bot.send_message(chat_id, f' kitayposilka {e}')

            try:
                Data().take_media_post('alikupon2018', vk_tokens[3], 3)
            except Exception as e:
                bot.send_message(chat_id, f' alikupon2018 {e}')
            try:
                Data().take_media_post('alikdarom', vk_tokens[4], 4)
            except Exception as e:
                bot.send_message(chat_id, f' alikdarom {e}')
            try:
                Data().take_media_post('onedollarali', vk_tokens[5], 5)
            except Exception as e:
                bot.send_message(chat_id, f' onedollarali {e}')
            time.sleep(20)


def start():
    top.setDefaultAppInfo("28620558", "1b42763e84700a9b0186eb733aade525")
    Epn().timer_refresh_token()
    print('start work')
    t = Main()
    t.start()



@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'but1 ':
        print('__\nsend post to SC\n__')
        try:
            msg = c.message.text
            Data().publish(chat_id_to_post, msg)
        except Exception as e:
            bot.send_message(chat_id, f'error send msg to SC {e}')


    elif c.data == 'but2 ':
        print('__\nsend post to alikupon\n__')
        try:
            msg = c.message.text
            Data().publish(chat_id_to_post2, msg)
        except Exception as e:
            bot.send_message(chat_id, f'error send msg to alikupon {e}')



if __name__ == '__main__':
    start()
    bot.polling(none_stop=True)
