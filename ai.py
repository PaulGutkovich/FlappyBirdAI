from game import *
import neat
import pickle
import os

gen = 0
screen_size = [480, 640]
screen = pygame.display.set_mode(screen_size)

# Defining the screen
screen_size = [480, 640]

# Load the background image
background_height = round(0.8 * screen_size[1])
background_img = pygame.image.load("background.png").convert_alpha()
background_img = pygame.transform.scale(background_img, ([screen_size[0], background_height]))

# Load bird and pipe images
bird_img = pygame.image.load("bird.png").convert_alpha()
pipe_img = pygame.image.load("pipe.png").convert_alpha()

# Caption for pygame window
pygame.display.set_caption("Flappy Bird")

def eval_genomes(genomes, config):
	global gen, screen_size, bird_img, pipe_img, background_img, background_height

	pygame.init()

	gen += 1
	nets = []
	birds = []
	ge = []

	screen = pygame.display.set_mode(screen_size)
	font = pygame.font.SysFont("comicsans", 50)

	for genome_id, genome in genomes:
		genome.fitness = 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		birds.append(Bird(screen, bird_img, 60, 40))
		ge.append(genome)

	pipe1 = Pipe(screen, pipe_img, 1, 100, 700)
	pipe2 = Pipe(screen, pipe_img, 2, 100, 700)
	pipes = [pipe1, pipe2]

	clock = pygame.time.Clock()

	run = True

	while run and len(birds) > 0:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		bird_0 = birds[0]
		if bird_0.x > pipes[0].x+pipes[0].width and bird_0.x < pipes[1].x:
			pipe_index = 1

		elif bird_0.x > pipes[1].x+pipes[1].width and bird_0.x < pipes[0].x:
			pipe_index = 0

		elif bird_0.x < pipes[0].x and bird_0.x < pipes[1].x:
			pipe_index = 0

		current_pipe = pipes[pipe_index]

		for i, bird in enumerate(birds):
			ge[i].fitness += 0.1
			bird.update_pos()

			output = nets[i].activate((bird.x, bird.y, abs(bird.y-current_pipe.bottom_y), abs(bird.y - current_pipe.top_y-current_pipe.height)))

			if output[0]>0.5:
				bird.flap()

		for pipe in pipes:
			pipe.update_pos()

			for i, bird in enumerate(birds):
				if pipe.collide(bird) or bird.hit_border():
					ge[i].fitness -= 1
					birds.pop(i)
					nets.pop(i)
					ge.pop(i)

		draw_all(screen, background_img, background_height, birds, pipes)
		pipe_label = font.render(str(pipe_index+1), 1, (255,0,0))
		screen.blit(pipe_label, (10,10))

		if len(ge) > 0 and ge[0].fitness >= 500:
			pickle.dump(nets[0], open("best.pickle", "wb"))
			break

		pygame.display.update()
		clock.tick(60)

	pygame.quit()



def run(config_file):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

    # Run for up to 50 generations.
	winner = p.run(eval_genomes, 50)

    # show final stats
	print('\nBest genome:\n{!s}'.format(winner))


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config.txt')
run(config_path)