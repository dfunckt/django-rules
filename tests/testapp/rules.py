from __future__ import absolute_import

import rules


# Predicates

@rules.predicate
def is_book_author(user, book):
    if not book:
        return False
    return book.author == user


is_editor = rules.is_group_member('editors')


# Rules

rules.add_rule('change_book', is_book_author | is_editor)
rules.add_rule('delete_book', is_book_author)


# Permissions

rules.add_perm('testapp.change_book', is_book_author | is_editor)
rules.add_perm('testapp.delete_book', is_book_author)
