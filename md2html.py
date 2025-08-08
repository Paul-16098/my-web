import re
from glob import glob
import os
from typing import Literal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# 定義輸出替換規則
OUTPUT_SUB: dict[re.Pattern[str], str] = {
    re.compile(
        r'<ul>\s*<li><em><a href="([^"]+)">([^<>]*)</a></em></li>\s*</ul>',
        re.I,
    ): r'<ul><li><a href="\1" style="color: black;text-decoration-line: none;"><cite>\2</cite></a></li></ul>',
    re.compile(
        r"<blockquote>\s*<p>\[!note\]<br />(([\s\w]|<br />)*)</p>\s*</blockquote>", re.I
    ): r'<div class="markdown-alert markdown-alert-note" dir="auto"><p class="markdown-alert-title" dir="auto"><svg class="octicon octicon-info mr-2" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path></svg>Note</p><p dir="auto">\1</p></div>',
    re.compile(
        r"<blockquote>\s*<p>\[!important\]<br />(([\s\w]|<br />)*)</p>\s*</blockquote>",
        re.I,
    ): r'<div class="markdown-alert markdown-alert-important" dir="auto"><p class="markdown-alert-title" dir="auto"><svg class="octicon octicon-report mr-2" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25Zm1.75-.25a.25.25 0 0 0-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h6.5a.25.25 0 0 0 .25-.25v-9.5a.25.25 0 0 0-.25-.25Zm7 2.25v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>Important</p><p dir="auto">\1</p></div>',
}


# 將 Markdown 轉換為 HTML 的函數
def md2html(
    input: str, TOCList: list[str], index_run: bool = False
) -> tuple[Literal[1], str] | int:
    output: str = input[0:-3] + ".html"  # 將 .md 後綴替換為 .html
    if input.endswith("index.md") and not index_run:
        with open(root + input, "rt", encoding="utf-8") as f:
            # 檢查是否以 TOC 標記開始
            if f.read().startswith("<!-- TOC -->"):
                return (1, input)  # 返回特殊值以指示索引文件

    # 使用 showdown 將 Markdown 轉換為 HTML
    os.system(
        f'showdown makehtml --flavor="github" -i {root + input} -o {root + output} 1>nul'
    )
    with open(root + output, "rt", encoding="utf-8") as f:
        output_raw = f.read()  # 讀取生成的 HTML 文件
    with open(root + output, "wt", encoding="utf-8") as f:
        new_output_raw = output_raw
        # 應用替換規則
        for p, s in OUTPUT_SUB.items():
            new_output_raw = p.sub(s, new_output_raw)

        f.write(html_t.replace("{}", new_output_raw))  # 寫入新的 HTML 文件
    return 0


# 生成目錄的函數
def MakeToc(TOCList: list[str], index: str):
    print("Generating TOC for:", root + index)
    TOCStrList: list[str] = ["<!-- TOC -->", "# toc\n"]
    for toc in TOCList:
        TOCStrList.append(f"- [{'.'.join(toc.split('.')[0:-1])}]({toc})")
    toc = "\n".join(TOCStrList)
    with open(root + index, "wt", encoding="utf-8") as f:
        f.write(toc)  # 寫入目錄內容


root = "./public/"  # 定義根目錄


# 自定義事件處理程序
class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent):
        p: str = str(event.src_path)
        if event.event_type in {"modified", "created"}:
            print(event.event_type, ": ", p)
            if p.endswith(".md"):
                set_observer()  # 重新設置觀察者
        else:
            print(event.event_type, "?: ", p)


# 主函數，用於處理 Markdown 文件
def main():
    TOCList: list[str] = []
    index: str | None = None
    for input in glob("**.*", root_dir=root):
        if not input.endswith(".md"):
            os.remove(root + input)  # 刪除非 Markdown 文件
            continue
        o = md2html(input, TOCList)  # 轉換 Markdown 為 HTML
        match o:
            case 0:
                pass
            case (1, index_path):
                index = index_path  # 記錄索引文件路徑
            case _:
                print("Warning: Unexpected return value")

    # 生成公用文件的鏈接
    for input in glob("./_public/**.*"):
        dinput = input.replace("./_public\\", ".\\public\\")
        print(input, "=>", dinput)
        os.link(input, dinput)

    # 收集所有已處理的 Markdown 文件以生成目錄
    for input in glob("**.*", root_dir=root):
        for ext in (".html", ".txt"):
            c = False
            for name in ("index.md", "404.html"):
                if input.startswith(name):
                    c = True
            if c:
                continue
            if input.endswith(ext):
                TOCList.append(input)  # 添加到目錄列表

    # 如果有索引文件，生成目錄
    if index is not None:
        MakeToc(TOCList, index)
        md2html(index, TOCList, True)


# 讀取 HTML 模板
with open("./html-t.html", "rt", encoding="utf-8") as f:
    html_t = f.read()


# 設置文件監視器
def set_observer():
    observer.unschedule_all()  # 取消所有已安排的任務
    main()  # 重新執行主函數
    observer.schedule(event_handler, root, recursive=True)  # 重新安排事件監視


# 首次執行主函數
main()

# 初始化文件系統監視器
event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, root, recursive=True)
observer.start()

try:
    while observer.is_alive():
        observer.join(1)  # 保持監視器運行
except KeyboardInterrupt:
    pass  # 捕獲鍵盤中斷

# 停止監視器
observer.stop()
observer.join()
