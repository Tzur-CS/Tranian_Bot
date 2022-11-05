from selenium import webdriver
from travian_bot import constants as const
import keyboard as keyboard
import schedule
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
import queue
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import DownloadMap

# https://t4.answers.travian.com/?view=answers&action=answer&aid=217
# PATH = "C:\Program Files (x86)\chromedriver.exe"
# SERVER_PATH_X2_AMERICA = "https://ts20.x2.america.travian.com/"
# SERVER_PATH_X2_ASIA = "https://ts20.x2.asia.travian.com/"
# USER_NAME = "GloryToEladR"  # "GloryToelad"
# PASSWORD = "bottestv1"

normal_village = {"wood": [1, 3, 14, 17], "crop": [2, 8, 9, 12, 13, 15], "clay": [5, 6, 16, 18],
                  "iron": [4, 7, 10, 11]}


class TravianBot:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.option = webdriver.ChromeOptions()
        # self.option.add_argument('headless')
        self.driver = webdriver.Chrome(const.PATH, options=self.option)
        self.driver.get(driver_path)
        self.driver.implicitly_wait(15)
        # self.rss_per_village = {"1" : {"wood": 0, "clay": 0, "iron": 0, "crop": 0}}
        self.rss_per_village = {}
        self.villages_task = dict()
        self.function_dic = {"up_b": self.upgrade_building, "b_b": self.upgrade_building,
                             "up_f": self.upgrade_filed, "w_q": self.work_queue}
        # self.task_queue = queue.Queue()
        # self.villages_list = list()
        schedule.every(1).minutes.do(self.next_task)
        schedule.every(1).minutes.do(self.p)

    def p(self):
        print("schedule")

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
        search[0].send_keys(const.USER_NAME)
        search[1].send_keys(const.PASSWORD)
        if self.is_exist(By.ID, 'cmpbntyestxt'):
            for cookies in self.driver.find_elements(By.ID, 'cmpbntyestxt'):
                if "Accept all" in cookies.text:
                    cookies.click()
        if self.is_exist(By.TAG_NAME, const.BUTTON):
            buttons = self.driver.find_elements(By.TAG_NAME, const.BUTTON)
            for button in buttons:
                if const.LOGIN in button.text:
                    button.click()
        self.update_villages_map()
        time.sleep(1)

    def click_navigation(self, icon: str):
        """
        click on a specific icon in the navigation bar
        :param icon: what kind of icon we what to click
        :return: None
        """
        if self.is_exist(By.ID, const.NAVIGATION):
            self.driver.find_element(By.ID, const.NAVIGATION).find_element(By.CLASS_NAME, icon).click()

    def task_to_village(self, task : str, task_input: str, village_num : str):
        """ construction
        this method push to the task queue a new task
        :param village_num:
        :param task: what kind of task to do
        :param task_input: function parameters
        :return: None
        """
        task_queue_v = self.villages_task[village_num]
        task_queue_v.put((task, task_input))
        # self.task_queue.put((function, fun_input))

    def update_villages_map(self):
        if self.is_exist(By.ID, "sidebarBoxVillagelist"):
            villages_icon = self.driver.find_element(By.ID, "sidebarBoxVillagelist")
            villages_list_icon = villages_icon.find_element(By.CLASS_NAME, "villageList")
            for village in villages_list_icon.find_elements(By.CLASS_NAME, "dropContainer"):
                village_num = village.get_attribute("data-sortindex")
                village_name = village.find_element(By.CLASS_NAME, "coordinatesGrid") \
                    .get_attribute("data-villagename")
                # self.villages_task[village_num] = queue.Queue()
                print(village_num + " " + village_name + " map added.")
                new_queue = queue.Queue()
                self.villages_task[village_num] = new_queue
            print("done with update villages map.")

    def updated_rss(self):
        """

        :return:
        """
        self.click_navigation(const.RSS_ICON)
        if self.is_exist(By.CLASS_NAME, "stockBarButton"):
            all_rss = self.driver.find_elements(By.CLASS_NAME, "stockBarButton")
            for i in range(0, 4):
                self.rss_per_village[const.RSS[i]] = self.str_to_int(all_rss[i].text)

    def can_build(self):
        """

        :return:
        """
        self.click_navigation(const.RSS_ICON)
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
        if building_name == "Rally Point":
            for slot in self.driver.find_elements(By.CLASS_NAME, const.BUILDING_SLOT):
                if building_name == "Rally Point" and slot.get_attribute("data-aid") == "39":
                    slot.click()
                    self.driver.find_element(By.CLASS_NAME, "buildingWrapper") \
                        .find_element(By.TAG_NAME, "button").click()
                    return

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
        for village in self.villages_task.items():
            print("tasks for villages: " + village[0])
            for task in village[1].queue:
                print(task)

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
                self.task_to_village(next_action, parameters)
                return
            if next_action == "c":
                return

    def get_next_task(self, village_queue):
        """
        get the next task from the task queue and exsuit it
        :return:
        """
        # for village_num_queue in self.villages_task.items():
        #     village_queue = village_num_queue[1]
        #     village_num = village_num_queue[0]
        if village_queue.qsize() > 0:
            action = village_queue.get()
            print(action)
            if action[0] == "up":
                if action[1] in const.RSS:
                    self.upgrade_filed(action[1])
                    return
                else:
                    self.upgrade_building(action[1])
                    return
            self.function_dic[action[0]](action[1])

    def next_task(self):
        """

        :return:
        """
        print("we entered to next task method")
        for village_items in self.villages_task.items():
            self.villages_list_chenger(village_items[0])
            print("we are in next task what to go to vellage " + village_items[0])
            time.sleep(0.5)
            if self.can_build():
                village_current_task = village_items[1]
                print(village_current_task)
                self.get_next_task(village_items[1])

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
        print("The current status of " + const.USER_NAME + ":")
        self.updated_rss()
        print("wood: {wood}, clay: {clay}, iron: {iron}, crop: {crop}".format(wood=self.rss_per_village[const.WOOD],
                                                                              clay=self.rss_per_village[const.CLAY],
                                                                              iron=self.rss_per_village[const.IRON],
                                                                              crop=self.rss_per_village[const.CROP]))
        print("Building List:")
        if self.is_exist(By.CLASS_NAME, const.BUILDING_LIST):
            if len(self.driver.find_element(By.CLASS_NAME, const.BUILDING_LIST).find_elements(By.CLASS_NAME,
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
        else:
            print("no building list, to build something?")
        print("-" * 60)

    def villages_list_chenger(self, village_num):
        if self.is_exist(By.ID, "sidebarBoxVillagelist"):
            villages_icon = self.driver.find_element(By.ID, "sidebarBoxVillagelist")
            villages_list_icon = villages_icon.find_element(By.CLASS_NAME, "villageList")
            for village in villages_list_icon.find_elements(By.CLASS_NAME, "dropContainer"):
                if village.get_attribute("data-sortindex") == village_num:
                    village.click()
                    time.sleep(1)
                    return

    def new_village(self):
        pass

    def new_village_day_one(self, village_num):
        # build warehouse and granary to lv 9 and 5 TODO: if the lv is high dont upgrade
        # for i in range(10):
        #     self.add_to_queue(self.upgrade_building, "Warehouse", village_num)
        # for i in range(6):
        #     self.add_to_queue(self.upgrade_building, "Granary", village_num)

        # build main building lv 20 with gold if we have any gold TODO: add a gold use option
        for i in range(20):
            self.task_to_village("up", "Main Building", village_num)

        for i in range(73):
            self.task_to_village("up", const.RSS[i % 4], village_num)

# schedule.every(5).minutes.do(next_task)
