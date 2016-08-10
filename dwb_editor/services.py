from django.utils.translation import ugettext as _


def sort_book_items(book, new_order):
    """Sort subset of items in a book.

    new_order - list of IDs.
    """
    if len(new_order) < 2:
        return

    # get old list of items
    order = book.get_item_order()

    # remove items that we are sorting except for the first element
    for item in new_order[1:]:
        order.remove(item)

    # add items back in order
    index = order.index(new_order[0])

    for item in new_order[1:]:
        index += 1
        order.insert(index, item)

    # save
    book.set_item_order(order)
    book.save()


def sort_book_chapters(book, new_order):
    """Sort H1 items in a book.

    new_order - list of IDs
    Order of items under H1 must not change.
    """
    items_to_sort = set(new_order)
    old_items = book.get_item_order()

    def get_subitems(all_items, first_item, end_item_set):
        """Return items starting with first_item.

        Ending before finding one from end_item_set.
        """
        found = False

        for item in all_items:
            if found:
                if item in end_item_set:
                    break
                else:
                    yield item
            else:
                if item == first_item:
                    found = True
                    yield item
                pass
            pass

    # Process each item in new_order
    new_items = []
    for item in new_order:
        # Add this item and all subitems to new_items """
        new_items = new_items + list(
            get_subitems(old_items, item, items_to_sort))

    # append all other items to the end
    new_items_set = set(new_items)
    for item in old_items:
        if item not in new_items_set:
            new_items.append(item)

    # make sure we didn't loose any items
    if len(new_items) != len(old_items):
        raise Exception(
            _("Sorting of chapters failed."))

    book.set_item_order(new_items)
    book.save()
