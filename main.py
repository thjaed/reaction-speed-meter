from machine import Pin, SPI # type: ignore
from ili9341 import Display, color565
from utime import ticks_us, ticks_ms, ticks_diff, sleep_us, sleep_ms # type: ignore
from random import randint

spi = SPI(0,
          baudrate=40_000_000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(18),
          mosi=Pin(19),
          miso=Pin(16))

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
WHITE = color565(255, 255, 255)

debounce_ms = 20
btn = Pin(2, Pin.IN, Pin.PULL_UP)
last_btn_state = btn.value()

def wait_for_press():
    # wait for press
    while btn.value():
        sleep_ms(1)

    sleep_ms(debounce_ms)

    # confirm still pressed
    if btn.value() == 0:
        print("Pressed")

        # wait for release (prevents double triggers)
        while btn.value() == 0:
            sleep_ms(1)

        return True

    return False

def start_measure():
    # Measure reaction time
    t0 = ticks_us()
    while btn.value() != 0:
        pass
    return ticks_diff(ticks_us(), t0)

def draw_text8x8_centre(text, colour, background, rotate=0, line=0):
    # Draw text in centre
    width_text = len(text) * 8
    height_text = 8

    x = (display.width // 2) - (width_text // 2)
    y = (display.height // 2) - (height_text // 2) + (line * 8)

    display.draw_text8x8(x, y, text, colour, background, rotate)

resp_high = ["High score, I guess.",
             "Some may call it impressive.",
             "Can you top that? Probably not.",
             "Wow... not bad."
             ]

resp_low = ["My dog could do better.",
            "Is it possible to take longer?",
            "You call THAT an attempt?",
            "That's embarassing"
            ]

resp_avg = ["Not great, not terrible.",
            "Mediocre at best.",
            "Come on, you can try harder than that.",
            "It's OK."
            ]

def analysis(speeds):
    latest = speeds[-1]
    if len(speeds) == 1:
        return resp_avg[randint(0, len(resp_avg) - 1)]
    if min(speeds) == latest:
        return resp_high[randint(0, len(resp_high) - 1)]
    elif max(speeds) == latest:
        return resp_low[randint(0, len(resp_low) - 1)]
    else:
        return resp_avg[randint(0, len(resp_avg) - 1)]


speeds = []

display.clear(RED)
draw_text8x8_centre("PRESS BUTTON TO PLAY", WHITE, RED)
wait_for_press()

while True:
    try:
        # Start screen
        display.clear(RED)
        draw_text8x8_centre("WAIT FOR BLUE", WHITE, RED)
        delay = randint(3000, 7000)
        
        cheated = False
        timer = ticks_ms()
        while ticks_diff(ticks_ms(), timer) < delay:
            if btn.value() == 0:
                sleep_ms(20)
                if btn.value() == 0:
                    cheated = True
                    break

        if cheated:
            # Too early
            display.clear(RED)
            draw_text8x8_centre("TOO EARLY!", WHITE, RED)
            draw_text8x8_centre("PRESS BUTTON TO PLAY AGAIN", WHITE, RED, line=2)
            while btn.value() == 0:
                sleep_ms(1)
            wait_for_press()

        else: 
            # Click screen
            t0 = ticks_us()
            display.clear(BLUE)
            draw_text8x8_centre("PRESS BUTTON!", WHITE, BLUE)
            device_ms = (ticks_diff(ticks_us(), t0) // 1000)

            # measure speed
            time_ms = ((start_measure()) // 1000) + (device_ms)

            # End screen
            display.clear(RED)
            speeds.append(time_ms)
            draw_text8x8_centre(f"YOU TOOK {time_ms}ms", WHITE, RED)
            draw_text8x8_centre(analysis(speeds), WHITE, RED, line=2)
            draw_text8x8_centre("PRESS BUTTON TO PLAY AGAIN", WHITE, RED, line=4)
            
            while btn.value() == 0:
                sleep_ms(1)
            wait_for_press()
            


    except KeyboardInterrupt:
        print("Goodbye!")
        display.clear()
        display.spi.deinit()
        break