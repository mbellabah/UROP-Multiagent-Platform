'''
This describes the state of the environment - will later be the time evolution of the environment
'''

import pygame, math, time, random, copy, sys, signal
from pygame.locals import *
from collections import OrderedDict
import threading


# MARK: Threading
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

# MARK: Requirements pertaining to the pygame interface
WIDTH = 1000
HEIGHT = 600
SCALE = 60

RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
ORANGE = (255,165,0)
PINK = (255,153,153)


# MARK: Classes pertaining to network elements
class EnvironmentMap(object):
    def __init__(self, node_pos, edges_list, agent_dict):
        '''
        :param node_pos: dict, giving the position of each object
        :param edges_list: str, gives the way in which nodes are connected
        '''

        pygame.init()

        self.ICON = pygame.image.load('Auxo_Logo_Black.png')
        self.DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FONT = pygame.font.SysFont('Arial', 18)
        pygame.display.set_caption('Multi-agent System, v1')
        pygame.display.set_icon(self.ICON)
        self.BACKGROUND = pygame.Surface(self.DISPLAYSURF.get_size())
        self.BACKGROUND = self.BACKGROUND.convert()
        self.BACKGROUND.fill(BLACK)

        self.agent_dict = agent_dict

        self.node_pos = node_pos
        self.edges_list = [x.split(':') for x in edges_list.split()]
        self.node_dict = {}
        self.edge_dict = {}
        self.network_graph = {}

        # MARK: Starting the GUI
        self.clock = pygame.time.Clock()
        self.DISPLAYSURF.blit(self.BACKGROUND, (0,0))

        hover = None
        mouse_click = False
        click_list = [0] * len(self.node_pos)

        self.build_network()

        self.draw_all_nodes(RED)
        for _, edge_obj in self.edge_dict.items():
            edge_obj.draw()

    @threaded
    def render_network(self):
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    break

                # elif event.type == MOUSEMOTION:
                #     self.mousex, self.mousey = event.pos
                #
                # elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                #     self.make_popup()

                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        pygame.quit()
                        sys.exit()
                        break

            pygame.display.update()
            self.clock.tick(60)

    def make_popup(self):   # Make popup menu on right click
        POPUPSURF = pygame.Surface((100, 100))
        options = [
            'Attack',
            'Talk'
        ]

        for i in range(len(options)):
            textSurf = self.FONT.render(options[i], 1, BLUE)
            textRect = textSurf.get_rect()
            top = textRect.top
            left = textRect.left
            top += pygame.font.Font.get_linesize(self.FONT)
            POPUPSURF.blit(textSurf, textRect)

        POPUPRECT = POPUPSURF.get_rect()
        POPUPRECT.centerx = WIDTH/2
        POPUPRECT.centery = HEIGHT/2
        self.DISPLAYSURF.blit(POPUPSURF, POPUPRECT)

    def build_network(self):
        # Create the node and edge objects
        for node_name, pos in self.node_pos.items():
            self.node_dict[node_name] = Node(node_name, pos, self.agent_dict[node_name], environment_map_obj=self)  # insert object
        for edge_name in self.edges_list:
            edge_name = tuple(edge_name)
            self.edge_dict[edge_name] = Edge(edge_name, (self.node_pos[edge_name[0]], self.node_pos[edge_name[1]]), environment_map_obj=self)

    def draw_all_nodes(self, color):
        for _, node_obj in self.node_dict.items():
            node_obj.change_color(color)
            node_obj.draw()

    def draw_indv_node(self, color, node_obj):
        node_obj.change_color(color)
        node_obj.draw()

    def draw_indv_edge(self, color, edge_obj):
        edge_obj.change_color(color)
        edge_obj.draw()

    def text_objects(self, text, font):
        textSurface = font.render(text, True, WHITE)
        return textSurface, textSurface.get_rect()

    def hover_display(self, text):
        text = f'{str(text)}'
        _text = pygame.font.FONT('freesansbold.ttf', 20)
        TextSurf, TextRect = self.text_objects(text, _text)
        TextRect.center = ((SCALE), (HEIGHT - (SCALE - 30)))
        self.DISPLAYSURF.blit(TextSurf, TextRect)

        pygame.display.update()
        time.sleep(0.1)
        self.DISPLAYSURF.fill(BLACK)


class Node(object):
    def __init__(self, name, pos, agent_object=None, environment_map_obj=None):   # Pos: Tuple
        self.name = str(name)
        self.x, self.y = pos
        self.color = RED
        self.circle_rect = None

        self.env_obj = environment_map_obj
        self.DISPLAYSURF = self.env_obj.DISPLAYSURF
        self.FONT = self.env_obj.FONT

    def draw(self):
        self.circle_rect = pygame.draw.circle(self.DISPLAYSURF, self.color, (self.x, self.y), 5)
        pygame.draw.circle(self.DISPLAYSURF, self.color, (self.x, self.y), 5)
        self.DISPLAYSURF.blit(self.FONT.render(self.name, True, GREEN), (self.x, self.y))

    def change_color(self, color=RED):
        self.color = color


class Edge(object):
    def __init__(self, label, start_end, environment_map_obj):   # start_end: tuple
        self.label = str(label)
        self.start, self.end = start_end
        self.color = RED

        self.env_obj = environment_map_obj
        self.DISPLAYSURF = self.env_obj.DISPLAYSURF
        self.FONT = self.env_obj.FONT

    @property
    def length(self):
        x_1, y_1 = self.start
        x_2, y_2 = self.end
        return int('%.0f' % math.hypot(x_1-x_2, y_1-y_2))

    def draw(self):
        mid_x = (self.start[0] + self.end[0])/2
        mid_y = (self.start[1] + self.end[1])/2
        pygame.draw.line(self.DISPLAYSURF, self.color, self.start, self.end)
        self.DISPLAYSURF.blit(self.FONT.render(str(self.length), True, WHITE), (mid_x, mid_y))

    def change_color(self, color=RED):
        self.color = color






