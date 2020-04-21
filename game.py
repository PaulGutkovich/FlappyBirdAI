import pygame
from pygame.locals import *
import time
import random

# Bird class
class Bird():
	def __init__(self, surface, image, width, height):
		self.surface = surface
		self.image = pygame.transform.scale(image, (width, height))    
		self.r = 20
		self.g = 0.7
		self.x = 200
		self.y = 20
		self.v_y = 0
		self.alive = True
		self.height = height
		self.width = width
		self.mask = pygame.mask.from_surface(self.image)
		self.score = 0

	# Blit the image of the bird onto the surface
	def draw(self):
		self.surface.blit(self.image, (round(self.x), round(self.y)))

	# Get mask of the bird (for collision detection)
	def get_mask(self):
		return self.mask

	# Vertical movement
	def update_pos(self):
		if self.alive:
			self.update_v()
			self.y += self.v_y
			self.mask = pygame.mask.from_surface(self.image)

		if self.hit_border():
			self.alive = False

	# Vertical accelerration (gravity)
	def update_v(self):
		self.v_y += self.g
		self.v_y = min(self.v_y, 10)

	# Flapping movement
	def flap(self):
		if self.alive:
			self.v_y = -10

	# Check if we hit the top or bottom of the screen
	def hit_border(self):
		if self.y+self.height >= 0.8*self.surface.get_rect()[-1] or self.y <= 0:
			return True

		return False

  
# Pipe class
class Pipe():
	def __init__(self, surface, image, number, width, height):
		self.surface = surface
		self.bottom_image = pygame.transform.scale(image, (width, height))
		self.top_image = pygame.transform.flip(self.bottom_image, False, True)
		self.bottom_y = random.randrange(250, 450)
		self.v_x = -3
		self.x = 190+290*number
		self.width = width
		self.height = height
		self.gap_size = 120
		self.top_y = self.bottom_y-self.height-self.gap_size
		self.passed = False


	# Blit pipe images onto surface
	def draw(self):
		self.surface.blit(self.bottom_image, (round(self.x), round(self.bottom_y)))
		self.surface.blit(self.top_image, (round(self.x), round(self.top_y)))

	# Update horizontal position
	def update_pos(self):
		self.x += self.v_x
		self.go_back()

	# Return back to right side of screen when pipe exits through left side
	def go_back(self):
		if self.x<=-1*self.width:
			self.x = 480
			self.bottom_y = random.randrange(250, 450)
			self.top_y = self.bottom_y - self.height - self.gap_size
			self.passed = False

	# Check collision with bird
	def collide(self, bird):
		top_offset = (self.x - bird.x, self.top_y - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom_y - round(bird.y))
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.top_image)
		bottom_mask = pygame.mask.from_surface(self.bottom_image)

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask,top_offset)

		if b_point or t_point:
			return True

		return False

# Draws everything
def draw_all(surface, background, background_height, birds, pipes):
	surface.blit(background, (0,0))

	for bird in birds:
		bird.draw()

	for pipe in pipes:
		pipe.draw()

	screen_size = surface.get_rect()[2:]
	pygame.draw.rect(surface, (242, 214, 148), (0, background_height, screen_size[0], screen_size[1]-background_height))


# main function
def main():
	#initilalize pygame
	pygame.init()
	# Defining the screen
	screen_size = [480, 640]
	screen = pygame.display.set_mode(screen_size)

	# Load the background image
	background_height = round(0.8 * screen_size[1])
	background_img = pygame.image.load("background.png").convert_alpha()
	background_img = pygame.transform.scale(background_img, ([screen_size[0], background_height]))

	# Define the font for printing the score
	font = pygame.font.SysFont("comicsans", 50)

	# Load bird and pipe images
	bird_img = pygame.image.load("bird.png").convert_alpha()
	pipe_img = pygame.image.load("pipe.png").convert_alpha()

	# Caption for pygame window
	pygame.display.set_caption("Flappy Bird")

	# Create bird and pipe instances
	b = Bird(screen, bird_img, 60, 40)
	pipe1 = Pipe(screen, pipe_img, 1, 100, 700)
	pipe2 = Pipe(screen, pipe_img, 2, 100, 700)

	# Pygame clock to ensure equal iteration times
	clock = pygame.time.Clock()

	# Main loop
	run = True
	while run:
		for event in pygame.event.get():

			# Check if the user quits the window
			if event.type == pygame.QUIT:
				run = False

			# Flap if we detect space key is pressed or if mouse is clicked
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					b.flap()

			elif event.type == pygame.MOUSEBUTTONDOWN:
				b.flap()

		# Bird dies if it collides with any pipe
		if pipe1.collide(b) or pipe2.collide(b):
			b.alive = False

		# If the bird is still alive, the pipes and bird will move
		if b.alive:
			b.update_pos()

			pipe1.update_pos()

			pipe2.update_pos()

		# If the bird is dead, we quit the main loop
		else:
			run = False

		birds = [b]
		pipes = [pipe1, pipe2]

		# Check if the bird passed any pipe, increase score
		for pipe in pipes:
			if not pipe.passed and b.x > pipe.x:
				pipe.passed = True
				b.score += 1

		# Draw the background, bird, and pipes
		draw_all(screen, background_img, background_height, birds, pipes)

		# Draw the score in the top left corner
		score_label = font.render("Score: "+str(b.score), 1, (255,0,0))
		screen.blit(score_label, (10,10))

		# Pgame update and clock tick
		pygame.display.update()
		clock.tick(60)

	# When we die, we wait a second then quit the window.
	time.sleep(1.)

	pygame.quit()

if __name__ == "__main__":
	main()     