//  Multiplayer Pong
let paddle_x = 0
let paddle_y = 0
let ball_x = 0
let ball_y = 0
let ball_x_dir = 1
let ball_y_dir = 1
let my_score = 0
let their_score = 0
let is_playing = false
let is_displaying_score = false
let is_controller_enabled = false
let is_connected = false
let host = false
let MAX_POINTS = 3
function draw_paddle(paddle_x: number, paddle_y: number) {
    led.plot(paddle_x - 1, paddle_y)
    led.plot(paddle_x, paddle_y)
    led.plot(paddle_x + 1, paddle_y)
}

function move_paddle(direction: number) {
    
    if (!is_controller_enabled) {
        return
    }
    
    led.unplot(paddle_x + direction * -1, paddle_y)
    paddle_x = paddle_x + direction
    paddle_x = Math.max(0, Math.min(paddle_x, 4))
    draw_paddle(paddle_x, paddle_y)
}

function reset_paddle() {
    
    paddle_x = 2
    paddle_y = 4
}

input.onButtonPressed(Button.A, function on_button_pressed_a() {
    
    if (!is_connected) {
        host = true
    }
    
    move_paddle(-1)
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    move_paddle(1)
})
function move_ball() {
    
    led.unplot(ball_x, ball_y)
    //  move ball
    ball_x = ball_x + ball_x_dir
    if (ball_x == 0 || ball_x == 4) {
        ball_x_dir = ball_x_dir * -1
    }
    
    ball_y = ball_y + ball_y_dir
    led.plot(ball_x, ball_y)
    //  check for paddle collision
    if (ball_y + ball_y_dir == paddle_y && (paddle_x - 1 <= ball_x && ball_x <= paddle_x + 1)) {
        ball_y_dir = ball_y_dir * -1
    }
    
}

function reset_ball() {
    
    ball_x = 2
    ball_y = 3
    ball_y_dir = -1
}

function display_score() {
    
    is_displaying_score = true
    is_controller_enabled = false
    for (let i = 1; i < 3; i++) {
        basic.clearScreen()
        basic.pause(250)
        basic.showNumber(my_score)
        basic.pause(250)
    }
    basic.clearScreen()
    is_controller_enabled = true
    is_displaying_score = false
}

function display_lose() {
    
    is_controller_enabled = false
    basic.clearScreen()
    basic.showLeds(`
            . . . . .
            . # . # .
            . . . . .
            . # # # .
            # . . . #
        `)
    basic.pause(3000)
}

function display_win() {
    
    is_controller_enabled = false
    basic.clearScreen()
    basic.showLeds(`
        . . . . .
        . # . # .
        . . . . .
        # . . . #
        . # # # .
    `)
    basic.pause(3000)
}

radio.onReceivedValue(function on_received_value(name: string, value: number) {
    
    if (name == "BALL") {
        //  flip it because screens are facing eachother
        ball_x_dir = value * -1
        //  Randomly place ball otherwise it's repetitive
        ball_x = randint(0, 4)
        if (ball_x == 0) {
            ball_x_dir = 1
        } else if (ball_x == 4) {
            ball_x_dir = -1
        }
        
        ball_y = -1
        ball_y_dir = 1
    }
    
})
function connect() {
    radio.sendString("PING")
    basic.pause(10)
}

radio.onReceivedString(function on_radio_received_string(received_str: string) {
    
    if (host && received_str == "PONG") {
        is_connected = true
    } else if (!host && received_str == "PING") {
        radio.sendString("PONG")
        is_connected = true
    } else if (received_str == "SCORE") {
        my_score = my_score + 1
        display_score()
        reset_paddle()
    } else if (received_str == "GAME_OVER") {
        is_playing = false
    }
    
})
basic.showString("PONG!")
basic.showLeds(`
        . . # . .
        . # . . .
        # # # # #
        . # . . .
        . . # . .
    `)
basic.forever(function on_forever() {
    
    is_playing = false
    while (!is_connected) {
        if (host) {
            connect()
        }
        
        basic.pause(200)
    }
    basic.clearScreen()
    for (let countdown = 3; countdown > 0; countdown += -1) {
        basic.showNumber(countdown)
        basic.pause(1000)
    }
    basic.clearScreen()
    reset_paddle()
    ball_x = 0
    ball_y = 0
    ball_x_dir = 1
    ball_y_dir = 1
    my_score = 0
    their_score = 0
    is_playing = true
    is_controller_enabled = true
    //  Host starts, hide ball from client
    if (!host) {
        ball_y = -1
        ball_y_dir = -1
    }
    
    //  game loop
    while (is_playing) {
        basic.pause(250)
        if (host && (my_score >= MAX_POINTS || their_score >= MAX_POINTS)) {
            is_playing = false
            radio.sendString("GAME_OVER")
            break
        }
        
        draw_paddle(paddle_x, paddle_y)
        move_ball()
        if (ball_y == 4) {
            basic.pause(250)
            //  slight pause to show ball hitting ground
            their_score = their_score + 1
            radio.sendString("SCORE")
            display_score()
            reset_paddle()
            reset_ball()
        }
        
        if (ball_y == -1) {
            radio.sendValue("BALL", ball_x_dir)
        }
        
    }
    //  game over
    //  wait for the score to stop being displayed
    while (is_displaying_score) {
        basic.pause(50)
    }
    if (my_score >= MAX_POINTS) {
        display_win()
    } else {
        display_lose()
    }
    
})
