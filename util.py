import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)  #


formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create a handler for outputting logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Create a handler for outputting logs to a file
file_handler = logging.FileHandler('output.log')
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


