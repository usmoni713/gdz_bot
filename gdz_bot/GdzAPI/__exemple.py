# -*- coding: utf-8 -*-
# by MrFriot
import asyncio
from time import time

import gdz_api


async def get_gdz():
    # User inputting class
    u_class: int = 8
    # User inputting subject
    u_subj: str = "География"
    # Find chapters with user parameters
    r_chapter: gdz_api.Chapter = await gdz_api.Api().get_chapter(u_class, u_subj)
    # print(f"chapter url: {r_chapter.url}")
    await r_chapter.get_books()
    for book in r_chapter.books:
        # Finding the right book
        if  'География' in book.title :
            # print(f"book url: {book.url}")
            structure: dict = await book.get_num_structure()
            print(f"\n\n{structure=}\n")
            # User inputting number
            u_section: str = "Номера"
            # User inputting number
            u_num: int = 1
            # Finding number
            r_num: gdz_api.Number = structure[u_section][u_num - 1]
            # print(f"number url: {r_num.url}")
            # Finding answer
            r_answers = await r_num.get_answers()
            # print(r_answers)
            break

if __name__ == "__main__":
    timer: float = time()
    asyncio.run(get_gdz())
    print("time of work:", time() - timer)
