import os

os.system('sudo cp twitch_onair_webserver_service.service /lib/systemd/system/twitch_onair_webserver_service.service')
os.system('sudo cp twitch_onair_neopixel_service.service /lib/systemd/system/twitch_onair_neopixel_service.service')
os.system('sudo cp powerButton.service /lib/systemd/system/powerButton.service')
os.system('sudo systemctl daemon-reload')
os.system('sudo systemctl enable twitch_onair_webserver_service')
os.system('sudo systemctl enable twitch_onair_neopixel_service')
os.system('sudo systemctl enable powerButton')