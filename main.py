from machine import Pin, SPI # type: ignore
from ili9341 import Display, color565
from utime import ticks_us, ticks_diff, sleep_us # type: ignore

spi = SPI(0,
          baudrate=80_000_000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(18),
          mosi=Pin(19),
          miso=Pin(16))

btn = Pin(2, Pin.IN, Pin.PULL_UP)
last_btn_state = btn.value() == 0

display = Display(
    spi,
    dc=Pin(15),
    cs=Pin(17),
    rst=Pin(14),
    width=320,
    height=240,
    bgr=False
)

RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
BLACK = color565(0, 0, 0)

FRAME_US = 33_333  # ~30 FPS


display.clear(GREEN if last_btn_state else RED)

while True:
    try:
        t0 = ticks_us()


        pressed = btn.value() == 0
        
        if pressed != last_state:
            print("Pressed" if pressed else "Not pressed")
            display.clear(GREEN if pressed else RED)
            last_state = pressed


        # frame limiter
        dt = ticks_diff(ticks_us(), t0)
        delay = FRAME_US - dt
        if delay > 0:
            sleep_us(delay)

    except KeyboardInterrupt:
        print("Goodbye!")
        display.clear()
        display.spi.deinit()
        break