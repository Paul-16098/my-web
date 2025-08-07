import re
from glob import glob
import os
from typing import Literal

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

OUTPUT_SUB: dict[re.Pattern[str], str] = {
    re.compile(
        '<ul>\\s*<li><em><a href="([^"]+)">([^<>]*)</a></em></li>\\s*</ul>',
        re.I,
    ): r'<ul><li><a href="\1" style="color: black;text-decoration-line: none;"><cite>\2</cite></a></li></ul>'
}


def md2html(
    input: str, TOCList: list[str], index_run: bool = False
) -> tuple[Literal[1], str] | int:
    output: str = input[0:-3] + ".html"
    if input.endswith("index.md") and not index_run:
        with open(root + input, "rt", encoding="utf-8") as f:
            if f.read().startswith("<!-- TOC -->"):
                return (1, input)

    TOCList.append(output)
    os.system(
        f'showdown makehtml --flavor="github" -i {root + input} -o {root + output} 1>nul'
    )
    with open(root + output, "rt", encoding="utf-8") as f:
        output_raw = f.read()
    with open(root + output, "wt", encoding="utf-8") as f:
        new_output_raw = output_raw
        for p, s in OUTPUT_SUB.items():
            new_output_raw = p.sub(s, new_output_raw)

        f.write(
            f"<!DOCTYPE html><html><head><meta charset='utf-8' /><link rel='stylesheet' type='text/css' media='screen' href='main.css'></head><body>{new_output_raw}</body></html>"
        )
    return 0


def g_toc(TOCList, index: str):
    print("f:", root + index)
    TOCStrList: list[str] = ["<!-- TOC -->", "# toc\n"]
    for toc in TOCList:
        TOCStrList.append(f"- [{toc[0:-5]}]({toc})")
    toc = "\n".join(TOCStrList) + "\n\n---\n"
    with open(root + index, "wt", encoding="utf-8") as f:
        f.write(toc)


root = "./public/"


class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent):
        p: str = str(event.src_path)
        if event.event_type in {"modified", "created"}:
            print(event.event_type, ": ", p)
            if p.endswith(".md"):
                observer.unschedule_all()
                main()
                observer.schedule(event_handler, root, recursive=True)
        else:
            print(event.event_type, "?: ", p)


def main():
    TOCList: list[str] = []
    index: str | None = None
    for input in glob("**.*", root_dir=root):
        if not input.endswith(".md"):
            os.remove(root + input)
            continue
        o = md2html(input, TOCList)
        match o:
            case 0:
                pass
            case (1, index_path):
                index = index_path
            case _:
                print("W: r=U")
    if index is not None:
        g_toc(TOCList, index)
        md2html(index, TOCList, True)
    for input in glob("./_public/**.*"):
        dinput = input.replace("./_public\\", "./public\\")
        print(input, "=>", dinput)
        os.link(input, dinput)


main()
event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, root, recursive=True)
observer.start()

try:
    while observer.is_alive():
        observer.join(1)
except KeyboardInterrupt:
    pass

observer.stop()
observer.join()
