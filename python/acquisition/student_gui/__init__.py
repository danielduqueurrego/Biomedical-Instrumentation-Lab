from __future__ import annotations


__all__ = ["StudentAcquisitionGui", "main"]


def __getattr__(name: str):
    if name == "StudentAcquisitionGui":
        from acquisition.student_gui.controller import StudentAcquisitionGui

        return StudentAcquisitionGui
    if name == "main":
        from acquisition.student_gui.controller import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
