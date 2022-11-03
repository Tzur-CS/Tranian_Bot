from selenium import webdriver
import queue
from travian_bot import constants as const
import keyboard as keyboard
import schedule
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import DownloadMap

# https://t4.answers.travian.com/?view=answers&action=answer&aid=217
PATH = "C:\Program Files (x86)\chromedriver.exe"
SERVER_PATH_X2_AMERICA = "https://ts20.x2.america.travian.com/"
SERVER_PATH_X2_ASIA = "https://ts20.x2.asia.travian.com/"
USER_NAME = "GloryToEladR"  # "GloryToelad"
PASSWORD = "bottestv1"

normal_village = {"wood": [1, 3, 14, 17], "crop": [2, 8, 9, 12, 13, 15], "clay": [5, 6, 16, 18],
                  "iron": [4, 7, 10, 11]}


class TravianBot:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.option = webdriver.ChromeOptions()
        # self.option.add_argument('headless')
        self.driver = webdriver.Chrome(PATH, options=self.option)
        self.driver.get(driver_path)
        self.driver.implicitly_wait(15)
        self.current_rss = {"wood": 0, "clay": 0, "iron": 0, "crop": 0}
        self.task_queue = queue.Queue()
        self.function_dic = {"up_b": self.upgrade_building, "b_b": self.upgrade_building,
                             "up_f": self.upgrade_filed, "w_q": self.work_queue}
        schedule.every(1).minutes.do(self.next_task)
        schedule.every(1).minutes.do(self.p)

    def p(self):
        print("test")

    def str_to_int(self, value: str):
        """
        str_to_int function will convernt a string number to int "1,234"->1234
        :param value: string type number
        :return: integer
        """
        result = 0
        for letter in value:
            if letter.isdigit():
                result = int(letter) + result * 10
        return result

    def is_exist(self, by: By, value: str):
        """

        :param by: by what HTML supported locator strategies
        :param value: the name of the locator
        :return: Ture if we find the element otherwise False
        """
        try:
            self.driver.find_element(by, value)
            return True
        except WebDriverException:
            print("An EXCEPTION was in is_exist " + by + "  " + value)
            return False

    def login_to_user(self):
        """
        this function login to the user
        :return: None
        """
        search = self.driver.find_elements(By.CLASS_NAME, "text")
        search[0].send_keys(USER_NAME)
        search[1].send_keys(PASSWORD)
        if self.is_exist(By.ID, 'cmpbntyestxt'):
            for cookies in self.driver.find_elements(By.ID, 'cmpbntyestxt'):
                if "Accept all" in cookies.text:
                    cookies.click()
        if self.is_exist(By.TAG_NAME, "button"):
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Login" in button.text:
                    button.click()
        time.sleep(1)

    def click_navigation(self, icon: str):
        """
        click on a specific icon in the navigation bar
        :param icon: what kind of icon we what to click
        :return: None
        """
        if self.is_exist(By.ID, const.NAVIGATION):
            self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, icon).click()

    # def click_resources(self):
    #     """
    #
    #     :return:
    #     """
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "resourceView").click()
    #
    # def click_buildings(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "buildingView").click()
    #
    # def click_map(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "map").click()
    #
    # def click_statistics(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "statistics").click()
    #
    # def click_report(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "reports").click()
    #
    # def click_messages(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "messages").click()
    #
    # def daily_quests(self):
    #     if self.is_exist(By.ID, const.NAVIGATION):
    #         self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, "dailyQuests").click()

    def add_to_queue(self, function, fun_input):
        """
        this method push to the task queue a new task
        :param function: what kind of task to do
        :param fun_input: function parameters
        :return: None
        """
        self.task_queue.put((function, fun_input))

    def get_next_function(self):
        """
        get the next task from the task queue and exsuit it
        :return:
        """
        if self.task_queue.qsize() > 0:
            action = self.task_queue.get()
            if action[0] == "up":
                if action[1] in const.RSS:
                    self.upgrade_filed(action[1])
                    return
                else:
                    self.upgrade_building(action[1])
                    return
            self.function_dic[action[0]](action[1])

    def updated_rss(self):
        """

        :return:
        """
        self.click_navigation(const.RSS_ICON)
        if self.is_exist(By.CLASS_NAME, "stockBarButton"):
            all_rss = self.driver.find_elements(By.CLASS_NAME, "stockBarButton")
            for i in range(0, 4):
                self.current_rss[const.RSS[i]] = self.str_to_int(all_rss[i].text)

    def can_build(self):
        """

        :return:
        """
        if not self.is_exist(By.ID, 'resourceFieldContainer'):
            self.click_navigation(const.RSS_ICON)
        if self.is_exist(By.CLASS_NAME, const.BUILDING_LIST):
            if len(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME, 'name')) \
                    == 2:
                return False
            else:
                return True
        return True

    #
    #
    # def click_rally_point():
    #     ToolBarNavigation.click_buildings(driver)
    #     driver.find_element(By.XPATH, '//*[@id="villageContent"]/div[21]/a').click()
    #
    #
    # def send_farm_list():
    #     click_rally_point()
    #     driver.find_element(By.LINK_TEXT, 'Farm List').click()
    #     driver.find_element(By.XPATH, '//*[@id="raidListMarkAll112"]').click()
    #     try:
    #         driver.find_element(By.XPATH, '//*[@id="raidList112"]/div[1]/form').click()
    #     except:
    #         print("not xpath")
    #
    #
    # def enter_coordinate_to_attack():
    #     driver.find_elements(By.NAME, "eventType")[2].click()
    #     driver.find_element(By.XPATH, '//*[@id="yCoordInput"]').send_keys("51")
    #     driver.find_element(By.XPATH, '// *[ @ id = "xCoordInput"]').send_keys("-6")
    #     driver.find_element(By.XPATH, '// *[ @ id = "xCoordInput"]').send_keys(Keys.ENTER)
    #     driver.find_element(By.ID, "checksum").click()
    #
    #
    # def click_send_troops():
    #     driver.find_element(By.LINK_TEXT, "Send troops").click()
    #
    #
    # def choose_troops():
    #     driver.find_element(By.NAME, "troop[t1]").send_keys("4")
    #
    #
    # def send_troops():
    #     driver.find_element(By.NAME, "send").click()
    #
    #
    # def attack_oasis_from_rally_point():
    #     ToolBarNavigation.click_buildings(driver)
    #     click_rally_point()
    #     click_send_troops()
    #     choose_troops()
    #     enter_coordinate_to_attack()
    #
    #
    def upgrade_building(self, building_name: str):
        """

        :param building_name:
        :return:
        """
        self.click_navigation(const.BUILDING_ICON)
        for slot in self.driver.find_elements(By.CLASS_NAME, const.BUILDING_SLOT):
            if slot.get_attribute('data-name') == building_name:
                slot.click()
                break
        for bwn in self.driver.find_elements(By.TAG_NAME, "button"):
            if "Upgrade to level" in bwn.text:
                print(bwn.text + building_name)
                bwn.click()
                break

    def build_building(self, building_name: str):
        """

        :param building_name:
        :return:
        """
        self.click_navigation(const.BUILDING_ICON)
        for slot in self.driver.find_elements(By.CLASS_NAME, const.BUILDING_SLOT):
            if slot.text == "":
                slot.find_element(By.TAG_NAME, "path").click()
                break
        for building in self.driver.find_elements(By.CLASS_NAME, "buildingWrapper"):
            if building_name in building.text:
                try:
                    building.find_element(By.TAG_NAME, "button").click()
                    break
                except:
                    print("we cant build {name}".format(name=building_name))
                    break

    def work_queue(self):
        """

        :return:
        """
        for work in self.task_queue.queue:
            print(work)

    def upgrade_filed(self, rss_type, village_type=normal_village):
        """

        :param rss_type:
        :param village_type:
        :return:
        """
        self.click_navigation(const.RSS_ICON)
        min_level_slot = None
        for filed in village_type.get(rss_type):
            if min_level_slot is None:
                min_level_slot = filed
            else:
                if self.driver.find_element(By.CLASS_NAME, const.buildingSlot.format(loc=min_level_slot)).text == "":
                    current_level = 0
                else:
                    current_level = int(
                        self.driver.find_element(By.CLASS_NAME, const.buildingSlot.format(loc=min_level_slot)).text)
                if self.driver.find_element(By.CLASS_NAME, const.buildingSlot.format(loc=filed)).text == "":
                    next_level = 0
                else:
                    next_level = int(self.driver.find_element(By.CLASS_NAME, const.buildingSlot.format(loc=filed)).text)
                if current_level > next_level:
                    min_level_slot = filed
        self.driver.find_element(By.CLASS_NAME, const.buildingSlot.format(loc=min_level_slot)).click()
        for bwn in self.driver.find_elements(By.TAG_NAME, "button"):
            if "Upgrade to level" in bwn.text:
                print("we upgrade {first} to lv {sec}".format(first=rss_type, sec=bwn.text[-1]))
                bwn.click()
                break

    def collect_rewords(self):
        """

        :return:
        """
        if self.is_exist(By.CLASS_NAME, 'mentor'):
            self.driver.find_element(By.CLASS_NAME, 'mentor').click()
            if self.is_exist(By.CLASS_NAME, 'collect'):
                for i in self.driver.find_elements(By.CLASS_NAME, 'collect'):
                    i.click()

    def action_chooser(self):
        """

        :return:
        """
        next_action = input()
        while next_action != 'c':
            print('For list of function press "f"\n'
                  'For list of Building press "b"\n'
                  'For enter a function press "e"\n'
                  'For cancel the request mode press "c"\n'
                  '(f, b, e , c) - ')
            next_action = input()
            if next_action == "f":
                print("The function as follow:\n "
                      "upgrade_filed(rss_type=(wood, clay, iron, crop), village_type=normal_village),\n"
                      "build_building(building_name: str), upgrade_building(building_name: str), stats()")
            if next_action == "b":
                print("The building are as follow:\n"
                      "Sawmill-מנסרה , Brickyard-בית יציקה , Iron Foundry- , Grain Mill- , Bakery- , Warehouse- ,\n "
                      "Granary- , Smithy- ,  Tournament Square - , Main Building - ,  Rally Point - ,\n"
                      "Marketplace - , arth Wall - , Embassy -	, Palisade - , Barracks - , Stonemason's Lodge - ,\n "
                      "Stable - , Brewery - , Workshop - , Trapper - , Academy - , Hero's Mansion - , Cranny - ,\n"
                      "Great Warehouse - , Town Hall - , Great Granary - , Residence - , Wonder of the World - ,\n"
                      "Palace - , Horse Drinking Trough - , Treasury - , Stone Wall - , Trade Office - ,\n"
                      "Command Center - , Great Barracks - , Makeshift Wall - , Great Stable - , City Wall - \n")
            if next_action == "e":
                print('Hello you have entered to New Task Queue Mode:\n'
                      'places enter next function:')
                next_action = input()
                if next_action == 'stats':
                    self.stats()
                    return
                if next_action == 'w_q':
                    self.work_queue()
                    return
                print("parameters:")
                parameters = input()
                self.add_to_queue(next_action, parameters)
                return
            if next_action == "c":
                return

    def next_task(self):
        """

        :return:
        """
        if self.can_build():
            self.get_next_function()

    def play(self):
        """

        :return:
        """
        while True:
            schedule.run_pending()
            if keyboard.is_pressed("a"):
                self.action_chooser()

    def stats(self):
        """

        :return:
        """
        self.click_navigation(const.RSS_ICON)
        print("-" * 60)
        print("The current status of " + USER_NAME + ":")
        self.updated_rss()
        print("wood: {wood}, clay: {clay}, iron: {iron}, crop: {crop}".format(wood=self.current_rss[const.WOOD],
                                                                              clay=self.current_rss[const.CLAY],
                                                                              iron=self.current_rss[const.IRON],
                                                                              crop=self.current_rss[const.CROP]))
        print("Building List:")
        if self.is_exist(By.CLASS_NAME, const.BUILDING_LIST):
            if len(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                              'name')) == 0:
                print("no building list, to build something?")
            elif len(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                                'name')) == 1:
                print(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME, 'name')[
                          0].text +
                      " finished in: " +
                      self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                            'buildDuration')[
                          0].text)
            elif len(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                                'name')) == 2:
                print(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME, 'name')[
                          0].text +
                      " finished in: " +
                      self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                                 'buildDuration')[
                          0].text)
                print(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME, 'name')[
                          1].text +
                      " finished in: " +
                      self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
                                                                                                 'buildDuration')[
                          1].text)
        print("-" * 60)



# schedule.every(5).minutes.do(next_task)
