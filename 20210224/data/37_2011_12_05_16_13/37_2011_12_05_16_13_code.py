########
#Important parameters
########


# viewing_distance = 60.0 #units can be anything so long as they match those used in screen_width below
# screen_width = 30.0 #units can be anything so long as they match those used in viewing_distance above
# screen_res = (1366,768) #pixel resolution of the screen
viewing_distance = 80 #units can be anything so long as they match those used in screen_width below
screen_width = 50 #units can be anything so long as they match those used in viewing_distance above
screen_res = (1600,900) #pixel resolution of the screen

response_modality = 'trigger' # 'key' or 'button' or 'trigger'
response_keys = ['z','/']
response_buttons = [8,9]
response_triggers = ['left','right']
trigger_criterion_value = -.5 #specify the trigger criterion

target_location_list = ['left','right','up','down']
target_list = ['black','white']
flankers_list = ['congruent','incongruent','neutral','neutral']

fixation_interval = 1.000
response_timeout = 1.000
ITI = 1.000

reps_per_block = 1
number_of_blocks = 30 #specify the number of blocks

instruction_size_in_degrees = 1 #specify the size of the instruction text
response_feedback_text_size_in_degrees = .5 #specify the size of the feedback text (if used)

target_size_in_degrees = .5 #specify the width of the target
flanker_separation_in_degrees = .25
offset_in_degrees = 3 #specify the vertical offset of the target from fixation

text_width = .9 #specify the proportion of the screen to use when drawing instructions


########
# Import libraries
########
import pygame
import Image
import aggdraw
import math
import sys
import os
import random
import time
import shutil
import hashlib
import multiprocessing
# import cv


########
# Start the random seed
########
seed = time.time() #grab the current time
random.seed(seed) #use the time to set the random seed


########
# Initialize pygame
########
pygame.init() #initialize pygame
pygame.mouse.set_visible(False) #make the mouse invisible

pygame.mixer.init()
error_sound = pygame.mixer.Sound('./_Stimuli/error.wav')

########
# Initialize the gamepad if necessary
########
if response_modality!='key':
	gamepad = pygame.joystick.Joystick(0)
	gamepad.init()


########
# set up the secondary process for writing data
########

if response_modality=='trigger':
	
	#create a multiprocessing Queue object
	writer_queue = multiprocessing.Queue()

	#create a class for messages to the trigger queue
	class writer_message(object):
		def __init__(self, message_type, sub = '', trial_info = '', trigger_file_name = '', left_values = '', left_times = '', right_values = '', right_times = '' ):
			self.message_type = message_type
			self.sub = sub
			self.trial_info = trial_info
			self.trigger_file_name = trigger_file_name
			self.left_values = left_values
			self.left_times = left_times
			self.right_values = right_values
			self.right_times = right_times

	#define a function to run continuously in a seperate process that monitors the writer queue for data to write and writes what it finds
	def writer(queue):
		initialized = False
		done = False
		while not done:
			if not queue.empty():
				from_queue = queue.get()
				if from_queue.message_type == 'done':
					done = True
					if initialized:
						trigger_file.close()
				elif from_queue.message_type == 'initialize':
					initialized = True
					trigger_file = open(from_queue.trigger_file_name,'a')
				elif from_queue.message_type == 'write':
					if len(from_queue.left_values)>1:
						for i in range(len(from_queue.left_values))[1:]:
							for j in range(len(from_queue.left_values[i])):
								to_write = from_queue.sub+'\t'+from_queue.trial_info+'\tleft\t'+str(from_queue.left_times[i][j])+'\t'+str(from_queue.left_values[i][j])+'\n'
								trigger_file.write(to_write)
					if len(from_queue.right_values)>1:
						for i in range(len(from_queue.right_values))[1:]:
							for j in range(len(from_queue.right_values[i])):
								to_write = from_queue.sub+'\t'+from_queue.trial_info+'\tright\t'+str(from_queue.right_times[i][j])+'\t'+str(from_queue.right_values[i][j])+'\n'
								trigger_file.write(to_write)


	#start up the separate process
	writer_process = multiprocessing.Process(target=writer, args=(writer_queue,))
	writer_process.start()


########
# Initialize the screen
########

screen = pygame.display.set_mode(screen_res, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) #initialize a screen
screen_x_center = screen_res[0]/2 #store the location of the screen's x center
screen_y_center = screen_res[1]/2 #store the location of the screen's y center


########
#Perform some calculations to convert stimulus measurements in degrees to pixels
########
screen_width_in_degrees = math.degrees(math.atan((screen_width/2.0)/viewing_distance)*2)
PPD = screen_res[0]/screen_width_in_degrees #compute the pixels per degree (PPD)

instruction_size = int(instruction_size_in_degrees*PPD)
response_feedback_text_size = int(response_feedback_text_size_in_degrees*PPD)


target_size = int(target_size_in_degrees*PPD)
flanker_separation = int(flanker_separation_in_degrees*PPD)
offset = int(offset_in_degrees*PPD)

########
#Define some useful colors
########
black = (0,0,0)
white = (255,255,255)
grey = (119,119,119)
red = (173,96,113)
green = (81,131,59)


########
#Initialize the fonts
########

response_feedback_text_font_size = 2
response_feedback_text_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', response_feedback_text_font_size)
response_feedback_text_height = response_feedback_text_font.size('XXX')[1]
while response_feedback_text_height<response_feedback_text_size:
	response_feedback_text_font_size = response_feedback_text_font_size + 1
	response_feedback_text_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', response_feedback_text_font_size)
	response_feedback_text_height = response_feedback_text_font.size('XXX')[1]

response_feedback_text_font_size = response_feedback_text_font_size - 1
response_feedback_text_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', response_feedback_text_font_size)
response_feedback_text_height = response_feedback_text_font.size('XXX')[1]

instruction_font_size = 2
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]
while instruction_height<instruction_size:
	instruction_font_size = instruction_font_size + 1
	instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
	instruction_height = instruction_font.size('XXX')[1]

instruction_font_size = instruction_font_size - 1
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]



########
# Create sprites for visual stimuli
########

#define a function to turn PIL/aggdraw images to pygame surfaces
def image2surf(image):
	mode = image.mode
	size = image.size
	data = image.tostring()
	return pygame.image.fromstring(data, size, mode)



# black_brush = aggdraw.Brush(black)
# white_brush = aggdraw.Brush(white)
# 
# white_circle = aggdraw.Draw('RGBA',[target_size,target_size],(0,0,0,0))
# white_circle.ellipse((0,0,target_size,target_size), white_brush)
# white_circle = image2surf(white_circle)
# 
# black_circle = aggdraw.Draw('RGBA',[target_size,target_size],(0,0,0,0))
# black_circle.ellipse((0,0,target_size,target_size), black_brush)
# black_circle = image2surf(black_circle)

white_circle = aggdraw.Draw('RGBA',[target_size,target_size],grey)
this_degree = 0
for i in range(12):
	this_degree = i*30
	if i%2==1:
		brush = aggdraw.Brush(white)
	else:
		brush = aggdraw.Brush(grey)
	for j in range(30):
		this_degree = this_degree+1
		white_circle.polygon(
	     (
	       int(round(target_size/2.0))
	       , int(round(target_size/2.0))
	       , int(round(target_size/2.0 + math.sin(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.sin((this_degree+1)*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos((this_degree+1)*math.pi/180)*target_size/2.0))
	     )
	     , brush
	    )
white_circle = image2surf(white_circle)

black_circle = aggdraw.Draw('RGBA',[target_size,target_size],grey)
this_degree = 0
for i in range(12):
	this_degree = i*30
	if i%2==1:
		brush = aggdraw.Brush(grey)
	else:
		brush = aggdraw.Brush(black)
	for j in range(30):
		this_degree = this_degree+1
		black_circle.polygon(
	     (
	       int(round(target_size/2.0))
	       , int(round(target_size/2.0))
	       , int(round(target_size/2.0 + math.sin(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.sin((this_degree+1)*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos((this_degree+1)*math.pi/180)*target_size/2.0))
	     )
	     , brush
	    )
black_circle = image2surf(black_circle)


neutral_circle = aggdraw.Draw('RGBA',[target_size,target_size],grey)
this_degree = 0
for i in range(12):
	this_degree = i*30
	if i%2==1:
		brush = aggdraw.Brush(white)
	else:
		brush = aggdraw.Brush(black)
	for j in range(30):
		this_degree = this_degree+1
		neutral_circle.polygon(
	     (
	       int(round(target_size/2.0))
	       , int(round(target_size/2.0))
	       , int(round(target_size/2.0 + math.sin(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos(this_degree*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.sin((this_degree+1)*math.pi/180)*target_size/2.0))
	       , int(round(target_size/2.0 + math.cos((this_degree+1)*math.pi/180)*target_size/2.0))
	     )
	     , brush
	    )
neutral_circle = image2surf(neutral_circle)

black_congruent = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
black_congruent.blit(black_circle,(target_size+flanker_separation,target_size+flanker_separation))
black_congruent.blit(black_circle,(0,target_size+flanker_separation))
black_congruent.blit(black_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
black_congruent.blit(black_circle,(target_size+flanker_separation,0))
black_congruent.blit(black_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))

black_incongruent = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
black_incongruent.blit(black_circle,(target_size+flanker_separation,target_size+flanker_separation))
black_incongruent.blit(white_circle,(0,target_size+flanker_separation))
black_incongruent.blit(white_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
black_incongruent.blit(white_circle,(target_size+flanker_separation,0))
black_incongruent.blit(white_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))

black_neutral = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
black_neutral.blit(black_circle,(target_size+flanker_separation,target_size+flanker_separation))
black_neutral.blit(neutral_circle,(0,target_size+flanker_separation))
black_neutral.blit(neutral_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
black_neutral.blit(neutral_circle,(target_size+flanker_separation,0))
black_neutral.blit(neutral_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))

white_congruent = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
white_congruent.blit(white_circle,(target_size+flanker_separation,target_size+flanker_separation))
white_congruent.blit(white_circle,(0,target_size+flanker_separation))
white_congruent.blit(white_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
white_congruent.blit(white_circle,(target_size+flanker_separation,0))
white_congruent.blit(white_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))

white_incongruent = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
white_incongruent.blit(white_circle,(target_size+flanker_separation,target_size+flanker_separation))
white_incongruent.blit(black_circle,(0,target_size+flanker_separation))
white_incongruent.blit(black_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
white_incongruent.blit(black_circle,(target_size+flanker_separation,0))
white_incongruent.blit(black_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))

white_neutral = pygame.Surface((target_size*3+flanker_separation*2,target_size*3+flanker_separation*2),pygame.SRCALPHA)
white_neutral.blit(white_circle,(target_size+flanker_separation,target_size+flanker_separation))
white_neutral.blit(neutral_circle,(0,target_size+flanker_separation))
white_neutral.blit(neutral_circle,(target_size*2+flanker_separation*2,target_size+flanker_separation))
white_neutral.blit(neutral_circle,(target_size+flanker_separation,0))
white_neutral.blit(neutral_circle,(target_size+flanker_separation,target_size*2+flanker_separation*2))


eraser = aggdraw.Draw('RGBA',[target_size*3+flanker_separation*2,target_size*3+flanker_separation*2],grey)
eraser = image2surf(eraser)


########
# Drawing and helper functions
########

#define a function to draw a pygame surface centered on given coordinates
def blit_to_screen(surf,x_offset=0,y_offset=0):
	x = screen_x_center+x_offset-surf.get_width()/2.0
	y = screen_y_center+y_offset-surf.get_height()/2.0
	screen.blit(surf,(x,y))



#define a function that draws a target on the screen
def draw_target(target_location,target,flankers):
	if target=='black':
		if flankers=='congruent':
			target=black_congruent
		elif flankers=='incongruent':
			target=black_incongruent
		else:
			target=black_neutral
	else:
		if flankers=='congruent':
			target=white_congruent
		elif flankers=='incongruent':
			target=white_incongruent
		else:
			target=white_neutral
	if target_location=='left':
		blit_to_screen( target , x_offset=-offset )
	elif target_location=='right':
		blit_to_screen( target , x_offset=offset )
	elif target_location=='up':
		blit_to_screen( target , y_offset=-offset )
	else:
		blit_to_screen( target , y_offset=offset )


#define a function that draws a target on the screen
def erase_target(target_location):
	if target_location=='left':
		blit_to_screen( eraser , x_offset=-offset )
	elif target_location=='right':
		blit_to_screen( eraser , x_offset=offset )
	elif target_location=='up':
		blit_to_screen( eraser , y_offset=-offset )
	else:
		blit_to_screen( eraser , y_offset=offset )


#define a function that waits for a given duration to pass
def simple_wait(duration):
	start = time.time()
	while time.time() < (start + duration):
		pass


#define a function that formats text for the screen
def draw_text(my_text, instruction_font, text_color, my_surface, text_width):
	my_surface_rect = my_surface.get_rect()
	text_width_max = int(my_surface_rect.size[0]*text_width)
	paragraphs = my_text.split('\n')
	render_list = []
	text_height = 0
	for this_paragraph in paragraphs:
		words = this_paragraph.split(' ')
		if len(words)==1:
			render_list.append(words[0])
			if (this_paragraph!=paragraphs[len(paragraphs)-1]):
				render_list.append(' ')
				text_height = text_height + instruction_font.get_linesize()
		else:
			this_word_index = 0
			while this_word_index < (len(words)-1):
				line_start = this_word_index
				line_width = 0
				while (this_word_index < (len(words)-1)) and (line_width <= text_width_max):
					this_word_index = this_word_index + 1
					line_width = instruction_font.size(' '.join(words[line_start:(this_word_index+1)]))[0]
				if this_word_index < (len(words)-1):
					#last word went over, paragraph continues
					render_list.append(' '.join(words[line_start:(this_word_index-1)]))
					text_height = text_height + instruction_font.get_linesize()
					this_word_index = this_word_index-1
				else:
					if line_width <= text_width_max:
						#short final line
						render_list.append(' '.join(words[line_start:(this_word_index+1)]))
						text_height = text_height + instruction_font.get_linesize()
					else:
						#full line then 1 word final line
						render_list.append(' '.join(words[line_start:this_word_index]))
						text_height = text_height + instruction_font.get_linesize()
						render_list.append(words[this_word_index])
						text_height = text_height + instruction_font.get_linesize()
					#at end of paragraph, check whether a inter-paragraph space should be added
					if (this_paragraph!=paragraphs[len(paragraphs)-1]):
						render_list.append(' ')
						text_height = text_height + instruction_font.get_linesize()
	num_lines = len(render_list)*1.0
	for this_line in range(len(render_list)):
		this_render = instruction_font.render(render_list[this_line], True, text_color)
		this_render_rect = this_render.get_rect()
		this_render_rect.centerx = my_surface_rect.centerx
		this_render_rect.centery = int(my_surface_rect.centery - text_height/2.0 + 1.0*this_line/num_lines*text_height)
		my_surface.blit(this_render, this_render_rect)


#define a function that waits for a response
def wait_for_response():
	pygame.event.clear()
	done = False
	while not done:
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				response = event.unicode
				if response == '\x1b':
					pygame.quit()
					if response_modality=='trigger':
						writer_queue.put(writer_message('done'))
						writer_process.join()
						simple_wait(1)
						if writer_process.is_alive():
							writer_process.terminate()
					try:
						data_file.close()
					except:
						pass
					sys.exit()
				else:
					done = True
			else:
				if response_modality=='button':
					if event.type == pygame.JOYBUTTONDOWN:
						response = event.button
						done = True
				else:
					if event.type == pygame.JOYAXISMOTION:
						if (event.axis==4):
							if event.value>trigger_criterion_value:
								response = 'left'
								done = True
						elif (event.axis==5):
							if event.value>trigger_criterion_value:
								response = 'right'
								done = True
	pygame.event.clear()				
	return response


#define a function that prints a message on the screen while looking for user input to continue. The function returns the total time it waited
def show_message(my_text):
	message_viewing_time_start = time.time()
	pygame.event.pump()
	pygame.event.clear()
	screen.fill(black)
	pygame.display.flip()
	screen.fill(black)
	draw_text(my_text, instruction_font, grey, screen, text_width)
	simple_wait(.5)
	pygame.display.flip()
	screen.fill(black)
	wait_for_response()
	pygame.display.flip()
	screen.fill(black)
	simple_wait(.5)
	message_viewing_time = time.time() - message_viewing_time_start
	return message_viewing_time


#define a function that requests user input
def get_input(get_what):
	get_what = get_what+'\n'
	text_input = ''
	screen.fill(black)
	pygame.display.flip()
	simple_wait(.5)
	my_text = get_what+text_input
	screen.fill(black)
	draw_text(my_text, instruction_font, grey, screen, text_width)
	pygame.display.flip()
	screen.fill(black)
	done = False
	while not done:
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				key_down = event.unicode
				if key_down == '\x1b':
					pygame.quit()
					if response_modality=='trigger':
						writer_queue.put(writer_message('done'))
						writer_process.join()
						simple_wait(1)
						if writer_process.is_alive():
							writer_process.terminate()
					try:
						data_file.close()
					except:
						pass
					sys.exit()
				elif key_down == '\x7f':
					if text_input!='':
						text_input = text_input[0:(len(text_input)-1)]
						my_text = get_what+text_input
						screen.fill(black)
						draw_text(my_text, instruction_font, grey, screen, text_width)
						pygame.display.flip()
				elif key_down == '\r':
					done = True
				else:
					text_input = text_input + key_down
					my_text = get_what+text_input
					screen.fill(black)
					draw_text(my_text, instruction_font, grey, screen, text_width)
					pygame.display.flip()
	screen.fill(black)
	pygame.display.flip()
	return text_input


#define a function that obtains subject info via user input
def get_sub_info():
	year = time.strftime('%Y')
	month = time.strftime('%m')
	day = time.strftime('%d')
	hour = time.strftime('%H')
	minute = time.strftime('%M')
	sid = get_input('SID (\'test\' to demo):')
	if sid != 'test':
		gender = get_input('Gender (m or f):')
		age = get_input('Age (2-digit number):')
		handedness = get_input('Handedness (r or l):')
		languages = get_input('Number of fluent languages:')
		music = get_input('Number of years playing a musical instrument:')
		gaming = get_input('Hours of gaming per week, averaged over the past 5 years:')
		password = get_input('Please enter a password:')
	else:
		gender='test'
		age='test'
		handedness='test'
		languages = 'test'
		music = 'test'
		gaming = 'test'
		password = 'test'
	password = hashlib.sha512(password).hexdigest()
	sub_info = [ sid , year , month , day , hour , minute , gender , age , handedness , languages , music , gaming , password ]
	return sub_info


#define a function that initializes the data file
def initialize_data_files(password):	
	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if sub_info[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(sub_info[0:6])
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)
	shutil.copy('main.py', '_Data/'+filebase+'/'+filebase+'_code.py')
	data_file_name = '_Data/'+filebase+'/'+filebase+'_data.txt'
	data_file  = open(data_file_name,'w')
	data_file.write(password+'\n')
 	header ='\t'.join(['id' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'gender' , 'age'  , 'handedness' , 'languages' , 'music' , 'gaming' , 'wait' , 'block' , 'trial' , 'target_location' , 'target' , 'flankers' , 'rt' , 'response' , 'error' , 'pre_target_response' , 'ITI_response' ])
	data_file.write(header+'\n')
	to_return = data_file
	if response_modality=='trigger':
		trigger_file_name = '_Data/'+filebase+'/'+filebase+'_trigger.txt'
		trigger_file  = open(trigger_file_name,'w')
		header ='\t'.join(['id' , 'block' , 'trial' , 'target_location' , 'target' , 'flankers' , 'trigger' , 'time' , 'value' ])
		trigger_file.write(header+'\n')
		trigger_file.close()
		writer_queue.put(writer_message('initialize',trigger_file_name=trigger_file_name))
	return to_return


#define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial combination of the independent variables.
def get_trials():
	trials=[]
	for target_location in target_location_list:
		for target in target_list:
			for flankers in flankers_list:
				for i in range(reps_per_block):
					if target_location=='neutral':
						target_location = random.choice(['up','down'])
					trials.append([target_location,target,flankers])
	random.shuffle(trials)
	return trials


#define a function to check for user input during a trial loop
def check_for_input(now):
	pygame.event.pump
	responses = []
	these_left_values = []
	these_left_times = []
	these_right_values = []
	these_right_times = []
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN :
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				if response_modality=='trigger':
					writer_queue.put(writer_message('done'))
					writer_process.join()
					simple_wait(1)
					if writer_process.is_alive():
						writer_process.terminate()
				try:
					data_file.close()
				except:
					pass
				sys.exit()
			else:
				responses.append(event.unicode)
		if response_modality=='button':
			if event.type == pygame.JOYBUTTONDOWN:
				responses.append(event.button)
		elif response_modality=='trigger':
			if event.type == pygame.JOYAXISMOTION:
				if event.axis==4:
					these_left_values.append(event.value)
					these_left_times.append(now)
					if event.value>=trigger_criterion_value:
						responses.append('left')
						if event.value==1:
							error_sound.play()
				elif event.axis==5:
					these_right_values.append(event.value)
					these_right_times.append(now)
					if event.value>=trigger_criterion_value:
						responses.append('right')
						if event.value==1:
							error_sound.play()
	return [responses,these_left_values,these_left_times,these_right_values,these_right_times]


#define a function that runs a block of trials
def run_block(block,message_viewing_time):
	#get a trial list
	trial_list = get_trials()

	#prep some variables
	trial_num = 0
	
	#start running trials
	for this_trial_info in trial_list:
		#bump the trial number
		trial_num = trial_num + 1
		
		#parse the trial info
		target_location,target,flankers = this_trial_info
				
		#prep the fixation screen
		screen.fill(grey)
		blit_to_screen(neutral_circle)
		
		#start the trial by showing the fixation screen
		pygame.display.flip() 
		
		#get the trial start time 
		trial_start_time = time.time()

		#prep the target screen
		screen.fill(grey)
		blit_to_screen(neutral_circle)
		draw_target(target_location,target,flankers)
		
		#prep some variables
		pre_target_response = 'FALSE'
		ITI_response = 'FALSE'
		response = 'NA'
		rt = 'NA'
		error = 'NA'
		
		#prep some data info to write later
		this_trial_info = '\t'.join(map(str,this_trial_info))
		this_trial_info = '\t'.join(map(str,[block,trial_num,this_trial_info]))
		
		target_done = False
		target_on = False
		target_on_time = trial_start_time+fixation_interval
		reseponse_timeout_time = target_on_time + response_timeout
		ITI_done = False
		left_values = [[-1]]
		left_times = [[0]]
		right_values = [[-1]]
		right_times = [[0]]
		response = False
		#start the trial loop
		loop_done = False
		while not loop_done:
			now = time.time()
			#check if the stimulus display needs updating
			if not target_done:
				if not target_on:
					if now>=target_on_time:
						target_on = True
						pygame.display.flip() #show the target
			else: #target is done
				if now>=reseponse_timeout_time:
					ITI_done_time = reseponse_timeout_time + ITI
					loop_done = True
					break
						
			#check for user input
			responses,these_left_values,these_left_times,these_right_values,these_right_times = check_for_input(now-target_on_time)
			if response_modality=='trigger':
				if len(these_left_values)>0:
					left_values.append(these_left_values)
					left_times.append(these_left_times)
				if len(these_right_values)>0:
					right_values.append(these_right_values)
					right_times.append(these_right_times)
				del these_left_values,these_left_times,these_right_values,these_right_times
			
			#process responses (if any)
			if len(responses)>0:
				if not target_on:
					pre_target_response = 'TRUE'
				else:
					rt = now - target_on_time
					ITI_done_time = now + ITI
					response = responses[0]
					loop_done = True
					
		#done the main loop
		#if necessary keep checking for trigger data to finish the response
		if response_modality=='trigger':		
			if response!='NA':
				left_done = False
				right_done = False
				# print [left_values[-1][-1],right_values[-1][-1]]
				response_done = False
				while not response_done:
					responses,these_left_values,these_left_times,these_right_values,these_right_times = check_for_input(time.time()-target_on_time)
					# print [responses,these_left_values,these_right_values]
					if len(these_left_values)>0:
						left_values.append(these_left_values)
						left_times.append(these_left_times)
						# print ['left',  left_values[-1][-1]]
					if len(these_right_values)>0:
						right_values.append(these_right_values)
						right_times.append(these_right_times)
						# print ['right',  right_values[-1][-1]]
					del these_left_values,these_left_times,these_right_values,these_right_times
					if left_values[-1][-1]<=-1:
						left_done = True
					if right_values[-1][-1]<=-1:
						right_done = True
					if (left_done) & (right_done):
						response_done = True
				
		#process the respose info
		if not response:
			response = 'NA'
			error = 'NA'
			screen.fill(grey)
			pygame.display.flip()
		else:			
			if response_modality=='key':
				if response==black_key:
					response = 'black'
				elif response==white_key:
					response = 'white'
			elif response_modality=='button':
				if response==black_button:
					response = 'black'
				elif response==white_button:
					response = 'white'
			else:
				if response==black_trigger:
					response = 'black'
				elif response==white_trigger:
					response = 'white'
			if response=='black':
				response_feedback_color = black
			elif response=='white':
				response_feedback_color = white
			if response == target:
				error = 'FALSE'
			else:
				error = 'TRUE'
			response_feedback_text = response_feedback_text_font.render(str(int(round(rt*1000))),True,response_feedback_color,grey)
			#prep and draw the ITI screen
			screen.fill(grey)
			blit_to_screen(response_feedback_text)
			pygame.display.flip()
		#wait for the ITI to elapse
		ITI_done = False
		while not ITI_done:
			now = time.time()
			if now>=ITI_done_time:
				ITI_done = True

			#check for user input
			responses,these_left_values,these_left_times,these_right_values,these_right_times = check_for_input(now-target_on_time)
			if response_modality=='trigger':
				if len(these_left_values)>0:
					left_values.append(these_left_values)
					left_times.append(these_left_times)
				if len(these_right_values)>0:
					right_values.append(these_right_values)
					right_times.append(these_right_times)
				del these_left_values,these_left_times,these_right_values,these_right_times

			#process responses (if any)
			if len(responses)>0:
				ITI_response = 'TRUE'
		
		#send analog trigger data to a seperate process to be written out to file
		if response_modality=='trigger':
			message = writer_message(message_type='write',sub=sub_info[0],trial_info=this_trial_info,left_values=left_values,left_times=left_times,right_values=right_values,right_times=right_times)
			writer_queue.put(message)
		#write out data
		trial_info = '\t'.join(map(str, [ sub_info_for_file , message_viewing_time , block , trial_num , target_location , target , flankers , rt , response , error , pre_target_response , ITI_response]))
		data_file.write(trial_info+'\n')


def do_demo():
	screen.fill(grey)
	response_feedback_text = instruction_font.render('White = '+white_trigger+'; black = '+black_trigger,True,white,grey)
	blit_to_screen(response_feedback_text)
	pygame.display.flip()
	screen_num = 0
	done = False
	while not done:
		update = False
		pygame.event.pump()
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN :
				response = event.unicode
				if response == '\x1b':
					pygame.quit()
					if response_modality=='trigger':
						writer_queue.put(writer_message('done'))
						writer_process.join()
						simple_wait(1)
						if writer_process.is_alive():
							writer_process.terminate()
					try:
						data_file.close()
					except:
						pass
					sys.exit()
				elif response=='2':
					screen_num = screen_num + 1
					update = True
				elif response=='1':
					screen_num = screen_num - 1
					update = True
				elif response=='q':
					done = True
		if update:
			screen.fill(grey)
			if screen_num==1:
				blit_to_screen(neutral_circle)
			elif screen_num==2:
				blit_to_screen(neutral_circle)
				blit_to_screen(white_neutral,x_offset=-offset)
			elif screen_num==3:
				response_feedback_text = response_feedback_text_font.render('549',True,white,grey)
				blit_to_screen(response_feedback_text)
			elif screen_num==4:
				blit_to_screen(neutral_circle)
			elif screen_num==5:
				blit_to_screen(neutral_circle)
				blit_to_screen(black_neutral,x_offset=offset)
			elif screen_num==6:
				response_feedback_text = response_feedback_text_font.render('483',True,black,grey)
				blit_to_screen(response_feedback_text)
			elif screen_num==7:
				blit_to_screen(neutral_circle)
			elif screen_num==8:
				blit_to_screen(neutral_circle)
				blit_to_screen(black_neutral,y_offset=-offset)
			elif screen_num==9:
				response_feedback_text = response_feedback_text_font.render('595',True,white,grey)
				blit_to_screen(response_feedback_text)
			pygame.display.flip()
				

########
# Start the experiment
########

#get subject info
sub_info = get_sub_info()
sub_info_for_file = '\t'.join(map(str,sub_info[0:-1]))
password = sub_info[-1]

#counter-balance stimulus-response mapping
mapping = [0,1]
if sub_info[0]!='test':
	if (int(sub_info[0])%2)==1:
		mapping = [1,0]


white_key = response_keys[mapping[0]]
black_key = response_keys[mapping[1]]
white_button = response_buttons[mapping[0]]
black_button = response_buttons[mapping[1]]
white_trigger = response_triggers[mapping[0]]
black_trigger = response_triggers[mapping[1]]
	
		
#initialize the data file
data_file = initialize_data_files(password)

#show some demo screens
do_demo()

message_viewing_time = show_message('Press any trigger to begin practice.')
run_block('practice',message_viewing_time)
message_viewing_time = show_message('Practice is complete.\nPress any trigger to begin the experiment.')

block = 0
for i in range(number_of_blocks):
	block = i+1
	run_block(block,message_viewing_time)
	if i<(number_of_blocks):
		message_viewing_time = show_message('Take a break!\nYou\'re about '+str(block)+'/'+str(number_of_blocks)+' done.\nWhen you are ready, press any trigger to continue the experiment.')

message_viewing_time = show_message('You\'re all done!\nPlease alert the person conducting this experiment that you have finished.')

pygame.quit()
if response_modality=='trigger':
	writer_queue.put(writer_message('done'))
	writer_process.join()
	simple_wait(1)
	if writer_process.is_alive():
		writer_process.terminate()
data_file.close()
sys.exit()
