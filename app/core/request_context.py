from fastapi import Request


def get_request_id(request: Request) -> str:
    return request.state.request_id
