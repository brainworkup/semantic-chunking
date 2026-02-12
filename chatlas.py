# chatlas

import os
from chatlas import ChatOllama

chat = ChatOllama(
    model = "gemma3:1b",
    system_prompt = "You are a terse and helpful assistant.",
)

chat.console()

from chatlas import ChatOllama
from shiny.express import ui

chat = ui.Chat(
    id="ui_chat"
)
chat.ui()

chat_model = ChatOllama(model = "gemma3:1b")

@chat.on_user_submit
async def handle_user_input():
    response = chat_model.stream(chat.user_input())
    await chat.append_message_stream(response)
