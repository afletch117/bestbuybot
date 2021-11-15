from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
import datetime
import random
import time
import info

# define the path to the driver for your browser on your machine
PATH = "/Users/yourname/WebDrivers/chromedriver"

driver = webdriver.Chrome(PATH)

# Enter your Twilio Account info here
alertNumber = 'xxx'
fromNumber = 'xxx'
accountSid = 'xxx'
authToken = 'xxx'
client = Client(accountSid, authToken)

HDMITEST = "https://www.bestbuy.com/site/best-buy-essentials-3-4k-ultra-hd-hdmi-cable-black/6472357.p?skuId=6472357"
HDMITEST2 = "https://www.bestbuy.com/site/dynex-4-hdmi-cable-black/6165873.p?skuId=6165873"
PS5 = "https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149"
PS5DIG = "https://www.bestbuy.com/site/sony-playstation-5-digital-edition-console/6430161.p?skuId=6430161"
XBOX_X = "https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324"

links = [PS5, PS5DIG, XBOX_X]
test_links = [HDMITEST, HDMITEST2]

isComplete = False
testMode = False

n = 1
start_time = datetime.datetime.now()
print(f"Launching Bot...   ---   Date: {start_time.year}-{start_time.month}-{start_time.day}, Time: {start_time.hour}:{start_time.minute}:{start_time.second}...")

while not isComplete:

    try:
        # randomize LINK, then navigate to product page
        LINK = random.choice(links)
        now = datetime.datetime.now()
        print(f"n={n}... runtime={(now - start_time)}... Checking: {LINK}")
        driver.get(LINK)

        # find "Add to Cart" button
        atcBtn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
        print("Add to cart button found...")

        # Text Message To let you know your item is available.
        try:
            client.messages.create(to=alertNumber, from_=fromNumber,
                                   body=f'This is your Bot! Your Item is Available at Best Buy!  Try to buy it yourself now! '
                                        f'This Bot will attempt '
                                        f'to buy in 15 minutes... {LINK}')
            print("Item located - text message sent via Twilio...")

        except (NameError, TwilioRestException):
            pass

        ## the bot now waits 15 minutes to avoid being temporally banned from adding items to cart.
        ## this is because when a bot refreshes the best buy site as much as this bot does,
        ## once the item becomes available, the best buy site blocks bots from adding items
        ## to your cart for 15 miunutes, but only for bots, human users can still add items to the cart during this time.
        print("Waiting 15 Minutes...")
        time.sleep(900)
        
        ## bot will now attempt to purchase your item
        driver.refresh()
        atcBtn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
        print("Add to cart button found, again...")

        # add item to cart
        atcBtn.click()

        # Text Message To let you know the bot is attempting purchase.
        try:
            client.messages.create(to=alertNumber, from_=fromNumber,
                                   body=f'Bot attempting purchase... {LINK}')
            print("Purchasing - text message sent via Twilio...")

        except (NameError, TwilioRestException):
            pass


    except:
        ## if "add to cart" button cannot be found, the bot will continue searching for items in your list
        n = n + 1
        continue


    try:
        # navigate to cart page
        driver.get("https://www.bestbuy.com/cart")

        # find and click "Checkout" button
        checkoutBtn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div[2]/div[1]/div/div[2]/div[1]/section[2]/div/div/div[4]/div/div[1]/button")))
        checkoutBtn.click()
        print("Successfully added to cart - beginning check out...")

        # fill in BestBuy email & password
        emailField = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fld-e")))
        pwField = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fld-p1")))
        emailField.send_keys(info.email)
        pwField.send_keys(info.password)

        # click "Sign In" Button
        signInButton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/main/div[2]/div[1]/div/div/div/div/div/form/div[3]/button")))
        signInButton.click()
        print("Signing in...")

        try:
            # set fulfillment preference to shipping
            shippingBtn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Switch to Shipping")))
            shippingBtn.click()
            print("Shipping selected as preferred fulfillment method...")
        except:
            continue

        try:
            # fill in card cvv
            cvvField = driver.find_element(By.ID, "cvv")
            cvvField.send_keys(info.cvv)
            print("CVV entered...")
        except:
            continue

        time.sleep(5)

        if testMode:
            now = datetime.datetime.now()
            print("Test Complete!   ---   %s:%s:%s" % (now.hour, now.minute, now.second))

        else:
            # click "Place Your Order" button
            placeYourOrderButton = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/main/div[2]/div[2]/div/div[4]/div[3]/div/div[2]/button")))
            placeYourOrderButton.click()
            now = datetime.datetime.now()
            print("Order Complete!   ---   %s:%s:%s" % (now.hour, now.minute, now.second))

        isComplete = True

    except:
        # if bot fails above, give error message and stop bot
        now = datetime.datetime.now()
        print("Error - stopping bot %s:%s:%s" % (now.hour, now.minute, now.second))
        isComplete = True
        # Text Message To alert you to the pressence of an error, and that the bot has stopped.
        try:
            client.messages.create(to=alertNumber, from_=fromNumber,
                                   body=f'Bot stopped - Error encountered.')
            print("Error - text message sent via Twilio...")

        except (NameError, TwilioRestException):
            pass
        continue
