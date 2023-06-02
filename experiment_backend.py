# Imports #
import numpy as np
import numpy.random as R
import glob
import platform
import sys
from experiment_results import *
from datetime import datetime, date
from psychopy import visual, event, core, gui, logging

pd.options.mode.chained_assignment = None


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# Functions #
def experiment_info():
    """
    Prompts experimenter for necessary inputs to experiment related to
    subject number, length of study list, and time each study image is
    to be presented.

    return:
        subj (int): subject number or id
        num (int): length of study list (number of images)
        time (float): time each study image is to be presented
    """
    expGui = gui.Dlg(title="Welcome to the Recognition Memory Experiment")

    expGui.addField('Subject number: ')
    expGui.addField('Number of images: ')
    expGui.addField('Presentation time (seconds): ')

    while True:
        expGui.show()
        if (expGui.data[0].isdigit()) and (expGui.data[1].isdigit()) and (expGui.data[2].replace('.', '', 1).isdigit()):
            subj = int(expGui.data[0])
            num = int(expGui.data[1])
            time = float(expGui.data[2])
            if (num >= 5) and (num <= 50) and (time >= 0) and (subj >= 0):
                break

    return subj, num, time


def add_data(path):
    """
        Reads image data paths to store into a data structure.

        Arguments:
            path (str): absolute path to target folder of dataset
        return:
            img_paths (list): a list containing the absolute path for each image in the
            dataset
    """
    # Account for if user has Windows OS
    if platform.system() == "Windows":
        sep = '\\'
    else:
        sep = '/'

    img_paths = [os.path.join(path, img) for img in glob.glob(path + sep + '*.jpg')]

    return img_paths


def generate_datasets(seed, num, imgs):
    """
        Creates datasets for the study phase and test phase from random images.

        Arguments:
            seed (int): value for seeding to generate random images
            num (int): length of study list (number of images)
            imgs (list): data structure containing paths of all images in overall dataset

        return:
            study_set (list): a list containing the absolute path for each image in the study dataset
            test_set (list): a list containing the absolute path for each image in the test dataset
    """
    size = len(imgs)
    study_set = []
    tmp = []

    R.seed(seed)

    for i in range(num):
        study_set.append(imgs[R.randint(0, size)])

    j = 0
    while j < num:
        img = imgs[R.randint(0, size)]
        if img not in study_set:
            tmp.append(img)
            j += 1

    test_set = [y for x in [study_set, tmp] for y in x]

    R.shuffle(test_set)

    return study_set, test_set


def image_stim(win, img):
    """
        Creates an image to present to the monitor.

        Arguments:
            win: psychopy window object
            img (str): path of image

        return:
            im: psychopy visual image object
    """

    im = visual.ImageStim(win, img, pos=[0, 0], size=0.3, name=str(os.path.basename(img)))

    return im


def pause(win, time):
    """
        Pauses experiment on a given image for a specified amount of time.

        Arguments:
            win: psychopy window object
            time (float): time in seconds to present image

        return:
            None: image is presented on window for provided duration
    """

    win.flip()
    core.wait(time)


def key_instructions(win, valid_keys):
    """
        Creates text to output keyboard instructions to monitor.

        Arguments:
            win: psychopy window object
            valid_keys (list): keyboard keys users can press as a valid response

        return:
            instructions: psychopy visual text object
    """

    old = valid_keys[0]
    new = valid_keys[1]
    text = "On the keyboard, press '" + str(old) + "' for previously seen images and '" + str(new) + "' for new images"

    instructions = visual.TextStim(win, text=text, pos=(0, -0.2), height=0.02, color='red')

    return instructions


def display_image(win, img, delay, time, valid_keys, test=True, instructions=None):
    """
        Displays an image stimulus in window for a specified amount of time.

        Arguments:
            win: psychopy window object
            img: psychopy visual image object
            delay (float): delay or interval between images
            time (float): duration image will display
            valid_keys (list): valid input for keyboard keys
            test (bool): true if image is being displayed for test phase, false if not
            instructions: psychopy visual text object

        return:
            resp (list): keyboard responses
            rt (list): reaction times
            valid (list): list indicating if key(s) is/are valid
            start (float): starting time of image presentation
            end (float): ending time of image presentation
    """

    resp = []
    rt = []
    valid = []
    start = 0.0
    end = 0.0
    logging.LogFile(f=sys.stdout, level=logging.DATA, filemode='w')

    clock = core.Clock()

    event.clearEvents()
    clock.reset()

    img.draw()
    if test:
        instructions.draw()

    win.flip()
    logging.data(msg=str(img.name) + ' is presented', obj=clock.getTime())
    start = float(clock.getTime())

    trial = True
    while trial:
        if clock.getTime() >= time:
            win.flip()
            logging.data(msg=str(img.name) + ' done presenting.', obj=clock.getTime())
            end = float(clock.getTime())
            trial = False

        keys = event.getKeys(timeStamped=clock)
        if keys:
            rt.append(keys[0][1])
            if test:
                if keys[0][0] in valid_keys:
                    valid.append("Yes")
                    logging.data(msg=str(img.name) + ' done presenting.', obj=clock.getTime())
                    if keys[0][0] == valid_keys[0]:
                        resp.append("old")
                    elif keys[0][0] == valid_keys[1]:
                        resp.append("new")
                    trial = False
                else:
                    resp.append(keys[0][0])
                    valid.append("No")

    if test:
        if len(valid) == 0:
            valid.append("No")
        if (len(resp) == 0) and (len(rt) == 0):
            resp.append("None")
            rt.append(-1)

    win.flip()
    logging.data(msg="Blank Screen", obj=clock.getTime())
    core.wait(delay)

    if test:
        return resp, rt, valid
    else:
        return start, end


def study_phase(win, data, df, num, time, delay, trial, subj, path, valid_keys):
    """
        Simulates a run for the study phase portion of the experiment.

        Arguments:
            win: psychopy window object
            data (list): image dataset
            df (pandas dataframe): dataframe to store experimental data
            num (int): length of study list (number of images)
            delay (float): delay or interval between images
            time (float): duration image will display
            trial (int): trial number of experiment
            subj (int): subject number or id
            path (str): path to target directory to store data
            valid_keys (list): valid input for keyboard keys

        return:
            path (str): Experimental data in dataframe is stored in csv to target directory
    """

    for run in range(num):
        img = image_stim(win, data[run])
        df['Image'].loc[run] = str(img.name)

        start, end = display_image(win, img, delay, time, valid_keys, test=False, instructions=None)

        df['Start'].loc[run] = start
        df['End'].loc[run] = end
        df['Delay'].loc[run] = delay
        df['Valid Keys'].loc[run] = valid_keys

    create_directory("study_phase", path, subj, trial, df=df)

    return path


def test_phase(win, data, df, num, time, delay, trial, subj, path, valid_keys):
    """
        Simulates a run for the test phase portion of the experiment.

        Arguments:
            win: psychopy window object
            data (list): image dataset
            df (pandas dataframe): dataframe to store experimental data
            num (int): length of test list (number of images)
            delay (float): delay or interval between images
            time (float): duration image will display
            trial (int): trial number of experiment
            subj (int): subject number or id
            path (str): path to target directory to store data
            valid_keys (list): valid input for keyboard keys

        return:
            path (str): Experimental data in dataframe is stored in csv to target directory
    """

    for run in range(num):
        img = image_stim(win, data[run])
        df['Image'].loc[run] = str(img.name)

        instr = key_instructions(win, valid_keys)
        resp, rt, valid = display_image(win, img, delay, time, valid_keys, test=True, instructions=instr)

        df['Responses'].loc[run] = resp
        df['Reaction Time'].loc[run] = rt
        df['Valid Response'].loc[run] = valid

        if "None" in resp:
            df['Number of Responses'].loc[run] = 0
        else:
            df['Number of Responses'].loc[run] = len(resp)

    path = create_directory("test_phase", path, subj, trial, df=df)

    return path


def create_directory(name, path, subj, trial, df=None):
    """
        Creates a new directory at specified path if does not already exist and/or
        stores dataframe as csv.
        Directory format is: path + subject id/number + date + trial number

        Arguments:
            name (str): name of csv
            df (pandas dataframe): dataframe to store experimental data
            path (str): path to target directory to store data
            subj (int): subject number or id
            trial (int): trial number of experiment

        return:
            path: absolute path of new created directory
            csv_path: absolute path of new CSV file
    """

    if platform.system() == "Windows":
        sep = '\\'
    else:
        sep = '/'

    dt = date.today()
    path = os.path.join(path, str(subj) + sep + str(dt) + sep + str(trial + 1))
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
        print(f"New directory to store subject and run experimental data was created at: {path}")

    if df is None:
        return path
    else:
        csv_path = path + sep + name + '.csv'
        df.to_csv(csv_path)
        return csv_path


def create_df(num, subj, test=True):
    """
        Creates a new dataframe to store experimental data.

        Arguments:
            num (int): length of image list (number of images)
            subj (int): subject number or id
            test (bool): true if creating dataframe for test phase, else false

        return:
            df (pandas dataframe): an initialized dataframe
    """
    if test:
        columns = ['Subject ID', 'Date', 'Image', 'Reaction Time', 'Responses', 'Number of Responses', 'Valid Response']
    else:
        columns = ['Subject ID', 'Date', 'Seed', 'Valid Keys', 'Image', 'Start', 'End', 'Exp. Timing',
                   'Delay']

    df = pd.DataFrame(index=np.arange(num), columns=columns)

    df['Subject ID'] = subj

    current_date = datetime.now()
    df['Date'] = str(current_date)

    return df


def end_experiment(win, path, subj, trial, imgs):
    """
        Closes down the window and ends experiment.

        Arguments:
            win: psychopy window object
            path (str): absolute path to target directory
            subj (int): subject number or ID
            trial (int): trial number
            imgs (list): study phase set of images

        return:
            None: outputs closing remark to screen, results and shuts down window
    """
    end = visual.TextStim(win,
                          text='End of trial. Thank you for participating.',
                          pos=(0, 0), height=0.05, color='black')
    end.draw()

    win.flip()
    core.wait(3)
    win.flip()
    win.close()

    print(color.BOLD + color.BLUE + "Would the experimenter like to process the results? " + color.END)
    print(color.DARKCYAN + "Type 'Y' for yes, else for no: " + color.END)
    prompt = input()

    if str(prompt).lower() != 'y':
        exit()
    else:
        results_df = load_data(path)
        output_results(results_df, path, subj, trial, imgs)

    core.quit()


def output_text(win, text):
    """
        Displays specified text instructions to screen.

        Arguments:
            win: psychopy window object
            text (str): text to output

        return:
            None: outputs closing text to screen.
    """
    text_screen = visual.TextStim(win, text=text, pos=(0, 0), height=0.05, color='black')
    text_screen.draw()

    key_instr = visual.TextStim(win, text="Press any key to continue", pos=(0, -0.05), height=0.03, color='black')
    key_instr.draw()

    win.flip()

    key = event.waitKeys(keyList=None)
    win.flip()
