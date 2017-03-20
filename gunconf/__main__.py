import argparse
from gunconf.ui.gunapp import GunApp
from gunconf.controler import Controler

def parseArgs():
    """ parse arguments """
    parser = argparse.ArgumentParser(description='gun configuration utility')
    parser.add_argument('--width', type=int, help='screen width')
    parser.add_argument('--height', type=int, help='screen height')
    return parser.parse_args()



if __name__ == '__main__':

    # parse arg
    args = parseArgs()

    # allocate controler
    controler = Controler()

    # allocate app
    app = GunApp(args.width, args.height)
    app.setCtrl(controler)

    controler.setCb(app.ctrlCb)
    controler.start()

    app.run()
