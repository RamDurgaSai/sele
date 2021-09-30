import sys
import requests
from selenium.webdriver import Firefox, FirefoxOptions
from webbrowser import open as open_in_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep, localtime
from os.path import join as jion_path, isdir,isfile
from os import getcwd, mkdir, remove
import pyautogui
from pyrogram import Client
from requests import get
import time
import json
from Log import Log
from Data import DataBase
from subprocess import Popen
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from deep_translator import GoogleTranslator,MicrosoftTranslator,MyMemoryTranslator
import calendar


class Sele():

    def __init__(self, echo=True):
        """
         Class Sele to Do Sele Stuff (No Public Meaning Yet)
        :param echo: Pass True to say Echo Text(Defaults to Ture)
        """
        self.load_settings()
        pyautogui.FAILSAFE = False
        self.log = Log('log.txt',debug_mode=True)
        self.db = DataBase(file="data.db")
        self.db.create_tables(*self.programs)

        print(
            f"""{Sele.__name__} V {self.__version__} copyright (C) 2021 https://github.com/RamDurgaSai/{Sele.__name__}\nRunning on {sys.platform} \n""")
        self.vpn_settings = None
        self.is_vpn_connected = None
        self.translator = None

    def load_settings(self):
        """
        To Load Settings(can Say Configurations) to class(self)
        :return: Nothing(say None) - Just loads things to class
        """
        with open("config.secret", mode="r", encoding="utf-8") as config:
            configs = json.load(config)
            self.__version__ = configs["__version__"]
            self.telegram = configs['telegram']
            self.pdisk = configs['pdisk']
            self.selenium = configs['selenium']
        with open("programs.json", mode="r", encoding="utf-8") as program:
            self.programs = json.load(program)
            # self.log.debug(f"Total Progarams \n{self.programs}", to_print=False)
        with open('channels.json', mode="r", encoding="utf-8") as channels:
            self.channels = json.load(channels)
            # self.log.debug(f"Total channles \n {self.channels}", to_print=False)

    def get_info(self, link: str, vpn: bool = True, latest_episode: bool = True) -> dict:
        """
        :param link: link of webpage
        :param latest_episode: pass True to get latest episode Info
        :return: dict containing video information
        """
        self.log.debug(f"Called Get Info with link:{link},latest_episode={latest_episode}", to_print=False)

        def setup_vpn():
            self.vpn_settings = initialize_VPN(area_input=["India"])
            rotate_VPN(self.vpn_settings)
            self.is_vpn_connected = True

        def _get_info(self, link, latest_episode):
            option = FirefoxOptions()
            option.add_argument("--headless")
            browser = Firefox(executable_path=self.selenium["executable_path"], options=option)
            self.log.debug(f"Scraping Content for {link} in headless Browser")
            browser.get(link)
            if latest_episode:
                latest_episode_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div/div[1]/div/div/div/a/article/div[4]/div[1]'
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, latest_episode_xpath)))
                latest_episode = browser.find_element_by_xpath(latest_episode_xpath)
                latest_episode.click()

            else:
                second_latest_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div/a/article/div[3]'
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, second_latest_xpath)))
                episode = browser.find_element_by_xpath(second_latest_xpath)
                episode.click()

            soup = BeautifulSoup(browser.page_source, "html.parser")
            for script in soup.find_all("script"):
                try:
                    if "window.APP_STATE" in str(script):
                        dic = json.loads(script.get_text()[17:])
                        episo = \
                        dic[link.replace("https://www.hotstar.com", "")]["initialState"]["contentDetail"]["trays"][
                            "items"][0]['assets']["items"][0]

                except Exception as e:
                    self.log.warn("Can't get Episode Description .." + str(e))
                    episo = {"title": None, "description": None}
            ###############
            scraped_data = {
                "name": soup.title.text.replace("'",''),
                "url": browser.current_url.replace("'",''),
                "image_url": soup.find("meta", property="og:image")['content'].replace("'",''),
                "description": soup.find("meta", attrs={"name": "description"})['content'].replace("'",''),
                "episode": {
                    "title": episo['title'].replace("'",''),
                    "description": str(episo['description']).replace("'",'')
                },
                "keywords": soup.find("meta", attrs={"name": "keywords"})['content'].replace("'",'').split(", ")
            }
            browser.quit()  # Just close the Browser
            self.log.debug(f"Scrapped Data for {link}\n{str(scraped_data)}", to_print=False)
            return scraped_data

        try:
            # if vpn:
            #     setup_vpn()
            self.log.debug("Connect to  Vpn Waiting for 10 sec")
            sleep(20)
            return _get_info(self, link, latest_episode)
        except Exception as e:
            self.log.error(f"Can't Scrap data Due to {e}\n ")
            self.log.debug("Trying to Scrap Again")
            self.get_info(link, vpn, latest_episode)

    def download(self, url: str, name: str, timeout: int = 300) -> str:
        """
        To Download Video by link
        :param url: url of source
        :param name: name of content(To save on Disk)
        :param timeout: timeout (Default 300s or 5 Min)
        :return: After Successfully Downloaded returns absolute path of Video
        """
        self.log.debug(f"Called Download with  url = {url}, str= {str} timeout = {timeout}", to_print=False)

        video_location = jion_path(getcwd(), "videos", f'{name}.mp4')
        self.log.debug(f"video_location is {video_location}")

        def _kill_browsers():
            self.log.debug(f"Killing Existing(Running Currently) Browsers ")
            Popen('taskkill /im firefox.exe /f', shell=False)
            Popen('taskkill /im chrome.exe /f', shell=False)

        def _download():
            if not isdir(jion_path(getcwd(), "videos")):
                mkdir(jion_path(getcwd(), "videos"))
                self.log.warn(f"Video Folder doesn't exit created new one at {jion_path(getcwd(), 'videos')}",
                              to_print=False)
            self.log.debug(f"Trying Dowload Video of link :-{url}")
            open_in_browser(url)  # Open in Browser

            sleep(10)
            x, y = pyautogui.size()
            pyautogui.click(x // 2, y // 2)  # Click on Center of Screen
            self.log.debug(f"Screen size is {pyautogui.size()}", to_print=False)
            oppened_time = time.time()
            while True:
                sleep(5)
                self.log.debug("Trying Locate Idm Download Button On Screen", to_print=False)
                location = pyautogui.locateOnScreen("images\\idm_download.PNG", grayscale=True,
                                                    confidence=.5)  # To get save_as box measures
                if location == None:
                    if int(time.time() - oppened_time) <= timeout:  # If waited timeout seconds
                        self.log.debug(f"Idm Button Not Found :: Waited {int(time.time() - oppened_time)}s",
                                       to_print=False)
                    else:
                        self.log.debug(f"TimedOutForIdmButton:: Waited {int(time.time() - oppened_time)}s")
                        raise Exception("TimeOutForIdmButton")
                else:

                    x, y = pyautogui.size()
                    pyautogui.click(x // 2, y // 2)  # Click on Center of Screen(To pause Video)
                    left, top, width, height = location
                    self.log.debug(f"Idm Button Found at {location}", to_print=False)
                    break
            sleep(60)

            pyautogui.click(x=left + width // 2, y=top + height // 2)  # Click on download Button

            sleep(1)
            position = pyautogui.locateOnScreen("images\\quality_480_p.png", grayscale=True, confidence=.5)
            left, top, width, height = position

            self.log.debug(f"Selected Video Quality at {position}", to_print=False)
            pyautogui.click(x=left + width // 2, y=top + height // 2)
            sleep(5)

            if pyautogui.locateOnScreen("images\\forbidden.png"):
                # if server forbidden the download
                self.log.error("Downloading Video is Forbidden")
                raise Exception("Server Forbidden the Download ")
            if pyautogui.locateOnScreen("images\\exists.png"):
                # if file already exits -- click on ok
                self.log.error("File Already exits -- Overwriting file", to_print=False)
                if pyautogui.locateOnScreen("images\\yes.png"):
                    pyautogui.click("images\\yes.png")
                else:
                    raise Exception("Can't find yes button when file aleardy exists")

            left, top, width, height = pyautogui.locateOnScreen("images\\save_as.png")
            pyautogui.click(x=left + 100, y=top + 10)

            pyautogui.hotkey("ctrl", 'a')  # select all
            pyautogui.press("clear")  # Back Space
            pyautogui.write(video_location)  # enter video_location

            sleep(3)
            pyautogui.click("images\\start_download.PNG")
            sleep(2)
            _kill_browsers()
            download_time_vpn = download_started_time = time.time()
            while None == pyautogui.locateOnScreen("images\\folder_icon.png"):
                self.log.debug(
                    f"Waiting for completion of dowload :: Waited {int(time.time() - download_started_time)}",
                    to_print=False)
                sleep(2)
                if pyautogui.locateOnScreen("images\\forbidden.png"):
                    # if server forbidden the download
                    raise Exception("Server Forbidden the Download ")
                if pyautogui.locateOnScreen("images\\exists.png"):
                    # if file already exits -- click on ok
                    if pyautogui.locateOnScreen("images\\yes.png"):
                        pyautogui.click("images\\yes.png")
                    else:
                        raise Exception("Can't find yes button when file aleardy exists")
                if time.time() - download_started_time > timeout * 10:
                    self.log.error(
                        f"waited more than {int((time.time() - download_started_time) // 60)} min  -- But can't download ")
                    raise Exception(
                        f"waited more than {int((time.time() - download_started_time) // 60)} min  -- But can't download ")

            # Video Completely Downloaded
            self.log.debug(f"Video Downloaded at {video_location} for url {url}")
            pyautogui.click("images\\close.png")

        try:
            _kill_browsers()
            sleep(5)
            _download()
            sleep(5)
            _kill_browsers()
        except Exception as e:
            self.log.error("Can't Download Due to Following Exception \n\n" + str(e) + "\n\nTrying to Redownload ... ")
            self.download(url, name, timeout)
        return video_location

    def send_video(self, video_file: str, name: str, description: str, thumb: str, chat_id: str = "testingmaa", ):
        """
        Send Video to Telegram
        :param file: path of video  
        :param name: name of video
        :param description: description of video (Caption)
        :param thumb: Thumbnail Path
        :param chat_id: chat_id path 
        :return: returns None after video post
        """""
        self.log.debug(
            f"Called send_video with \nvideo_file = {video_file} \n name = {name} \n description = {description}"
            f"\n chat_id ={chat_id} ", to_print=False)
        self.log.debug(f"getting thubnail for {thumb} and saving in images/thumb ", to_print=False)
        with open("images\\thumb.png", "wb") as file:
            file.write(get(thumb).content)

        def progress(current, total):
            self.log.debug(f' progress of sending video :- {current * 100 / total}', to_print=False)
            if total == current:
                return

        with Client("do", api_hash=self.telegram['api_hash'], api_id=self.telegram['api_id'],
                    no_updates=True) as telegram:
            self.log.debug(f"sending video {video_file} to telegram")
            telegram.send_video(chat_id=chat_id, video=video_file, caption=description, thumb="images\\thumb.png",
                                file_name=name, supports_streaming=True, progress=progress)

    def send_picture(self, photo, description):
        self.log.debug(
            f"Called send_video with \nphoto = {photo}  \n description = {description}", to_print=False)
        with Client("do", api_hash=self.telegram['api_hash'], api_id=self.telegram['api_id'],
                    no_updates=True) as telegram:
            for channel in self.channels["public"]:
                self.log.debug(f"sending picture {photo} to telegram channel {channel}")
                telegram.send_photo(chat_id=channel, photo=photo, caption=description)

    def pdisk_link(self, video_location: str, title: str, description: str) -> str:
        """
        To Upload video to Pdisk.com
        :param video_location: path of video
        :param title: title for video
        :param description: Description for Video
        :return: pdisk url of video after successful upload
        """
        self.log.debug("Disconnect vpn ---> waiting ")
        sleep(20)
        self.log.debug(
            f"Called pdisk_link method with video_location = {video_location} ", to_print=False)

        get_url, post_url, api_key = self.pdisk['get_url'], self.pdisk['post_url'], self.pdisk['api_key']

        get = requests.get(url=get_url, params={"api_key": api_key})

        create_url, sign_url = json.loads(get.text)["data"]["create_url"], json.loads(get.text)['data']['sign_url']
        self.log.debug(f"Uploading Video to pdisk {video_location}")
        with open(video_location, 'rb') as file:
            put = requests.put(url=sign_url, data=file, headers={"Content-Type": None})

        if put.status_code == 200:
            data = {
                "api_key": api_key,
                "content_src": create_url,
                "link_type": "link",
                "title": title,
                "description": description
            }

            post = requests.post(url=post_url, data=data)

            item_id = json.loads(post.text)['data']['item_id']

            link = f'https://www.pdisk.me/share-video?videoid={item_id}'

            self.log.debug(f"video is uploaded to pdisk and available at {link}")

            return link

    def translate(self,text, to_lang="telugu"):
        try:
            if not self.translator:
                self.translator = GoogleTranslator(source='auto', target=to_lang)
            return self.translator.translate(text)
        except:
            return text

    def run(self):
        year, month, day, hour, minute, second, wd, yd, isd = localtime()
        date = 10_000 * year + 100 * month + day
        try:

            for key, value in self.programs.items():
                info = self.db.select("info", table=key, date=date)

                if len(info) == 0 or info == None:  # Not exists
                    self.log.debug(f"Doing Work for program {key}")
                    info = self.get_info(value, latest_episode=True)  # Get Info
                    # Update In DataBase
                    self.db.insert(table=key,date = date,info=info)
                else:
                    info,  = info[0]
                    info = json.loads(str(info).replace("'",'"'))

                program_name = list(str(info['name']).split("-"))[0]

                video_path = self.db.select("path",table=key,date=date)
                video_path, = video_path[0]

                if video_path == None or len(video_path) == 0 or not isfile(video_path) :
                    video_path = self.download(info["url"],
                                               f"{program_name}-{int(second)}-{hour}-{day}-{month}-{year}")  # Download it
                    self.db.insert(table= key,date = date,path = video_path) # Update in DB


                pdisk_url = self.db.select("pdisk",table=key,date=date)
                self.log.debug("fetch of pdisk \n"+str(pdisk_url))
                if None == pdisk_url or len(pdisk_url) == 0:
                    video_name_for_pdisk = f'{calendar.month_name[month]} {day} - {calendar.day_name[wd]} {program_name}'
                    video_description_for_pdisk = info["episode"]["description"]
                    pdisk_url = self.pdisk_link(video_location=video_path, title=self.translate(video_name_for_pdisk),
                                            description=self.translate(video_description_for_pdisk))
                    self.db.update(table=key,date= date, pdisk = pdisk_url)
                else:
                    pdisk_url, = pdisk_url[0]

                telegram_status, = self.db.select("telegram",table=key,date=date)
                self.log.debug("fetch of telegram \n"+str(telegram_status))
                if None == telegram_status or bool(telegram_status[0]):
                    description_for_telegram = \
                        f'**{calendar.month_name[month]} {day} ({calendar.day_name[wd]}) {program_name}** \n\n' \
                        f'{info["episode"]["title"]}\n\n {info["episode"]["description"]}\n\n' \
                        f' 🖥 WATCH ONLINE || DOWNLOAD⬇️ \n\n[Ultra 📡 Fast Speed (Boosted🚀)]Watch on PLAYit⤵     ️\n\n▶ (480p) - {pdisk_url}\n\n  ' \
                        + " ".join(
                            ["#" + keyw.replace(" ", "_") for keyw in info['keywords']])

                    self.log.debug(f"Modified Description is {description_for_telegram}", to_print=False)

                    self.send_picture(photo=info['image_url'], description=self.translate(description_for_telegram))
                    self.db.update(type="telegram",table=key,date=date,data = True)
                try:
                    remove(video_path)
                except Exception as e:
                    self.log.debug(f"can't delete {video_path} due to {e}", to_print=False)
        except Exception as e:
            self.log.warn(f"Algorithm Failed Due to \n \n\n----> Restarting Algorithm ",to_print=True)
            raise e
            self.run()



def test_log():
    log = Log("log.txt")
    log.debug("djfkljdklfjd")


def test_get_info():
    s = Sele()
    for key, values in s.programs.items():
        s.get_info(link=values, latest_episode=False, vpn=False)


if __name__ == '__main__':
    Sele().run()
    # test_log()
    # test_get_info()
