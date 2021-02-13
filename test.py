from datetime import datetime, timedelta

from .main import deep_diff

if __name__ == "__main__":
    today = datetime.today()
    tests = [
        ({"name": 'my object', "description": 'it\'s an object!', "details": {"it": 'has', "an": 'array', "with": ['a', 'few', 'elements']}},
         {"name": 'updated object', "description": 'it\'s an object!', "details": {"it": 'has', "an": 'array', "with": ['a', 'few', 'more', 'elements', {"than": 'before'}]}}),
        (1, 2),
        (1, None),
        (None, 1),
        (1, 1),
        ("asd", "asd"),
        ("asd", "qwe"),
        ({"ciao": 1}, {"ciao": 2}),
        ({"ciao": 1}, {"ehi": 1, "ciao": 2}),
        ({"ehi": 1, "ciao": 2}, {"ciao": 1}),
        ({"ciao": 1}, {"ciao2": 1}),
        ({"ciao": 1}, {"ciao2": 2}),
        ({"ciao": {"ehi": 1}}, {"ciao": {"ehi": 1}}),
        ({"ciao": {"ehi": 2}}, {"ciao": {"ehi": 1}}),
        ({"ciao": {"ehi": 1}}, {"ciao": {"ehi": 2}}),
        ({"ciao": {"ehi": 1}}, {"ciao2": {"ehi": 12}}),
        ({"ciao": {"ehi": 1}}, {"ciao2": {"ehi2": 1}}),
        ({"ciao": {"ehi1": 1}}, {"ciao": {"ehi": 1}}),
        ({"ciao": {"ehi": 2}}, {"ciao": {"ehi": 1}}),
        ([1, 2, 3], [1, 2, 3]),
        ([1, 2, 3], [1, 3, 3]),
        ([1, 2, 3], [1, 3, 2]),
        ([1, 2], [1, 2, 3]),
        ([1, 2, 3], [2, 3]),
        ([1, 2, 3], [2, 1]),
        ([{"ehi": 2}, 2, 3], [{"ehi": 2}, 2, 3]),
        ([{"ehi": 2}, 2, 3], [{"ehi": 2}, 2, 4]),
        ([{"ehi": 2}, 2, 3], [2, {"ehi": 2}, 3]),
        ([{"ehi": 2}, 2, 3], [2, {"ehi": 1}, 3]),
        ([{"ehi": 2}, 2, 3], [2, {"ciao": 2}, 3]),
        ({"a": [1, 2]}, {"a": [1, 2]}),
        ({"a": [1, 2]}, {"a": [2, 1]}),
        ({"a": [1]}, {"a": [2, 1]}),
        ({"a": [1, 2]}, {"a": [1]}),
        ({"a": [1, 2]}, {"a": [2, 1, 3]}),
        (today, today),
        (today, datetime.today() - timedelta(1))
    ]
    for test in tests:
        changes = deep_diff(test[0], test[1])
        changes = [x.__dict__ for x in changes]
        changes_oi = deep_diff(test[0], test[1], order_independent=True)
        changes_oi = [x.__dict__ for x in changes_oi]
        print("next")
