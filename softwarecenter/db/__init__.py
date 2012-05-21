import logging
try:
    from debfile import DebFileApplication
    DebFileApplication  # pyflakes
except Exception, e:
    log_exception = True

    if type(e) is ImportError:
        if 'apt.debfile' in e.message:
            log_exception = False

    if log_exception:
        logging.exception("DebFileApplication import")

    class DebFileApplication():
        pass
