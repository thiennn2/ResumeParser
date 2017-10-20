"""
coding=utf-8
"""
import logging

import os
import pandas
import yaml

CONFS = None

AVAILABLE_EXTENSIONS = {'.csv', '.doc', '.docx', '.eml', '.epub', '.gif', '.htm', '.html', '.jpeg', '.jpg', '.json',
                        '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx', '.ps', '.psv', '.rtf', '.tff',
                        '.tif', '.tiff', '.tsv', '.txt', '.wav', '.xls', '.xlsx'}


def load_confs(confs_path='../confs/confs.yaml'):
    # TODO Docstring
    global CONFS

    if CONFS is None:
        try:
            CONFS = yaml.load(open(confs_path))
        except IOError:
            confs_template_path = confs_path + '.template'
            logging.warn(
                'Confs path: {} does not exist. Attempting to load confs template, from path: {}'.format(confs_path,
                                                                                                         confs_template_path))
            CONFS = yaml.load(open(confs_template_path))
    return CONFS


def get_conf(conf_name):
    return load_confs()[conf_name]

def archive_dataset_schemas(step_name, local_dict, global_dict):
    """
    Archive the schema for all available Pandas DataFrames
     - Determine which objects in namespace are Pandas DataFrames
     - Pull schema for all available Pandas DataFrames
     - Write schemas to file
    :param step_name: The name of the current operation (e.g. `extract`, `transform`, `model` or `load`
    :param local_dict: A dictionary containing mappings from variable name to objects. This is usually generated by
    calling `locals`
    :type local_dict: dict
    :param global_dict: A dictionary containing mappings from variable name to objects. This is usually generated by
    calling `globals`
    :type global_dict: dict
    :return: None
    :rtype: None
    """
    logging.info('Archiving data set schema(s) for step name: {}'.format(step_name))

    # Reference variables
    data_schema_dir = get_conf('data_schema_dir')
    schema_output_path = os.path.join(data_schema_dir, step_name + '.csv')
    schema_agg = list()

    env_variables = dict()
    env_variables.update(local_dict)
    env_variables.update(global_dict)

    # Filter down to Pandas DataFrames
    data_sets = filter(lambda (k, v): type(v) == pandas.DataFrame, env_variables.iteritems())
    data_sets = dict(data_sets)

    for (data_set_name, data_set) in data_sets.iteritems():
        # Extract variable names
        logging.info('Working data_set: {}'.format(data_set_name))

        local_schema_df = pandas.DataFrame(data_set.dtypes, columns=['type'])
        local_schema_df['data_set'] = data_set_name

        schema_agg.append(local_schema_df)

    # Aggregate schema list into one data frame
    agg_schema_df = pandas.concat(schema_agg)

    # Write to file
    agg_schema_df.to_csv(schema_output_path, index_label='variable')