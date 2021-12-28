import os

os.system('sudo systemctl disable twitch_onair_webserver_service')
os.system('sudo systemctl disable twitch_onair_neopixel_service')
os.system('sudo systemctl disable powerButton')
os.system('sudo systemctl disable functionButton')
os.system('sudo systemctl disable oled_service')
os.system('sudo rm /lib/systemd/system/twitch_onair_webserver_service.service')
os.system('sudo rm /lib/systemd/system/twitch_onair_neopixel_service.service')
os.system('sudo rm /lib/systemd/system/powerButton.service')
os.system('sudo rm /lib/systemd/system/functionButton.service')
os.system('sudo rm /lib/systemd/system/oled_service.service')
os.system('sudo systemctl daemon-reload')