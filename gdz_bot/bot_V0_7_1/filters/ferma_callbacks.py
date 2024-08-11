from aiogram.filters.callback_data import CallbackData
import logging

logger = logging.getLogger(__name__)
logger.info("started!")


class choose_book_CallbackFactory(CallbackData, prefix="cbk", sep="~"):
    """
    Callback factory for choosing a book. Sends a book's number as a parameter.

    Args:
        number_book (int): Number of the book to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.
    """

    number_book: int
    for_sl_book: bool = False


class add_or_del_on_ls_selected_books_CallbackFactory(
    CallbackData, prefix="selected_book", sep="~"
):
    """
    Callback factory for adding a book to the list of selected books.

    Sends a book's number as a parameter.
    """

    number_book: int
    del_book: bool = False
# increase priority


class increase_or_lower_priority_sl_book_CallbackFactory(CallbackData, prefix="inc", sep="~"):
    """
    Callback factory for increasing the priority of the selected book.
    """
    number_book: int
    coeficiant: int


class choose_section_CallbackFactory(CallbackData, prefix="csc", sep="~"):
    """
    Callback factory for choosing a section of the book.

    Sends a section's name as a parameter.

    Args:
        name_section (str): Name of the section to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.
    """

    name_section: str
    c: str = "a"


class choose_number_CallbackFactory(CallbackData, prefix="cnr", sep="~"):
    """
    Callback factory for choosing a number.

    Sends a number as a parameter.

    Args:
        number (str): Number to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.

    """

    number: str


class choose_obj_CallbackFactory(CallbackData, prefix="cobj", sep="~"):
    """
    Callback factory for choosing an object.

    Sends the chosen object's name as a parameter.

    Args:
        obj (str): Name of the object to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.

    """

    obj: str
    erase_user_data_up_to_this_point: bool = False


class choose_class_CallbackFactory(CallbackData, prefix="choose_class", sep="~"):
    """
    Callback factory for choosing a user's class.

    Sends the chosen class as a parameter.

    Args:
        user_class (int): Number of the class to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.

    """

    user_class: int
    erase_user_data_up_to_this_point: bool = False


class choose_author_CallbackFactory(CallbackData, prefix="choose_author", sep="~"):
    """
    Callback factory for choosing an author.

    Sends the chosen author as a parameter.

    Args:
        author (str): Name of the author to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.

    """

    author: str


class choose_book_and_cover_CallbackFactory(
    CallbackData, prefix="choose_cover", sep="~"
):
    """Callback factory for choosing a book and cover.

    Sends a book's number as a parameter.

    Args:
        number_book (int): Number of the book to choose.
        erase_user_data_up_to_this_point (bool): Whether to delete all user data
            up to this point. Default: False.

    """

    number_book: int
    erase_user_data_up_to_this_point: bool = False


class turn_over_CallbackFactory(CallbackData, prefix="turn_over", sep="~"):
    """Callback factory for turning over a page.

    Sends how many pages to turn over as a parameter.

    Args:
        add_current_page (int): Number of pages to turn over. Positive numbers
            mean turning over forward, negative numbers - backward.

    """

    name: str = ""
    add_current_page: int = 1
    for_sl_book: bool = False


class one_level_back_CallbackFactory(CallbackData, prefix="level_back", sep="~"):
    """Callback factory for going one level back from a certain level.

    Sends the level's name as a parameter.

    Args:
        level (str): Name of the level to go back from.

        level (str): Name of the level to go back from.
    """

    level: str = ""


class show_alert__will_be_soon_CallbackFactory(
    CallbackData, prefix="will_be_soon", sep="~"
):
    """Callback factory for showing alert about soon availability.

    Currently does nothing, but may be used in the future.
    """

    nothing: str = "choom"


class meny_CallbackFactory(CallbackData, prefix="meny", sep="~"):
    """Callback factory for main menu.

    Currently does nothing, but may be used in the future.
    """

    nothing: str = "choom"
