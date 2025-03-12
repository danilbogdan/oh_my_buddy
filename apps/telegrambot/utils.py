import re

from markdown_it import MarkdownIt

# _ * [ ] ( ) ~ ` > # + - = | { } . !
SPECIAL_CHARS_REGEX = r"([_\*\[\]\(\)~`>#+\-=|{}\.\!])"


def escape_special_chars(text: str) -> str:
    return re.sub(SPECIAL_CHARS_REGEX, r"\\\1", text)


def process_tokens(tokens) -> str:
    result = []
    for token in tokens:
        if token.type == "text":
            # Для текстовых токенов экранируем спецсимволы
            result.append(escape_special_chars(token.content))
        elif token.type == "code_inline":
            # inline-код оставляем без изменений
            result.append("`" + token.content + "`")
        elif token.type in ("code_block", "fence"):
            # Блочные элементы кода (fence — с информацией о языке)
            info = token.info.strip() if token.type == "fence" else ""
            if info:
                result.append(f"```{info}\n{token.content}\n```")
            else:
                result.append("```\n" + token.content + "\n```")
        elif token.type == "inline" and token.children:
            # Если токен inline содержит дочерние токены — обрабатываем их рекурсивно
            result.append(process_tokens(token.children))
        elif token.type.endswith("_open"):
            # Обрабатываем открывающие токены некоторых конструкций Markdown
            if token.tag == "em":
                result.append("*")
            elif token.tag == "strong":
                result.append("**")
            elif token.tag == "link":
                result.append("[")
            else:
                # Можно добавить обработку других тегов по необходимости
                pass
        elif token.type.endswith("_close"):
            # Обрабатываем закрывающие токены
            if token.tag == "em":
                result.append("*")
            elif token.tag == "strong":
                result.append("**")
            elif token.tag == "link":
                # Из закрывающего токена ссылки получаем URL (атрибут href)
                href = ""
                if token.attrs:
                    for attr in token.attrs:
                        if attr[0] == "href":
                            href = attr[1]
                            break
                result.append("](" + href + ")")
            else:
                pass
        elif token.type == "paragraph_open":
            # Для абзаца можно ничего не добавлять, его границы зададутся закрывающим токеном
            pass
        elif token.type == "paragraph_close":
            result.append("\n\n")
        else:
            # Для остальных токенов, если есть дочерние — обрабатываем их
            if token.children:
                result.append(process_tokens(token.children))
            else:
                result.append(token.content)
    return "".join(result)


def escape_markdown_message(message: str) -> str:
    md = MarkdownIt()
    tokens = md.parse(message)
    return process_tokens(tokens)
