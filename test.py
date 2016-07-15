import environ

ROOT_DIR = environ.Path(__file__) - 3

print (ROOT_DIR())

print (type(ROOT_DIR()))
