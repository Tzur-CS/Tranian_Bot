import time
from travian_bot.bot import TravianBot

# https://t4.answers.travian.com/?view=answers&action=answer&aid=217
PATH = "C:\Program Files (x86)\chromedriver.exe"
SERVER_PATH_X2_AMERICA = "https://ts20.x2.america.travian.com/"
SERVER_PATH_X2_ASIA = "https://ts20.x2.asia.travian.com/"


def run(botr):
    botr.login_to_user()
    # botr.villages_list_chenger("2")
    botr.new_village_day_one("2")
    # botr.get_next_task(botr.villages_task["2"])
    # time.sleep(5)
    # print("______________")
    # botr.get_next_task(botr.villages_task["2"])
    # time.sleep(5)
    # print("______________")
    botr.task_to_village("up", "Cranny", "1")
    # time.sleep(5)
    # print("______________")
    botr.task_to_village("up", "Cranny", "1")
    # time.sleep(5)
    # print("______________")
    botr.work_queue()

    # botr.new_village_day_one("2")
    # botr.next_task()
    botr.play()


if __name__ == '__main__':
    bot = TravianBot(SERVER_PATH_X2_ASIA)
    run(bot)
    time.sleep(10)
    # option = webdriver.ChromeOptions()
    # # option.add_argument('headless')
    # driver = webdriver.Chrome(PATH, options=option)
    # driver.get(SERVER_PATH_X2_ASIA)
    # driver.implicitly_wait(4)
    # driver = web_driver.Webdriver()
    # bot = bot.TravianBot(driver)
    # login_to_user()
    # updated_rss()
    # build_building("Residence")
    # build_building("Marketplace")
    # collect_rewords()

    # play()
    # add_to_queue(upgrade_building, 'Cranny')
    # add_to_queue(upgrade_building, 'Cranny')
    # get_next_function()
    #
    #
    # get_next_function()
    # stats()
    # time.sleep(10)
    # driver.quit()  # .quit()
