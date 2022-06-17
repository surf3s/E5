import e5py.e5 as e5
from kivy import resources

if __name__ == '__main__':
    resources.resource_add_path(e5.resourcePath())  # add this line
    e5.E5App().run()
