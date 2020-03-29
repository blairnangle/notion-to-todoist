#!/usr/bin/env python

from typing import Tuple
import config_loader
import notion_client
import todoist_client

config: dict = config_loader.load_config()
USER: str = config['notion']['user']
NOTION_API_TOKEN: str = config['notion']['api_token']
TODOIST_API_TOKEN: str = config['todoist']['api_token']


def count_todos(todos: list) -> Tuple[int, int]:
    undone: int = 0
    done: int = 0
    for todo in todos:
        if todo['done']:
            done += 1
        else:
            undone += 1

    return undone, done


def execute():
    for pair in config['migration']:
        todos: list = notion_client.get_todos(USER, pair['notion'], NOTION_API_TOKEN)
        notion_undone, notion_done = count_todos(todos)
        notion_total = notion_undone + notion_done

        print("{total} todos exported from Notion page \"{page}\" ({undone} undone and {done} done)".format(
            total=notion_total,
            page=pair['notion'],
            undone=notion_undone,
            done=notion_done))

        todoist_undone, todoist_done = todoist_client.create_tasks(pair['todoist'], todos, TODOIST_API_TOKEN)
        todoist_total = todoist_undone + todoist_done

        print("{total} tasks imported into Todoist project \"{project}\" ({undone} undone and {done} done)".format(
            total=todoist_total,
            project=pair['todoist'],
            undone=todoist_undone,
            done=todoist_done))


execute()
