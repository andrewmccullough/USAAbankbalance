import json
import os
import platform

try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait as Wait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as conditions
    from selenium.common.exceptions import TimeoutException
except ImportError:
    print("You don't have selenium installed.")
    exit()

if platform.system() == "Darwin":
    try:
        import pync
    except ImportError:
        pync = None
        print("You don't have pync installed.")
        print("The script will continue to function, but will be missing features.")
else:
    pync = None


# How long Selenium will wait to find an element.
MAX_WAIT = 5

# CSS selector of the element containing your account balance.
# If you are modifying this selector, remember that this script visits the mobile version of USAA.com.
BALANCE_ELEMENT_SELECTOR = "#id3 > ul > li:nth-child(1) > a > span > span.acct-bal"


def click(selector):
    Wait(driver, MAX_WAIT).until(
        conditions.element_to_be_clickable((By.CSS_SELECTOR, selector))
    ).click()


def keys(selector, string):
    Wait(driver, MAX_WAIT).until(
        conditions.visibility_of_element_located((By.CSS_SELECTOR, selector))
    ).send_keys(string)


def out(string: str, ALL: bool=False):
    if ALL:
        if pync:
            pync.notify(string, title="Bank balance")
        print(string)
    else:
        if VERBOSITY == 200:
            print(string)
        elif VERBOSITY == 300:
            if pync:
                pync.notify(string, title="Bank balance")
            else:
                print(string)
        elif VERBOSITY == 400:
            out(string, True)


def acknowledge():
    input("Press return to continue. ")
    print()


def missing(details: list, possible_user_error: bool=True):
    out("The script encountered a problem.", True)
    print("An element was missing when the script tried to " + details[0] + ".")
    print("USAA may have changed their website. If you believe this is the case, start an issue on GitHub.")
    if possible_user_error:
        print(details[1])
        print("Please confirm that it is correct in the config.json file, or by deleting the config.json file and running the script again.")
    print("The script cannot continue. Goodbye!")
    driver.quit()
    if UPDATE_CONFIG:
        f = open("config.json", "w")
        f.write(json.dumps(config))
        f.close()
    exit()


def welcome():
    global USAA_USERNAME, USAA_PASSWORD, USAA_PIN, config, UPDATE_CONFIG, VERBOSITY

    print("It appears this is your first time using this script.")
    print("You can read the code in this file to ensure that I am not collecting your credentials.")
    print("I cannot vouch for the security or privacy policies of project dependencies, however.")
    print("Use this script at your own risk.")
    acknowledge()

    USAA_USERNAME = input("Please enter your USAA username. ")
    USAA_PASSWORD = input("Please enter your USAA password. ")
    USAA_PIN = input("Please enter your USAA PIN. ")
    print("These will be stored in the config.json file.")
    acknowledge()

    print("As the script encounters security questions, it will ask you for your help.")
    print("It will remember your responses in the config.json file.")
    acknowledge()

    print("You can control how much information this script shares with you by adjusting its verbosity.")
    print("100: no output to report progress (will still notify of errors and balance).") if pync else print("100: no output to report progress (will only show errors and balance in the console).")
    print("200: prints output to console to report progress (will still notify of errors and balance).") if pync else print("200: prints output to console to report progress (in addition to errors and balance).")
    if pync:
        print("300: sends notifications to report progress, errors, and balance.")
        print("400: prints to console and sends notifications to report progress, errors, and balance.")

    print("Enter 100, 200, 300, or 400 to set the script verbosity. (This can be changed in the config.json file.)") if pync else print("Enter 100 or 200 to set the script verbosity. (This can be changed in the config.json file.)")

    desired = input().strip()
    if desired in ["100", "200", "300", "400"]:
        VERBOSITY = int(desired)
    else:
        print("That wasn't a valid response. Instead, the script will use the default (200).")
        VERBOSITY = 200

    print("Setup is complete!")
    acknowledge()

    config = {
        "securityQuestions": {

        },
        "credentials": {
            "username": USAA_USERNAME,
            "password": USAA_PASSWORD,
            "PIN": USAA_PIN
        },
        "verbosity": VERBOSITY
    }

    UPDATE_CONFIG = True


try:
    if __name__ == '__main__':

        if os.path.isfile("config.json"):
            f = open("config.json", "r")
            try:
                config = json.load(f)

                UPDATE_CONFIG = False
                USAA_USERNAME = config["credentials"]["username"]
                USAA_PASSWORD = config["credentials"]["password"]
                USAA_PIN = config["credentials"]["PIN"]
                VERBOSITY = config["verbosity"]
            except json.JSONDecodeError:
                f.close()
                os.remove("config.json")
                welcome()
            except KeyError:
                f.close()
                os.remove("config.json")
                welcome()
        else:
            welcome()

        if VERBOSITY == 300 and not pync:
            print("Your verbosity is set to 300 but you do not have pync installed. The script cannot send notifications to you, so progress, errors, and balance will be printed to the console.")

        try:
            out("Opening Selenium.")
            driver = webdriver.Chrome()

            try:
                out("Navigating to USAA login.")
                driver.get("https://mobile.usaa.com")

                try:
                    click("#logOnButton > a")
                except TimeoutException:
                    missing(["navigate to the login form"], False)

                # initial login from homepage
                out("Entering credentials.")
                try:
                    keys("#input_onlineid", USAA_USERNAME)
                    keys("#input_password", USAA_PASSWORD)
                    click("input[type='submit']")
                except TimeoutException:
                    missing(["enter and submit your username or password"], False)

                # PIN entry
                out("Entering PIN.")
                try:
                    keys("#pinTextField", USAA_PIN)
                    click("button[type='submit']")
                except TimeoutException:
                    missing([
                        "enter and submit your PIN",
                        "It's possible that the username or password the script tried to enter was incorrect."
                    ])

                # security question challenge
                try:
                    challenge = driver.find_element(By.CSS_SELECTOR, "label[for='securityQuestionTextField']").text
                except TimeoutException:
                    missing([
                        "retrieve the security question",
                        "It's possible that the PIN the script tried to enter was incorrect."
                    ])

                if challenge in config["securityQuestions"].keys():
                    response = config["securityQuestions"][challenge]
                else:
                    out("The script encountered a new security question and needs help.", True)
                    print("Please answer the following security question.")
                    response = input(challenge + " ")
                    config["securityQuestions"][challenge] = response
                    UPDATE_CONFIG = True

                out("Responding to security question. (" + challenge + ")")
                try:
                    keys("#securityQuestionTextField", response)
                    click("button[type='submit']")
                except TimeoutException:
                    missing(["respond to the security question"], False)

                try:
                    click("#ma")
                except TimeoutException:
                    missing([
                        "view your accounts",
                        "It's possible the response to the security question the script tried to enter was incorrect."
                    ])
                out("Successfully logged in.")

                try:
                    balance = Wait(driver, MAX_WAIT).until(
                        conditions.visibility_of_element_located((
                            By.CSS_SELECTOR,
                            BALANCE_ELEMENT_SELECTOR
                        ))
                    ).text.strip()
                    out("Your balance is currently " + balance + ".", True)
                except TimeoutException:
                    missing(["view your account balance"], False)

            finally:
                driver.quit()

        finally:
            if UPDATE_CONFIG:
                f = open("config.json", "w")
                f.write(json.dumps(config))
                f.close()
except KeyboardInterrupt:
    print("Goodbye!")
    pass
