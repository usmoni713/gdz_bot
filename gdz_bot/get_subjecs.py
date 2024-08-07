import asyncio
from pprint import pprint
from GdzAPI import gdz_api


user = gdz_api.Api()


async def get_subjecs_for_class(class_: int) -> list[str]:
    """
    This function returns list of subjects to their classes
    :param class_: number of class
    :return: list of subjects
    """
    result: list[str] = []
    try:
        all_chapters = await user.get_available_chapters()
        for chapter in all_chapters:
            if chapter.class_ == class_:
                result.append(chapter.subject)
    except Exception as error:
        print(f"[ERR] can't get subjects | error: {error}")
    return result


async def main():
    tasks: list[asyncio.Task] = []
    for cl in range(1, 4):
        tasks.append(asyncio.create_task(gdz_api.get_subjecs_for_class(cl)))
    A = await asyncio.gather(*tasks)
    pprint(A)


if __name__ == "__main__":
    asyncio.run(main())
