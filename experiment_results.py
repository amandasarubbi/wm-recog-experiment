# Imports #
import pandas as pd
import os
from ast import literal_eval
from datetime import datetime, date


# Functions #
def load_data(path):
    """
        Loads data at specified CSV file path into a dataframe.

        Arguments:
            path (str): absolute path to CSV file.

        return:
            df (pandas dataframe): dataframe containing CSV contents
    """
    df = pd.read_csv(path,
                     encoding='iso-8859-1',
                     header='infer',
                     index_col=0,
                     skiprows=None,
                     low_memory=False,
                     converters={"Responses": literal_eval, "Reaction Time": literal_eval,
                                 'Valid Response': literal_eval})
    return df


def format_df(df, img_list):
    """
        Formats dataframe for results processing.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents
            img_list (list): list of images from study set

        return:
            df (pandas dataframe): dataframe containing formatted CSV contents
    """
    tmp = df[['Image', 'Reaction Time', 'Responses', 'Valid Response']]

    tmp = tmp.apply(pd.Series.explode)

    tmp['Study Imgs'] = tmp['Image'].apply(lambda x: any([os.path.basename(k) in x for k in img_list]))
    tmp['Hits'] = tmp.apply(hits, axis=1)
    tmp['False Alarms'] = tmp.apply(false_alarms, axis=1)
    tmp['New to New'] = tmp.apply(new_to_new, axis=1)
    tmp['New to Old'] = tmp.apply(new_to_old, axis=1)
    tmp['Valid RT'] = tmp.apply(valid_rt, axis=1)

    return tmp


def process_data(df):
    """
        Processes df contents to calculate proportion of hits, false alarms,
        and average reaction time.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            hit rate (float): hit rate ratio
            false_alarm_rate (float): false alarm rate ratio
            avg_rt (float): average rate of reaction time
    """

    hits = len(df[df['Hits'] == 1])
    false_alarm = len(df[df['False Alarms'] == 1])
    true_new = len(df[df['New to New'] == 1])
    false_new = len(df[df['New to Old'] == 1])

    old_items = hits + false_new
    new_items = false_alarm + true_new

    hit_rate = hits / old_items
    false_alarm_rate = false_alarm / new_items

    hit_rate = round(hit_rate, 2)
    false_alarm_rate = round(false_alarm_rate, 2)

    avg_rt = df['Valid RT'].astype(float).mean()
    avg_rt = round(avg_rt, 4)

    return hit_rate, false_alarm_rate, avg_rt


def store_results(path, data):
    """
        Stores results into a CSV at specified path.

        Arguments:
            path (str): absolute path to target directory
            data (list): results of data processing

        return:
            dir_path (str): absolute path to new CSV file
    """
    df = pd.DataFrame(data=[data],
                      columns=["Subject ID", 'Trial', 'Hit Ratio', 'False Alarm Ratio', 'Average RT (sec)'])

    dir_path = os.path.dirname(path)

    dt = datetime.now()
    format_dt = str(dt)

    dir_path = os.path.join(dir_path, format_dt + "_results.csv")
    df.to_csv(dir_path, index=False)

    return dir_path


def output_results(df, path, subj, trial, img_list):
    """
        Main driver function to perform processing and outputting of
        results

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents
            path (str): absolute path to target directory
            subj (int): subject number or ID
            trial (int): trial number
            img_list (list): list of images from study set

        return:
            None: outputs and or saves results
    """

    f_df = format_df(df, img_list)

    hit_ratio, false_alarm_ratio, rt_avg = process_data(f_df)

    data = [subj, trial, hit_ratio, false_alarm_ratio, rt_avg]

    print(f"The proportion of hits for Subject {subj}, Trial {trial} is {hit_ratio}.")
    print(f"The proportion of false alarms for Subject {subj}, Trial {trial} is {false_alarm_ratio}.")
    print(f"The average reaction time (seconds) for Subject {subj}, Trial {trial} is {rt_avg}.")

    print("Save results? Type 'Y' for yes, else for no: ")
    save = input()

    if str(save).lower() != 'y':
        exit()
    else:
        results = store_results(path, data)
        print(f"Results have been saved to: {results}")


def hits(df):
    """
        Processes dataframe for responses saying "old" for "old" images.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            df[col] (pandas dataframe): dataframe containing CSV contents
    """
    if df['Valid Response'] == "Yes":
        if (df['Responses'] == 'old') and (df['Study Imgs'] is True):
            return 1
        else:
            return 0


def false_alarms(df):
    """
        Processes dataframe for responses saying "old" for "old" new images.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            df[col] (pandas dataframe): dataframe containing CSV contents
    """
    if df['Valid Response'] == "Yes":
        if (df['Responses'] == 'old') and (df['Study Imgs'] is False):
            return 1
        else:
            return 0


def new_to_new(df):
    """
        Processes dataframe for responses saying "new" for "new" images.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            df[col] (pandas dataframe): dataframe containing CSV contents
    """
    if df['Valid Response'] == "Yes":
        if (df['Responses'] == 'new') and (df['Study Imgs'] is False):
            return 1
        else:
            return 0


def new_to_old(df):
    """
        Processes dataframe for responses saying "new" for "old" images.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            df[col] (pandas dataframe): dataframe containing CSV contents
    """
    if df['Valid Response'] == "Yes":
        if (df['Responses'] == 'new') and (df['Study Imgs'] is True):
            return 1
        else:
            return 0


def valid_rt(df):
    """
        Processes dataframe for responses that are valid.

        Arguments:
            df (pandas dataframe): dataframe containing CSV contents

        return:
            df[col] (pandas dataframe): dataframe containing CSV contents
    """
    if df['Valid Response'] == "Yes":
        return df['Reaction Time']
