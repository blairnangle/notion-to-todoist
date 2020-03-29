from notion import block
from notion.client import NotionClient

NOTION_URL = "https://www.notion.so/"


def get_todos(user, page, api_token):
    client: NotionClient = NotionClient(token_v2=api_token)
    todos: list = []
    notion_page: block = client.get_block(NOTION_URL + user + "/" + page)

    for child in notion_page.children:
        todos.append(
            {
                "content": child.title,
                "done": child.checked
            }
        )

    return todos
