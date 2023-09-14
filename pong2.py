import pygame as pg
import pymunk
import random


class Constants():
    # some constants, modify as you like (may broke the game)
    def __init__(self):
        # screen values
        self.WIDTH = 900
        self.HEIGHT = 525
        self.FPS = 600

        # some colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)

        self.PADDLE_OFFSET = 20
        self.BALL_VELOCITY = 200


class Ball():
    def __init__(self, screen, space, cons, x, y, radius):
        self.screen = screen
        self.space = space
        self.cons = cons

        self.radius = radius
        self.color = self.cons.WHITE

        self.body = pymunk.Body(200)
        self.body.position = (x, y)
        self.body.velocity = (0, 0)

        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.999
        self.shape.density = 1

        self.space.add(self.body, self.shape)

    def draw(self):
        x = int(self.body.position.x)
        y = int(self.body.position.y)
        pg.draw.circle(self.screen, self.color, (x, y), self.radius)

    def is_out_of_the_screen(self):
        x = self.body.position.x

        if 0 > x or x > self.cons.WIDTH:
            return True

    def check_horizontal_edges(self):
        y = self.body.position.y

        if 0 > y - self.radius or y + self.radius > self.cons.HEIGHT:
            return True

    def reset_pos(self):
        # center of the screen
        self.body.position = (self.cons.WIDTH / 2, self.cons.HEIGHT / 2)


class Paddle():
    def __init__(self, screen, space, cons, x):
        self.screen = screen
        self.space = space
        self.cons = cons

        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = (x, self.cons.HEIGHT / 2)  # center

        # the endpoints are relative to the body position (its center)
        self.shape = pymunk.Segment(self.body, (0, -45), (0, 45), 10)
        self.shape.elasticity = 1

        self.space.add(self.body, self.shape)

        self.moving_up = False
        self.moving_down = False

    def draw(self):
        # we need the global coords for the start/end points of the line, relative to the whole space

        # a and b are the offsets
        p1 = self.body.local_to_world(self.shape.a)
        p2 = self.body.local_to_world(self.shape.b)

        pg.draw.line(self.screen, self.cons.WHITE, p1, p2, 10)

    def update(self):

        # y-offset relatives to the position (the center)
        y1 = self.body.local_to_world(self.shape.a).y
        y2 = self.body.local_to_world(self.shape.b).y

        if self.moving_up and self.moving_down:
            self.body.velocity = (0, 0)

        elif self.moving_up and y1 >= 0:
            self.body.velocity = (0, -500)

        elif self.moving_down and y2 <= self.cons.HEIGHT:
            self.body.velocity = (0, 500)

        # if neither is true
        else:
            self.body.velocity = (0, 0)


class Pong():
    def __init__(self):
        pg.init()

        pg.mixer.init()
        self.volume = 0.1
        self.paddle_sound = pg.mixer.Sound('sounds/paddle.mp3')
        self.paddle_sound.set_volume(self.volume)
        self.point_sound = pg.mixer.Sound('sounds/point.mp3')
        self.point_sound.set_volume(self.volume)
        self.wall_sound = pg.mixer.Sound('sounds/wall.mp3')
        self.wall_sound.set_volume(self.volume)

        self.cons = Constants()
        # it will be recieved by the ball and paddle objects
        self.screen = pg.display.set_mode((self.cons.WIDTH, self.cons.HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.space = pymunk.Space()
        self.running = True
        self.playing = False

        # create ball
        self.ball = Ball(self.screen, self.space, self.cons,
                         self.cons.WIDTH / 2, self.cons.HEIGHT / 2, 8)

        # create paddles
        self.paddle1 = Paddle(self.screen, self.space, self.cons,
                              self.screen_rect.left + self.cons.PADDLE_OFFSET)
        self.paddle2 = Paddle(self.screen, self.space, self.cons,
                              self.screen_rect.right - self.cons.PADDLE_OFFSET)

        # create screen segments
        self.tl = (0, 0)
        self.tr = (self.cons.WIDTH, 0)
        self.bl = (0, self.cons.HEIGHT)
        self.br = (self.cons.WIDTH, self.cons.HEIGHT)

        self.create_segment(self.tl, self.tr)  # top
        # self.create_segment(self.tl, self.bl) # left
        self.create_segment(self.bl, self.br)  # bottom
        # self.create_segment(self.br, self.tr) # right

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                    elif event.key == pg.K_SPACE and not self.playing:
                        dir_ = random.choice([-1, 1])
                        self.ball.body.velocity = (
                            dir_*self.cons.BALL_VELOCITY, dir_*self.cons.BALL_VELOCITY)
                        self.playing = True

                    elif event.key == pg.K_w:
                        self.paddle1.moving_up = True

                    elif event.key == pg.K_s:
                        self.paddle1.moving_down = True

                    elif event.key == pg.K_o:
                        self.paddle2.moving_up = True

                    elif event.key == pg.K_l:
                        self.paddle2.moving_down = True

                elif event.type == pg.KEYUP:

                    if event.key == pg.K_w:
                        self.paddle1.moving_up = False

                    elif event.key == pg.K_s:
                        self.paddle1.moving_down = False

                    elif event.key == pg.K_o:
                        self.paddle2.moving_up = False

                    elif event.key == pg.K_l:
                        self.paddle2.moving_down = False

            # update the position of the paddles
            self.paddle1.update()
            self.paddle2.update()
            if self.ball.is_out_of_the_screen():
                self.point_sound.play()
                self.ball.reset_pos()
                self.ball.body.velocity = (0, 0)
                self.playing = False

            # draw stuff
            self.screen.fill(self.cons.BLACK)
            pg.draw.line(self.screen, self.cons.WHITE, (self.cons.WIDTH /
                         2, 0), (self.cons.WIDTH / 2, self.cons.HEIGHT), 10)
            self.ball.draw()
            self.paddle1.draw()
            self.paddle2.draw()

            pg.display.flip()
            self.space.step(1/self.cons.FPS)

        pg.quit()

    def create_segment(self, pos1, pos2):
        segment_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment_shape = pymunk.Segment(segment_body, pos1, pos2, 0)
        segment_shape.elasticity = 1
        self.space.add(segment_body, segment_shape)


game = Pong()
game.run()
