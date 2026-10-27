// ---- GLOBALS ----
input.buttonA1.onEvent(ButtonEvent.Click, function () {
    zumo.clear()
    zumo.writeStringNewLine("AUTO CAL")
    zumo.writeStringNewLine("SPIN 10s")
    zumo.Initialization(Lightype.DIGITAL)
    zumo.autoCalibrateBorder()
    LEFT_BORDER_THRESHOLD = zumo.leftBorderThreshold()
    RIGHT_BORDER_THRESHOLD = zumo.rightBorderThreshold()
    calibrated = true
    zumo.clear()
    zumo.writeStringNewLine("READY!")
    zumo.writeStringNewLine("L:" + ("" + LEFT_BORDER_THRESHOLD))
    zumo.writeStringNewLine("R:" + ("" + RIGHT_BORDER_THRESHOLD))
    music.baDing.play()
})
input.buttonD12.onEvent(ButtonEvent.Click, function () {
    if (!(calibrated)) {
        zumo.clear()
        zumo.writeStringNewLine("PRESS A1")
        zumo.writeStringNewLine("TO CALIBRATE")
        pause(1000)
    } else {
        music.playMelody("B A G A G F A C5 ", 250)
        while (true) {
            check_border()
            if (border_detected) {
                do_border_escape()
            } else {
                check_near_border()
                if (is_near_border) {
                    zumo.stopMotor(ZumoMotor.All)
                    check_border()
                    if (border_detected) {
                        do_border_escape()
                    }
                } else {
                    dist = get_distance()
                    check_border()
                    if (border_detected) {
                        do_border_escape()
                    } else {
                        check_near_border()
                        if (is_near_border) {
                            zumo.stopMotor(ZumoMotor.All)
                            check_border()
                            if (border_detected) {
                                do_border_escape()
                            }
                        } else {
                            in_range = 0 <= dist && dist <= TARGET_MAX
                            if (in_range) {
                                target_locked = true
                                lost_count = 0
                                zumo.clear()
                                zumo.writeStringNewLine("TARGET!")
                                zumo.writeStringNewLine("D: " + ("" + dist))
                                attack_burst()
                            } else if (target_locked) {
                                lost_count += 1
                                if (lost_count <= LOST_TARGET_LIMIT) {
                                    zumo.clear()
                                    zumo.writeStringNewLine("TARGET! (HOLD)")
                                    zumo.writeStringNewLine("MISS: " + ("" + lost_count))
                                    attack_burst()
                                } else {
                                    target_locked = false
                                    lost_count = 0
                                    zumo.clear()
                                    zumo.writeStringNewLine("SEARCHING")
                                    zumo.writeStringNewLine("D:" + ("" + dist))
                                    search_burst()
                                }
                            } else {
                                zumo.clear()
                                zumo.writeStringNewLine("SEARCHING")
                                zumo.writeStringNewLine("D:" + ("" + dist))
                                search_burst()
                            }
                        }
                    }
                }
            }
        }
    }
})
function check_near_border () {
    sensors2 = zumo.readLine()
    left_margin = Math.trunc(LEFT_BORDER_THRESHOLD / 2)
    right_margin = Math.trunc(RIGHT_BORDER_THRESHOLD / 2)
    left_near = sensors2[LEFT_INDEX] > LEFT_BORDER_THRESHOLD - left_margin
    right_near = sensors2[RIGHT_INDEX] > RIGHT_BORDER_THRESHOLD - right_margin
    is_near_border = left_near || right_near
}
function attack_burst () {
    i = 0
    while (i < 40) {
        check_border()
        if (border_detected) {
            do_border_escape()
            i = 40
        } else {
            check_near_border()
            if (is_near_border) {
                zumo.runMotor(ZumoMotor.left, ATTACK_SLOWDOWN_SPEED)
                zumo.runMotor(ZumoMotor.right, ATTACK_SLOWDOWN_SPEED)
            } else {
                zumo.runMotor(ZumoMotor.left, ATTACK_SPEED)
                zumo.runMotor(ZumoMotor.right, ATTACK_SPEED)
            }
            pause(2)
            i += 1
        }
    }
}
function get_distance () {
    d1 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    d2 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    d3 = zumo.HCSR04(pins.D1, pins.D0)
    pause(1)
    if (d1 <= 0 && d2 <= 0 && d3 <= 0) {
        return 999
    }
    if (d1 <= 0) {
        d1 = 9999
    }
    if (d2 <= 0) {
        d2 = 9999
    }
    if (d3 <= 0) {
        d3 = 9999
    }
    high = Math.max(d1, Math.max(d2, d3))
    low = Math.min(d1, Math.min(d2, d3))
    median = d1 + d2 + d3 - high - low
    if (median == 9999) {
        return 999
    }
    return median
}
function check_border () {
    sensors = zumo.readLine()
    left_hit = sensors[LEFT_INDEX] > LEFT_BORDER_THRESHOLD
    right_hit = sensors[RIGHT_INDEX] > RIGHT_BORDER_THRESHOLD
    border_detected = left_hit || right_hit
}
function search_burst () {
    j = 0
    while (j < 40) {
        check_border()
        if (border_detected) {
            do_border_escape()
            j = 40
        } else {
            check_near_border()
            if (is_near_border) {
                zumo.runMotor(ZumoMotor.left, SEARCH_SLOWDOWN_SPEED)
                zumo.runMotor(ZumoMotor.right, SEARCH_SLOWDOWN_SPEED)
            } else {
                zumo.runMotor(ZumoMotor.left, SEARCH_SPEED)
                zumo.runMotor(ZumoMotor.right, SEARCH_SPEED)
            }
            pause(2)
            j += 1
        }
    }
}
function do_border_escape () {
    escape_left = left_hit
    escape_right = right_hit
    target_locked = false
    lost_count = 0
    attempts = 0
    zumo.stopMotor(ZumoMotor.All)
    pause(80)
    zumo.clear()
    zumo.writeStringNewLine("BORDER!")
    zumo.runMotor(ZumoMotor.left, 0 - REVERSE_SPEED)
    zumo.runMotor(ZumoMotor.right, 0 - REVERSE_SPEED)
    pause(BORDER_REVERSE_MS)
    zumo.stopMotor(ZumoMotor.All)
    pause(20)
    if (escape_left && !(escape_right)) {
        zumo.turnRight(TURN_SPEED)
    } else if (escape_right && !(escape_left)) {
        zumo.turnLeft(TURN_SPEED)
    } else {
        zumo.turnRight(TURN_SPEED)
    }
    pause(BORDER_TURN_MS)
    check_border()
    while (border_detected && attempts < 6) {
        if (escape_left && !(escape_right)) {
            zumo.turnRight(TURN_SPEED)
        } else if (escape_right && !(escape_left)) {
            zumo.turnLeft(TURN_SPEED)
        } else {
            zumo.turnRight(TURN_SPEED)
        }
        pause(160)
        check_border()
        attempts += 1
    }
    zumo.runMotor(ZumoMotor.left, SEARCH_SPEED)
    zumo.runMotor(ZumoMotor.right, SEARCH_SPEED)
}
let attempts = 0
let escape_right = false
let escape_left = false
let j = 0
let right_hit = false
let left_hit = false
let sensors: number[] = []
let median = 0
let low = 0
let high = 0
let d3 = 0
let d2 = 0
let d1 = 0
let i = 0
let right_near = false
let LEFT_INDEX = 0
let left_near = false
let right_margin = 0
let left_margin = 0
let sensors2: number[] = []
let lost_count = 0
let target_locked = false
let in_range = false
let dist = 0
let is_near_border = false
let border_detected = false
let calibrated = false
let RIGHT_BORDER_THRESHOLD = 0
let LEFT_BORDER_THRESHOLD = 0
let BORDER_TURN_MS = 0
let BORDER_REVERSE_MS = 0
let LOST_TARGET_LIMIT = 0
let RIGHT_INDEX = 0
let TARGET_MAX = 0
let TURN_SPEED = 0
let REVERSE_SPEED = 0
let SEARCH_SLOWDOWN_SPEED = 0
let SEARCH_SPEED = 0
let ATTACK_SLOWDOWN_SPEED = 0
let ATTACK_SPEED = 0
// ---- CONSTANTS ----
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
// ---- SETUP ----
zumo.createI2C(pins.SCL, pins.SDA)
zumo.init(128, 64)
zumo.enableIMU()
zumo.clear()
zumo.writeStringNewLine("PRESS A1")
zumo.writeStringNewLine("TO CALIBRATE")
