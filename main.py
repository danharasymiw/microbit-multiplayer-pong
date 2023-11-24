# Multiplayer Pong Player 1
paddle_x = 0
paddle_y = 0
ball_x = 0
ball_y = 0
ball_x_dir = 1
ball_y_dir = 1
my_score = 0
their_score = 0
is_playing = False
is_displaying_score = False
is_controller_enabled = False

is_connected = False

MAX_POINTS = 3


host = False

def draw_paddle(paddle_x, paddle_y):
    led.plot(paddle_x - 1, paddle_y)
    led.plot(paddle_x, paddle_y)
    led.plot(paddle_x + 1, paddle_y)

def move_paddle(direction):
    global paddle_x, paddle_y, is_controller_enabled
    if not is_controller_enabled:
        return
    led.unplot(paddle_x + (direction * -1), paddle_y)
    paddle_x = paddle_x + direction
    
    paddle_x = max(0, min(paddle_x, 4))
    draw_paddle(paddle_x, paddle_y)

def reset_paddle():
    global paddle_x, paddle_y
    paddle_x = 2
    paddle_y = 4

def on_button_pressed_a():
    global is_connected, host
    if not is_connected:
        host = True
    move_paddle(-1)
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_b():    
    move_paddle(1)
input.on_button_pressed(Button.B, on_button_pressed_b)

def move_ball():
    global ball_x, ball_y, ball_x_dir, ball_y_dir, paddle_x, paddle_y
    led.unplot(ball_x, ball_y)
    
    # move ball
    ball_x = ball_x + ball_x_dir
    if ball_x == 0 or ball_x == 4:
        ball_x_dir = ball_x_dir * -1
    
    ball_y = ball_y + ball_y_dir
    
    led.plot(ball_x, ball_y)

    # check for paddle collision
    if ball_y + ball_y_dir == paddle_y and \
        paddle_x - 1 <= ball_x <= paddle_x + 1:
        ball_y_dir = ball_y_dir * -1
    

def reset_ball():
    global ball_x, ball_y, ball_y_dir
    ball_x = 2
    ball_y = 3
    ball_y_dir = -1

def display_score():
    global my_score, is_controller_enabled, is_displaying_score
    is_displaying_score = True
    is_controller_enabled = False
    for i in range(1, 3):
        basic.clear_screen()
        basic.pause(250)
        basic.show_number(my_score)
        basic.pause(250)
    
    basic.clear_screen()
    is_controller_enabled = True
    is_displaying_score = False

def display_lose():
    global is_controller_enabled
    is_controller_enabled = False
    basic.clear_screen()
    basic.show_leds("""
            . . . . .
            . # . # .
            . . . . .
            . # # # .
            # . . . #
        """)
    basic.pause(3000)

def display_win():
    global is_controller_enabled
    is_controller_enabled = False
    basic.clear_screen()
    basic.show_leds("""
        . . . . .
        . # . # .
        . . . . .
        # . . . #
        . # # # .
    """)
    basic.pause(3000)


def on_received_value(name, value):
    global ball_x, ball_y, ball_x_dir, ball_y_dir
    if name == "BALL":
        # flip it because screens are facing eachother
        ball_x_dir = value * -1

        # Randomly place ball otherwise it's repetitive
        ball_x = randint(0, 4)
        if ball_x == 0:
            ball_x_dir = 1
        elif ball_x == 4:
            ball_x_dir = -1
        ball_y = -1
        ball_y_dir = 1
        
    pass
radio.on_received_value(on_received_value)



def connect():
    radio.send_string("PING")
    basic.pause(10)

def on_radio_received_string(received_str):
    global is_connected, host, my_score, is_playing
    if host and received_str == "PONG":
        is_connected = True
    elif not host and received_str == "PING":
        radio.send_string("PONG")
        is_connected = True
    elif received_str == "SCORE":
        my_score = my_score + 1
        display_score()
        reset_paddle()
    elif received_str == "GAME_OVER":
        is_playing = False
    
radio.on_received_string(on_radio_received_string)

basic.show_string("PONG!")
basic.show_leds("""
        . . # . .
        . # . . .
        # # # # #
        . # . . .
        . . # . .
    """)
def on_forever():
    global paddle_x, paddle_y, ball_x, ball_y, ball_x_dir, ball_y_dir, my_score, their_score, is_connected, host, is_playing, is_controller_enabled, MAX_POINTS, is_displaying_score
    
    is_playing = False
    while not is_connected:
        if host:
            connect()
        basic.pause(200)

    basic.clear_screen()
    for countdown in range(3, 0, -1):
        basic.show_number(countdown)
        basic.pause(1000)
    basic.clear_screen()
    
    reset_paddle()
    ball_x = 0
    ball_y = 0
    ball_x_dir = 1
    ball_y_dir = 1
    my_score = 0
    their_score = 0

    is_playing = True
    is_controller_enabled = True
    
    # Host starts, hide ball from client
    if not host:
        ball_y = -1
        ball_y_dir = -1

    # game loop
    while is_playing:
        basic.pause(250)

        if host and (my_score >= MAX_POINTS or their_score >= MAX_POINTS):
            is_playing = False
            radio.send_string("GAME_OVER")
            break

        draw_paddle(paddle_x, paddle_y)
        move_ball()

        if ball_y == 4:
            basic.pause(250) # slight pause to show ball hitting ground
            their_score = their_score + 1
            radio.send_string("SCORE")
            display_score()
            reset_paddle()
            reset_ball()
        if ball_y == -1:
            radio.send_value("BALL", ball_x_dir)


    # game over
    # Wait for the score to stop being displayed
    while is_displaying_score:
        basic.pause(50)
    if my_score >= MAX_POINTS:
        display_win()
    else:
        display_lose()

basic.forever(on_forever)
