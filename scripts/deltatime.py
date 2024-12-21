import bge

def init(context):
    context.prev_frame_timestamp = bge.logic.getClockTime()

def update(context):
    timestamp = bge.logic.getClockTime()
    delta = timestamp - context.prev_frame_timestamp
    context.prev_frame_timestamp = timestamp
    return delta
