from machine import Pin, SPI, PWM # type: ignore
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

buzzer = PWM(Pin(6))

RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)

def play_tone(freq, duration):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    sleep_ms(duration)
    buzzer.duty_u16(0)

def play_tune(tune):
    for tone in tune:
        freq, duration = tone
        play_tone(freq, duration)

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

resp_high = ["Crazy improvement!",
             "Some may call it impressive.",
             "Can you top that? Probably not.",
             "Wow... not bad.",
             "You must be cheating."
             ]

resp_low = ["My dog could do better.",
            "Is it possible to take longer?",
            "You call THAT an attempt?",
            "That's embarassing.",
            "That was so slow!"
            ]

resp_improve = ["Ok, getting better!",
                "You're improving!",
                "That was alright!",
                "Let's see if you can keep it up."
                ]

resp_worse = ["A slight decline.",
              "Going the wrong way.",
              "Try harder.",
              "You're getting worse."
              ]

tune_highscore = [
    (700, 100),
    (1200, 400)
]

tune_lowscore = [
    (300, 200),
    (250, 250),
    (220, 200),
    (200, 700)
]

tune_start = [
    (500, 200),
    (250, 200),
    (150, 200),
    (300, 200),
    (700, 200)
]

def analysis(speeds):
    latest = speeds[-1]
    if len(speeds) == 1:
        if latest < 215:
            return "A very strong start!"
        elif latest < 260:
            return "Average start."
        elif latest < 320:
            return "That was a bad start."
        else:
            return "Terrible start!"
        
    historical = speeds[:-1:]

    if len(historical) > 3:
        historical = historical[-3:]
    hist_avg = sum(historical) / len(historical)
    print(f"historical average: {hist_avg}  this score: {latest}")
    ratio = latest / hist_avg
    print(f"ratio: {ratio}")
    print("\n")
    
    if ratio < 0.5:
        return resp_high[randint(0, len(resp_high) - 1)]
    elif ratio < 1:
        return resp_improve[randint(0, len(resp_improve) - 1)]
    elif 0.98 <= ratio <= 1.02:
        return "Exactly average."
    elif ratio > 1.5:
        return resp_low[randint(0, len(resp_low) - 1)]
    elif ratio > 1:
        return resp_worse[randint(0, len(resp_worse) - 1)]

speeds = []

display.clear(RED)
play_tune(tune_start)
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

            if min(speeds) == time_ms and len(speeds) != 1:
                draw_text8x8_centre("NEW HIGH SCORE", WHITE, RED, line=-3)
                play_tune(tune_highscore)
            elif max(speeds) == time_ms and len(speeds) != 1:
                draw_text8x8_centre("WORST SCORE", WHITE, RED, line=-3)
                play_tune(tune_lowscore)

            draw_text8x8_centre("PRESS BUTTON TO PLAY AGAIN", WHITE, RED, line=6)
            
            while btn.value() == 0:
                sleep_ms(1)
            wait_for_press()
            


    except KeyboardInterrupt:
        print("Goodbye!")
        display.clear()
        display.spi.deinit()
        break