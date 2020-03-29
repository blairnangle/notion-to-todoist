import json
import uuid
from typing import Tuple

import requests
from ratelimit import limits, sleep_and_retry

TODOIST_URL = "https://api.todoist.com/rest/v1/"


def _get_project_id(name: str, headers: dict) -> int:
    projects: list = requests.get(
        TODOIST_URL + "projects",
        headers=headers).json()

    for project in projects:
        if project['name'] == name:
            return project['id']


def _project_exists(name: str, headers: dict) -> bool:
    if 200 == requests.get(
            TODOIST_URL + "projects/" + str(_get_project_id(name, headers)),
            headers=headers).status_code:
        return True
    else:
        return False


def _create_project(name: str, headers: dict) -> None:
    local_headers: dict = headers.copy()
    local_headers["Content-Type"] = "application/json"
    local_headers["X-Request-Id"] = str(uuid.uuid4())

    requests.post(
        TODOIST_URL + "projects",
        data=json.dumps(
            {
                "name": name
            }
        ),
        headers=local_headers).json()


@sleep_and_retry
@limits(calls=15, period=60)
def _create_task(content: str, project_id: int, headers: dict) -> json:
    local_headers: dict = headers.copy()
    local_headers["Content-Type"] = "application/json"
    local_headers["X-Request-Id"] = str(uuid.uuid4())

    for i in range(0, 5):
        while True:
            try:
                response = requests.post(
                    TODOIST_URL + "tasks",
                    data=json.dumps(
                        {
                            "content": content,
                            "project_id": project_id
                        }
                    ),
                    headers=local_headers)
            except Exception:
                continue
            return response


@sleep_and_retry
@limits(calls=15, period=60)
def _close_task(task_id: int, headers) -> None:
    requests.post(TODOIST_URL + "tasks/" + str(task_id) + "/close", headers=headers)


def create_tasks(project: str, todos: list, api_token: str) -> Tuple[int, int]:
    headers = {"Authorization": "Bearer %s" % api_token}

    if not _project_exists(project, headers):
        _create_project(project, headers)

    project_id: int = _get_project_id(project, headers)

    undone: int = 0
    done: int = 0

    for todo in todos:
        task_id: int = _create_task(todo['content'], project_id, headers).json()['id']
        if todo['done']:
            _close_task(task_id, headers)
            done += 1
        else:
            undone += 1

    return undone, done
