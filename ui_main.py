"""
This script executes a working memory recognition-designed experiment based on user/experimenter inputs.
Participant trial data is read into unique dataframes that are converted into CSV files and stored in a 
new user-specified local directory. At the end of the trial, the user/experimenter can indicate whether
they would like to calculate and locally save experiment trial metrics.

- This script serves as the driver program for "experiment.py" and "experiment_results.py"

"""
#########################################################################
__author__ = "Amanda Sarubbi"

#########################################################################
from experiment_backend import *
from experiment_results import *


# Global Variables ######################################################

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


# Functions ##############################################################

def get_info():
    """
        Prompts experimenter for absolute paths of dataset and directory to save
        data generated during experiment as well as a seed for random generator.

        return:
            dataset_path (str): absolute path to parent directory of dataset
            save_path (str): target path to an existing or new directory to save experiment data
    """
    print(
        color.BOLD + color.BLUE + "Experimenter must enter the following information prior to starting the experiment:" + color.END)
    print(color.DARKCYAN + "Enter the absolute path to the parent directory of the dataset: " + color.DARKCYAN)
    dataset_path = input()
    print(
        color.DARKCYAN + "Enter the target path to an existing or new directory to save experiment data: " + color.END)
    save_path = input()
    print(color.DARKCYAN + "Enter a seed: " + color.END)
    seed = input()
    print(color.DARKCYAN + "Enter the number of trials for the experiment: " + color.END)
    trials = input()
    print(color.DARKCYAN + "Enter the time delay between images: " + color.END)
    delay = input()
    print(color.DARKCYAN + "Enter the valid keyboard key for old: " + color.END)
    old_key = input()
    print(color.DARKCYAN + "Enter the valid keyboard key for new: " + color.END)
    new_key = input()

    keys = [old_key, new_key]

    if not os.path.exists(dataset_path):
        print(
            color.BOLD + color.RED + color.UNDERLINE + "Invalid input. Dataset directory does not exist:" + color.END)
        print(dataset_path)
        print(color.BOLD + color.RED + "Exiting." + color.END)
        exit(1)
    if (not seed.isdigit()) or (not trials.isdigit()) or (not delay.replace('.', '', 1).isdigit()):
        print(
            color.BOLD + color.RED + color.UNDERLINE + "Invalid input. Must be an integer:" + color.END)
        print(color.BOLD + color.RED + "Exiting." + color.END)
        exit(1)

    return dataset_path, save_path, int(seed), int(trials), float(delay), keys


def main(win, dataset_dir, target_dir, seed, trials, delay, keys):
    subject, num_images, timing = experiment_info()

    df_study = create_df(num_images, subject, test=False)
    df_test = create_df(num_images * 2, subject, test=True)

    df_study['Seed'] = seed
    df_study['Exp. Timing'] = timing

    dataset = add_data(dataset_dir)

    study_data, test_data = generate_datasets(seed, num_images, dataset)

    test_path = ""

    for trial in range(trials):
        output_text(win, "Now starting the study phase of Trial: " + str(trial + 1))
        study_path = study_phase(win,
                                 study_data, df_study, num_images, timing, delay, trial, subject, target_dir, keys)
        output_text(win, "End of study phase of Trial: " + str(trial + 1))

        output_text(win, "Now starting the test phase of Trial: " + str(trial + 1))
        test_path = test_phase(win,
                               test_data, df_test, num_images * 2, timing, delay, trial, subject, target_dir, keys)
        output_text(win, "End of test phase of Trial: " + str(trial + 1))

    end_experiment(win, test_path, subject, trials, study_data)


if __name__ == '__main__':

    first_dir, sec_dir, rseed, num_tri, num_del, val_keys = get_info()

    try:
        win = visual.Window([800, 800], fullscr=False, monitor='testMonitor', screen=0, allowGUI=True,
                            units='height', color='white')

        main(win, first_dir, sec_dir, rseed, num_tri, num_del, val_keys)

    except Exception as ex:
        win.close()
        print(ex)
        core.quit()
