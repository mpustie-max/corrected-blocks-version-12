# ---- GLOBALS ----

def on_button_a1_click():
    global LEFT_BORDER_THRESHOLD, RIGHT_BORDER_THRESHOLD, calibrated
    zumo.clear()
    zumo.write_string_new_line("AUTO CAL")
    zumo.write_string_new_line("SPIN 10s")
    zumo.initialization(Lightype.DIGITAL)
    zumo.auto_calibrate_border()
    LEFT_BORDER_THRESHOLD = zumo.left_border_threshold()
    RIGHT_BORDER_THRESHOLD = zumo.right_border_threshold()
    calibrated = True
    zumo.clear()
    zumo.write_string_new_line("READY!")
    zumo.write_string_new_line("L:" + ("" + str(LEFT_BORDER_THRESHOLD)))
    zumo.write_string_new_line("R:" + ("" + str(RIGHT_BORDER_THRESHOLD)))
    music.ba_ding.play()
input.button_a1.on_event(ButtonEvent.CLICK, on_button_a1_click)

def on_button_d12_click():
    global dist, in_range, target_locked, lost_count
    if not (calibrated):
        zumo.clear()
        zumo.write_string_new_line("PRESS A1")
        zumo.write_string_new_line("TO CALIBRATE")
        pause(1000)
    else:
        music.play_melody("B A G A G F A C5 ", 250)
        while True:
            check_border()
            if border_detected:
                do_border_escape()
            else:
                check_near_border()
                if is_near_border:
                    zumo.stop_motor(ZumoMotor.ALL)
                    check_border()
                    if border_detected:
                        do_border_escape()
                else:
                    dist = get_distance()
                    check_border()
                    if border_detected:
                        do_border_escape()
                    else:
                        check_near_border()
                        if is_near_border:
                            zumo.stop_motor(ZumoMotor.ALL)
                            check_border()
                            if border_detected:
                                do_border_escape()
                        else:
                            in_range = 0 <= dist and dist <= TARGET_MAX
                            if in_range:
                                target_locked = True
                                lost_count = 0
                                zumo.clear()
                                zumo.write_string_new_line("TARGET!")
                                zumo.write_string_new_line("D: " + ("" + str(dist)))
                                attack_burst()
                            elif target_locked:
                                lost_count += 1
                                if lost_count <= LOST_TARGET_LIMIT:
                                    zumo.clear()
                                    zumo.write_string_new_line("TARGET! (HOLD)")
                                    zumo.write_string_new_line("MISS: " + ("" + str(lost_count)))
                                    attack_burst()
                                else:
                                    target_locked = False
                                    lost_count = 0
                                    zumo.clear()
                                    zumo.write_string_new_line("SEARCHING")
                                    zumo.write_string_new_line("D:" + ("" + str(dist)))
                                    search_burst()
                            else:
                                zumo.clear()
                                zumo.write_string_new_line("SEARCHING")
                                zumo.write_string_new_line("D:" + ("" + str(dist)))
                                search_burst()
input.button_d12.on_event(ButtonEvent.CLICK, on_button_d12_click)

def check_near_border():
    global sensors2, left_margin, right_margin, left_near, right_near, is_near_border
    sensors2 = zumo.read_line()
    left_margin = int(LEFT_BORDER_THRESHOLD / 2)
    right_margin = int(RIGHT_BORDER_THRESHOLD / 2)
    left_near = sensors2[LEFT_INDEX] > LEFT_BORDER_THRESHOLD - left_margin
    right_near = sensors2[RIGHT_INDEX] > RIGHT_BORDER_THRESHOLD - right_margin
    is_near_border = left_near or right_near
def attack_burst():
    global i
    i = 0
    while i < 40:
        check_border()
        if border_detected:
            do_border_escape()
            i = 40
        else:
            check_near_border()
            if is_near_border:
                zumo.run_motor(ZumoMotor.LEFT, ATTACK_SLOWDOWN_SPEED)
                zumo.run_motor(ZumoMotor.RIGHT, ATTACK_SLOWDOWN_SPEED)
            else:
                zumo.run_motor(ZumoMotor.LEFT, ATTACK_SPEED)
                zumo.run_motor(ZumoMotor.RIGHT, ATTACK_SPEED)
            pause(2)
            i += 1
def get_distance():
    global d1, d2, d3, high, low, median
    d1 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    d2 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    d3 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    if d1 <= 0 and d2 <= 0 and d3 <= 0:
        return 999
    if d1 <= 0:
        d1 = 9999
    if d2 <= 0:
        d2 = 9999
    if d3 <= 0:
        d3 = 9999
    high = max(d1, max(d2, d3))
    low = min(d1, min(d2, d3))
    median = d1 + d2 + d3 - high - low
    if median == 9999:
        return 999
    return median
def check_border():
    global sensors, left_hit, right_hit, border_detected
    sensors = zumo.read_line()
    left_hit = sensors[LEFT_INDEX] > LEFT_BORDER_THRESHOLD
    right_hit = sensors[RIGHT_INDEX] > RIGHT_BORDER_THRESHOLD
    border_detected = left_hit or right_hit
def search_burst():
    global j
    j = 0
    while j < 40:
        check_border()
        if border_detected:
            do_border_escape()
            j = 40
        else:
            check_near_border()
            if is_near_border:
                zumo.run_motor(ZumoMotor.LEFT, SEARCH_SLOWDOWN_SPEED)
                zumo.run_motor(ZumoMotor.RIGHT, SEARCH_SLOWDOWN_SPEED)
            else:
                zumo.run_motor(ZumoMotor.LEFT, SEARCH_SPEED)
                zumo.run_motor(ZumoMotor.RIGHT, SEARCH_SPEED)
            pause(2)
            j += 1
def do_border_escape():
    global escape_left, escape_right, target_locked, lost_count, attempts
    escape_left = left_hit
    escape_right = right_hit
    target_locked = False
    lost_count = 0
    attempts = 0
    zumo.stop_motor(ZumoMotor.ALL)
    pause(80)
    zumo.clear()
    zumo.write_string_new_line("BORDER!")
    zumo.run_motor(ZumoMotor.LEFT, 0 - REVERSE_SPEED)
    zumo.run_motor(ZumoMotor.RIGHT, 0 - REVERSE_SPEED)
    pause(BORDER_REVERSE_MS)
    zumo.stop_motor(ZumoMotor.ALL)
    pause(20)
    if escape_left and not (escape_right):
        zumo.turn_right(TURN_SPEED)
    elif escape_right and not (escape_left):
        zumo.turn_left(TURN_SPEED)
    else:
        zumo.turn_right(TURN_SPEED)
    pause(BORDER_TURN_MS)
    check_border()
    while border_detected and attempts < 6:
        if escape_left and not (escape_right):
            zumo.turn_right(TURN_SPEED)
        elif escape_right and not (escape_left):
            zumo.turn_left(TURN_SPEED)
        else:
            zumo.turn_right(TURN_SPEED)
        pause(160)
        check_border()
        attempts += 1
    zumo.run_motor(ZumoMotor.LEFT, SEARCH_SPEED)
    zumo.run_motor(ZumoMotor.RIGHT, SEARCH_SPEED)
attempts = 0
escape_right = False
escape_left = False
j = 0
right_hit = False
left_hit = False
sensors: List[number] = []
median = 0
low = 0
high = 0
d3 = 0
d2 = 0
d1 = 0
i = 0
right_near = False
LEFT_INDEX = 0
left_near = False
right_margin = 0
left_margin = 0
sensors2: List[number] = []
lost_count = 0
target_locked = False
in_range = False
dist = 0
is_near_border = False
border_detected = False
calibrated = False
RIGHT_BORDER_THRESHOLD = 0
LEFT_BORDER_THRESHOLD = 0
BORDER_TURN_MS = 0
BORDER_REVERSE_MS = 0
LOST_TARGET_LIMIT = 0
RIGHT_INDEX = 0
TARGET_MAX = 0
TURN_SPEED = 0
REVERSE_SPEED = 0
SEARCH_SLOWDOWN_SPEED = 0
SEARCH_SPEED = 0
ATTACK_SLOWDOWN_SPEED = 0
ATTACK_SPEED = 0
# ---- CONSTANTS ----
ATTACK_SPEED = 70
ATTACK_SLOWDOWN_SPEED = 20
SEARCH_SPEED = 50
SEARCH_SLOWDOWN_SPEED = 15
REVERSE_SPEED = 55
TURN_SPEED = 60
TARGET_MAX = 40
RIGHT_INDEX = 4
LOST_TARGET_LIMIT = 15
BORDER_REVERSE_MS = 350
BORDER_TURN_MS = 420
# ---- SETUP ----
zumo.create_i2c(pins.SCL, pins.SDA)
zumo.init(128, 64)
zumo.enable_imu()
zumo.clear()
zumo.write_string_new_line("PRESS A1")
zumo.write_string_new_line("TO CALIBRATE")