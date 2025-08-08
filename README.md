# my-web

## use

1. `pip install -r .\pyproject.toml` or
   `uv pip install -r .\pyproject.toml`

2. `npm install` or
   `pnpm install`

3. put the Markdown file to `./public` and o to `./_public`

4. `python ./md2html.py` or
   `vscode tasks: md2html`

5. `simple-http-server --ip 127.0.0.1 -i --nocache --try-file ./404.html` or
   `vscode tasks: start server`

## cofg

if `./public/index.md` exists and start with `<!-- TOC -->`
the `./md2html.py` will make toc.

## todo

- [x] [github markdown extension alerts](https://github.blog/changelog/2023-12-14-new-markdown-extension-alerts-provide-distinctive-styling-for-significant-content/)

## test

[the test md file](public/test.md) | [the test html file](public/test.html)

## note

the `./_public/github.css` form https://github.com/sindresorhus/github-markdown-css
