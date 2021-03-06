#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
from parlai.scripts.display_data import display_data as display, setup_args
from parlai.agents.repeat_label.repeat_label import RepeatLabelAgent
from parlai.core.worlds import create_task

import unittest
import io
import itertools
from contextlib import redirect_stdout


def product_dict(dictionary):
    keys = dictionary.keys()
    vals = dictionary.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))


class TestWoW(unittest.TestCase):
    """Basic tests on the train_model.py example."""

    def test_output(self):
        dts = ['train', 'valid', 'test']
        main_task = 'wizard_of_wikipedia'
        variants = ['WizardOfWikipediaTeacher',
                    'WizardDialogKnowledgeTeacher',
                    'BasicdialogTeacher',
                    'DocreaderTeacher',
                    'GeneratorTeacher']
        variant_args = {
            'WizardOfWikipediaTeacher': {},
            'WizardDialogKnowledgeTeacher': {
                'label_type': ['response', 'chosen_sent'],
                'include_knowledge': [False, True],
                'include_checked_sentence': [False, True]
            },
            'BasicdialogTeacher': {
                'wizard_dialog': [False, True]
            },
            'DocreaderTeacher': {
                'teacher_type': ['docs', 'docs_sentence', 'more_docs',
                                 'more_docs_sentence', 'span']
            },
            'GeneratorTeacher': {
                'only_checked_knowledge': [False, True],
                'ignorant_dropout': [0, 0.5, 1]
            }
        }
        splits = ['random_split', 'topic_split']

        for datatype in dts:
            for task_var in variants:
                for split in splits:
                    task_name = '{}:{}:{}'.format(main_task, task_var, split)
                    opt_defaults = {
                        'task': task_name,
                        'datatype': datatype
                    }
                    task_args = variant_args[task_var]
                    if len(task_args) == 0:
                        print('Testing {} with args {}'.format(task_name,
                                                               opt_defaults))
                        self.run_display_test(opt_defaults)
                    else:
                        for combo in product_dict(task_args):
                            args = {**opt_defaults, **combo}
                            print('Testing {} with args {}'.format(
                                task_name,
                                args))
                            self.run_display_test(args)

    def run_display_test(self, kwargs):
        f = io.StringIO()
        with redirect_stdout(f):
            parser = setup_args()
            parser.set_defaults(**kwargs)
            opt = parser.parse_args()
            agent = RepeatLabelAgent(opt)
            world = create_task(opt, agent)
            display(opt)

        str_output = f.getvalue()
        self.assertTrue(
            '[ loaded {} episodes with a total of {} examples ]'.format(
                world.num_episodes(), world.num_examples()
            ) in str_output,
            'Wizard of Wikipedia failed with following args: {}'.format(opt)
        )


if __name__ == '__main__':
    unittest.main()
