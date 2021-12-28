import os

os.system('sudo cp twitch_onair_webserver_service.service /lib/systemd/system/twitch_onair_webserver_service.service')
os.system('sudo cp twitch_onair_neopixel_service.service /lib/systemd/system/twitch_onair_neopixel_service.service')
os.system('sudo cp powerButton.service /lib/systemd/system/powerButton.service')
os.system('sudo cp functionButton.service /lib/systemd/system/functionButton.service')
os.system('sudo cp oled_service.service /lib/systemd/system/oled_service.service')
os.system('sudo systemctl daemon-reload')
os.system('sudo systemctl enable twitch_onair_webserver_service')
os.system('sudo systemctl enable twitch_onair_neopixel_service')
os.system('sudo systemctl enable powerButton')
os.system('sudo systemctl enable functionButton')
os.system('sudo systemctl enable oled_service')