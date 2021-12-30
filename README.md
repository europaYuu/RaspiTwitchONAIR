# RaspiTwitchONAIR
A series of Raspberry Pi services for checking twitch stream status over the net and displaying the result via Neopixel / WS2812 LEDs. Has a web interface for configuration and supports a 128x32 I2C OLED for displaying Hostname / IP for the web interface and status updates.

Build guide / Manual coming soon.

# Wiring Diagram:
![wiring-diagram](https://user-images.githubusercontent.com/92567050/147701979-cc543aa8-460a-4540-a70d-cbe288f3aaaa.png)

# Materials:
I've included (mostly) amazon links so it's easier to identify parts, but you don't need to buy some of the huge packs linked and a lot of the materials can be found cheaper off amazon, especially the glues.

## Parts (Electronics):
- Raspberry Pi Zero W
- [Neopixel LED Strip](https://www.adafruit.com/product/1138?length=1)
- [LM2596 Buck Converter](https://www.amazon.ca/Yizhet-LM2596-Converter-Adjustable-Supply/dp/B08Q2YKJ6Q/ref=sr_1_6?crid=1C14WU76FDVU&keywords=lm2596&qid=1640811759&sprefix=lm259%2Caps%2C203&sr=8-6)
- 500-100µF Capacitor
- [128x32 I2C OLED](https://www.amazon.ca/gp/product/B07D9H83R4/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)
- [5v-24v Wall Adapter Power Supply](https://www.amazon.ca/gp/product/B086JRWFD9/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
- [(Optional) 3mm 3v LED (Disk Activity Light)](https://www.amazon.ca/gp/product/B09JMZD19D/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
- 2x 330 Ohm Resistors (One if you don't need to use the Disk Activity Light)
- [2x Momentary switches for Reset / Function Button](https://www.amazon.ca/Twidec-Normal-Momentary-Pre-soldered-PBS-110-XR/dp/B07RV1D98T/ref=sr_1_6?crid=1UFS8E0OWLAL2&keywords=momentary+switch&qid=1640813085&sprefix=momentary+switch%2Caps%2C123&sr=8-6)

## Parts (Connectors):
- [5.5mm x 2.1mm DC Barrel Jack](https://www.amazon.ca/gp/product/B092Z6ZG3V/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1)
- [Dupont Connectors](https://www.amazon.ca/gp/product/B07DF9BJKH/ref=ppx_yo_dt_b_asin_title_o02_s01?ie=UTF8&psc=1)
- [Optional: JST Connectors for power](https://www.amazon.ca/gp/product/B013WTV270/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1)

## Parts (Hardware):
- [3mm Threaded Brass Inserts; 5.6mm height, 4.6mm outer diameter](https://www.amazon.ca/gp/product/B087N4LVD1/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1)
- [3mm Button Head Screws](https://www.amazon.ca/gp/product/B073VKDZJ2/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)
- [Optional: 3mm Socket Head Screws](https://www.amazon.ca/gp/product/B073VKGW3K/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1)
- [Optional: Square Adhesive Bumper Pads (for feet)](https://www.amazon.ca/gp/product/B07PDSXKD9/ref=ppx_yo_dt_b_asin_title_o00_s02?ie=UTF8&psc=1)

## Tools:
- 3D Printer for case
- Soldering iron for wires & brass threaded inserts
- [Crimping tool for Dupont Connectors](https://www.amazon.ca/gp/product/B078WPT5M1/ref=ppx_yo_dt_b_asin_title_o09_s00?ie=UTF8&psc=1)
- [Medium cyanoacrylate glue](https://www.amazon.ca/Starbond-EM-150-Medium-Premium-Cyanoacrylate/dp/B00C32MHJU/ref=sr_1_6?crid=FS0JS0DZP54T&keywords=medium%2BCA%2Bglue&qid=1640812658&sprefix=medium%2Bca%2Bglue%2Caps%2C132&sr=8-6&th=1) & [accelerator](https://www.amazon.ca/Install-Bay-Accelerator-2-Ounce-INSTAC/dp/B001JT00MY/ref=pd_sbs_4/141-1155150-9580568?pd_rd_w=dWrha&pf_rd_p=01fdeee8-dd76-431b-910b-f00bfed49bd2&pf_rd_r=N14MB2S4SRG8HPN669ZP&pd_rd_r=77d850a2-56d8-4b2f-b0b5-c73f9fdc9796&pd_rd_wg=HjkWo&pd_rd_i=B001JT00MY&th=1) for parts that need gluing
- Hex driver (case screws)
- Side Cutters (Wires)
- Wire stripper (Wiring)
- heat shrink tubing (Wiring)
